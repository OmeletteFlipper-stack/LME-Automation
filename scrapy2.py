import pandas as pd

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
websites = {'aluminum': 'https://www.lme.com/en/metals/non-ferrous/lme-aluminium#Trading+summary', 
            'copper':'https://www.lme.com/en/metals/non-ferrous/lme-copper#Trading+summary', 
            'zinc' : 'https://www.lme.com/en/Metals/Non-ferrous/LME-Zinc#Intraday+prices+and+monthly+quotes'}  #   A dictionary that holds all the LME Websites
files = {
    'Aluminum' : "LME Aluminum.csv",
    'Copper' :"LME Copper.csv",
    'Zinc' : "LME Zinc.csv"
}
from selenium import webdriver
from selenium.webdriver.common.by import By
from shutil import which
from selenium.webdriver.firefox.options import Options

import time

def scrape(website):
  options = Options()
    options.headless = True  # headless mode for CI

    firefox_path = which("firefox")
    if firefox_path:
        options.binary_location = firefox_path

    driver = webdriver.Firefox(options=options)
    try:
        # Open the website
        driver.get(website)
        print("Website opened")

        time.sleep(1)
        bid = driver.find_element(
            By.XPATH,
            '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'
            )
        offer = driver.find_element(
            By.XPATH, 
            '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[2]'
        )

        bids, offers =  float(bid.text), float(offer.text)
        driver.quit()
    finally:
        print("prices scraped")
        return bids, offers
        

def update_files(file_path, bid, offer):
    df = pd.read_csv(file_path,skiprows=2, skipfooter=1, engine='python')
    from datetime import datetime, timedelta
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%d %b %Y')
    print(df.head())
    new_row = pd.DataFrame([{
        'Date': yesterday_str,
        'Low': bid / 2204.62,
        'High': offer / 2204.62,
        'Last': ((bid + offer) / 2) / 2204.62,
        'Change': None,
        '% Change': None
    }])

    df = pd.concat([new_row, df], ignore_index=True, axis=0)
    print(df.head())

    
    df.to_csv(file_path, index=False)
    print("file updated.")

bids, offers = scrape(websites['aluminum']) # aluminum
update_files(files['Aluminum'], bids, offers)

bids, offers = scrape(websites['copper'])   # copper 
update_files(files['Copper'], bids, offers)

driver = webdriver.Firefox()
try:

    driver.get(websites['zinc'])
    print("Website opened")
    time.sleep(1)
    bid = driver.find_element(
        By.XPATH,
        '/html/body/main/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'
        )
finally:
    bids = float(bid.text)
    driver.quit()
update_files(files['Zinc'], bids, bids)
