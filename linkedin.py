import os
import urllib
import time
from scraper import Scraper
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains


class LinkedInJobListScraper(Scraper):
    '''This class helps you to scrape linkedin and get useful information'''
    
    def __init__(self):
        super().__init__()
    
    def login(self, username, password):
        # login linkedin using your username and password
        self.driver.find_element_by_id('username').send_keys(username)
        self.driver.find_element_by_id('password').send_keys(password)
        selector = '#app__container > main > div > form > div.login__form_action_container > button'
        self.driver.find_element_by_css_selector(selector).click()

    def search(self, keywords, date_posted=None, location=None):
        # search jobs based on the provided conditions
        base_url = 'https://www.linkedin.com/jobs/search/'
        # create empty variables for date and location queries
        date_query = ''
        location_query = ''
        keywords_query = f'keywords={keywords}'
        # linkedin is using seconds to filter date range
        if date_posted is not None:
            date_query = f'f_TPR=r{date_posted*60*60*24}&'
        if location is not None:
            location_query = f'&location={urllib.parse.quote(location)}'
        # concatenate queries and create a search query
        search_query = f'?{date_query}{keywords_query}{location_query}'
        self.search_url = f'{base_url}{search_query}'
        self.get_website(self.search_url, 2)
    
    def job_list_scroll(self):
        # scroll the job list container
        # job list container is about 6000 px in height
        # unless scroll little by little, you cannot obtain all objects
        height = 0
        selector = '#ember4 > div.application-outlet > div.authentication-outlet > section.job-search-ext.job-search-ext--two-pane > div.jobs-search-two-pane__wrapper.jobs-search-two-pane__wrapper--two-pane > div > div > div.jobs-search-two-pane__results.jobs-search-two-pane__results--responsive.display-flex > div.jobs-search-results.jobs-search-results--is-two-pane'
        for _ in range(1, 20):
            height += 300  # scroll 300 px each loop
            query = "document.querySelector('"
            query += selector
            query += "').scrollTop = "
            query += f"{str(height)};"
            self.driver.execute_script(query)
        time.sleep(2)

    def get_job_list(self):
        # get links for each job posting
        selector = '#ember4 > div.application-outlet > div.authentication-outlet > section.job-search-ext.job-search-ext--two-pane > div.jobs-search-two-pane__wrapper.jobs-search-two-pane__wrapper--two-pane > div > div > div.jobs-search-two-pane__results.jobs-search-two-pane__results--responsive.display-flex > div.jobs-search-results.jobs-search-results--is-two-pane > div > ul'
        job_list_elem = self.driver.find_element_by_css_selector(selector)
        links = self.get_links(job_list_elem)
        # if job_list does not exist, create one
        if hasattr(self, 'job_list') is False:
            self.job_list = []
        match_string = 'https://www.linkedin.com/jobs/view/'
        for link in links:
            link = link[:45]
            if (link not in self.job_list) and (match_string in link):
                self.job_list.append(link)

    def get_page_numbers(self):
        # get page numbers
        selector = '#ember4 > div.application-outlet > div.authentication-outlet > section.job-search-ext.job-search-ext--two-pane > div.jobs-search-two-pane__wrapper.jobs-search-two-pane__wrapper--two-pane > div > div > div.jobs-search-two-pane__results.jobs-search-two-pane__results--responsive.display-flex > div.jobs-search-results.jobs-search-results--is-two-pane > div > section > artdeco-pagination > ul'
        page_elems = self.driver.find_element_by_css_selector(selector)
        page_nums = page_elems.find_elements_by_tag_name('li')
        self.page_nums = []
        for page_num in page_nums:
            self.page_nums.append(int(page_num.text))

    def move_next_page(self, page_num):
        # go to next page. LinkedIn's paging system is 25 increments
        next_page_url = f'{self.search_url}&start={str((page_num-1)*25)}'
        self.get_website(next_page_url, 2)


if __name__ == "__main__":
    # sample code    
    username = os.environ['LINKEDIN_USERNAME']
    password = os.environ['LINKEDIN_PASSWORD']
    login_url = 'https://www.linkedin.com/uas/login?trk=guest_homepage-basic_nav-header-signin'
    linkedin = LinkedInJobListScraper()
    linkedin.get_website(login_url, 2)
    linkedin.login(username, password)
    linkedin.search('Software Engineer', 1, 'New York, New York')
    linkedin.get_page_numbers()
    for page_num in linkedin.page_nums:
        if page_num != 1:
            linkedin.move_next_page(page_num)
        linkedin.job_list_scroll()
        linkedin.get_job_list()
        print(len(linkedin.job_list))
        linkedin.take_screenshot(f'page{str(page_num)}.png')
    with open('urls.txt', 'w', encoding='utf-8') as f:
        for item in linkedin.job_list:
            f.write(f'{item}\n')
    linkedin.close_connection()
