

import requests
from bs4 import BeautifulSoup

from urllib.request import Request, urlopen

from blm_scrapper import NBCScraper



from selenium import webdriver
import selenium.webdriver.support.ui as ui

import pandas as pd

#/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome  --user-data-dir="~/ChromeProfile1" --remote-debugging-port=9222
import os

from  datetime import datetime


def fetch_article_html(driver, article_url):
    try:
        driver.get(article_url)

        headline = driver.title
        print("Processing :", headline)

        return driver.page_source

    except requests.RequestException as e:
        print(f"Failed to retrieve article details: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def process_csv():
    #========================================================

    input_path = "inputs_curated"

    output_root = "data"

    id = "Michael Brown"
    source = "CBSNews"

    # keyword = "Michael Brown"
    keyword = "Darren Wilson;Michael Brown;Ferguson"
    # keyword = "BLM;Black Lives Matter"
    #========================================================


    port = "9221"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:"+port) 
    options.debugger_address="127.0.0.1:"+port
    options.add_argument("--incognito")
    options.add_argument('"--headless=new"')

    print("not done")
    driver = webdriver.Chrome(options=options)

    csv_path = os.path.join(input_path, os.path.join( os.path.join(id, source), keyword+".csv"))
    df = pd.read_csv(csv_path)

    source_path = os.path.join(id, source) 
    output_directory = os.path.join("results", source_path) 
    os.makedirs(output_directory, exist_ok=True)
    
    data_all = []


    out_dir_article_body = os.path.join(output_root, os.path.join(os.path.join(id, source)))
    os.makedirs(out_dir_article_body, exist_ok=True)




    for ind in df.index:

        url = df['Url'][ind]

        article_str = fetch_article_html(driver, url)

        scraper = CBSScraper(id, article_str)

        article_data = scraper.fetch_single_article(scraper.soup, url)  

        article_body = scraper.fetch_article_body(scraper.soup) 

        date_file = article_data[1]
        headline = article_data[3]

        date_obj = datetime.strptime(date_file, '%m-%d-%Y')
        date = date_obj.strftime('%B %Y')

        date_file = date_obj.strftime('%m-%d-%Y')

        new_output_dir = os.path.join(out_dir_article_body, date)
        if not os.path.exists(new_output_dir):
            os.makedirs(new_output_dir, exist_ok=True)    

        output_file = os.path.join(new_output_dir, headline+" "+date_file+".txt" )

        article_data[-2] = new_output_dir
        print(output_file)

        with open(output_file, "w") as f:
            f.write(article_body)

        data_all.append(article_data)   
        # print(data_all)

    NBCScraper.save_to_csv(data_all, os.path.join(output_directory, keyword+".csv"))  


if __name__ =="__main__":
    process_csv()
