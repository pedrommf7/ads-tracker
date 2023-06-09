from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

import requests
import sys

if(len(sys.argv) < 2):
    print("Usage: python main.py <page_url>")
    exit()

#Get Program Args
page_url = sys.argv[1]

ADS_LIST_URL = "https://pgl.yoyo.org/as/serverlist.php?hostformat=adblockplus;showintro=0"

#Get Ads Servers
ads_list_page = requests.get(ADS_LIST_URL)
ads_list = ads_list_page.text.splitlines()
#Remove lines that are not ads servers
ads_list = [x for x in ads_list if x.startswith('||')]
#Remove the || from the beginning of the line
ads_list = [x.replace('||', '') for x in ads_list]
#Remove the ^ from the end of the line
ads_list = [x.replace('^', '') for x in ads_list]

def start_driver():
    # Create a new instance of the Chrome driver
    options = ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        options = options
    )
    return driver

def load_page(page_url, driver):
    print("=====================================")
    print("Loading page: ",page_url)
    
    driver.switch_to.new_window('tab')
    driver.get(page_url)
    
    driver_requests = driver.requests.copy()
    del driver.requests

    return driver_requests

def is_ad_request(request):
    request_url = request.url

    # Check if the request URL contains any of the ad server names
    for ad_server in ads_list:
        if ad_server in request_url:
            return True
        
    return False

def analyse_page_load(driver_requests):
    total_downloaded_bytes = 0
    total_ads_bytes = 0
    total_requests_number = 0
    total_ads_number = 0
    
    # Access requests via the `requests` attribute
    for request in driver_requests:
        if request.response and request.response.status_code == 200:
            response_size = 0
            try:
                response_size = int(request.response.headers['content-length'])
            except:
                pass

            total_downloaded_bytes += int(response_size)
            total_requests_number += 1
            if is_ad_request(request):
                total_ads_bytes += int(response_size)
                total_ads_number += 1

    if total_downloaded_bytes == 0:
        total_downloaded_mb = 0
    else:
        total_downloaded_mb = total_downloaded_bytes / 1024 / 1024
    
    if total_ads_bytes == 0:
        total_ads_mb = 0
        percentage_of_ads = 0
    else:
        total_ads_mb = total_ads_bytes / 1024 / 1024
        percentage_of_ads = total_ads_bytes / total_downloaded_bytes * 100

    print('Total downloaded: %.2f MB' % total_downloaded_mb)
    print('Total ads: %.2f MB (%.2f%%)' % (total_ads_mb, percentage_of_ads))
    print('Total requests: %d' % total_requests_number)
    print('Total ads requests: %d' % total_ads_number)
    print("=====================================")


driver = start_driver()
driver_requests = load_page(page_url, driver)
analyse_page_load(driver_requests)

driver.quit()