import bs4
import requests
import json
recipeList = []

for counter in range(12):
    url = "https://food.ndtv.com/recipe/recipe-load-more/type/recipe/page/{}/query/indian/lang/1".format(counter)
    request = requests.get(url)
    bs = bs4.BeautifulSoup(request.text, 'html.parser')
    links = bs.find_all('a', href=True)
    for link in links:
        isRecipe = "https://food.ndtv.com/recipe-" in link['href']
        isHindi = "-hindi-" in link['href']
        if(isRecipe and not isHindi):
            recipe_ingredient = ""
            recipe_directions = ""
            recipe_dict = {}
            recipe_req = requests.get(link['href'])
            recipe_bs = bs4.BeautifulSoup(recipe_req.text, 'html.parser')
            headingName = recipe_bs.select('h1')[0].get_text().replace('Recipe','')
            # print(headingName)
            recipe_dict['heading'] = headingName

            ingredient_list = recipe_bs.find("div", {"class": "ingredients"}).find('ul')
            for ingredient in ingredient_list.find_all('li'):
                recipe_ingredient += ingredient.get_text() + "| "
            
            # print(recipe_ingredient)
            recipe_dict['ingredients'] = recipe_ingredient

            direction_list = recipe_bs.find('div', {'class': 'method'}).find('ul')
            for direction in direction_list.find_all('li'):
                recipe_directions += direction.get_text() + "| "

            # print(recipe_directions)
            recipe_dict['directions'] = recipe_directions

            recipeList.append(recipe_dict)


print(len(recipeList))
file_obj = open("ndtv.json","w")
recipeJson = json.dump(recipeList, file_obj, indent=2)
            


