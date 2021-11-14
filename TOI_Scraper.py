### IMP
# Create the folders for the years you are scrapping


# Import the requried packages
import requests
from bs4 import BeautifulSoup
import os
import csv
from datetime import timedelta, date
import re


# Set the starting value for timestamp
ts = 37104
first_date = date(2001, 8, 1)


# Set the timeframe for scraping
dates = []
start_date = date(2016, 1, 1)
end_date = date(2017, 1, 1)

# Get the starting timeframe
ts = ts + abs(first_date - start_date).days

# Compile the dates
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        dates.append((start_date + timedelta(n)).strftime("%Y-%m-%d"))
daterange(start_date, end_date)

# List for storing urls with bad html or ssl certificate errors
erroneous = []

# Loop through dates in the archive
for date in dates:
    year = date.split('-')[0]
    month = date.split('-')[1]
    date_number = date.split('-')[2]

# Generate the url
    url = 'https://timesofindia.indiatimes.com/'+year+'/'+month+'/'+date
    tail = '/archivelist/year-'+year+',month-'+month+',starttime-'+str(ts)+'.cms'

    ts += 1
    url = url+tail

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

# Save the csv per month
    file_name = month+'-'+year+'.csv'

    file_exists = os.path.exists(year+'/'+file_name)

    with open(year+'/'+file_name, 'a', newline='', encoding='utf-8') as file:
        if not file_exists:
            row_list = [["SN", "Title", "Keywords", "Created_Date", "Updated_Date", "Month", "Year", "Time", "TimeZone", "Place", "Author", "Source", "Text", "URL"]]
            writer = csv.writer(file)
            writer.writerows(row_list)

# Define keywords
    keywords = []


# Contains the urls matching the keywords
    considerable = []

    all_links = soup.find_all('span', attrs={'style':'font-family:arial ;font-size:12;color: #006699'})

    for links in all_links:
        link = links.find_all('a')
        for in_link in link:
            clean = in_link.text.lower()
            keys = []
            if(any(keyword in clean for keyword in keywords)):
                for i in keywords:
                    if(i in clean):
                        keys.append(i)
                considerable.append([in_link, keys])

    k = 0

    row_list = []

    for link, keys in considerable:
        page_url = str(link.get('href'))
        try:
        	r = requests.get(page_url)
        	soup = BeautifulSoup(r.text, 'html.parser')
        except:
        	erroneous.append([page_url, 'ssl'])
        	print ('ssl')
        	continue

# Get the article properties like place, text, date, etc

        place = 'india'
        if(page_url.split('//')[2].split('/')[0] == 'city'):
            place = page_url.split('//')[2].split('/')[1]

        try:
            title = soup.find('h1', attrs={'class':'_23498'}).text.strip()
        except:
            makeshift = page_url.split('//')[2].split('/')
            title = makeshift[len(makeshift) - 1]
            erroneous.append([page_url, date])


        try:
            full_text =soup.find('div', attrs={'class':'_1_Akb'}).text.replace('Download The Times of India News App for Latest India News','').strip()
            
            clean = re.compile('<.*?>')
            cleantext = re.sub(clean, '', full_text)

            timestamp = soup.find('div', attrs={'class':'_3Mkg- byline'})
            info = timestamp.text.split('|')

            timeinfo = info[len(info) - 1].split(',')

            timezone_info = timeinfo[2].split(' ')
            time = timezone_info[1].strip()
            timezone = timezone_info[2].strip()

            year = timeinfo[1].strip()

            month = timeinfo[0].split(' ')[2].strip()
            date_in = timeinfo[0].split(' ')[3].strip()

            if(len(info) > 2):
                author = info[0].strip()
            else:
                author = ''
            source = info[len(info) - 2].strip()
            k += 1
            row = [k, title, keys, date_number, date_in, month, year, time, timezone, place, author, source, cleantext, page_url]
            row_list.append(row)
        except:
            erroneous.append([page_url, date])

# Write the csv file per day
    with open(year+'/'+file_name, 'a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

    print(date+'done')

# Logs the erroneous urls in a log file
with open('log.txt', 'w') as a:
	a.write(str(erroneous))