print('''        
               AAA               BBBBBBBBBBBBBBBBB   BBBBBBBBBBBBBBBBB   
              A:::A              B::::::::::::::::B  B::::::::::::::::B  
             A:::::A             B::::::BBBBBB:::::B B::::::BBBBBB:::::B 
            A:::::::A            BB:::::B     B:::::BBB:::::B     B:::::B
           A:::::::::A             B::::B     B:::::B  B::::B     B:::::B
          A:::::A:::::A            B::::B     B:::::B  B::::B     B:::::B
         A:::::A A:::::A           B::::BBBBBB:::::B   B::::BBBBBB:::::B 
        A:::::A   A:::::A          B:::::::::::::BB    B:::::::::::::BB  
       A:::::A     A:::::A         B::::BBBBBB:::::B   B::::BBBBBB:::::B 
      A:::::AAAAAAAAA:::::A        B::::B     B:::::B  B::::B     B:::::B
     A:::::::::::::::::::::A       B::::B     B:::::B  B::::B     B:::::B
    A:::::AAAAAAAAAAAAA:::::A      B::::B     B:::::B  B::::B     B:::::B
   A:::::A             A:::::A   BB:::::BBBBBB::::::BBB:::::BBBBBB::::::B
  A:::::A               A:::::A  B:::::::::::::::::B B:::::::::::::::::B 
 A:::::A                 A:::::A B::::::::::::::::B  B::::::::::::::::B  
AAAAAAA                   AAAAAAABBBBBBBBBBBBBBBBB   BBBBBBBBBBBBBBBBB                                                                                                                                                  
''')
print("This code is designed to scrape multiple data sources and export the data of certain metals at 9am EST to a CSV.")
import pandas as pd
websites = {'aluminum': 'https://www.lme.com/en/metals/non-ferrous/lme-aluminium#Trading+summary', 
            'copper':'https://www.lme.com/en/metals/non-ferrous/lme-copper#Trading+summary', 
            'zinc' : 'https://www.lme.com/en/metals/non-ferrous/lme-zinc#Summary'}  #   A dictionary that holds all the LME Websites
files = {
    'Aluminum' : "LME Aluminum.csv",
    'Copper' :"LME Copper.csv",
    'Zinc' : "LME Zinc.csv"
}

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=options)

def scrape(website):
  from selenium.webdriver.support.ui import WebDriverWait
  bids = offers = None
  driver = create_driver()
  try:
    # Open the website
    driver.get(website)
    
    WebDriverWait(driver, 10).until(
            lambda d: float(d.find_element(
                By.XPATH, 
                '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'
            ).text) >= 1
        )

    print("Website opened")
    offer = driver.find_element(
    By.XPATH, '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'
    )

    offer = driver.find_element(
        By.XPATH, 
        '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[2]'
      )

    bids, offers =  float(bid.text), float(offer.text)
    driver.quit()
  finally:
      
    print("prices scraped: ",bids, " ",offers)
    return bids, offers
    

def update_files(file_path, bid, offer):
    df = pd.read_csv(file_path,skiprows=2, skipfooter=1, engine='python')
    from datetime import datetime, timedelta
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%d %b %Y')
    print(df.head())
    new_row = pd.DataFrame([{
        'Date': yesterday_str,
        'Low': 0,
        'High': 0,
        'Last': ((bid + offer) / 2) / 2204.62,
        'Change': 0,
        '% Change': 0
    }])

    df = pd.concat([new_row, df], ignore_index=True, axis=0)
    print(df.head())

    
    df.to_csv(file_path, index=False)
    print("file updated.")
  
if __name__ == "__main__":
  print('aluminum')
  bids, offers = scrape(websites['aluminum']) # aluminum
  update_files(files['Aluminum'], bids, offers)

  print('copper')
  bids, offers = scrape(websites['copper'])   # copper 
  update_files(files['Copper'], bids, offers)
  
  driver = create_driver()
  print('zinc')
  try:  # Zinc
      driver.get(websites['zinc'])
      print("Website opened")
      time.sleep(1)
      bid = driver.find_element(
          By.XPATH,
          '/html/body/main/div[1]/div/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'
          )
      bids = float(bid.text)
  finally:
      driver.quit()
  update_files(files['Zinc'], bids, bids)

