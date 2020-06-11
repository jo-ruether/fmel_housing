# Scraping FMEL Listings with Selenium

## Setup

### Dependencies

* selenium `conda install selenium` or `pip install selenium`
* python-telegram-bot `conda install -c conda-forge python-telegram-bot` or `pip install python-telegram-bot`
* pandas `conda install pandas` or `pip install pandas`

### Config file

Rename `config_sample.ini` to `config.ini` and fill in your login credentials.

### Chromium Browser Driver

1. Install Chromium Web Browser (not the standard snap version of Chromium)
2. Download a ChromeDriver corresponding to your version of Chrome (https://chromedriver.chromium.org/downloads)
3. Copy it to the same directory as `fmel.py`
4. Make it executable with `chmod +x chromedriver`?
5. Add the ChromeDriver to PATH (`PATH=$PATH:~/path/to/chromedriver`)



## Building Blocks

### FMEL Webscraper

The scraper works just like a human would to read all room offers from the FMEL website. It opens a browser driver, logs in with the credentials provided in the `config.ini` file and consecutively clicks every move-in date and house. If this software runs permanently on a server, you can set the `headless` flag to run the Chrome driver without actually opening a browser window.

![FMEL Scraper](doc/fmel_scraper.gif)
