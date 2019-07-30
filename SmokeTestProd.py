from selenium import webdriver
import unittest
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
'''
This is an automated front end smoke test for Catalog. Because this is only a smoke test, none of the tests assert very complicated things. Mostly they are just checking to see if the page loaded without error,
there are items displayed, filters displayed, etc. This should only be used to quickly determine that there are no major errors in the build, then some manual testing should still be done.

Coverage (All of the tests are perfromed on both WSS and TRS where applicable):

. Searching
. FSR
. Filters (Category, Brand and Spec facets)
. All varieties of PLP load without error (Search results, category pages, specialized pages, group specials, etc.)
. Sorting on PLPs (only checks sorting links to the correct URL, does NOT verify the validity of the order. Do this manually.)
. Pagination on PLPs
. TRS Product Pages load without error
. Search Within
. Auto Suggest

'''
#Tests for ensuring searching is functional, has pagination and returns items/filters/categories.
class Searching(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    #Search the top 10 search terms on WSS. Verify items, category tiles and filters display. Check pagination is functioning.
    def test_top_10_searches_wss(self):
        terms = ['napkins', 'freezer', 'plates', 'cutting board', 'plastic cups', 'ice maker', 'ice machine', 'refrigerator', 'stainless steel table', 'gloves']
        driver = self.driver
        driver.get("https://www.webstaurantstore.com")
        driver.maximize_window()
        for term in terms:
            print("Searching for " + term + " on WSS...")
            inputElement = driver.find_element_by_name("searchval")
            inputElement.clear()
            inputElement.send_keys(term)
            inputElement.submit()
            self.assertIn('category-grid', driver.page_source) #Check if Category Tiles exist on the page. If there are none, this class does not appear in the HTML.
            self.assertIn("productBox1", driver.page_source) # This checks that an arbitrary product box exists, which indicates that there are items displaying on the page
            self.assertIn('class="filter-list__content"', driver.page_source) # This checks that the Filters List on the side is present.
            inputElement = driver.find_element_by_class_name("icon-right-open") 
            inputElement.click() #Clicks button to go to next page
            self.assertIn('?page=2', driver.current_url)
            self.assertIn("productBox1", driver.page_source)
            self.assertIn('class="filter-list__content"', driver.page_source)

    #Same thing but for TRS
    def test_top_10_searches_trs(self):
        terms = ['napkins', 'freezer', 'plates', 'cutting board', 'plastic cups', 'ice maker', 'ice machine', 'refrigerator', 'stainless steel table', 'gloves']
        driver = self.driver
        driver.get("https://test.therestaurantstore.com/stores/set/1")
        driver.maximize_window()
        for term in terms:
            print("Searching for " + term + " on TRS...")
            inputElement = driver.find_element_by_name("search_values")
            inputElement.clear()
            inputElement.send_keys(term)
            inputElement.submit()
            self.assertIn('category-listing-block', driver.page_source)
            self.assertIn('ag-details-block item', driver.page_source)
            self.assertIn('class="filters"', driver.page_source)
            inputElement = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div/div/div[2]/div[3]/ul/li[11]/a')
            inputElement.click()
            self.assertIn('ag-details-block item', driver.page_source)
            self.assertIn('class="filters"', driver.page_source)
    
    #Searching on FSR
    def test_FSR_search(self):
        terms = ['crepes', 'cutting board', 'bar']
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/food-service-resources.html")
        driver.maximize_window()
        proceed = 0
        while (proceed == 0): #This is because sometimes Test 404's on FSR. One of the servers must have issues, so It will refresh until it doesn't 404.
            if ("Sorry, but this page doesn't exist" in driver.page_source):
                driver.refresh()
            else:
                proceed = 1

        for term in terms:
            print("Searching for " + term + " on Food Service Resources...")
            inputElement = driver.find_element_by_id("term")
            inputElement.clear()
            inputElement.send_keys(term)
            inputElement.submit()

            proceed = 0
            while (proceed == 0):
                if ("Sorry, but this page doesn't exist" in driver.page_source):
                    driver.refresh()
                else:
                    proceed = 1

            inputElement = driver.find_element_by_xpath('//*[@id="page"]/div[1]/div[2]/div/a[1]/span[2]/h2') #Check if results are displayed
            self.assertTrue(inputElement.is_displayed())
            inputElement = driver.find_element_by_xpath('//*[@id="page"]/div[3]/ul/li[2]') #Check that the sidebar categories are displayed
            self.assertTrue(inputElement.is_displayed())

#Testing functionality of various elements on Category pages
class Categories(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def test_10_categories_wss(self):
        #I just selected 10 categories at random. Feel free to add more/change these.
        pages = ['https://www.webstaurantstore.com/51211/desks-and-desk-bases.html',
                'https://www.webstaurantstore.com/261/disposable-gloves.html', 
                'https://www.webstaurantstore.com/56253/thermocouple-thermometers-and-probes.html',
                'https://www.webstaurantstore.com/41983/wood-serving-and-display-platters-trays.html',
                'https://www.webstaurantstore.com/50887/stoneware-bowls.html',
                'https://www.webstaurantstore.com/2835/chef-knives.html',
                'https://www.webstaurantstore.com/3337/chef-coats.html',
                'https://www.webstaurantstore.com/14821/gas-connectors-and-gas-hoses.html',
                'https://www.webstaurantstore.com/47305/foam-hinged-take-out-containers.html',
                'https://www.webstaurantstore.com/10397/ramekins-and-sauce-cups.html']

        driver = self.driver
        for page in pages:
            print("Checking category page: " + page)
            driver.get(page)
            # All I'm checking is that items and filters appear on the page.
            for _ in range(2):
                self.assertIn("productBox1", driver.page_source)
                self.assertIn('class="filter-list box"', driver.page_source)
                if '"icon-right-open"' in driver.page_source:
                    inputElement = driver.find_element_by_class_name("icon-right-open") 
                    inputElement.click() #Clicks button to go to next page

    def test_10_categories_trs(self):
        #I just selected 10 categories at random. Feel free to add more/change these.
        pages = ['https://www.therestaurantstore.com/categories/51211/desks-and-desk-bases.html',
                'https://www.therestaurantstore.com/categories/261/disposable-gloves.html', 
                'https://www.therestaurantstore.com/categories/56253/thermocouple-thermometers-and-probes.html',
                'https://www.therestaurantstore.com/categories/41983/wood-serving-and-display-platters-trays.html',
                'https://www.therestaurantstore.com/categories/50887/stoneware-bowls.html',
                'https://www.therestaurantstore.com/categories/2835/chef-knives.html',
                'https://www.therestaurantstore.com/categories/3337/chef-coats.html',
                'https://www.therestaurantstore.com/categories/14821/gas-connectors-and-gas-hoses.html',
                'https://www.therestaurantstore.com/categories/47305/foam-hinged-take-out-containers.html',
                'https://www.therestaurantstore.com/categories/10397/ramekins-and-sauce-cups.html']

        driver = self.driver
        for page in pages:
            print("Checking category page: " + page)
            driver.get(page)
            if ("Before we continue, let's get your store location!" in driver.page_source):
                inputElement = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div[2]/div[2]/div[1]/a[2]')
                inputElement.click() #TRS makes you select a store before browsing the site
            else:
                self.assertIn("ag-details-block item", driver.page_source)
                self.assertIn('class="filters"', driver.page_source)

class AutoSuggest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def test_auto_suggest_exists_wss(self):
        print("Checking Auto Suggest is functional...")
        search_param = "ham"
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/")
        driver.maximize_window()
        inputElement = driver.find_element_by_name("searchval")
        inputElement.send_keys(search_param)
        driver.implicitly_wait(20)
        self.assertIn ("hamburger press", driver.find_element_by_xpath('//*[@id="searchForm"]/div/ul/li[2]/span[2]').text)
        self.assertIn ("Hamburger Presses", driver.find_element_by_xpath('//*[@id="searchForm"]/div/ul/li[12]/span[2]').text)
        self.assertIn ('Arm & Hammer', driver.find_element_by_xpath('//*[@id="searchForm"]/div/ul/li[20]/span[2]').text)

    def test_auto_suggest_links(self):
        print("Checking Auto Suggest links work...")
        search_param = "ham"
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/")
        driver.maximize_window()
        inputElement = driver.find_element_by_name("searchval")
        inputElement.send_keys(search_param)
        driver.implicitly_wait(20)
        inputElement = driver.find_element_by_xpath('//*[@id="searchForm"]/div/ul/li[2]/span[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/search/hamburger-press.html', driver.current_url)

class TRSProductPage(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def test_trs_product_page(self):
        pages = ['https://www.therestaurantstore.com/items/396801',
                'https://www.therestaurantstore.com/items/449459',
                'https://www.therestaurantstore.com/items/466919',
                'https://www.therestaurantstore.com/items/367425',
                'https://www.therestaurantstore.com/items/23747']

        driver = self.driver
        for page in pages:
            print("Checking TRS Product Page: " + page)
            driver.get(page)
            if ("Before we continue, let's get your store location!" in driver.page_source):
                inputElement = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div[2]/div[2]/div[1]/a[2]')
                inputElement.click() #TRS makes you select a store before browsing the site
            else:
                self.assertIn('class="large-visual"', driver.page_source)
                self.assertIn('class="price "', driver.page_source)

class Specials(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        print("Checking specials.cfm...")

    def tearDown(self):
        self.driver.close()

    def test_specials_loads(self):
        
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/specials.html?forcecacheupdate=1')
        self.assertIn("productBox1", driver.page_source)
        self.assertIn('class="filter-list box"', driver.page_source)

    def test_specials_pagination(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/specials.html?forcecacheupdate=1')
        for _ in range(6):
            self.assertIn("productBox1", driver.page_source)
            self.assertIn('class="filter-list box"', driver.page_source)
            inputElement = driver.find_element_by_class_name("icon-right-open") 
            inputElement.click() #Clicks button to go to next page

class GroupSpecials(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        

    def tearDown(self):
        self.driver.close()

    def test_group_specials_loads(self):
        pages = ['https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087',
                'https://www.webstaurantstore.com/groupspecials.cfm?group_num=2902089',
                'https://www.webstaurantstore.com/groupspecials.cfm?group_num=9040269']

        driver = self.driver
        for page in pages:
            print("Checking Group Specials page: " + page)
            driver.get(page)
            self.assertIn("productBox1", driver.page_source)
            self.assertIn('class="filter-list box"', driver.page_source)

    def test_group_specials_pagination(self):
        pages = ['https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087',
                'https://www.webstaurantstore.com/groupspecials.cfm?group_num=2902089',
                'https://www.webstaurantstore.com/groupspecials.cfm?group_num=9040269']

        driver = self.driver
        for page in pages:
            print("Checking Group Specials page: " + page)
            driver.get(page)
            for _ in range(2):
                self.assertIn("productBox1", driver.page_source)
                self.assertIn('class="filter-list box"', driver.page_source)
                inputElement = driver.find_element_by_class_name("icon-right-open") 
                inputElement.click() #Clicks button to go to next page

class SpecializedPages(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
       

    def tearDown(self):
        self.driver.close()

    def test_specialized_loads(self):
        pages = ['https://www.webstaurantstore.com/specializedpage.cfm?index=14122',
                'https://www.webstaurantstore.com/specializedpage.cfm?index=1025',
                'https://www.webstaurantstore.com/specializedpage.cfm?index=1029']

        driver = self.driver
        for page in pages:
            print("Checking Specialized Page: " + page)
            driver.get(page)
            self.assertIn("productBox1", driver.page_source)
            self.assertIn('class="filter-list box"', driver.page_source)

    def test_specialized_pagination(self):
        pages = ['https://www.webstaurantstore.com/specializedpage.cfm?index=14122',
                'https://www.webstaurantstore.com/specializedpage.cfm?index=1025',
                'https://www.webstaurantstore.com/specializedpage.cfm?index=1029']

        driver = self.driver
        for page in pages:
            print("Checking Specialized Page: " + page)
            driver.get(page)
            for _ in range(2):
                self.assertIn("productBox1", driver.page_source)
                self.assertIn('class="filter-list box"', driver.page_source)
                inputElement = driver.find_element_by_class_name("icon-right-open") 
                inputElement.click() #Clicks button to go to next page

class PLPSorting(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        print("Checking PLP sorting...")

    def tearDown(self):
        self.driver.close()

    def test_search_result_sorting(self):
        terms = ['napkins']
        driver = self.driver
        driver.get("https://www.webstaurantstore.com")
        driver.maximize_window()
        
        for term in terms:
            inputElement = driver.find_element_by_name("searchval")
            inputElement.clear()
            inputElement.send_keys(term)
            inputElement.submit()
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[1]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=price_asc', driver.current_url)
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=price_desc', driver.current_url)
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[1]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=rating_asc', driver.current_url)
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[2]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=rating_desc', driver.current_url)
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[1]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=date_desc', driver.current_url)
            inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[2]')
            inputElement.click()
            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?order=date_asc', driver.current_url)
            self.assertIn("productBox1", driver.page_source)

    def test_category_page_sorting(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html')
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=price_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=price_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=rating_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=rating_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=date_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/51211/desks-and-desk-bases.html?order=date_asc', driver.current_url)
        self.assertIn("productBox1", driver.page_source)
        
    def test_specials_sorting(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/specials.html')
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=price_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=price_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=rating_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=rating_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=date_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specials.html?order=date_asc', driver.current_url)
        self.assertIn("productBox1", driver.page_source)
    def test_group_specials_sorting(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087')
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=price_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=price_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=rating_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=rating_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=date_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&order=date_asc', driver.current_url)
        self.assertIn("productBox1", driver.page_source)
    def test_specialized_page_sorting(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/specializedpage.cfm?index=14122')
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=price_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=price_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=rating_asc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[2]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=rating_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[1]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=date_desc', driver.current_url)
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[3]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/specializedpage.cfm?index=14122&order=date_asc', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

    def test_sorting_with_filters(self):
        driver = self.driver
        driver.get('https://www.webstaurantstore.com/3337/chef-coats.html?filter=type:unisex-chef-coats&filter=product-line:chef-revival-bronze')
        inputElement = driver.find_element_by_xpath('//*[@id="sort_options"]/optgroup[1]/option[2]')
        inputElement.click()
        self.assertEqual('https://www.webstaurantstore.com/3337/chef-coats.html?filter=type:unisex-chef-coats&filter=product-line:chef-revival-bronze&order=price_desc', driver.current_url)

       
class SearchWithin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        print("Checking Search Within...")

    def tearDown(self):
        self.driver.close()

    def test_search_result_search_within(self):
        terms = ['napkins']
        driver = self.driver
        driver.get("https://www.webstaurantstore.com")
        driver.maximize_window()
        
        for term in terms:
            inputElement = driver.find_element_by_name("searchval")
            inputElement.clear()
            inputElement.send_keys(term)
            inputElement.submit()

            inputElement = driver.find_element_by_name("withinval")
            inputElement.clear()
            inputElement.send_keys('cocktail napkin')
            inputElement.submit()

            self.assertEqual('https://www.webstaurantstore.com/search/napkins.html?withinval=cocktail+napkin', driver.current_url)
            self.assertIn("productBox1", driver.page_source)

        
    def test_category_page_search_within(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/3337/chef-coats.html")
        driver.maximize_window()

        inputElement = driver.find_element_by_name("withinval")
        inputElement.clear()
        inputElement.send_keys('button strips')
        inputElement.submit()

        self.assertEqual('https://www.webstaurantstore.com/3337/chef-coats.html?withinval=button+strips', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

        
    def test_group_specials_search_within(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087")
        driver.maximize_window()

        inputElement = driver.find_element_by_name("withinval")
        inputElement.clear()
        inputElement.send_keys('japanese')
        inputElement.submit()

        self.assertEqual('https://www.webstaurantstore.com/groupspecials.cfm?group_num=12061087&withinval=japanese', driver.current_url)
        self.assertIn("productBox1", driver.page_source)
        

class Filters(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        print("Checking filters...")

    def tearDown(self):
        self.driver.close()

    def test_single_spec_filter(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/50889/stoneware-plates.html")
        driver.maximize_window()
        
        inputElement = driver.find_element_by_xpath('//*[@id="collapseShape"]/a[1]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/50889/stoneware-plates.html?filter=shape:oval', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

    def test_multiple_spec_filters(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/2997/refrigerator-freezer-thermometers.html")
        driver.maximize_window()
        
        inputElement = driver.find_element_by_xpath('//*[@id="collapseType"]/a[3]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/2997/refrigerator-freezer-thermometers.html?filter=type:refrigerator-freezer-thermometers', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

        inputElement = driver.find_element_by_xpath('//*[@id="collapseMinimum_Temperature"]/a[1]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/2997/refrigerator-freezer-thermometers.html?filter=type:refrigerator-freezer-thermometers&filter=minimum-temperature:-40-degrees-f', driver.current_url)
        self.assertIn("productBox1", driver.page_source)
    
    def test_brand_filter(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/14821/gas-connectors-and-gas-hoses.html")
        driver.maximize_window()

        inputElement = driver.find_element_by_xpath('//*[@id="collapseVendor"]/a[4]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/14821/gas-connectors-and-gas-hoses.html?vendor=T-S-Brass-and-Bronze-Works', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

        inputElement = driver.find_element_by_xpath('//*[@id="collapseT___S_Accessories"]/a[2]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/14821/gas-connectors-and-gas-hoses.html?filter=t-s-accessories:swivelink&vendor=T-S-Brass-and-Bronze-Works', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

    def test_category_filter(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/search/plates.html")
        driver.maximize_window()

        inputElement = driver.find_element_by_xpath('//*[@id="section1"]/a[1]/label/span')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/search/plates.html?category=3787', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

        inputElement = driver.find_element_by_xpath('//*[@id="section1"]/a[1]/label/span')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/search/plates.html', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

        inputElement = driver.find_element_by_xpath('//*[@id="section2"]/a[1]/label/span')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/search/plates.html?category=14177', driver.current_url)
        self.assertIn("productBox1", driver.page_source)

    def test_price_filter(self):
        driver = self.driver
        driver.get("https://www.webstaurantstore.com/specials.html")
        driver.maximize_window()
        
        inputElement = driver.find_element_by_xpath('//*[@id="collapsePrice"]/a[2]/label/label/div')
        inputElement.click()

        self.assertEqual('https://www.webstaurantstore.com/specials.html?price=100,200', driver.current_url)
        self.assertIn("productBox1", driver.page_source)


if __name__ == "__main__":
    unittest.main()	
