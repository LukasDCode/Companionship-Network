import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

def read_network(path_to_network, verbose):

    # Uppercase Letters for dataframe columns, lowercase letters for the network attributes
    df = pd.read_csv(path_to_network, sep=' ', skiprows=2, names= ["BuyerID", "SellerID", "Review", "Time"])
    if verbose:
        print("Information about the dataframe:")
        print(df.head())
        print(df.info())

    # create lists with unique entries of both buyers and sellers to initiate unconnected nodes in the network
    buyer_list = ['b'+str(x) for x in list(set(df['BuyerID'].tolist()))]
    seller_list = ['s'+str(x) for x in list(set(df['SellerID'].tolist()))]
    if verbose: print("# of Buyer nodes", len(buyer_list), "; # of Seller nodes", len(seller_list))

    # create a multiedge-graph and fill it with all buyer & seller nodes, but first without edges
    # it is not directed, because networkx 2.8.4 does not provide some functions for directed graphs
    B = nx.MultiGraph(name="Companion Network")
    B.add_nodes_from(buyer_list, bipartite=0)
    B.add_nodes_from(seller_list, bipartite=1)

    # add all edges, iterate through df and add each edge with a review and time attribute
    # lowercase letters are for network/edge attributes, Uppercase letters are for dataframe columns
    for index, row in df.iterrows():
        B.add_edge("b"+str(row["BuyerID"]), "s"+str(row["SellerID"]), review=row['Review'], time=row['Time'])
        if verbose and index<5:
            print(row['BuyerID'], row['SellerID'], row['Review'], row['Time'])

    if verbose:
        print(nx.info(B))
        print("Graph is bipartite:", nx.is_bipartite(B))

    return B


if __name__ == "__main__":
    verbose = False #False #True

    # bipartite multiweighted
    # edges: 50632 buyer_nodes: 10106 seller_nodes: 6624
    filename = "../network/ia-escorts-dynamic.edges"
    network = read_network(filename, verbose)

    """
    print(network["b1"]["s1"][0]["time"])
    print(network["b1"]["s1"][0]["review"])
    """

    # https://networkx.org/documentation/stable/reference/algorithms/component.html
    print("conneected components:", nx.number_connected_components(network))
    comp = nx.node_connected_component(network, "s57") # the connected component including 's57' has x nodes in it
    print(len(comp))

    ccomp = nx.connected_components(network)
    print(sum(1 for x in ccomp)) # total of 418 connected components
