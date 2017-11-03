from urllib.request import urlopen
from bs4        import BeautifulSoup
import json

url = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
page = urlopen(url)
soup = BeautifulSoup(page)
right = soup.find_all("table", class_='wikitable sortable plainrowheaders')

#Generate lists
A=[]
B=[]
C=[]
D=[]
E=[]
F=[]
G=[]

for row in right[0].find_all('tr'):
    cells = row.find_all("td")
    states= row.find_all("th") #To store second column data
    if len(cells)==6:      #Only extract table body not heading
        A.append(cells[0].find(text=True))
        B.append(states[0].find(text=True))
        C.append(cells[1].find(text=True))
        D.append(cells[2].find(text=True))
        E.append(cells[3].find(text=True))
        F.append(cells[4].find(text=True))
        G.append(cells[5].find(text=True))
        
        dick_table = {
			"Serial No." : A,
			"State"      : B,
			"ACapital"   : C,
			"LCapital"   : D,
			"JCapital"   : E,
			"Year"       : F,
			"FormerC"    : G
		}        
with open("table_wikipedia_data.json", "w") as writeJSON:
	json.dump(dick_table, writeJSON)
