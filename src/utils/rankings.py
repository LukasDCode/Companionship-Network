from collections import Counter

def get_most_frequent(ranking):
    # ranking = {'id': [(time, review), (.,.), ...], 'id2': [...] }
    # counter = {'id': count, 'id2': count2, ...}
    freq_counter = Counter()
    for entry in ranking:
        freq_counter[entry] = len(ranking[entry])
    # return = [('id', count), ('id2', count2), ...]
    return freq_counter.most_common()

def rank_by_avg_review(ranking):
    avg_review_counter = Counter()
    for entry in ranking:
        avg_rating = 0.0
        for _, review in ranking[entry]:
            avg_rating += review
        avg_review_counter[entry] = avg_rating/len(ranking[entry])
    return avg_review_counter.most_common() 