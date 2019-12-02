import pandas as pd
import argparse
import string

import nltk

from nltk import pos_tag, RegexpParser, ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.tree import Tree
from nltk.tokenize import word_tokenize, PunktSentenceTokenizer
from nltk.corpus import state_union
from nltk.stem import WordNetLemmatizer, PorterStemmer

class ExtractTuple:
    def __init__(self):
        self.accepted_puntuations = ['-']
        self.rejected_words_ingredients = ['cup', 'tablespoon', 'teaspoon']

        self.action_words = ['break', 'melt', 'spread', 'layer', 'roll out',
                            'fry', 'peel', 'mix', 'whip', 'saute', 'taste',
                            'cut', 'chop', 'slice', 'grate', 'boil', 'steam',
                            'pinch', 'pour', 'add', 'barbeque', 'roast', 'bake',
                            'stir', 'weigh', 'whisk', 'combine', 'fold', 'fill',
                            'heat']


        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

    def substring_matching(self, str1, str2):
        str1 = [s for s in str1.split(' ') if s != '']
        str2 = [s for s in str2.split(' ') if s != '']

        i = 0
        j = 0
        count = 0
        while i < len(str1) and j < len(str2):
            if str1[i] == str2[j]:
                i += 1
                j += 1
                count += 1
            else:
                i += 1

        if count >= len(str1)*0.2:
            return True

        return False

    def is_valid_ingredient(self, ingredients, ingredient):
        for ing in ingredients:
            if self.substring_matching(ingredient, ing):
                return True
            if self.substring_matching(ing, ingredient):
                return True
        return False

    def pos_tag(self, text):
        return nltk.pos_tag(text)

    def extract_ingredient(self, text):
        text = [char for char in text.split(' ') if char != '']
        tags = self.pos_tag(text)

        i = 0
        ingredient = []
        tuples = []
        continoues = False
        while i < len(tags):
            if tags[i][1].startswith('NN'):
                continoues = True
                word = self.lemmatizer.lemmatize(tags[i][0])
                if word not in self.rejected_words_ingredients:
                    ingredient.append(self.lemmatizer.lemmatize(word))
            if tags[i][1] == 'JJ' or tags[i][1] == 'VBD' or tags[i][1] == 'VBP':
                continoues = True
                word = self.lemmatizer.lemmatize(tags[i][0])
                if word not in self.rejected_words_ingredients:
                    ingredient.append(self.lemmatizer.lemmatize(word))
            elif tags[i][0] in self.accepted_puntuations and continoues:
                continoues = True
                word = self.lemmatizer.lemmatize(tags[i][0])
                if word not in self.rejected_words_ingredients:
                    ingredient.append(self.lemmatizer.lemmatize(word))
            else:
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join(ingredient)
                    if not (ingredient.endswith('ed') or ingredient.endswith('ing') or ingredient in string.punctuation):
                        tuples.append(ingredient)
                    ingredient = []

            i += 1

        if ingredient != []:
            ingredient = ' '.join(ingredient)
            if not (ingredient.endswith('ed') or ingredient.endswith('ing') or ingredient in string.punctuation):
                tuples.append(ingredient)
            ingredient = []

        return tuples

    def extract(self, text, ingredients):
        tuples = []
        text = [char for char in text.split(' ') if char != '']
        tags = self.pos_tag(text)

        # print(tags)

        action = None
        i = 0
        ingredient = []
        continoues = False
        while i < len(tags):
            # if tags[i][1] == 'NNP' or tags[i][1].startswith('VB'):
            #     if tags[i][0].lower() in self.action_words:
            #         action = tags[i][0].lower()

            if tags[i][1] == 'NNP':
                if tags[i][0].lower() in self.action_words:
                    action = tags[i][0].lower()
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join([self.lemmatizer.lemmatize(word) for word in ingredient])
                    if action != None:
                        if self.is_valid_ingredient(ingredients, ingredient):
                            tuples.append([action, ingredient])
                    ingredient = []
            elif tags[i][1] == 'JJ' or tags[i][1] == 'VBD':
                continoues = True
                ingredient.append(tags[i][0])
            elif tags[i][1].startswith('NN'):
                continoues = True
                ingredient.append(tags[i][0])
            elif tags[i][1].startswith('VB'):
                if tags[i][0].lower() in self.action_words:
                    # print(tags[i][0])
                    action = tags[i][0].lower()
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join([self.lemmatizer.lemmatize(word) for word in ingredient])
                    if action != None:
                        # print(self.is_valid_ingredient(ingredients, ingredient), ingredient)
                        if self.is_valid_ingredient(ingredients, ingredient):
                            tuples.append([action, ingredient])
                    ingredient = []
            elif tags[i][0] in self.accepted_puntuations and continoues:
                continoues = True
                ingredient.append(tags[i][0])
            else:
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join([self.lemmatizer.lemmatize(word) for word in ingredient])
                    if action != None:
                        if self.is_valid_ingredient(ingredients, ingredient):
                            tuples.append([action, ingredient])
                    ingredient = []

            # print(action, ingredient, tags[i])
            i += 1

        return tuples


parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', help='Path to cleaned dataset', default='dataset/processed_recipes.tsv', type=str)
parser.add_argument('--num_recipes', '-n', help='Number of Recipes to process', default=10, type=int)
args = parser.parse_args()

df = pd.read_csv(args.file, sep='\t')

writer = open('extracted_tuples.txt', 'w')

for index in range(args.num_recipes):
    title = df.title[index]
    ingredients = df.ingredients[index].split('|')
    ingredients = [ing for ing in ingredients if 'Add' not in ing]
    directions = df.directions[index]

    extractor = ExtractTuple()

    for i in range(len(ingredients)):
        tuples = ' '.join(extractor.extract_ingredient(ingredients[i]))
        ingredients[i] = tuples
    ingredients = [ing for ing in ingredients if ing != '']
    # print(ingredients)

    tuples = extractor.extract(directions, ingredients)
    writer.write('\n*** RECIPE ***\n')
    writer.write('INGREDIENTS: {}\n\n'.format(', '.join(ingredients)))
    writer.write('DIRECTIONS: {}\n\n'.format(directions))

    tuple_formatted = []

    for tup in tuples:
        tuple_formatted.append('({}, {})'.format(tup[0], tup[1]))

    writer.write('TUPLES: {}\n'.format(' -> '.join(tuple_formatted)))

    print('{} of {} processed.'.format(index+1, args.num_recipes))

writer.close()
