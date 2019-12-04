import networkx as nx 
import matplotlib.pyplot as plt
import argparse
import pandas as pd

# parser = argparse.ArgumentParser()
# parser.add_argument('--file', '-f', help='Path to tuples', type=str)
# args = parser.parse_args()

G=nx.Graph()

f = open('extracted_tuples.txt','r')
for i, line in enumerate(f):
    if (i + 1)%7 == 0:
        tuples = line[8:].split(' -> ')
        for t in range(0, len(tuples) - 1):
            G.add_node(tuples[t].split(',')[1].replace(')',''))
            G.add_edge(tuples[t].split(',')[1].replace(')',''), tuples[t+1].split(',')[1].replace(')',''))

G.add_node(tuples[len(tuples) - 1].split(',')[1].replace(')',''))
nx.draw(G, with_labels=True, node_size=400)
plt.savefig("graph.png")
plt.show()
