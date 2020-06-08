from selenium import webdriver
from time import sleep
import utils
import re


def launch_driver():
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    # driverpath = 'C:\\Users\\Johannes\\Downloads\\chromedriver_win32\\chromedriver'
    # driverpath = '/usr/lib/chromium-browser/chromedriver' # On Hetzner server
    driverpath = 'chromedriver'
    driver = webdriver.Chrome(driverpath, chrome_options=options)
    return driver


def login(driver):
    # Logs in with my credentials on the FMEL Login page
    URL_login = 'https://accommodation.fmel.ch/StarRezPortal/AE18865B/7/8/Login-Login?IsContact=False'
    driver.get(URL_login)
    driver.find_element_by_class_name('cc-allow').click()
    driver.find_element_by_name('Username').send_keys('jlruther@kth.se')
    driver.find_element_by_name('Password').send_keys('Mangobaum19')
    driver.find_element_by_xpath('//*[@title="Login"]').click()


def navigate_to_listings(driver):
    # Move to the "book now" page
    URL_book_now = 'https://accommodation.fmel.ch/StarRezPortal/DBB80B99/71/1105/Book_now-Continue_the_booking'
    driver.get(URL_book_now)

    save_continue_button = driver.find_elements_by_xpath('//*[@title="Save & Continue"]')
    save_continue_button[0].click()
    
    # Waiting for page to load. There must be a better way to do this...
    sleep(2)    

    room_dict = {}

    # Click the Apply button for all move-in dates 
    apply_buttons = driver.find_elements_by_xpath('//*[@title="Apply"]')
    for button in apply_buttons:
        sleep(1)
        button.click()
        sleep(3)
        (date, domiciles) = scrape_listings(driver)
        room_dict[date] = domiciles
        sleep(1.5)
        driver.execute_script("window.history.go(-1)")

    return room_dict


def scrape_listings(driver):
    "Returns the move in date and its houses for date link"
    houses = []
    # element = driver.find_elements_by_xpath("//span[contains(text(), 'Falaises')]")
    # if len(element) != 0:
    #     houses.append("Falaises")
    url = driver.current_url
    url = url.split("DateStart=")[1]
    date = url.split("&DateEnd=")[0]
    date = re.sub('%20', '', date)
    # date = date.split("%20")
    date = utils.convert_string_to_date(date)

    select_buttons = driver.find_elements_by_xpath('//*[@title="Select"]')
    no_sel_buttons = len(select_buttons)
    domiciles = []
    for i in range(no_sel_buttons):
        sleep(2)
        select_buttons = driver.find_elements_by_xpath('//*[@title="Select"]')
        select_buttons[i].click()
        sleep(3)
        domiciles = domiciles + scrape_id(driver)
        sleep(3)
        driver.execute_script("window.history.go(-1)")
    return date, domiciles


def scrape_id(driver):
    "Scrapes all unique room names for one student house"
    domiciles = []
    try:
        sleep(5)
        results_list = driver.find_element_by_class_name('results-list')
        titles = results_list.find_elements_by_class_name('title')

        for title in titles:
            domicile = title.text
            print(domicile)
            domiciles.append(domicile)
    except:
        pass
    return domiciles


if __name__ == "__main__":
    driver = launch_driver()
    login(driver)
    sleep(3)
    move_ins = navigate_to_listings(driver)
    print(move_ins)

#<input class="medium ui-input" id="5b4c8ff3c3184a50aa89ae4b2622971e_input" name="Username" onchange="starrez.library.controls.FlagChanged($('#5b4c8ff3c3184a50aa89ae4b2622971e'));" spellcheck="false" type="text" value="">
#<input class="medium ui-dont-track ui-input" id="291045ab3d7a49598ab6452fcbf1592b_input" name="Password" onchange="" spellcheck="false" type="password" value="">








#39 8fd6dd0962f4842bba80d07ef7b0a1c > div:nth-child(2) > div.actions.ui-actions > button
