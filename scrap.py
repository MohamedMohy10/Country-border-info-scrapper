import requests
from bs4 import BeautifulSoup
import re
import csv



def string_formatter(string):
    """Takes Country borders string and splits it to two strings containing country names and their corresponding border length"""
    countries = ', '.join(re.findall(r'([A-Za-z\s\']+)\s\d+', string))
    lengths = ', '.join(re.findall(r'[A-Za-z\s\']+\s([\d,.]+ km)', string))
    return (countries,lengths)


def main(url):
    """Main program function"""
    # reading page contents
    page = url.content
    soup = BeautifulSoup(page, "lxml")

    content = soup.find('div', {'class':'col-lg-9 col-md-12 col-sm-12'})
    countries_list = content.find_all("div", {'class':"pb30"})
    

    def get_country_details(country):
        # Get country name
        country_name = country.h3.text
        
        # defining values defaults
        borderCountry_data = [] # list of dictionaries of country border
        totalBorder_data = []
        
        border_total = '0 km'
        border_country = '-'
        border_length = '0 km'
        notes = '-'
        
        for i in range(len(country.find_all('strong'))):
            # getting the total border
            if country.find('strong').text == 'total:':
                border_total = country.find('strong').next_sibling.strip()
                
                # Getting the borders info (only present if there is a 'total' obviously)
                if border_total.strip() != '0 km':
                    country.find('strong').decompose()
                    country_details = country.find('strong').next_sibling.strip()
                    [border_country, border_length] = string_formatter(country_details)
                    country.find('strong').decompose()
                    
            if country.find('strong'):
                if country.find('strong').text == 'note:':
                    notes = country.find('strong').next_sibling.strip()
            else:
                break
            
        # first requirment country_name | border_country | border_length
        borderCountry_data.append(
            {
                'country_name': country_name,
                'border_country': border_country,
                'border_length': border_length
            }
        )
        
        # Second requirment country_name | border_total | border_notes
        totalBorder_data.append(
            {
                'country_name': country_name,
                'border_total': border_total,
                'notes': notes
            }
        )
        
    # Call get_country_details for each country
    for country in countries_list:
        get_country_details(country)
        
        
    return(borderCountry_data, totalBorder_data)


def csv_maker(borderCountry_data, totalBorder_data):
    """Takes the two lists generated in main() and converts them to .csv"""
    # Write the data to the CSV file
    keys1 = borderCountry_data[0].keys()
    keys2 = totalBorder_data[0].keys()
    
    # creating the 1st file
    with open('./border_country data.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys1)
        writer.writeheader()
        writer.writerows(borderCountry_data)
        print("==> 'border_country data.csv' file created")
    
    # creating the 2nd file
    with open('./total_border data.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys2)
        writer.writeheader()
        writer.writerows(totalBorder_data)
        print("==> 'total_border data.csv' file created")



# Main program
url = requests.get("https://www.cia.gov/the-world-factbook/field/land-boundaries/")
(data1, data2) = main(url)
csv_maker(data1, data2)
