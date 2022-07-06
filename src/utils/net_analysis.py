import matplotlib.pyplot as plt


def plot_degree_dist(G):
    degrees = [G.degree(n) for n in G.nodes()]
    degrees = sorted(degrees, reverse=True)

    degrees_len = len(degrees)
    prob = [degrees.count(x) / degrees_len for x in degrees]
    
    x1 = degrees
    x2 = prob

    ax = plt.gca()
    ax.scatter(x1, x2)
    ax.set_yscale('log')
    ax.set_xscale('log')

    ax.set_title('Degree distribution')
    ax.set_xlabel('Degree')
    ax.set_ylabel('Probability')

    plt.show()