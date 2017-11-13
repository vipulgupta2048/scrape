from bs4 import BeautifulSoup
import requests
url = raw_input("Enter a website address")
response = requests.get(url)
data = response.text
soup = BeautifulSoup(data)
for link in soup.find_all('a')
     print link.get('href')
