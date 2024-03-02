from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
base_url = "https://www.grailed.com"

driver.get(base_url)

def get_to_search_bar_to_search(driver, timeout=5):
    popup_locater = (By.CSS_SELECTOR, "div.Modal-Content > div.Modal-Body")

    try:
        # click on the search bar first
        search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
        search_bar.click()
        wait = WebDriverWait(driver, timeout)
        popup = wait.until(EC.presence_of_element_located(popup_locater))

        driver.send_keys(Keys.ESCAPE)

        # check if popup is still there
       # popup = driver.find_element(popup_locater)
    except (NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error interacting with element: {e}")
    except TimeoutException:
        print("Element not found within timeout!")

get_to_search_bar_to_search(driver)