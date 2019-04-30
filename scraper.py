import time
import traceback

from selenium import webdriver


class Scraper:

    def __init__(self):
        # initiate chrome options
        chrome_options = webdriver.ChromeOptions()
        # configure chrome options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # construct driver
        driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver = driver
    
    def get_website(self, url, load_time):
        # get website and save it into the driver
        try:
            self.driver.get(url)
            # wait until the page loads
            time.sleep(load_time)
            
        except:
            traceback.print_exc()
    
    def get_links(self, element):
        # get a tags from a chunk of html codes
        elem_list = element.find_elements_by_tag_name('a')
        urls = []
        for elem in elem_list:
            url = elem.get_attribute('href')
            urls.append(url)
        return urls
    
    def take_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def close_connection(self):
        # close the browser
        self.driver.quit()


if __name__ == "__main__":

    site = Scraper()
    site.get_website('https://www.linkedin.com/uas/login?trk=guest_homepage-basic_nav-header-signin', 3)
    #site.get_links()
    site.take_screenshot('test.png')
    site.close_connection()
