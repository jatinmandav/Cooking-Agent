import requests
import bs4
import json

url1 = "https://www.thespruceeats.com/indian-basics-4162610"
url2 = "https://www.thespruceeats.com/exploring-indian-food-4162609"
url3 = "https://www.thespruceeats.com/indian-appetizers-4162608"
url4 = "https://www.thespruceeats.com/indian-main-dishes-4162607"
url5 = "https://www.thespruceeats.com/indian-side-dishes-4162606"
url6 = "https://www.thespruceeats.com/indian-pickles-chutneys-4162605"
url7 = "https://www.thespruceeats.com/indian-desserts-4162604"
urls = [url1, url2, url3, url4, url5, url6, url7]
recipeList = []
for u in urls:
    res = requests.get(u)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    headings = soup.findAll('a',href=True)
    for heading in headings:
        url = heading['href']
        valid = ("-195" in url) or ("-180" in url)
        if(valid):
            try:
                ind_ingredient = ""
                ind_directions = ""
                recipeDictionary = {}
                # print(url)
                res_ind = requests.get(url)
                soup_ind = bs4.BeautifulSoup(res_ind.text, 'html.parser')
                headingName = soup_ind.select('h1')[0].getText()
                recipeDictionary["heading"] = headingName
                #HEADING NAME
                # print(headingName)
                #INGREDIENTS SECTION
                ingredientSection = soup_ind.select('section', {'id':'section--ingredients_1-0'})[0]
                unorderedList = ingredientSection.find('ul')
                for individual in unorderedList.findAll('li'):
                    ind_ingredient += individual.getText().rstrip() + "|"

                recipeDictionary["ingredients"] = ind_ingredient
                # print("Ingredients: " + ind_ingredient)

                #DIRECTIONS SECTION
                directionsSection = soup_ind.select('section', {'class':'section--instructions'})[1]
                dirList = directionsSection.find('ol')
                for ind in dirList.findAll('p'):
                    ind_directions += ind.get_text().rstrip() + "|"

                recipeDictionary["directions"] = ind_directions
                # print("Directions: " + ind_directions)

                recipeList.append(recipeDictionary)   
            except:
                continue


file_obj = open("second.json","w")
recipeJson = json.dump(recipeList, file_obj, indent=2)
