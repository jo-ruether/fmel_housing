from selenium import webdriver

from time import sleep
import configparser


def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')

    # driverpath = 'C:\\Users\\Johannes\\Downloads\\chromedriver_win32\\chromedriver'
    # driverpath = '/usr/lib/chromium-browser/chromedriver' # On Hetzner server
    driverpath = 'chromedriver'
    driver = webdriver.Chrome(driverpath, chrome_options=options)
    return driver


class FMELScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = init_driver()

        # Keep results in a dict that maps move-in dates to rooms
        self.room_dict = {}

    def login(self):
        # Move to login interface
        self.driver.get('https://fmel.ch/en/')
        book_now_link = self.driver.find_element_by_link_text("Book Now")
        book_now_link.click()
        login_link = self.driver.find_element_by_link_text("Login:")
        login_link.click()

        # Fill in login credentials
        self.driver.find_element_by_class_name('cc-allow').click()
        self.driver.find_element_by_name('Username').send_keys(username)
        self.driver.find_element_by_name('Password').send_keys(password)
        self.driver.find_element_by_xpath('//*[@title="Login"]').click()

    def navigate_to_listings(self):

        # Move to the "book now" page
        book_now_link = self.driver.find_element_by_link_text("Book now")
        book_now_link.click()
        save_continue_button = self.driver.find_elements_by_xpath('//*[@title="Save & Continue"]')
        save_continue_button[0].click()

        # Waiting for page to load. There must be a better way to do this...
        sleep(1)

        date_elements = self.driver.find_elements_by_class_name('gap-below')
        dates = []
        for elem in date_elements:
            dates.append(elem.text.split(" ")[1])

        # Click the 'Apply' button for all move-in dates
        apply_buttons = self.driver.find_elements_by_xpath('//*[@title="Apply"]')
        for b in range(len(apply_buttons)):
            sleep(1)
            apply_buttons = self.driver.find_elements_by_xpath('//*[@title="Apply"]')
            apply_buttons[b].click()
            sleep(2)
            # For every move-in date, scrape all available rooms
            self.room_dict[dates[b]] = self.scrape_listings()
            sleep(1.5)
            self.driver.execute_script("window.history.go(-1)")

    def scrape_listings(self):
        """
        Returns the move in date and available rooms for date link.
        """

        # This page shows all student houses for which there are rooms available.
        # Underneath every house there is a select button. Click them one by one
        select_buttons = self.driver.find_elements_by_xpath('//*[@title="Select"]')
        room_names = []
        for b in range(len(select_buttons)):
            sleep(1)
            select_buttons = self.driver.find_elements_by_xpath('//*[@title="Select"]')
            select_buttons[b].click()
            sleep(2)
            # For every houses page, find all available rooms
            room_names = room_names + self.get_room_names()
            sleep(2)
            self.driver.execute_script("window.history.go(-1)")
        return room_names

    def get_room_names(self):
        """
        Scrapes all unique room names for one student house.
        Every room name consists of the name of the house and a room number.
        """
        room_names = []
        try:
            sleep(3)
            results_list = self.driver.find_element_by_class_name('results-list')
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

    scraper = FMELScraper(username, password)
    scraper.login()
    sleep(2)
    scraper.navigate_to_listings()

    print(scraper.room_dict)
