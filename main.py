from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.collections import LineCollection


def make_lattice(context: str, dictionary: dict):
    use_words = []
    length = len(context)
    for place in range(length):
        first_character = context[place]
        for key, data in dict.items(dictionary):
            word = data[0]
            if word[0] == first_character:
                use_words.append([place, place + len(word), key, word])

    lattice_list = [[7, [-1]]]
    flag = length

    while flag > 0:
        to_exchange = []

        for head_and_lattice in lattice_list:
            head = head_and_lattice[0]
            if head > 0:
                for word in use_words:
                    if word[1] == head:
                        to_exchange.append([word[0], [word[2]] + head_and_lattice[1]])
            else:
                to_exchange.append(head_and_lattice)

        lattice_list = to_exchange

        flag = max([i[0] for i in lattice_list])

    return [[0] + hu[1] for hu in lattice_list]


def plot(dictionary: dict, cost_dictionary: dict, cost: list,
         route: list, solid: list, dashed: list, x_gap: float, height: float, count: int):
    word = set()
    for r in route:
        word = word | set(r)

    fig, ax = plt.subplots(figsize=(10, 5))
    for r in word:
        data = dictionary[r]
        patch = patches.Rectangle(xy=dictionary[r][3], width=len(data[0]) - x_gap, height=height,
                                  color="lightgreen")
        ax.add_patch(patch)
        plt.text(data[3][0], data[3][1],
                 "{0}\n{1}\n{2}".format(data[0], data[1], data[2]),
                 fontname="MS Gothic", fontsize=10)
        plt.text(data[3][0], data[3][1] + height,
                 "{0}".format(cost[r]), fontsize=11, color="red")
        ax.set_xlim([-0.5, 9])
        ax.set_ylim([-2.5, 2])

    solid_lines = []
    for sss in solid:
        w_right = dictionary[sss[0]][0]
        p_right = dictionary[sss[0]][3]
        p_left = dictionary[sss[1]][3]
        xytext = (p_right[0] + len(w_right) - x_gap, p_right[1] + 0.5 * height)
        xy = (p_left[0], p_left[1] + 0.5 * height)
        solid_lines.append([xytext, xy])
        cost_sss = cost_dictionary[sss]

        ax.text((xy[0] + xytext[0]) / 2, (xy[1] + xytext[1]) / 2, cost_sss,
                horizontalalignment="center")

    lc = LineCollection(solid_lines, linestyles="-", edgecolors="black")
    ax.add_collection(lc)

    dashed_lines = []
    for ddd in dashed:
        w_right = dictionary[ddd[0]][0]
        p_right = dictionary[ddd[0]][3]
        p_left = dictionary[ddd[1]][3]
        xytext = [p_right[0] + len(w_right) - x_gap, p_right[1] + 0.5 * height]
        xy = [p_left[0], p_left[1] + 0.5 * height]
        dashed_lines.append([xytext, xy])
        cost_sss = cost_dictionary[ddd]

        ax.text((xy[0] + xytext[0]) / 2, (xy[1] + xytext[1]) / 2, cost_sss,
                horizontalalignment="center")
    lc = LineCollection(dashed_lines, linestyles="--", edgecolors="black")
    ax.add_collection(lc)

    plt.savefig("result{0}.png".format(count))
    plt.close()


def subset_viterbi(goal: int, cost: list, route: list, lattice: list,
                   dictionary: dict, cost_dictionary: dict, solid_list: list, dashed_list: list):
    new = []
    for i in lattice:
        if goal in i:
            frm = i[i.index(goal) - 1]

            c = cost_dictionary[(frm, goal)]

            if cost[frm] >= 0:
                new_cost = cost[frm] + dictionary[goal][2] + c
                new_route = route[frm] + [goal]
                new.append([new_cost, new_route])
                for r in range(len(new_route) - 1):
                    nr = tuple(new_route[r: r + 2])
                    if nr not in solid_list and nr not in dashed_list:
                        dashed_list.append(nr)
            else:
                return False

    flag = -1
    for ll in new:
        if flag < 0:
            cost[goal] = ll[0]
            route[goal] = ll[1]
        else:
            if ll[0] < flag:
                cost[goal] = ll[0]
                route[goal] = ll[1]

    for r in range(len(route[goal]) - 1):
        aa = tuple(route[goal][r: r + 2])
        if aa not in solid_list:
            solid_list.append(aa)
        if aa in dashed_list:
            dashed_list.remove(aa)

    return


def viterbi(lattice: list, dictionary: dict, cost_dictionary: dict):
    cost = [0] + [-1 for _ in range(len(dictionary) - 1)]
    route = [[0]] + [[] for _ in range(len(dictionary) - 1)]
    solid = []
    dashed = []
    x_gap = 0.5
    height = 0.5
    count = 0

    while not route[-1]:
        for d in dictionary.keys():
            if cost[d] < 0:
                subset_viterbi(d, cost, route, lattice, dictionary, cost_dictionary, solid, dashed)

                plot(dictionary, cost_dictionary, cost, route, solid, dashed, x_gap, height, count)
                count += 1


if __name__ == "__main__":
    sample = "さけようとした"

    # { index : ["文字", "種類", "生起確率", [ラティス図における左下の座標] }
    word_dictionary = {0: ["#", "文頭", 0, (0, 0)],
                       1: ["さけよ", "動詞", 2700, (1, 0)],
                       2: ["さけ", "名詞", 1500, (1, -1)],
                       3: ["よう", "動詞", 700, (3, -1)],
                       4: ["ようと", "名詞", 1200, (3, -2)],
                       5: ["う", "感動詞", 800, (4, 1)],
                       6: ["う", "助動詞", 0, (4, 0)],
                       7: ["と", "助詞", 0, (5, 0)],
                       8: ["した", "名詞", 1400, (6, -1)],
                       9: ["し", "動詞", 1200, (6, 0)],
                       10: ["た", "助動詞", 0, (7, 0)],
                       -1: ["#", "文末", 0, (8, 0)]}

    node_dictionary = {(0, 1): 900,
                       (0, 2): 300,
                       (1, 5): 1500,
                       (5, 1): 1500,
                       (1, 6): 400,
                       (6, 1): 400,
                       (2, 3): 800,
                       (3, 2): 800,
                       (2, 4): 1500,
                       (4, 2): 1500,
                       (9, 7): 500,
                       (7, 9): 500,
                       (9, 4): 800,
                       (4, 9): 800,
                       (9, 10): 200,
                       (10, 9): 200,
                       (7, 5): 1200,
                       (5, 7): 1200,
                       (7, 6): 700,
                       (6, 7): 700,
                       (7, 3): 1500,
                       (3, 7): 1500,
                       (7, 8): 1000,
                       (8, 7): 1000,
                       (4, 8): 1500,
                       (8, 4): 1500,
                       (10, -1): 300,
                       (8, -1): 900}

    lat = make_lattice(sample, word_dictionary)
    viterbi(lat, word_dictionary, node_dictionary)
