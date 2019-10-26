import pandas as pd
import string
from tqdm import tqdm

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    for punct in string.punctuation:
        text = text.replace(punct, ' {} '.format(punct))
    text = text.replace('  ', ' ')
    if text[0] == " ":
        return text[1:]
    return text

def process_recipe(title, ingredients, directions):
    title = clean_text(title)
    ing = clean_text(ingredients)
    ingredients = []
    for i in ing.split('|'):
        if i != ' ':
            if i[0] == " ":
                i = i[1:]
            if i[-1] == " ":
                i = i[:-1]
            ingredients.append(i)

    directions = clean_text(directions)

    return title, '|'.join(ingredients), directions

df = pd.read_json('dataset/recipes.json')

titles_list = []
ingredients_list = []
directions_list = []

for i in tqdm(range(len(df))):
    title = df.heading[i]
    ingredients = df.ingredients[i]
    directions = ' '.join(df.directions[i].split('|'))
    t, i, d = process_recipe(title, ingredients, directions)
    titles_list.append(t)
    ingredients_list.append(i)
    directions_list.append(d)

df = pd.DataFrame([titles_list, ingredients_list, directions_list])
df = df.transpose()
df.columns = ['title', 'ingredients', 'directions']
df.to_csv('dataset/processed_recipes.tsv', sep='\t', index=False)
