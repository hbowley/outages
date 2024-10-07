from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re

# Specify the path to EdgeDriver
edge_driver_path = "C:/Program Files/EdgeDriver/msedgedriver.exe"  # Change to the location of your EdgeDriver

# Set up the Edge driver (this will be used inside the function)
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)

# Define the web scraping function
def scrape_county_data(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    try:
        # Extract general data for the county
        county_name = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@id='CountyName']"))).text
        total_customers_tracked = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='col-xs-4 col-sm-12'])[1]"))).text
        total_customers_out = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='col-xs-4 col-sm-12'])[2]"))).text
        outage_percentage = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='col-xs-4 col-sm-12'])[3]"))).text
        last_updated = driver.find_element(By.CSS_SELECTOR, ".datetime").text

        # Extract all utility providers and their respective data
        utilities = driver.find_elements(By.XPATH, "//tr[@class='']//td[@class='row']")

        # Loop through each utility provider on the page
        utilities_data = []
        for utility in utilities:
            utility_provider = utility.find_element(By.XPATH, ".//div[@class='col-xs-12 col-md-5']/a").text
            utility_customers_tracked = utility.find_element(By.XPATH, ".//div[@class='text-right col-xs-6 col-md-2']").text
            utility_customers_out = utility.find_element(By.XPATH, ".//div[@class='text-right col-xs-6 col-md-2'][2]").text  # Specific to each utility
            
            utilities_data.append({
                "Utility Provider": utility_provider,
                "Utility Customers Tracked": utility_customers_tracked,
                "Utility Customers Out": utility_customers_out
            })

    except Exception as e:
        # Handle missing data gracefully and print exception for debugging
        print(f"Error scraping {url}: {e}")
        county_name = "Not Found"
        total_customers_tracked = "Not Found"
        total_customers_out = "Not Found"
        outage_percentage = "Not Found"
        last_updated = "Not Found"
        utilities_data = [{"Utility Provider": "Not Found", "Utility Customers Tracked": "Not Found", "Utility Customers Out": "Not Found"}]

    # Return the data as a dictionary with the utilities data as a list of dictionaries
    return {
        "County Name": county_name,
        "Total Customers Tracked": total_customers_tracked,
        "Total Customers Out": total_customers_out,
        "Outage Percentage": outage_percentage,
        "Last Updated": last_updated,
        "Utilities": utilities_data
    }

# Read in the CSV and clean column names
mc_counties = pd.read_csv("counties.csv")

def clean_column_names(df):
    df.columns = [re.sub(r'\W+', '_', col).strip().lower() for col in df.columns]
    return df

mc = clean_column_names(mc_counties)

# Loop over the URLs in the 'link' column and scrape data
all_data = []
for link in mc['link']:
    county_data = scrape_county_data(link)
    all_data.append(county_data)

# Flatten the utilities data into a DataFrame
expanded_data = []
for county in all_data:
    for utility in county['Utilities']:
        expanded_data.append({
            "County Name": county['County Name'],
            "Total Customers Tracked": county['Total Customers Tracked'],
            "Total Customers Out": county['Total Customers Out'],
            "Outage Percentage": county['Outage Percentage'],
            "Last Updated": county['Last Updated'],
            "Utility Provider": utility['Utility Provider'],
            "Utility Customers Tracked": utility['Utility Customers Tracked'],
            "Utility Customers Out": utility['Utility Customers Out']
        })

# Convert the flattened data into a DataFrame
scraped_df = pd.DataFrame(expanded_data)

# Print the resulting DataFrame
print(scraped_df)

# Save the DataFrame to a CSV (if needed)
scraped_df.to_csv("scraped_data_with_utilities.csv", index=False)

# Close the browser
driver.quit()


