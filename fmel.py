from selenium import webdriver

from time import sleep
import utils
import re
import configparser
import time


def launch_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # driverpath = 'C:\\Users\\Johannes\\Downloads\\chromedriver_win32\\chromedriver'
    # driverpath = '/usr/lib/chromium-browser/chromedriver' # On Hetzner server
    driverpath = 'chromedriver'
    driver = webdriver.Chrome(driverpath, chrome_options=options)
    return driver


def login(driver, username, password):
    # Logs in with my credentials on the FMEL Login page
    URL_login = 'https://accommodation.fmel.ch/StarRezPortal/AE18865B/7/8/Login-Login?IsContact=False'
    driver.get(URL_login)
    driver.find_element_by_class_name('cc-allow').click()
    driver.find_element_by_name('Username').send_keys(username)
    driver.find_element_by_name('Password').send_keys(password)
    driver.find_element_by_xpath('//*[@title="Login"]').click()


def navigate_to_listings(driver):
    # Move to the "book now" page
    URL_book_now = 'https://accommodation.fmel.ch/StarRezPortal/DBB80B99/71/1105/Book_now-Continue_the_booking'
    driver.get(URL_book_now)

    save_continue_button = driver.find_elements_by_xpath('//*[@title="Save & Continue"]')
    save_continue_button[0].click()
    
    # Waiting for page to load. There must be a better way to do this...
    sleep(1)

    # Keep results in a dict that maps move-in dates to rooms
    room_dict = {}

    date_elements = driver.find_elements_by_class_name('gap-below')
    dates = []
    for elem in date_elements:
        dates.append(elem.text.split(" ")[1])

    # Click the 'Apply' button for all move-in dates
    apply_buttons = driver.find_elements_by_xpath('//*[@title="Apply"]')
    for b in range(len(apply_buttons)):
        sleep(1)
        apply_buttons = driver.find_elements_by_xpath('//*[@title="Apply"]')
        apply_buttons[b].click()
        sleep(2)
        # For every move-in date, scrape all available rooms
        room_dict[dates[b]] = scrape_listings(driver)
        sleep(1.5)
        driver.execute_script("window.history.go(-1)")

    return room_dict


def scrape_listings(driver):
    """
    Returns the move in date and available rooms for date link.
    """

    # This page shows all student houses for which there are rooms available.
    # Underneath every house there is a select button. Click them one by one
    select_buttons = driver.find_elements_by_xpath('//*[@title="Select"]')
    room_names = []
    for b in range(len(select_buttons)):
        sleep(1)
        select_buttons = driver.find_elements_by_xpath('//*[@title="Select"]')
        select_buttons[b].click()
        sleep(2)
        # For every houses page, find all available rooms
        room_names = room_names + get_room_names(driver)
        sleep(2)
        driver.execute_script("window.history.go(-1)")
    return room_names


def get_room_names(driver):
    """
    Scrapes all unique room names for one student house.
    Every room name consists of the name of the house and a room number.
    """
    room_names = []
    try:
        sleep(3)
        results_list = driver.find_element_by_class_name('results-list')
        titles = results_list.find_elements_by_class_name('title')
        for title in titles:
            room_name = title.text
            print(room_name)
            room_names.append(room_name)
    except:
        pass
    return room_names


if __name__ == "__main__":

    # Read username and password for the FMEL page from a config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config['FMEL']['username']
    password = config['FMEL']['password']

    driver = launch_driver()
    login(driver, username, password)
    sleep(3)
    move_ins = navigate_to_listings(driver)
    print(move_ins)
