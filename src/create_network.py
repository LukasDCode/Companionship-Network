import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

def read_network(path_to_network):

    df = pd.read_csv(path_to_network, sep=' ', skiprows=2, names= ["BuyerID", "SellerID", "Review", "Time"])
    #df = df[['BuyerID', 'SellerID']]
    print(df.head())
    print(df.info())
    
    B = nx.Graph()

    buyer_list = list(set(df['BuyerID'].tolist()))
    seller_list = list(set(df['SellerID'].tolist()))

    buyer_list = ['b'+str(x) for x in buyer_list]
    seller_list = ['s'+str(x) for x in seller_list]

    print("buyer length", len(buyer_list), "seller length", len(seller_list))

    B.add_nodes_from(buyer_list, bipartite=0)
    B.add_nodes_from(seller_list, bipartite=1)

    print(nx.info(B))

    """
    ## Logic to add nodes and edges to graph with their metadata
    for r, d in df.join(roles).iterrows():
        pid = 'P{0}'.format(d['PersonID'])  # pid = "Person I.D."
        cid = 'C{0}'.format(d['CrimeID'])  # cid = "Crime I.D."
        bipartite_G.add_node(pid, bipartite='person')
        bipartite_G.add_node(cid, bipartite='crime')
        bipartite_G.add_edge(pid, cid, role=d['roles'])

    ## Logic to add gender metadata to nodes
    for idx in gender.index:
        nodeid = 'P{0}'.format(idx+1)
        bipartite_G.node[nodeid]['gender'] = gender.loc[idx]["gender"]
    """


    # Reading the file. "DiGraph" is telling to reading the data with node-node. "nodetype" will identify whether the node is number or string or any other type.
    #g = nx.read_edgelist(path_to_network, create_using=nx.MultiDiGraph(), nodetype = int, data=(("review", int), ("time", int),))

    # check if the data has been read properly or not.
    

    return B


if __name__ == "__main__":
    # bipartite multiweighted
    # edges: 50632 buyer_nodes: 10106 seller_nodes: 6624
    filename = "../network/ia-escorts-dynamic.edges"
    read_network(filename)
