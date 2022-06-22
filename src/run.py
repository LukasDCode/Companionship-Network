import argparse
import math
import networkx as nx
from datetime import datetime
from collections import Counter
import matplotlib.pylab as plt

from create_network import read_network
from utils.rankings import get_most_frequent, rank_by_avg_review, sort_avg_review_list
from utils.list_utils import print_top_and_bottom_of_list, turn_weighted_ranking_to_dict


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
            or as highly critical buyers, who expected more from their purchase.
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

    # Here, finally the giant component gets analyzed
    #TODO change back verbose to variable and not hardcoded True
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
    # this is where all the important stuff from the giant component happens
    # here all other methods are called
    print("Giant component size of", len(comp))
    subgraph = network.subgraph(comp)
    subgraph.name = "Giant Component of Companion Network"
    if verbose:
        print(nx.info(subgraph))
        general_edge_analysis(subgraph)

    buyer_ranking, seller_ranking = get_ranking_from_all_nodes(comp, subgraph)
    if verbose: make_prints_from_rankings(buyer_ranking, seller_ranking)
    # format for both: [(id, avg_review, num_reviews), (id2, avg_review2, num_reviews2), ...] sorted in descending order
    ranking_review_buyer, ranking_review_seller = get_2_attribute_ranking_rankings(buyer_ranking, seller_ranking, verbose)
    weighted_buyer_ranking = get_weighted_buyer_ranking(ranking_review_buyer)

    if verbose:
        print("Print weighted list:")
        print_top_and_bottom_of_list(weighted_buyer_ranking, k=7)

    weighted_buyer_ranking_dict = turn_weighted_ranking_to_dict(weighted_buyer_ranking)
    weighted_seller_ranking_dict, weighted_seller_list = get_weighted_seller_ranking(subgraph, comp, weighted_buyer_ranking_dict, verbose)

    """
    Here we are working with 2848 sellers and 4200 buyers from the giant component.
    All others with less edges have been filtered out because they are less connected and their rankings do not provide any information.
    """

    weighted_seller_ranking_list = sort_avg_review_list(weighted_seller_list)
    change_counter_dict = compare_weighted_with_unweighted(weighted_seller_ranking_list, ranking_review_seller)
    plot_change_counter_dict(change_counter_dict)


def plot_change_counter_dict(change_counter_dict):
    # Source: https://stackoverflow.com/a/37266356
    lists = sorted(change_counter_dict.items()) # sorted by key, return a list of tuples
    x, y = zip(*lists) # unpack a list of pairs into two tuples
    plt.bar(x, y)
    plt.title('Sellers that changed their ranking after weighting the buyers.')
    plt.xlabel('Change of ranks')
    plt.ylabel('Number of sellers that changed rank')
    #plt.show()
    plt.savefig("../plots/rank_change_of_sellers_after_weighting_buyers.png")
    plt.close()   


def compare_weighted_with_unweighted(weighted_ranking, unweighted_ranking):
    # print only the first 5 and the last 5 entries
    print_range = 5
    if len(weighted_ranking) != len(unweighted_ranking):
        print("Weighted and unweighted seller list do not have the same length! Could not compare!")
        print("Weighted:", len(weighted_ranking), "unweighted:", len(unweighted_ranking))
    else:
        #print_range = list(range(print_range))
        #print_range.extend(list(range(len(weighted_ranking)-5, len(weighted_ranking))))
        print("Comparison between weighted and unweighted seller ranking:")
        for index in range(print_range):# range(len(weighted_ranking)):
            (w_id, w_avg_review, w_num_reviews) = weighted_ranking[index] # w for weighted
            (u_id, u_avg_review, u_num_reviews) = unweighted_ranking[index] # u for unweighted
            print(str(index+1)+".", w_id, "avg", w_avg_review, "#", w_num_reviews, "vs.", u_id, "avg", u_avg_review, "#", u_num_reviews)
        print("...")
        for index in range(len(weighted_ranking)-print_range, len(weighted_ranking)):# range(len(weighted_ranking)):
            (w_id, w_avg_review, w_num_reviews) = weighted_ranking[index] # w for weighted
            (u_id, u_avg_review, u_num_reviews) = unweighted_ranking[index] # u for unweighted
            print(str(index+1)+".", w_id, "avg", w_avg_review, "#", w_num_reviews, "vs.", u_id, "avg", u_avg_review, "#", u_num_reviews)
        
        return analyze_change_of_ranks(weighted_ranking, unweighted_ranking)


def analyze_change_of_ranks(weighted_ranking, unweighted_ranking):
    change_counter = Counter()
    for w_index, (w_id, _, _) in enumerate(weighted_ranking):
        for u_index, (u_id, _, _) in enumerate(unweighted_ranking):
            if w_id == u_id:
                change = u_index - w_index
                change_counter[change] += 1
    return dict(change_counter)

        
def get_weighted_seller_ranking(graph, comp, weighted_buyer_rankin_dict, verbose):
    # format: weighted_seller_ranking_dict = {'id': (weighted_ranking, num_of_reviews), 'id2': ...}
    # format: weighted_seller_ranking_list = [(id, weighted_review, num_reviews), (id2, weighted_review2, num_reviews2), ...]
    weighted_seller_ranking_dict, weighted_seller_ranking_list = {}, []
    for node in comp:
        weighted_ranking = 0.0
        # leave out all the nodes which are only loosely connected to the giant component by less than 3 edges
        edges = graph.edges(node)
        if len(edges) > 2:
            # only looking at seller nodes here
            if node[0] == 's':
                for edge in edges:
                    (u,v) = edge
                    data = graph.get_edge_data(u,v)
                    buyer_id = ""
                    for index in range(len(data)):
                        # u and v are not always the same (buyer or seller) because the graph is undirected
                        if u[0] == 'b': buyer_id = u
                        else: buyer_id = v
                        if buyer_id in weighted_buyer_rankin_dict:
                            weighted_ranking += weighted_buyer_rankin_dict[buyer_id] * data[index]['review'] # += weight * review
                        
                weighted_seller_ranking_dict[node] = (weighted_ranking, len(edges))
                weighted_seller_ranking_list.append((node, weighted_ranking, len(edges)))
    return weighted_seller_ranking_dict, weighted_seller_ranking_list


def get_weighted_buyer_ranking(ranking):
    # give each buyer a ranking depending on the average review he gives and the amount of all reviews
    weighted_ranking = []
    for (id, avg_review, num_reviews) in ranking:
        weight = (1.1-abs(avg_review)) * math.log(num_reviews, 2)
        weighted_ranking.append((id, weight))
    return weighted_ranking
    """
    Explanation for the calculation of 'weight':
    Buyers who will always give negative (-1) or positive (1) reviews, will have an avg_review of -1 or 1 respectively.
    But these reviews are not as informative, as they either always like their purchase or they always dislike it.
    So these buyers are weighted less, but they can still make up for it by the amount of reviews they give.
    The amount of reviews is scaled down logarithmically, because just someone gives 1000 reviews
    it does not mean that his opinion is worth 1000 more of someone who just gives 1 review.
    But someone who gives a lot of reviews, and therefore a lot of data, should still be rewarded for his behavior,
    this is why the amount of reviews are scaled back by a logarithm to the base of 2.
    """


def get_2_attribute_ranking_rankings(buyer_ranking, seller_ranking, verbose):
    # format: [(id, avg_review, num_reviews), (id2, avg_review2, num_reviews2), ...] sorted in descending order
    ranking_review_buyer = rank_by_avg_review(buyer_ranking)
    ranking_review_seller = rank_by_avg_review(seller_ranking)

    if verbose:
        # print only the top 5 and bottom 5 of the rankings
        print_range = 5
        print("Average buyer ranking:")
        for id, avg_review, num_of_reviews in ranking_review_buyer[:print_range]:
            print("Buyer", id, "with avg review score of", avg_review, "and", num_of_reviews, "purchases")
        print("...")
        for id, avg_review, num_of_reviews in ranking_review_buyer[-print_range:]:
            print("Buyer", id, "with avg review score of", avg_review, "and", num_of_reviews, "purchases")

        print("Average seller ranking:")
        for id, avg_review, num_of_reviews in ranking_review_seller[:print_range]:
            print("Seller", id, "with avg review score of", avg_review, "and", num_of_reviews, "sells")
        print("...")
        for id, avg_review, num_of_reviews in ranking_review_seller[-print_range:]:
            print("Seller", id, "with avg review score of", avg_review, "and", num_of_reviews, "sells")

    return ranking_review_buyer, ranking_review_seller


def get_ranking_from_all_nodes(comp, subgraph):
    # format: dict = {'id': [(time, review), (time, review), ...], 'id2': [(),(), ...], ...}
    buyer_ranking, seller_ranking = {}, {}

    for node in comp:
        # leave out all the nodes which are only loosely connected to the giant component by less than 3 edges
        # they do not provide any informational value for this analysis, as their participation is too rare
        edges = subgraph.edges(node)
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
    return buyer_ranking,seller_ranking


def make_prints_from_rankings(buyer_ranking, seller_ranking):
    print_range = 5
    # format: [(id, frequency), (id2, frequency2), ...] sorted in descending order
    most_frequent_buyer = get_most_frequent(buyer_ranking)
    most_frequent_seller = get_most_frequent(seller_ranking)
    print("Buyer frequency:", most_frequent_buyer[:print_range], "...")
    print("Seller frequency:", most_frequent_seller[:print_range], "...")


def general_edge_analysis(graph):
    edges = graph.edges.data()
    positive_review_counter, negative_review_counter, neutral_review_counter = 0, 0, 0
    min_time, max_time = 2999999999, 0 # min = 24.Jan.2065 some time
    for (u,v,data) in edges:
        if data['review'] == 1: positive_review_counter += 1
        elif data['review'] == 0: neutral_review_counter += 1
        elif data['review'] == -1: negative_review_counter += 1
        else: raise ValueError("Review value not within {1;0;-1} -->", data['review']) # should not occur
        # for the first iteration only one time condition can be met,
        # but for multiple runs it is a little more efficient, because of less checks
        if data['time'] < min_time: min_time = data['time']
        elif data['time'] > max_time: max_time = data['time']
    print("Total amount of positive reviews:", positive_review_counter)
    print("Total amount of neutral  reviews:", neutral_review_counter)
    print("Total amount of negative reviews:", negative_review_counter)
    print("First review happend on", datetime.fromtimestamp(min_time).strftime('%d %B %Y'))
    print("Last  review happend on", datetime.fromtimestamp(max_time).strftime('%d %B %Y'))

    nodes = list(graph.nodes)
    buyer_counter, seller_counter, seller_counter_mediocre_connected = 0, 0, 0
    for node in nodes:
        if node[0] == 'b':
            buyer_counter += 1
        elif node[0] == 's':
            seller_counter += 1
            num_edges = len(graph.edges(node))
            if num_edges > 2: seller_counter_mediocre_connected += 1
    print("Total amount of buyer  nodes:", buyer_counter)
    print("Total amount of seller nodes:", seller_counter)
    print("out of which", seller_counter_mediocre_connected, "have more than 2 edges to buyers")


def main(args):
    # bipartite multiweighted
    # edges: 50632 buyer_nodes: 10106 seller_nodes: 6624
    filename = "../network/ia-escorts-dynamic.edges"
    network = read_network(filename, verbose=args.verbose)
    network = cleanse_network(network, verbose=args.verbose)
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
