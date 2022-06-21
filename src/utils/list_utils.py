def print_top_and_bottom_of_list(list_to_print, k):
    for item in list_to_print[:k]:
        print(item)
    print("...")
    for item in list_to_print[-k:]:
        print(item)

def turn_weighted_ranking_to_dict(list_to_dict):
    dict_from_list = {}
    for (id, weight) in list_to_dict:
        dict_from_list[id] = weight
    return dict_from_list