from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.collections import LineCollection


# 文字列と辞書から、可能性のある単語列をリストとして返す関数
def make_lattice(context_: str, dictionary_: dict):
    # 解析対象の文字列の中から、辞書にあるものをリストアップする
    use_words = []
    length = len(context_)
    for start in range(length):
        first_char = context_[start]
        for key, data in dict.items(dictionary_):
            word = data[0]
            if word[0] == first_char:
                use_words.append([start, start + len(word), key, word])

    # リストアップした単語のすべての繋がり方を後ろから求める
    lattice_list = [[length, [-1]]]  # [[(先頭の位置), [(先頭を除く単語列)]]]
    flag = length
    while flag > 0:  # すべての繋がり方が解析対象の文字列の先頭までいけば終わり
        tmp = []
        for head_and_lattice in lattice_list:
            head = head_and_lattice[0]
            if head > 0:
                for word in use_words:
                    if word[1] == head:
                        tmp.append([word[0], [word[2]] + head_and_lattice[1]])
            else:
                tmp.append(head_and_lattice)
        lattice_list = tmp
        flag = max([i[0] for i in lattice_list])

    return [[0] + i[1] for i in lattice_list]  # [[0, i, j, ..., -1], [...], ... ] ijkは辞書のkeyに対応


# 実線と破線を描画(plot()で使う)
def line_collect(ax_: plt.subplot, nodes_: list[tuple], dictionary_: dict, cost_dictionary_: dict,
                 x_gap_: float, height_: float, dashed: bool = False):
    collection = []
    for node in nodes_:
        right_word = dictionary_[node[0]][0]
        right_point = dictionary_[node[0]][3]
        left_point = dictionary_[node[1]][3]
        xytext = (right_point[0] + len(right_word) - x_gap_, right_point[1] + 0.5 * height_)
        xy = (left_point[0], left_point[1] + 0.5 * height_)
        collection.append([xytext, xy])
        cost_sss = cost_dictionary_[node]
        ax_.text((xy[0] + xytext[0]) / 2, (xy[1] + xytext[1]) / 2, cost_sss,
                 horizontalalignment="center")
    if dashed:
        lc = LineCollection(collection, linestyles="--", edgecolors="black")
    else:
        lc = LineCollection(collection, linestyles="-", edgecolors="black")
    ax_.add_collection(lc)


# ビタビ探索中の状態図を描画
def plot(dictionary_: dict, cost_dictionary_: dict, cost_memory_: list, path_memory_: list,
         solid_nodes_: list[tuple], dashed_nodes_: list[tuple], x_gap_: float, height_: float, count_: int):
    word_set = set()
    for num in path_memory_:
        word_set = word_set | set(num)

    fig, ax = plt.subplots(figsize=(10, 5))

    for num in word_set:
        data = dictionary_[num]
        patch = patches.Rectangle(xy=dictionary_[num][3], width=len(data[0]) - x_gap_,
                                  height=height_, color="lightgreen")
        ax.add_patch(patch)
        plt.text(data[3][0], data[3][1],
                 "{0}\n{1}\n{2}".format(data[0], data[1], data[2]),
                 fontname="MS Gothic", fontsize=10)
        plt.text(data[3][0], data[3][1] + height_,
                 "{0}".format(cost_memory_[num]), fontsize=11, color="red")
        ax.set_xlim([-0.5, 9])
        ax.set_ylim([-2.5, 2])

    line_collect(ax, solid_nodes_, dictionary_, cost_dictionary_, x_gap_, height_)
    line_collect(ax, dashed_nodes_, dictionary_, cost_dictionary_, x_gap_, height_, dashed=True)

    plt.savefig("result{0}.png".format(count_))
    plt.close()


# 部分問題を解く関数。今までに解いた問題の解をもとに、文頭からある文字(goal)までの最小コストとそのパスを求める。
def subset_viterbi(goal_: int, cost_memory_: list, path_memory_: list, lattice_: list[list],
                   dictionary_: dict, cost_dictionary_: dict, solid_nodes_: list[tuple], dashed_nodes_: list[tuple]):
    candidates = []
    for lat in lattice_:
        if goal_ in lat:
            _from = lat[lat.index(goal_) - 1]  # goalのちょうど一つ後ろの単語
            cost = cost_dictionary_[(_from, goal_)]  # _fromとgoalの接続コスト

            if cost_memory_[_from] == -1:  # goalの一つ後ろの単語までの最小コストがすべて求まっていなければ、後回しにする。
                return
            else:
                new_cost = cost_memory_[_from] + dictionary_[goal_][2] + cost
                new_path = path_memory_[_from] + [goal_]
                candidates.append([new_cost, new_path])
                for r in range(len(new_path) - 1):
                    new_node = tuple(new_path[r: r + 2])
                    if new_node not in solid_nodes_ and new_node not in dashed_nodes_:
                        dashed_nodes_.append(new_node)
    # 最適解の候補の中から最もコストが小さいものを選び、メモリを更新し、実線と破線を追加
    flag = -1
    for cost_and_path in candidates:
        if flag == -1:
            cost_memory_[goal_] = cost_and_path[0]
            path_memory_[goal_] = cost_and_path[1]
        else:
            if cost_and_path[0] < flag:
                cost_memory_[goal_] = cost_and_path[0]
                path_memory_[goal_] = cost_and_path[1]

    for r in range(len(path_memory_[goal_]) - 1):
        node_update = tuple(path_memory_[goal_][r: r + 2])
        if node_update not in solid_nodes_:
            solid_nodes_.append(node_update)
        if node_update in dashed_nodes_:
            dashed_nodes_.remove(node_update)

    return


# ビタビ探索の関数。sub_viterbi()を繰り返し、途中結果・最終結果をplot()で描画する。
def viterbi(lattice_: list[list], dictionary_: dict, cost_dictionary_: dict):
    cost_memory = [0] + [-1 for _ in range(len(dictionary_) - 1)]
    path_memory = [[0]] + [[] for _ in range(len(dictionary_) - 1)]
    solid_nodes = []
    dashed_nodes = []
    x_gap = 0.5
    height = 0.5
    count = 0

    while not path_memory[-1]:
        for word in dictionary_.keys():
            if cost_memory[word] < 0:
                subset_viterbi(word, cost_memory, path_memory, lattice_, dictionary_,
                               cost_dictionary_, solid_nodes, dashed_nodes)

                plot(dictionary_, cost_dictionary_, cost_memory, path_memory,
                     solid_nodes, dashed_nodes, x_gap, height, count)
                count += 1


if __name__ == "__main__":
    sample_context = "さけようとした"

    # { index : ["文字", "種類", "生起コスト", (ラティス図における左下の座標)] }
    # 今回は（ラティス図における左下の座標）は、make_lattice()の返り値より手動で設定した。
    dictionary = {0: ["#", "文頭", 0, (0, 0)],
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

    node_and_cost = {(0, 1): 900,
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

    lattice = make_lattice(sample_context, dictionary)
    viterbi(lattice, dictionary, node_and_cost)
