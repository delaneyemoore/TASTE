import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import ast
import math
import pandas as pd
# import astpretty
from scipy.stats import skew
import random



def get_avg(nums):
    total_sum = 0
    for num in nums:
        total_sum += num
    size = len(nums)
    return total_sum/size


def find_min(prev_min, values):
    current_min = 10000000000000000
    for val in values:
        if current_min > val > prev_min:
            current_min = val
    return current_min


def get_indices(snapshot, creation_values):
    indices = []
    for i in range(len(creation_values)-1):
        if creation_values[i] == snapshot:
            indices.append(i)
    return indices


def find_depths(tree, depth_dict, depth, code):
    # current_tree = ast.dump(tree)
    code_seg = ast.get_source_segment(code, tree)
    if code_seg is None:
        if depth == 0:
            depth_dict[tree] = depth
            depth += 1
            for node in ast.iter_child_nodes(tree):
                find_depths(node, depth_dict, depth, code)
    else:
        depth_dict[tree] = depth
        depth += 1
        for node in ast.iter_child_nodes(tree):
            find_depths(node, depth_dict, depth, code)
    return depth_dict


def get_max(children):
    height_max = -1
    for c in children:
        if c[1] > height_max:
            height_max = c[1]
    return height_max


def find_heights(tree, height_dict, height, code):
    # current_tree = ast.dump(tree)
    # Base Case
    code_seg = ast.get_source_segment(code, tree)
    label = get_label(tree, code)
    heights = []
    if code_seg is None:
        if label == "Root":
            for child in ast.iter_child_nodes(tree):
                child_height = find_heights(child, height_dict, height, code)
                if child_height != -1:
                    height_dict[child] = child_height
                    heights.append((child, child_height))
                else:
                    heights.append((child, child_height))
        else:
            return -1
    else:
        for child in ast.iter_child_nodes(tree):
            child_height = find_heights(child, height_dict, height, code)
            if child_height != -1:
                height_dict[child] = child_height
                heights.append((child, child_height))
            else:
                heights.append((child, child_height))
    height = get_max(heights) + 1
    height_dict[tree] = height
    return height


def get_heights(snap_dict, height_dict, heights, ordered_keystrokes, creation_values, code, labels, prev_min=-1):
    cont = True
    while cont:
        current_min = find_min(prev_min, creation_values)
        prev_min = current_min
        if current_min == 10000000000000000:
            cont = False
        else:
            for node in snap_dict:
                if snap_dict[node] == current_min:
                    this_height = height_dict[node]
                    lab = get_label(node, code)
                    labels.append(lab)
                    heights.append(this_height)
    return heights, ordered_keystrokes


# find avg depth of tree base on snapshots
# root = 0, deepest leaf = max value
def get_avg_depths(snap_dict, depth_dict, depths, avg_depths, creation_values, prev_min=-1):
    cont = True
    while cont:
        current_min = find_min(prev_min, creation_values)
        prev_min = current_min
        if current_min == 10000000000000000:
            cont = False
        else:
            for node in snap_dict:
                if snap_dict[node] == current_min:
                    this_depth = depth_dict[node]
                    depths.append(this_depth)
                    this_avg = get_avg(depths)
                    avg_depths.append(this_avg)
    return avg_depths


def get_depths(snap_dict, depth_dict, depths, ordered_keystrokes, creation_values, code, labels, prev_min=-1):
    cont = True
    while cont:
        current_min = find_min(prev_min, creation_values)
        prev_min = current_min
        if current_min == 10000000000000000:
            cont = False
        else:
            for node in snap_dict:
                if snap_dict[node] == current_min:
                    this_depth = depth_dict[node]
                    lab = get_label(node, code)
                    labels.append(lab)
                    depths.append(this_depth)
    return depths, ordered_keystrokes


# draws graph
def create_avg_graph(tree, snap_dict, creation_values):
    depths = []
    avg_depths = []
    depth_dict = {}
    depth_dict = find_depths(tree, depth_dict, 0)
    avg_depths = get_avg_depths(snap_dict, depth_dict, depths, avg_depths, creation_values)
    snaps = []
    for i in range(1, len(avg_depths)+1, 1):
        snaps.append(i)
    plt.clf()
    plt.bar(snaps, avg_depths)
    plt.title('Average Depth of Temporal AST Over Time')
    plt.xlabel('Snapshot')
    plt.ylabel('Average Depth')
    # plt.show()
    plt.savefig('AvgDepthStudent1.png', dpi=100)   # bbox_inches='tight'


def create_depth_graph(tree, snap_dict, creation_values, code, studentassignment):
    # astpretty.pprint(ast.parse(code), show_offsets=False)
    depths = []
    ordered_keystrokes = []
    depth_dict = {}
    depth_dict = find_depths(tree, depth_dict, 0, code)
    labels = []
    depths, ordered_keystrokes = get_depths(snap_dict, depth_dict, depths, ordered_keystrokes,
                                            creation_values, code, labels)
    mod_depth = depth_dict[tree]
    snaps = []
    for i in range(1, len(depths) + 1, 1):
        snaps.append(i)
    plt.clf()
    plt.rcParams.update({'font.size': 55})
    freq_series = pd.Series(depths)
    plt.figure(figsize=(80, 20))
    ax = freq_series.plot(kind="bar", fontsize=40)
    # helps set tick spacing for x axis
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    #ax.set_title("Depth of Each Node in Order of Creation")
    #ax.set_xlabel("Nodes in Order of Creation")
    #ax.set_ylabel("Depth of Node")
    plt.xlabel("Nodes in Order of Creation", labelpad=15)
    plt.ylabel("Depth of Node", labelpad=15)
    # ax.fontsize(22)
    rects = ax.patches

    for rect, dep, label in zip(rects, depths, labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height + .05, dep, ha="center", va="bottom", fontsize=24
        )
        ax.text(rect.get_x() + rect.get_width() / 2., (0.5 * height) - .1,
                label,
                ha='center', va='bottom', rotation=90, color='white', fontsize=12)

    # plt.show()
    fig_file_name = 'dataCreation/Depth' + studentassignment + '.png'
    # plt.savefig(fig_file_name, dpi=100)  # bbox_inches='tight'
    fig = ax.get_figure()
    fig.savefig(fig_file_name)
    plt.close(fig)
    #area_score = get_area_score(depths)
    #mid_score = get_midline_score(depths)
    #print("skew: " + str(skew))
    # print("midline score: " + str(mid_score))
    #return area_score, mid_score
    return depths


def create_height_graph(tree, snap_dict, creation_values, code, studentassignment):
    # astpretty.pprint(ast.parse(code), show_offsets=False)
    heights = []
    ordered_keystrokes = []
    height_dict = {}
    find_heights(tree, height_dict, 0, code)
    labels = []
    heights, ordered_keystrokes = get_heights(snap_dict, height_dict, heights, ordered_keystrokes, creation_values, code, labels)
    # mod_depth = height_dict[tree]
    snaps = []
    for i in range(1, len(heights) + 1, 1):
        snaps.append(i)
    plt.clf()
    plt.rcParams.update({'font.size': 55})
    freq_series = pd.Series(heights)
    plt.figure(figsize=(80, 20))
    ax = freq_series.plot(kind="bar", fontsize=40)
    # helps set tick spacing for x axis
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xlabel("Nodes in Order of Creation", labelpad=15)
    plt.ylabel("Height of Node", labelpad=15)
    # ax.fontsize(22)
    rects = ax.patches
    for rect, dep, label in zip(rects, heights, labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height + .05, dep, ha="center", va="bottom", fontsize=24
        )
        ax.text(rect.get_x() + rect.get_width() / 2., (0.5 * height) - .1,
                label,
                ha='center', va='bottom', rotation=90, color='white', fontsize=12)

    # plt.show()
    fig_file_name = 'dataCreation/Height' + studentassignment + '.png'
    # plt.savefig(fig_file_name, dpi=100)  # bbox_inches='tight'
    fig = ax.get_figure()
    fig.savefig(fig_file_name)
    plt.close(fig)
    #area_score = get_area_score(depths)
    #mid_score = get_midline_score(depths)
    #print("skew: " + str(skew))
    # print("midline score: " + str(mid_score))
    #return area_score, mid_score
    return heights


# measure monotinicity
def get_monotinicity(elements):
    prev = elements[0]
    score = 0
    elements_len = len(elements)
    for i in range(1, elements_len):
        current = elements[i]
        if prev > current:
            score += 1
        prev = current
    monotinicity = score/elements_len
    monotinicity = 1 - monotinicity
    return monotinicity


# i think i can ge rid of this function and reference the get label function from tempASTkeystroke.py
def get_label(tree_node, code):
    code_seg = ast.get_source_segment(code, tree_node)
    #if code_seg is None:
    #    return None
    node_type = type(tree_node).__name__
    if node_type == "Module":
        return "Root"
    elif node_type == "BinOp":
        op = (type(tree_node.op).__name__)
        if op == "Mult":
            return "Multiply"
        elif op == "Div":
            return "Divide"
        elif op == "Pow":
            return "Power"
        elif op == "Sub":
            return "Subtract"
        else:
            return op
    elif node_type == "Name":
        return code_seg
    elif node_type == "Constant":
        if len(code_seg) > 10:
            return code_seg[0:10]
        else:
            return code_seg
    elif node_type == "Call":
        if type(tree_node.func).__name__ == "Attribute":
            if type(tree_node.func.value).__name__ == "Subscript":
                string = str(tree_node.func.value.value) + "[" + str(tree_node.func.value.slice) + "]"
            elif type(tree_node.func.value).__name__ == "Call":
                try:
                    string = tree_node.func.id + "()"
                except:
                    pass
                try:
                    string = tree_node.func.value.id
                except:
                    string = node_type
            else:
                try:
                    string = tree_node.func.value.id
                except:
                    string = tree_node.func.value.attr
            return string
        else:
            return tree_node.func.id + "()"
    elif node_type == "Expr":
        return code_seg
    elif node_type == "Assign":
        # targets = tree_node.targets
        # string = ""
        # length = len(targets)
        # for t in targets:
        #    string += t.id
        #    if t != targets[length - 1]:
        #        string += ", "
        # string += " ="
        return "="
    elif node_type == "Assign":
        return "="
    else:
        return node_type


def get_slope_score(depths):
    slopes = []
    return 0


def get_area_score(depths):
    length = len(depths)
    half = math.ceil(length/2)
    left = 0
    for i in range(0, half-1):
        left += depths[i]
    right = 0
    for j in range(half, length-1):
        right += depths[j]
    try:
        value = left/right
    except:
        value = 0
    return value


# The sample skewness is computed as the Fisher-Pearson coefficient of skewness
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
def get_skew(depths):
    return skew(depths)


def get_midline_score(depths):
    total = 0
    for d in depths:
        total += d
    tracker = 0
    half = total/2
    index = 0
    cont = True
    while cont:
        tracker += depths[index]
        if tracker >= half:
            cont = False
        else:
            index += 1
    value = index/(len(depths))
    return value


def get_tdbu_metric(skewActual, skewBU, skewTD):
    tdbu = (skewActual - skewBU) / (skewTD - skewBU)
    return tdbu

