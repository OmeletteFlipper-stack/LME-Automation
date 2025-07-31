from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options)

def update_files(file_path, bid, offer):
    if bid is None or offer is None:
        print("Bid or offer is None. Skipping file update.")
        return  # Exit early if data is invalid

    df = pd.read_csv(file_path, engine='python')
    from datetime import datetime, timedelta

    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%d %b %Y')
    print(df.head())

    new_row = pd.DataFrame([{
        'Date': yesterday_str,
        'Low': round(bid / 2204.62,4),
        'High': round(offer / 2204.62,4),
        'Last': round(((bid + offer) / 2) / 2204.62,4),
        'Change': 0,
        '% Change': 0
    }])

    df = pd.concat([new_row, df], ignore_index=True, axis=0)
    print(df.head())

    df.to_csv(file_path, index=False)
    print("File updated.")

commodity_Sites = {"Zinc" : "https://www.lme.com/en/metals/non-ferrous/lme-zinc#Summary",
                   "Aluminum" : "https://www.lme.com/en/metals/non-ferrous/lme-aluminium#Trading+summary",
                   "Copper" : "https://www.lme.com/en/metals/non-ferrous/lme-copper#Trading+summary"}

def scrape_commodity_prices(url):
    driver = create_driver()
    driver.get(url)
    try:
        # Wait for the table body to be loaded (more reliable than a specific cell)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.data-set-table__body'))
        )
    except Exception as e:
        print("Timed out waiting for page to load:", e)
        driver.quit()
        return None, None

    # Parse the page with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()  # Close the browser after loading and parsing

    # Find the row for "3-month"
    rows = soup.find_all('tr', class_='data-set-table__row')
    for row in rows:
        contract_cell = row.find('th', attrs={'data-table-column-header': 'Contract'})
        if contract_cell and contract_cell.get_text(strip=True) == '3-month':
            bid_cell = row.find('td', attrs={'data-table-column-header': 'Bid'})
            offer_cell = row.find('td', attrs={'data-table-column-header': 'Offer'})

            if bid_cell and offer_cell:
                bid = float(bid_cell.get_text(strip=True).replace(',', ''))
                offer = float(offer_cell.get_text(strip=True).replace(',', ''))
                print("3-month Bid:", bid, "\n3-month Offer:", offer)
                return bid, offer

    print("3-month contract not found.")

    
def zinc_scrape(url):
    driver = create_driver()
    driver.get(url)
    try:
        # Wait up to 10 seconds for the "Bid" cell to be present in the DOM
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/main/div[1]/div/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]"))
        )

    except Exception as e:
        print("Timed out waiting for page to load:", e)
        driver.quit()
        return None, None
    html =  driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    bid_cell = soup.find('td', attrs={'data-table-column-header': 'Bid'})
    offer_cell = soup.find('td', attrs={'data-table-column-header': 'Offer'})
    bid_cell = bid_cell.get_text(strip=True)
    offer_cell = offer_cell.get_text(strip=True)

    print("Bid:", bid_cell
          , "\nOffer:", offer_cell)
    return float(bid_cell), float(offer_cell)


print("Zinc")
zincBid, zincOffer = scrape_commodity_prices(commodity_Sites['Zinc'])
print("Aluminum")
aluBid, aluOffer = scrape_commodity_prices(commodity_Sites['Aluminum'])
print("Copper")
coppBid, coppOffer = scrape_commodity_prices(commodity_Sites['Copper'])

update_files('LME Zinc.csv', zincBid, zincOffer)
update_files('LME Aluminum.csv', aluBid, aluOffer)  
update_files('LME Copper.csv', coppBid, coppOffer)
