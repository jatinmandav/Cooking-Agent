import requests
import bs4
import json

#appetizers
url1 = 'https://www.allrecipes.com/recipes/1874/world-cuisine/asian/indian/appetizers/?internalSource=hub%20nav&referringId=233&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202&page=2'
#main-dishes
url2 = 'https://www.allrecipes.com/recipes/17136/world-cuisine/asian/indian/main-dishes/'
#breads
url3 = 'https://www.allrecipes.com/recipes/1876/world-cuisine/asian/indian/bread/?internalSource=hub%20nav&referringId=233&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202'
#side dishes
url4 = 'https://www.allrecipes.com/recipes/1877/world-cuisine/asian/indian/side-dishes/?internalSource=hub%20nav&referringId=233&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202'
#dessert
url5 = 'https://www.allrecipes.com/recipes/1879/world-cuisine/asian/indian/desserts/?internalSource=hub%20nav&referringId=233&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202'
#drinks
url6 = 'https://www.allrecipes.com/recipes/15935/world-cuisine/asian/indian/drinks/?internalSource=hub%20nav&referringId=233&referringContentType=Recipe%20Hub&linkName=hub%20nav%20daughter&clickId=hub%20nav%202'

urls = [url1, url2, url3, url4, url5, url6]
recipeList = []

for u in urls:
    res = requests.get(u)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    previousUrl = ""
    for anchor in soup.find_all('a', href=True):
        url = anchor['href']
        # valid = "https://www.allrecipes.com/recipe/" in url
        valid = ("https://www.allrecipes.com/video/" in url) or ("https://www.allrecipes.com/recipe/" in url)
        if(valid and previousUrl!=url):
            ingredient = ""
            prepTime = ""
            recipeDictionary = {}
            res_ind = requests.get(anchor['href'])
            soup_ind = bs4.BeautifulSoup(res_ind.text, 'html.parser')
            headingName = soup_ind.select('h1')[0].getText()
            recipeDictionary["heading"] = headingName
            
            # HEADING OF THE DISH
            # print(headingName)

            #INGREDIENTS OF THE DISH
            for i in soup_ind.findAll('ul', {'id': ['lst_ingredients_1', 'lst_ingredients_2']}):
                for j in i.findAll('li', {'class': 'checkList__line'}):
                    ingredient += j.get_text().rstrip() + "| "

            recipeDictionary["ingredients"] = ingredient

            #DIRECTIONS OF THE DISH
            for directions in soup_ind.findAll('div', {'class': 'directions--section__steps'}):
                for li in directions.findAll('span', {'class': 'recipe-directions__list--item'}):
                    item = li.get_text().rstrip()
                    prepTime += item
                    if(item != ""):
                        prepTime += "| "

            recipeDictionary["directions"] = prepTime
            # print(prepTime+ "\n")

            previousUrl = url

            recipeList.append(recipeDictionary)

file_obj = open("first.json","w")
recipeJson = json.dump(recipeList, file_obj, indent=2)
