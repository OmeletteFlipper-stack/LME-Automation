import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options)

driver = create_driver()
driver.get('https://www.tradingview.com/symbols/LME-UP1%21/ideas/?contract=UPQ2025')

price_element = float(WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".last-zoF9r75I.js-symbol-last > span")
    )
).text.replace(",",""))
def update_files(file_path,opening):
    df = pd.read_csv(file_path, engine='python')

    from datetime import datetime, timedelta
    today_str = datetime.today().strftime('%d %b %Y')

    print(df.head())
    new_row = pd.DataFrame([{
        'Date': today_str,
        'Low': None,
        'High': None,
        'Last': round(opening/2204.62,4),
        'Change': None,
        '% Change': None
    }])

    df = pd.concat([new_row, df], ignore_index=True, axis=0)
    df['Change'] = round(df['Last'] - df['Last'].shift(-1), 2)
    df['% Change'] = round(df['Change'] / df['Last'].shift(-1), 3)
    print(df.head())

    
    df.to_csv(file_path, index=False)
    print("file updated.")

update_files('Midwest Premium.csv',price_element)
