# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 09:30:02 2019

@author: Alex Palomino
"""


# libraries
import pandas as pd
import numpy as np
import networkx as nx #networkX version 2.2
from networkx.algorithms.approximation import min_weighted_dominating_set
import matplotlib.pyplot as plt
 
# Build a dataframe with 4 connections
# https://python-graph-gallery.com/320-basic-network-from-pandas-data-frame/

# Load Network Data
df = pd.read_csv('ca_sandia_auth.csv', header=0); #ca_sandia_auth.csv is directed
df = df.sort_values(by = ['from', 'to'])
df = pd.DataFrame(df, columns=['from', 'to', 'edges', 'willingness', 'influenced'])
df.reset_index(drop=True, inplace=True)
 
# Build your graph. Note that we use the DiGraph function to create a directed graph.
#G=nx.from_pandas_dataframe(df_SandiaAuth, 'from', 'to', create_using=nx.DiGraph() )

# Build your graph
G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph()) 

# Plot it
plt.figure(3,figsize=(8,8)) 
#nx.draw(G, with_labels=True, node_size=5, node_color="skyblue", alpha=0.5, linewidths=40)
#nx.draw(G, with_labels=True, node_size=1500, node_color="skyblue", node_shape="o", alpha=0.5, linewidths=4, font_size=25, font_color="grey", font_weight="bold", width=2, edge_color="grey")
#nx.draw(G, with_labels=True, width=2, node_color="skyblue", style="solid")
#nx.draw(G, with_labels=True, width=2, node_color='skyblue', edge_color=df_SandiaAuth['edges'], edge_cmap=plt.cm.Blues)
nx.draw(G, with_labels=True, width=df['edges'],  node_color="skyblue")
plt.title("Sandia Authorship Network")

plt.show()

#%% Graph Node Heuristics

# https://networkx.github.io/documentation/stable/reference/algorithms/index.html

heuristics = ['betweeness_cent', 'closeness_cent', 'degree_cent', 'in_degree_cent', 'out_degree_cent', 'min dominant']

bc = nx.betweenness_centrality(G);
cc = nx.closeness_centrality(G); # same as "distance centrality"
dc = nx.degree_centrality(G);
# --- networkx.algorithms.centrality.degree_centrality --- #
#The degree centrality values are normalized by dividing by the maximum possible degree in a simple graph n-1 where n is the number of nodes in G.
#For multigraphs or graphs with self loops the maximum degree might be higher than n-1 and values of degree centrality greater than 1 are possible.
in_dc = nx.in_degree_centrality(G);
out_dc = nx.out_degree_centrality(G);

# --- Min Weight Dominating set only for undirected graph --- #
#This algorithm computes an approximate minimum weighted dominating set for the graph G. The upper-bound on the size of the solution is log w(V) * OPT. Runtime of the algorithm is \(O(|E|)\).
#References: Vazirani, Vijay Approximation Algorithms (2001)

#mwds = list(min_weighted_dominating_set(G, weight=None))
#dct = dict(zip(np.arange(0,df.values.max(),1), [0]*df.values.max()))
#
#for m in mwds:
#    dct[m] = 1;
#mwds = dct;

#networkx.algorithms.approximation.dominating_set.min_weighted_dominating_set
max_nodes = np.max([df['from'].values.max(), df['to'].values.max()]);
df_nodes = pd.DataFrame(data=None, index=np.arange(0,max_nodes,1), columns=heuristics)

df_nodes['betweeness_cent'] = pd.DataFrame.from_dict(bc, orient='index')
df_nodes['closeness_cent'] = pd.DataFrame.from_dict(cc, orient='index')
df_nodes['degree_cent'] = pd.DataFrame.from_dict(dc, orient='index')
df_nodes['in_degree_cent'] = pd.DataFrame.from_dict(in_dc, orient='index')
df_nodes['out_degree_cent'] = pd.DataFrame.from_dict(out_dc, orient='index')
#df_nodes['min dominant'] = pd.DataFrame.from_dict(mwds  , orient='index')

#%% Agglomerate Nodes by Influence

def glom(seeds, steps):    
    
    df['influenced'] = np.where(df['from'].isin(seeds), 10, 0)
    #df['influenced'] = df['from'].apply(lambda x: 10 if x == v else 0)
    #df['influenced'].at[df['from'].iloc[v]] = 10;      
    
    for v in seeds:
        i = 0;
        df_seed = df[df['from'] == v]
        print('\n', df_seed)
    
        for idx, row in df_seed.iterrows():
            rnd = random.random()
            print(rnd, df_seed['willingness'].loc[idx])
            
            if rnd < df_seed['willingness'].loc[idx]:
                print('--- Success')
                
                to_inf = df_seed['to'].iloc[i];
                seeds.append(to_inf) #add 'TO' vertex to seeds
                df['influenced'].at[to_inf] = 1
                
                i += 1;
            else:
                print('--- Failure')
            
            steps += 1; #count attempts to influence a vertex
            print('** ', steps, ' **')
        
        seeds.remove(v)
    
    df_inf = df[df['influenced'] > 0]
    
    # RECURSE if there are uninfluenced vertices
    if np.any(df['influenced'] == 0):
        glom(seeds, steps)   
        
    
    return df, df_inf, steps
     
#%% Seed Nodes
            
import random

# Assign likelihood of adoption for all vertices
df['willingness'] = df['willingness'].apply(lambda x: random.random())
df['influenced'] = np.zeros((len(df),1))

# Assign Seed Vertices 
n = 3
seeds = random.sample(set(np.arange(0,len(df),1)), n)
seeds = [30, 33, 40, 60];
print('Seeds: ', seeds)

#lambda x: True if x % 2 == 0 else False
steps = 0;


df, df_inf, steps = glom(seeds, steps)


    
    
