from math import round
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options)


def get_copper_prices(url="https://comexlive.org/copper/", headless=True):
    driver = create_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-table"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all("table", class_="main-table bold")
        high, low, open_price = None, None, None

        for table in tables:
            header_cells = table.find_all("td")
            headers = [cell.get_text(strip=True).lower() for cell in header_cells]
            if "high" in headers and "low" in headers and "open" in headers:
                data_row = table.find_all("tr")[1]
                data_cells = data_row.find_all("td")
                if len(data_cells) == 3:
                    high = float(data_cells[0].get_text(strip=True))
                    low = float(data_cells[1].get_text(strip=True))
                    open_price = float(data_cells[2].get_text(strip=True))
                break
        return high, low, open_price
    finally:
        driver.quit()

# Example usage
high, low, open_price = get_copper_prices()
print("High:", high)
print("Low:", low)
print("Open:", open_price)

def update_files(file_path, low, high,opening):
    df = pd.read_csv(file_path, engine='python')

    from datetime import datetime, timedelta
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%d %b %Y')

    print(df.head())
    new_row = pd.DataFrame([{
        'Date': yesterday_str,
        'Low': low,
        'High': high,
        'Last': round((low+high)/2,3),
        'Change': 0,
        '% Change': 0
    }])

    df = pd.concat([new_row, df], ignore_index=True, axis=0)
    print(df.head())

    
    df.to_csv(file_path, index=False)
    print("file updated.")

update_files('COMEX Copper.csv', low, high, open_price)
