import os
import time
from random import choice, uniform

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def sleep_randomly(t):
    time.sleep(t * uniform(0.8, 1.2))

def send_keys_slowly(element, text):
    for character in text:
        element.send_keys(character)
        sleep_randomly(0.1)

def extract_remaining_days(confirm_buttons):
    least_remaining = float("inf")

    for cb in confirm_buttons:
        countdown = cb.get_attribute("data-original-title")
        if countdown is None:
            countdown = cb.text
        print("Countdown text:", countdown)
        remaining = int(countdown.split(" ")[2])
        least_remaining = min(least_remaining, remaining)

    if least_remaining == float("inf"):
        least_remaining = default_interval
    
    return least_remaining

def confirm_if_needed(confirm_buttons):
    for button in confirm_buttons:
        print("Confirm text:", button.text)
        if button.text.replace(" ", "").replace("\n", "").lower() == "confirm":
            print("Confirming... ", end="")
            button.click()
            print(" ...Confirmed")
        sleep_randomly(5)

# load environment variables
load_dotenv()
login_url = os.getenv("X_LOGIN_URL")
main_url = os.getenv("X_MAIN_URL")
confirm_url = os.getenv("X_CONFIRM_URL")
username = os.getenv("X_USERNAME")
password = os.getenv("X_PASSWORD")
default_interval = int(os.getenv("X_DEFAULT_INTERVAL"))

# set options to mask the browser
options = Options()
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ",
]
options.add_argument(f"user-agent={choice(user_agents)}")
options.add_argument("lang=en-GB;q=0.9,en;q=0.8,en-US;q=0.7,sl;q=0.6")
options.add_argument("accept_encoding=gzip, deflate, br")
options.add_argument('--headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

def main():
    # start the browser
    driver = webdriver.Chrome(options=options)

    # navigate to the login page
    driver.get(login_url)
    print("Login page loaded")
    sleep_randomly(3)

    # fill in the login form
    username_element = driver.find_element(By.ID, "username")
    send_keys_slowly(username_element, username)
    sleep_randomly(0.5)

    password_element = driver.find_element(By.ID, "password")
    send_keys_slowly(password_element, password)
    sleep_randomly(0.5)

    print("Form filled")

    # submit the form
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    print("Form submitted")

    # wait for the login to complete
    login_wait = WebDriverWait(driver, 15)
    login_wait.until(lambda driver: driver.current_url == main_url)
    print("Login successful")
    sleep_randomly(5)

    # navigate to confirm page
    driver.get(confirm_url)
    print("Confirm page loaded")

    # collect all confirm buttons
    confirm_buttons = []
    try:
        confirm_buttons = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td[data-title='Host'] div:nth-child(2) a")))
        print("Found", len(confirm_buttons), "countdown markers")
    except TimeoutException:
        print("Timed out waiting for confirm buttons")

    # determine how many days to wait before rechecking
    remaining_days = extract_remaining_days(confirm_buttons)
    sleep_randomly(5)

    # extract the potentail confirm buttons
    confirm_buttons = driver.find_elements(By.CSS_SELECTOR, "#host-panel > table tbody tr td:last-child button:first-child")
    print("Found", len(confirm_buttons), "confirm buttons")

    # confirm if needed
    confirm_if_needed(confirm_buttons)
 
    return remaining_days

if __name__ == "__main__":
    while True:
        print("Starting task")
        remaining_days = main()
        print("Completed task")
        print("Sleeping for", remaining_days - 1, "days")
        time.sleep((remaining_days - 1) * 24 * 60 * 60)
        print("--------------------")