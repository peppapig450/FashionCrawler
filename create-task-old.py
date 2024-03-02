from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get('https://www.grailed.com')

try:
    wait = WebDriverWait(driver, 10)
  #  accept_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#onetrust-accept-btn-handler")))
#    accept_button.click()
    accept_button = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-selector")
    driver.execute_script("arguments[0].click();", accept_button)

except:
    print("Accept button not found.")
    driver.quit()

#search_bar = driver.find_element(By.ID, "header_search-input")
driver.implicitly_wait(5)
#search_bar.send_keys("supreme belt")
input()