import argparse
import networkx as nx
from tqdm import tqdm

from create_network import read_network
from utils.rankings import get_most_frequent, rank_by_avg_review


def cleanse_network(network, verbose):
    # gather all nodes of components with size 2
    connected_components = nx.connected_components(network)
    remove_2_node_components = []
    removed_comp_counter, removed_edges_counter = 0, 0
    for comp in connected_components:
        # store all nodes which are part of a component of size 2 in a list
        if len(comp) == 2:
            tmp = network.subgraph(comp)
            
            # get information about all 2-node-components with more than 1 edge
            if verbose and tmp.number_of_edges() > 1:
                (u,v) = comp
                print("These 2-node-components have more than one edge:", u, v, "# of edges", tmp.number_of_edges())
                print(tmp.get_edge_data(u,v))

            removed_edges_counter += tmp.number_of_edges()
            removed_comp_counter += 1
            remove_2_node_components.extend(list(comp))

    # remove all nodes which are part of a component of size 2
    for node in remove_2_node_components:
        network.remove_node(node) # networkx automatically removes all edges to/from this node
        """
        Out of all the 2-node-components that get removed 5 have 2 edges instead of 1. (None with more than 2 edges.)
        But all of those 10 edges have a rating of +1 one, making them little informative.
        Thus, they are removed here.
        """

    if verbose:
        print("Components of size 2 removed:", removed_comp_counter)
        print("Removed nodes:", 2*removed_comp_counter, "Removed edges:", removed_edges_counter)
    return network

def analyze_entire_network(network, verbose):
    # https://networkx.org/documentation/stable/reference/algorithms/component.html
    print("Total amount of connected components:", nx.number_connected_components(network))
    connected_components = nx.connected_components(network)
    comp_size_3_counter, comp_size_4_counter, comp_size_5_to_8_counter = 0, 0, 0
    buyer_heavy_size_3_comp_counter, seller_heavy_size_3_comp_counter = 0, 0
    size_3_comp_num_of_edges = 0
    buyer_heavy_size_4_comp_counter, seller_heavy_size_4_comp_counter, balanced_size_4_comp_counter = 0, 0, 0
    size_4_comp_num_of_edges = 0
    size_5_to_8_comp_num_of_edges = 0

    # iterate through all components and do different analyses on them
    for comp in connected_components:
        #print("Size of component:", len(comp))
        if len(comp) == 3:
            comp_size_3_counter += 1
            buyer_heavy, seller_heavy = analyze_size_3_comp(comp)
            buyer_heavy_size_3_comp_counter += buyer_heavy
            seller_heavy_size_3_comp_counter += seller_heavy

            tmp = network.subgraph(comp)
            if verbose and tmp.number_of_edges() > 2:
                (u,v,w) = comp
                print("This 3-node-component has more than two edges:", u, v, w, "# of edges", tmp.number_of_edges())
                print(tmp.get_edge_data(u,v), tmp.get_edge_data(u,w), tmp.get_edge_data(v,w))
            size_3_comp_num_of_edges += tmp.number_of_edges()

            """
            Out of all 3-node-components, 3 have more than 2 edges. All 3 of them have 3 edges.
            All of these 3 edges have a weighting of +1, making them little informative.
            """
            
        elif len(comp) == 4:
            comp_size_4_counter += 1
            buyer_heavy, seller_heavy, balanced = analyze_size_4_comp(comp)
            buyer_heavy_size_4_comp_counter += buyer_heavy
            seller_heavy_size_4_comp_counter += seller_heavy
            balanced_size_4_comp_counter += balanced

            tmp = network.subgraph(comp)
            if verbose and tmp.number_of_edges() > 3:
                (u,v,w,x) = comp
                print("This 4-node-component has more than three edges:", u, v, w, x, "# of edges", tmp.number_of_edges())
                print(tmp.get_edge_data(u,v), tmp.get_edge_data(u,w))
                print(tmp.get_edge_data(u,x), tmp.get_edge_data(v,w))
                print(tmp.get_edge_data(v,x), tmp.get_edge_data(w,x))

                print("u, v, w, x", comp)

            size_4_comp_num_of_edges += tmp.number_of_edges()

            """
            Out of all 4-node-components, 2 have more than 3 edges. Both have 4 egdes.
            One has 4 edges with +1 reviews, making them little informative.
            But it has to be said that the component consists of 1 seller and 3 buyers, which all seemed to be satisfied with the product/service.
            The other has 4 edges with one 0 review and three -1 reviews, outlining it as either a bad service/product
            or as highly critical buyers, who expected more for their money.
            Looking closer at the components reveals that it consists of 2 sellers and 2 buyers.
            Lets call the sellers s1 & s2 and the buyers b1 & b2.
            In chronological order:
            1. b2 bought from s2 and left a review of -1
            2. b2 bought from s2 and left a review of -1 AGAIN
            3. b2 bought from s1 and left a review of 0
            4. b1 bought from s1 and left a review of -1

            If this would be put into a little context, it could be told as so:
            b2 bought the service/product of s2 (1.) and was not happy with what he got. He chose to gave s2 another chance and bought again from s2 (2.).
            But because he was not satisfied again, he switched seller and bought from s1 the next time (3.).
            As the service/product was better from s1 he told a friend of his, who then also turned to s1 and bought there (4.),
            but did not like the recommendation of his friend, as he rated the service/product as insufficient.
            """

        elif 5 <= len(comp) <= 8:
            comp_size_5_to_8_counter += 1
            size_5_to_8_comp_num_of_edges += network.subgraph(comp).number_of_edges()
            # TODO maybe more analysis here

        else: 
            # store giant component to analyze it later on, after all the 3 & 4 node components
            giant_component = comp
    
    # TODO uncomment
    """
    print("Components of size 3:", comp_size_3_counter)
    print("Buyer-heavy components of size 3:", buyer_heavy_size_3_comp_counter)
    print("Seller-heavy components of size 3:", seller_heavy_size_3_comp_counter)
    print("Amount of edges within all components of size 3:", size_3_comp_num_of_edges)

    print("Components of size 4:", comp_size_4_counter)
    print("Buyer-heavy components of size 4:", buyer_heavy_size_4_comp_counter)
    print("Seller-heavy components of size 4:", seller_heavy_size_4_comp_counter)
    print("Buyer-Seller-balanced components of size 4:", balanced_size_4_comp_counter)
    print("Amount of edges within all components of size 4:", size_4_comp_num_of_edges)

    print("Components of size 5, 6, 7 or 8:", comp_size_5_to_8_counter)
    print("Amount of edges within all components of size 5, 6, 7 or 8:", size_5_to_8_comp_num_of_edges)
    """

    # TODO change verbose back to variable
    analyze_giant_component(giant_component, network, True) #verbose)


def analyze_size_3_comp(comp):
    """
    return
    1,0 = comp contains 2 buyers and 1 seller
    0,1 = comp contains 1 buyer and 2 sellers
    """
    buyer_counter, seller_counter = 0, 0
    for node in comp:
        if node[0] == 's':
            seller_counter += 1
        elif node[0] == 'b':
            buyer_counter += 1
        else:
            raise TypeError("Node is neither Seller nor Buyer:", node)

    if buyer_counter > seller_counter:
        return 1, 0
    elif seller_counter > buyer_counter:
        return 0, 1
    else:
        # this should only occur in an Error case, because we have components of size 3
        return 0, 0

def analyze_size_4_comp(comp):
    """
    return
    1,0,0 = comp contains 3 buyers and 1 seller
    0,1,0 = comp contains 1 buyer and 3 sellers
    0,0,1 = comp contains 2 buyers and 2 sellers
    """
    buyer_counter, seller_counter = 0, 0
    for node in comp:
        if node[0] == 's':
            seller_counter += 1
        elif node[0] == 'b':
            buyer_counter += 1
        else:
            raise TypeError("Node is neither Seller nor Buyer:", node)

    if buyer_counter > seller_counter:
        return 1, 0, 0
    elif seller_counter > buyer_counter:
        return 0, 1, 0
    elif seller_counter == buyer_counter:
        return 0, 0, 1
    else:
        # this should only occur in an Error case
        return 0, 0, 0
    
def analyze_giant_component(comp, network, verbose):
    subgraph = network.subgraph(comp)
    subgraph.name = "Giant Component of Companion Network"
    if verbose:
        print(nx.info(subgraph))
    
    buyer_ranking, seller_ranking = {}, {}

    #TODO remove
    break_counter = 10

    # TODO uncomment & switch
    #for node in tqdm(comp):
    for node in comp:

        # TODO remove counter break code
        if break_counter <= 0:
            break
        break_counter -= 1

        edges = network.edges(node)
        if len(edges) > 2:

            if node[0] == 'b':
                buyer_ranking[node] = []
                for edge in edges:
                    (u,v) = edge
                    data = subgraph.get_edge_data(u,v)
                    for index in range(len(data)):
                        buyer_ranking[node].append((data[index]['time'], data[index]['review']))

            elif node[0] == 's':
                seller_ranking[node] = []
                for edge in edges:
                    (u,v) = edge
                    data = subgraph.get_edge_data(u,v)
                    for index in range(len(data)):
                        seller_ranking[node].append((data[index]['time'], data[index]['review']))
                    

    most_frequent_buyer = get_most_frequent(buyer_ranking)
    most_frequent_seller = get_most_frequent(seller_ranking)
    print("Buyer frequency:", most_frequent_buyer)
    print("Seller frequency:", most_frequent_seller)
    most_frequent_buyer_dict = dict(most_frequent_buyer)
    most_frequent_seller_dict = dict(most_frequent_seller)

    ranking_review_buyer = rank_by_avg_review(buyer_ranking)
    ranking_review_seller = rank_by_avg_review(seller_ranking)

    print("Average buyer ranking:")
    for id, avg_review in ranking_review_buyer:
        print("Buyer", id, "with avg review score of", avg_review, "and", most_frequent_buyer_dict[id], "purchases")

    print("Average seller ranking:")
    for id, avg_review in ranking_review_seller:
        print("Seller", id, "with avg review score of", avg_review, "and", most_frequent_seller_dict[id], "sells")



def main(args):
    # bipartite multiweighted
    # edges: 50632 buyer_nodes: 10106 seller_nodes: 6624
    filename = "../network/ia-escorts-dynamic.edges"
    
    # TODO
    network = read_network(filename, verbose=False) #verbose=args.verbose)

    # TODO
    network = cleanse_network(network, verbose=False) #verbose=args.verbose)
    analyze_entire_network(network, verbose=args.verbose)    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode toggle')
    args = parser.parse_args()
    main(args)


    """
    Does the performance of escorts increase or decrease over time?
    What buyers tend towards giving higher ratings and what buyers do rather give lower ratings,
    and then maybe do a ranking among them.
    And based on this ranking, we could also adjust the rating of the escorts, something similar to a hub-authority thing.
    
    so for instance you could explore some extensions for this kind of networks, as the usual metrics might need to be adapted
    you could also create projections on either side of the network (with all edges, just positive, just edges, etc) and study those, etc, etc
    """
