import operator
from collections import Counter


def get_most_frequent(ranking):
    # format: ranking = {'id': [(time, review), (.,.), ...], 'id2': [...] }
    # format: counter = {'id': count, 'id2': count2, ...}
    freq_counter = Counter()
    for entry in ranking:
        freq_counter[entry] = len(ranking[entry])
    # format: return = [('id', count), ('id2', count2), ...] sorted in descending order
    return freq_counter.most_common()

def rank_by_avg_review_old(ranking):
    # format: ranking = {'id': [(time, review), (.,.), ...], 'id2': [...] }
    # format: counter = {'id': avg_review, 'id2': avg_review2, ...}
    avg_review_counter = Counter()
    for entry in ranking:
        avg_rating = 0.0
        for _, review in ranking[entry]:
            avg_rating += review
        avg_review_counter[entry] = avg_rating/len(ranking[entry])
    # format: return = [(id, avg_review), (id2, avg_review2), ...] sorted in descending order
    return avg_review_counter.most_common() 

def rank_by_avg_review(ranking):
    # format: ranking = {'id': [(time, review), (.,.), ...], 'id2': [...] }
    # format: avg_review_list = [(id, avg_review, #_of_reviews), (x, x, x), ...]
    avg_review_list = []
    for entry in ranking:
        avg_rating = 0.0
        for _, review in ranking[entry]:
            avg_rating += review
        avg_review_list.append((entry, avg_rating/len(ranking[entry]), len(ranking[entry])))
    # format: return = [(id, avg_review, #_of_reviews), (x, x, x), ...] sorted in descending order
    return sort_avg_review_list(avg_review_list)

def sort_avg_review_list(avg_review_list):
    # sort the list first by the avg_review in descending order and then by the amount of reviews in descending order
    return sorted(avg_review_list, key = lambda y: (y[1], y[2]), reverse=True)
    