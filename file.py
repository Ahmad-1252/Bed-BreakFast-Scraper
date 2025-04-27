import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from lxml import etree
import time

# optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_chromedriver(headless=False):
    print("getting the chromedriver")
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.managed_default_content_settings.javascript": 1,  # Enable JS
    })
    options.add_argument("--disable-logging")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if headless:
        options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(300)  # Set timeout to 30 seconds
    pid = driver.service.process.pid
    print(f"Chrome WebDriver initialized with PID: {pid}")
    return driver, pid


def get_element_hrefs(url, base_url, category):
    try:
        # Define headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ),
        }

        # Make a GET request to the URL
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize total_pages
        total_pages = 1

        if category == 'places':
            elements = soup.select('a.text-ink.hover\:text-primary.font-semibold')

        elif category == 'restaurants':
            # Extract pagination elements
            pagination = soup.select('div.inline-flex.flex-col.gap-4.items-center.flex-wrap.max-w-full div a:last-of-type')
            
            # Safely get total_pages
            try:
                if pagination:
                    total_pages = int(pagination[0].text.strip())
            except ValueError:
                print(f"Warning: Unable to parse total pages for URL: {url}")
                total_pages = 1

            elements = soup.select('.text-current.hover\:text-current.hover\:no-underline.decoration-none.group\/card.cursor-pointer')

        # Extract href attributes
        hrefs = [element.get('href') for element in elements if element.get('href')]

        return hrefs, total_pages

    except requests.exceptions.RequestException as e:
        print(f"Request failed for URL: {url} | Error: {e}")
    except Exception as e:
        print(f"An error occurred while processing category '{category}': {e}")

    return [], 1



def extract_data_from_page(url):
    """
    Extracts hotel details from a given hotel detail URL.

    Parameters:
        url (str): URL of the hotel detail page.

    Returns:
        dict: A dictionary containing extracted hotel details.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ),
    }

    try:
        # Make a GET request to the URL
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        tree = etree.HTML(response.text)

        # Extract hotel details using XPath
        hotel_name = tree.xpath("//h1[@class='line-clamp-5 lg:line-clamp-3 xl:line-clamp-4']/text()")
        hotel_name = hotel_name[0].strip() if hotel_name else "N/A"

        area = tree.xpath('(//div[@class="flex gap-1.5 items-center justify-start flex-wrap"]/span/a)[last() - 2]//text()')
        area = area[0].strip() if area else "N/A"
        
        city = tree.xpath('(//div[@class="flex gap-1.5 items-center justify-start flex-wrap"]/span/a)[last() - 1]//text()')
        city = city[0].strip() if city else "N/A"
        
        country = tree.xpath('(//div[@class="flex gap-1.5 items-center justify-start flex-wrap"]/span/a)[last()]//text()')
        country = country[0].strip() if country else "N/A"
        
        activities = tree.xpath('(//div[contains(., "Activities")])[9]//li/text()')
        activities = ', '.join(activities) if activities else "N/A"
        
        address_lines = tree.xpath('//div[@class="flex flex-col gap-0.5 md:gap-1"]/div/text()')
        full_address = ' '.join(address_lines) if address_lines else "N/A"

        # phone = tree.xpath('//div[@class="flex flex-col gap-0.5 md:gap-1"]/div/text()')
        referenceWebsite = tree.xpath('//a[@rel="noreferrer noopener"]/@href')
        referenceWebsite = referenceWebsite[0] if referenceWebsite else ""
        # Return the extracted data as a dictionary
        return {
            'name': hotel_name,
            'Area': area,
            'city': city,
            'Country': country,
            'Address': full_address,
            'activities': activities,
            'Website': referenceWebsite,
            'url': url,
        }

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed for URL: {url} | Error: {e}")
    except Exception as e:
        print(f"Error extracting data from URL: {url} | Error: {e}")

    return {}

def extract_data_from_page_selenium(url, driver):
    """
    Extracts hotel details from a given hotel detail URL using Selenium.

    Parameters:
        url (str): URL of the hotel detail page.

    Returns:
        dict: A dictionary containing extracted hotel details.
    """
    try:
        # Load the page
        driver.get(url)
        
        # Extract hotel name
        hotel_name = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'line-clamp')]"))
        ).text if driver.find_elements(By.XPATH, "//h1[contains(@class, 'line-clamp')]") else "N/A"

        # Extract area, city, and country
        type = driver.find_elements(By.XPATH, '//li[@class="relative pl-5 first-letter:uppercase mb-0.5"]')
        type = type[0].text.strip() if type else "N/A"
        
        # Extract area
        rooms = driver.find_elements(By.XPATH, '//li[@class="relative pl-5 first-letter:uppercase mb-0"]')
        rooms = rooms[0].text.strip() if rooms else "N/A"
    
        # Extract area, city, and country
        area = driver.find_elements(By.XPATH, '(//div[contains(@class, "flex gap-1.5")]/span/a)[last() - 2]')
        area = area[0].text.strip() if area else "N/A"
        
        city = driver.find_elements(By.XPATH, '(//div[contains(@class, "flex gap-1.5")]/span/a)[last() - 1]')
        city = city[0].text.strip() if city else "N/A"
        
        country = driver.find_elements(By.XPATH, '(//div[contains(@class, "flex gap-1.5")]/span/a)[last()]')
        country = country[0].text.strip() if country else "N/A"
        
        # Extract activities
        activities_elements = driver.find_elements(By.XPATH, '(//div[contains(., "Activities")])[9]//li')
        activities = ', '.join([elem.text.strip() for elem in activities_elements]) if activities_elements else "N/A"
        
        # Extract full address
        address_elements = driver.find_elements(By.XPATH, '//div[@class="flex flex-col gap-0.5 md:gap-1"]/div')
        full_address = ' '.join([elem.text.strip() for elem in address_elements]) if address_elements else "N/A"

        # Extract website link
        reference_website_elements = driver.find_elements(By.XPATH, '//a[@rel="noreferrer noopener"]')
        reference_website = reference_website_elements[0].get_attribute("href") if reference_website_elements else ""

        # phone btn
        phone_number = "N/A"
        try:
            driver.execute_script("window.scrollBy(0,4300)")
            # Initialize the phone number to a default value
            try:
                # Wait for the phone button to be clickable and click it
                phone_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(., "View phone number")]')
                ))
                if phone_btn:
                    phone_btn.click()
            except:
                print(f"Error finding the phone button")
            # Pause to allow content to load
            time.sleep(3)
            try:
                # Wait for the phone number to be visible and extract it
                phone_number_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.XPATH, '(//div[@class="flex flex-col gap-0.5 md:gap-1 items-start md:col-span-2 inline mt-1 md:mt-0"]/div)[2]')
                ))
                phone_number = phone_number_element.text.strip() if phone_number_element else "N/A"
                print(f"Phone number: {phone_number}")
            except:
                print(f"Error extracting phone number")

        except Exception as e:
            print(f"Error clicking phone button or extracting phone number")



        # Return the extracted data
        return {
            'Hotle Name': hotel_name,
            'Area': area,
            'City': city,
            'Country': country,
            'Type': type,
            'Rooms': rooms,
            'Address': full_address,
            'Activities': activities,
            'Phone Number': phone_number,
            'Reference Website': reference_website,
            'url': url,
        }

    except Exception as e:
        print(f"Error extracting data from URL: {url} | Error: {e}")

    return {}


def save_to_excel(data, output_file):
    """
    Saves the data to an Excel file.
    """
    try:
        df = pd.DataFrame(data)
        if os.path.exists(output_file):
            old_data = pd.read_excel(output_file)
            df = pd.concat([old_data, df], ignore_index=True)
        df.to_excel(output_file, index=False)
        return
    except Exception as e:
        print(f"Error saving data to Excel: {e}")
        print("Error saving data to Excel!")
        return    

def main():
    """
    Main function to fetch and save hotel data.
    """
    # File paths
    url_file = 'bed_and_breakfast_urls.xlsx'
    output_file = 'bed_and_breakfast.xlsx'
    output_backup_file = 'bed_and_breakfast_backup.xlsx'

    # Handle backup of existing output file
    if os.path.exists(output_file):
        if os.path.exists(output_backup_file):
            os.remove(output_backup_file)
        os.rename(output_file, output_backup_file)

    # Base URL and initial page for popular cities
    base_url = 'https://www.bedandbreakfast.nl'
    url = f"{base_url}/en/popular-cities"

    # Fetch the list of city links
    places_hrefs, _ = get_element_hrefs(url, base_url, category='places')

    if not places_hrefs:
        print("No city links found. Exiting.")
        return
    print(f"Extracted {len(places_hrefs)} city links.")

    # Collect all hotel data
    all_hrefs = []
    single_hrefs = []
    for m, city_href in enumerate(places_hrefs):
        # Ensure city_href is a valid string
        if isinstance(city_href, str):
            city_url = base_url + city_href
            print(f"Processing {m+1}/{len(places_hrefs)} city: {city_url}")

            try:
                href_links, total_page = get_element_hrefs(city_url, base_url, category='restaurants')
                single_hrefs = href_links
                print(f"Fetched {len(href_links)} restaurant links for city: {city_url}.")
            except ValueError:
                print(f"Failed to fetch data for URL: {city_url}")
                continue

            # If no links are found, log and skip
            if not href_links:
                print(f"No restaurant links found for city: {city_url}")
                continue

            all_hrefs.extend(href_links)

            # Fetch links for subsequent pages
            for page in range(2, total_page + 1):
                paginated_url = f"{city_url}?page={page}"
                try:
                    href_links, _ = get_element_hrefs(paginated_url, base_url, category='restaurants')
                    all_hrefs.extend(href_links)
                    single_hrefs.extend(href_links)
                    print(f"Fetched page {page} of {total_page}.")
                except Exception as e:
                    print(f"Failed to fetch page {page} for URL: {paginated_url} | Error: {e}")
                    break
            print("Total sinle count : {}".format(len(single_hrefs)))

    # Save data to Excel
    if all_hrefs:
        print(f"Saving {len(all_hrefs)} records to {url_file}...")
        df = pd.DataFrame({'Hotel Links': all_hrefs})
        df.to_excel(url_file, index=False)
        print("Data saved successfully!")
    else:
        print("No data to save.")

    # Backup data if no data was saved
    if os.path.exists(output_file):
        if os.path.exists(output_backup_file):
            os.remove(output_backup_file)
        os.rename(output_file ,output_backup_file)
        print("Backup saved successfully!")
    else:
        print("No backup saved. Data was saved successfully.")
    
    print("Extracting the Data")
    print("Starting to extract data...")
    # Extract data from each hotel page
    driver , _ = get_chromedriver(headless=True)
    all_data = []
    data_urls = pd.read_excel(url_file)['Hotel Links'].to_list()
    
    for i, link in enumerate(data_urls):
        try:
            print(f"Processing {i+1}/{len(data_urls)} data for URL: {base_url+link}")
            data = extract_data_from_page_selenium(base_url+link, driver)
            print(data)
            if data:
                all_data.append(data)
            if i % 100 == 0:
                print(f"Extracted {i+1} out of {len(data_urls)} records.")
                save_to_excel(all_data, output_file)
                all_data = []
                print(f"Data saved to {output_file}")
                print("Data saved successfully!")
        except Exception as e:
            print(f"Failed to extract data for URL: {link} | Error: {e}")
    if all_data:
        save_to_excel(all_data, output_file)
        print(f"Data saved to {output_file}")
        print("Data saved successfully!")

    print("Script execution completed.")

if __name__ == "__main__":
    main()
