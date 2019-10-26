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
        self.rejected_words_ingredients = ['cup', 'tablespoon', 'teaspoon', 'tablespoons']
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

    def pos_tag(self, text):
        return nltk.pos_tag(text)

    def extract_ingredient(self, text):
        # ner = self.ner_tagger.ner_tag(text)
        text = [char for char in text.split(' ') if char != '']
        tags = self.pos_tag(text)
        print()
        print(tags)

        i = 0
        ingredient = []
        tuples = []
        continoues = False
        while i < len(tags):
            if tags[i][1].startswith('NN'):
                continoues = True
                if tags[i][0] not in self.rejected_words_ingredients:
                    ingredient.append(self.lemmatizer.lemmatize(tags[i][0]))
            # elif tags[i][1] == 'JJ' or tags[i][1] == 'VBP' or tags[i][1] == 'VBN':
            #     continoues = True
            #     if tags[i][0] not in self.rejected_words_ingredients:
            #         ingredient.append(self.lemmatizer.lemmatize(tags[i][0]))
            elif tags[i][0] in self.accepted_puntuations and continoues:
                continoues = True
                if tags[i][0] not in self.rejected_words_ingredients:
                    ingredient.append(self.lemmatizer.lemmatize(tags[i][0]))
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

        print(tags)

        action = None
        i = 0
        ingredient = []
        continoues = False
        while i < len(tags):
            if tags[i][1] == 'NNP':
                action = tags[i][0]
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join(ingredient)
                    if action != None:
                        tuples.append([action, ingredient])
                    ingredient = []
            elif tags[i][1] == 'JJ' or tags[i][1] == 'VBD':
                continoues = True
                ingredient.append(tags[i][0])
            elif tags[i][1].startswith('NN'):
                continoues = True
                ingredient.append(tags[i][0])
            elif tags[i][1].startswith('VB'):
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join(ingredient)
                    if action != None:
                        tuples.append([action, ingredient])
                    ingredient = []
            elif tags[i][0] in self.accepted_puntuations and continoues:
                continoues = True
                ingredient.append(tags[i][0])
            else:
                continoues = False
                if ingredient != []:
                    ingredient = ' '.join(ingredient)
                    if action != None:
                        tuples.append([action, ingredient])
                    ingredient = []

            # print(tags[i], ingredient)
            i += 1
        return tuples


parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', help='Path to cleaned dataset', default='dataset/processed_recipes.tsv', type=str)
args = parser.parse_args()

df = pd.read_csv(args.file, sep='\t', lineterminator='\n')

index = 1
title = df.title[index]
ingredients = df.ingredients[index].split('|')
ingredients = [ing for ing in ingredients if 'Add' not in ing]
directions = df.directions[index]

extractor = ExtractTuple()

for i in range(len(ingredients)):
    tuples = '|'.join(extractor.extract_ingredient(ingredients[i]))
    print(tuples)
    ingredients[i] = tuples

print(directions)

print()
tuples = extractor.extract(directions, ' '.join(ingredients))

for tup in tuples:
    print(tup)
