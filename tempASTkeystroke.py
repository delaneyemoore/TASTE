import pandas as pd
import ast
import networkx as nx
from networkx import *
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import numpy as np
import pygraphviz
import depthGraph
import pickle
from networkx.readwrite import json_graph
import json



def get_label(tree_node, code):
    code_seg = ast.get_source_segment(code, tree_node)
    #if code_seg is None:
        #return None
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
                # string = tree_node.func.value.id  # + " " + tree_node.func.value.attr
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


def get_create_value(tree_node, parent_node, code, values):
    # find code segment responsible for node
    code_seg = ast.get_source_segment(code, tree_node)
    if code_seg is None:
        return None
    #print(tree_node)
    #print(tree_node.lineno)
    #print(tree_node.col_offset)
    #print(code_seg)
    #code_seg = list(code_seg)

    lineno = tree_node.lineno - 1
    col = tree_node.col_offset
    index = new_lines[lineno] + col
    char = code[index]
    value = values[index]
    node_dict[tree_node] = value
    return value
    '''
    if len(code_seg) == 1:
        try:
            isin = parent_seg.count(code_seg[0])
        except:
            isin = 0
        if isin > 0:
            code_seg = parent_seg
            code_seg = list(code_seg)
    length = len(code_seg)
    start_index = -1
    count = 0
    current_index = 0
    cont = True
    # find code segment in words, once found, give index label
    while cont is True:
        char = code[count]
        current_char = code_seg[current_index]
        if current_char == char:
            if current_index == 0:
                start_index = count
            if current_index == length - 1:
                cont = False
            current_index += 1
        else:  # word != code_word
            start_index = -1
            current_index = 0
        if count == len(code) - 1:
            cont = False
        count += 1
    # snapshot value for node found at start_index
    if start_index == -1:
        try:
            isin = parent_seg.count(code_seg[0])
        except:
            isin = 0
        if isin > 0:
            value = parent_node[1]
    else:
        value = values[start_index]
    node_dict[tree_node] = value
    return value
    '''


def compare_nodes(node1, node2, code1, code2, parent1, parent2, values1, values2):
    # first check nodes are same type
    # string1 = ast.get_source_segment(code, node1)
    # string2 = ast.get_source_segment(code, node2)
    cv1 = get_create_value(node1, parent1, code1, values1)
    cv2 = get_create_value(node2, parent2, code2, values2)
    # check to see if the code segments are the same
    if cv1 == cv2:
        return True
    else:
        return False


def find_compilable_state(node, parent, trees, code, values, tree_values, tree_codes):
    cont = True
    counter = 0
    code_seg = ast.get_source_segment(code, node)
    if code_seg is None:
        return None
    while cont:
        tree = trees[counter]
        values_compare = tree_values[counter]
        code_compare = tree_codes[counter]
        parent_compare = (None, None)
        for n in ast.iter_child_nodes(tree):
            result = compare_nodes(node, n, code, code_compare, parent, parent_compare, values, values_compare)
            parent_compare = (n, result)
            if result:
                cont = False
                break
        counter += 1
        if counter >= len(trees):
            counter = len(trees) - 1
            cont = False
    return counter


def build_temp_ast_intermediate(code, parent, tree_node, prev, nodes, edges, label_dict, states, trees, values, tree_values, tree_codes):
    # all nodes will be assigned the compilable state value
    # add node to nodes
    if type(tree_node).__name__ == "Module":
        cs = 0
    else:
        cs = find_compilable_state(tree_node, parent, trees, code, values, tree_values, tree_codes)
    if cs is not None:
        node_index = len(nodes)
        name = type(tree_node).__name__ + str(node_index)  # + " snap: " + str(node_size[0])
        label = get_label(tree_node, code)
        label_dict[name] = label
        nodes.append(name)
        states.append(cs)
        if prev != node_index:
            edges.append((nodes[prev], nodes[node_index]))
        parent_node = (tree_node, cs)
        for child in ast.iter_child_nodes(tree_node):
            build_temp_ast_intermediate(code, parent_node, child, node_index, nodes, edges, label_dict, states, trees, values, tree_values, tree_codes)


def build_graph_intermediate(nodes, edges, label_dict, compilable_states, studentassign):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    plt.figure(3, figsize=(800, 100), dpi=30)
    compile_max = 0
    for v in compilable_states:
        if v > compile_max:
            compile_max = v
    # draw temporal ast
    options = {
        "labels": label_dict,
        "with_labels": True,
        "font_size": 85,
        "arrows": True,
        "arrowstyle": "->",
        "arrowsize": 200,
        "node_size": 290000,
        "node_shape": "o",
        "node_color": compilable_states,
        "edgecolors": "black",
        "linewidths": 20,
        "cmap": plt.cm.get_cmap('bwr'),
        "width": 25,
        "vmin": 0,
        "vmax": compile_max
    }
    pos = graphviz_layout(G, prog='dot')
    draw_networkx(G, pos, **options)
    # graph_to_json(G)
    plt_file = "compilablestatesgraphs/intermediateAST" + studentassign + ".png"
    plt.savefig(plt_file)


def build_temp_ast(code, values, tree_node, parent_node, prev, nodes, edges, creation_values, label_dict):
    # find node size
    if type(tree_node).__name__ == "Module":
        node_val = 0
        node_dict[tree_node] = 0
    else:
        node_val = get_create_value(tree_node, parent_node, code, values)
    # append size to list
    if node_val is not None:
        # add node to nodes
        node_index = len(nodes)
        name = type(tree_node).__name__ + str(node_index)  # + " snap: " + str(node_size[0])
        label = get_label(tree_node, code)
        label_dict[name] = label
        nodes.append(name)
        creation_values.append(node_val)
        # node_dict[tree_node] = node_val
        if prev != node_index:
            edges.append((nodes[prev], nodes[node_index]))
        parent_node = (tree_node, node_val)
        for child in ast.iter_child_nodes(tree_node):
            build_temp_ast(code, values, child, parent_node, node_index, nodes, edges, creation_values, label_dict)


def graph_to_json(G):
    data = json_graph.node_link_data(G)
    with open('jsonGraphs/graph' + studentassign + '.json', 'w') as f:
        json.dump(data, f, indent=4)


def build_graph(nodes, edges, creation_values, label_dict):
    G = nx.DiGraph()
    #print(len(nodes))
    #print(nodes)
    #print(creation_values)
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    plt.clf()
    plt.figure(3, figsize=(800, 100), dpi=30)
    creation_max = 0
    for v in creation_values:
        if v > creation_max:
            creation_max = v
    # draw temporal ast
    options = {
        "labels": label_dict,
        "with_labels": True,
        "font_size": 85,
        "arrows": True,
        "arrowstyle": "->",
        "arrowsize": 200,
        "node_size": 290000,
        "node_shape": "o",
        "node_color": creation_values,
        "edgecolors": "black",
        "linewidths": 20,
        "width": 25,
        "cmap": plt.cm.get_cmap('coolwarm'),
        "vmin": 0,
        "vmax": creation_max
    }
    pos = graphviz_layout(G, prog='dot')
    draw_networkx(G, pos, **options)
    #graph_to_json(G)
    #print(json_graph.node_link_data(G))
    #data = json_graph.node_link_data(G)
    # https://ipython-books.github.io/64-visualizing-a-networkx-graph-in-the-notebook-with-d3js/
    nodesJson = [{'name': str(list(G.nodes)[i]), 'creationValue': creation_values[i]} for i in range(len(G.nodes.items()))]
    linksJson = [{'source': u[0][0], 'target': u[0][1]} for u in G.edges.items()]
    #with open('jsonGraph2.json', 'w') as f:
    #    json.dump({'nodes': nodesJson, 'links': linksJson},
    #              f, indent=4)
    #with open('jsonGraph.json', 'w', encoding='utf-8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)
    #with open('jsonGraph.json', 'w') as f:
    #    json.dump(data, f, ensure_ascii=False)
    #print(list(G.nodes))
    #print("hi")
    plt_file = "SIGSCESubmission/TAST" + studentassign + ".png"
    plt.savefig(plt_file)


def write_code_from_csv(a):
    code = ''
    values = []
    counter = 0
    # write out code and find creation values for each character
    for index, row in a.iterrows():
        i = int(row.SourceLocation)
        # Delete code
        code = code[:i] + code[i + len(row.DeleteText):]
        values = values[:i] + values[i + len(row.DeleteText):]
        # if row.DeleteText != '':
        #     delete = len(row.DeleteText)
        #     pop_list = []
        #     for char in range(delete):
        #         pop_list.append(i)
        #         i += 1
        #     for j in range(len(pop_list) - 1, -1, -1):
        #         values.pop(j)
        # Insert code
        m = len(row.InsertText)
        n = row.InsertText
        code = code[:i] + row.InsertText + code[i:]
        if row.InsertText != '':
            text = list(row.InsertText)
            for t in text:
                values.insert(i, counter)
                i += 1
        # increase creation value counter
        counter += 1
        len_code = len(code)
        # this could be where we attempt to build an intermediate AST
    #print(code)
    #print(values)
    return code, values


def draw_tree(nodes, edges, creation_values, label_dict, fig, axs, ind):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    #plt.clf()
    #plt.figure(3, figsize=(800, 100), dpi=30)
    creation_max = 0
    for v in creation_values:
        if v > creation_max:
            creation_max = v
    # draw temporal ast
    options = {
        "labels": label_dict,
        "with_labels": True,
        "font_size": 85,
        "arrows": True,
        "arrowstyle": "->",
        "arrowsize": 200,
        "node_size": 290000,
        "node_shape": "o",
        "node_color": creation_values,
        "edgecolors": "black",
        "linewidths": 20,
        "width": 25,
        "cmap": plt.cm.get_cmap('coolwarm'),
        "vmin": 0,
        "vmax": creation_max
    }
    pos = graphviz_layout(G, prog='dot')
    draw_networkx(G, pos, ax=axs[ind], **options)


def draw_forest():
    plt.clf()
    #height = 100 * (len(graphs))
    plt.figure(figsize=(600, 500))
    ratios = []
    for i in range(len(graphs*2)):
        if i % 2 == 0:
            ratios.append(20)
        else:
            ratios.append(450)
    # gridspec_kw = {'height_ratios': [4, 1, 4, 1, 4]}
    fig, axs = plt.subplots(len(graphs)*2, 1, figsize=(450, 150), gridspec_kw={'height_ratios': ratios})
    ind = 0
    for g in graphs:
        axs[ind].text(0.5, 0.5, g['file_name'], size=100, ha='center', va='center')
        axs[ind].axis('off')
        ind += 1
        draw_tree(g['nodes'], g['edges'], g['creation_values'], g['label_dict'], fig, axs, ind)
        ind += 1
    # plt.show()
    plt_file = "SIGSCESubmission/Forest" + studentassignment + ".png"
    plt.savefig(plt_file)


def create(values, code, studentassignment):
    # only for csv maker
    global new_lines
    new_lines = [0]
    code_list = list(code)
    for i in range(len(code_list)):
        char = code_list[i]
        if char == "\n":
            new_lines.append(i + 1)
    # only for csv maker
    global studentassign
    studentassign = studentassignment
    '''f = open("presExamples/" + studentassignment + ".txt", "w")
    f.write(code)
    f.close()'''
    nodes = []
    edges = []
    creation_values = []
    label_dict = {}
    global node_dict
    node_dict = {}
    parent_node = None
    try:
        tree = ast.parse(code)
        build_temp_ast(code, values, tree, parent_node, 0, nodes, edges, creation_values, label_dict)
        depths = find_depths(tree, node_dict, creation_values, code)
        height_dict = {}
        depthGraph.find_heights(tree, height_dict, -1, code)
        heights = depthGraph.get_heights(node_dict, height_dict, [], creation_values, code, [])
        return depths, heights
        # height_dict = {}
        # depthGraph.create_height_graph(tree, node_dict, creation_values, code, studentassignment)
        # print(height_dict)
        '''
        this_graph = {
            "file_name": file,
            "nodes": nodes,
            "edges": edges,
            "creation_values": creation_values,
            "label_dict": label_dict
        }
        if (len(nodes) > 1):
            graphs.append(this_graph)
            '''
        # depthGraph.create_graph(tree, node_dict, creation_values, code, studentassignment)
        # build_graph(nodes, edges, creation_values, label_dict)
        # return depthGraph.create_graph(tree, node_dict, creation_values, code, studentassignment)
        #return find_depths(tree, node_dict, creation_values, code)  # this line for csvMaker only
    # build_graph(nodes, edges, creation_values, label_dict)
    # return \
    # depthGraph.create_graph(tree, node_dict, creation_values, code, studentassignment)
    except:
        print("failed " + studentassign)
        return 0, 0
        #return None


def find_depths(tree, snap_dict, creation_values, code):
    depths = []
    labels = []
    depth_dict = {}
    depth_dict = depthGraph.find_depths(tree, depth_dict, 0, code)
    depths = depthGraph.get_depths(snap_dict, depth_dict, depths, creation_values, code, labels)
    return depths
    #depths = depthGraph.get_depths(snap_dict, depth_dict, depths, creation_values, code, labels)
    #return depthGraph.get_skew(depths)


# make program dynamic
'''
student_number = '1'
assignment_number = '6'
file_name = "task1.py"
student = "Student" + str(student_number)
assignment = "Assign" + str(assignment_number)
global studentassignment
studentassignment = student + assignment
# selection of student code to be
df = pd.read_csv('keystrokes.csv')
a_temp = df[(df.SubjectID == student) & (df.AssignmentID == assignment)]
#files = a_temp.CodeStateSection.unique()
file = 'task1.py'
a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file_name)].copy()
# a = df[(df.SubjectID == student) & (df.AssignmentID == assignment)].copy()
a = a[a.EventType == 'File.Edit'].copy()
a.loc[a.InsertText.isna(), 'InsertText'] = ''
a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
a.head()
results = write_code_from_csv(a)
code = results[0]
global new_lines
new_lines = [0]
code_list = list(code)
for i in range(len(code_list)):
    char = code_list[i]
    if char == "\n":
        new_lines.append(i + 1)
#print(new_lines)
values = results[1]
create(values, code, studentassignment)'''
# student_number = input("Which student number would you like?")
# assignment_number = input("Which assignment number would you like")
# file_name = input("Which file name would you like?")
#students = []
    # for i in range(1, 45):
    #students.append(i)
# student_number = "28"
#skews = []
#for student in students:
'''
assignments = [6, 7, 8, 9, 10, 11, 12, 13]
students = []
for i in range(1, 45):
    students.append(i)
#global graphs
#graphs = []
# for making TAST
for student_number in students:
    for assignment_number in assignments:
        # student_number = "28"
        # assignment_number = "6"
        file_name = "task1.py"
        student = "Student" + str(student_number)
        assignment = "Assign" + str(assignment_number)
        global studentassignment
        studentassignment = student + assignment
        # selection of student code to be
        df = pd.read_csv('keystrokes.csv')
        a_temp = df[(df.SubjectID == student) & (df.AssignmentID == assignment)]
        files = a_temp.CodeStateSection.unique()
        # print(files)
        #for file_name in files:
            #global file
            #file = file_name
        a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file_name)].copy()
        # a = df[(df.SubjectID == student) & (df.AssignmentID == assignment)].copy()
        a = a[a.EventType == 'File.Edit'].copy()
        a.loc[a.InsertText.isna(), 'InsertText'] = ''
        a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
        a.head()
        results = write_code_from_csv(a)
        code = results[0]
        global new_lines
        new_lines = [0]
        code_list = list(code)
        for i in range(len(code_list)):
            char = code_list[i]
            if char == "\n":
                new_lines.append(i + 1)
        #print(new_lines)
        values = results[1]
        create(values, code, studentassignment)
        # draw_forest()
    #skew = create(values, code, studentassignment)
    #    skews.append((student_number, skew))'''
'''
f = open("presExamples/" + studentassignment + "code.txt", "w")
f.write(code)
f.close()
'''


# compare nodes
'''
    if type(node1).__name__ == type(node2).__name__:
        equal = True
        fields1 = []
        for field in ast.iter_fields(node1):
            fields1.append(field)
        fields2 = []
        for field in ast.iter_fields(node2):
            fields2.append(field)
        # check if nodes have same attribute values
        if len(fields1) == len(fields2):
            for i in range(len(fields1)):
                if fields1[i] != fields2[i]:
                    equal = False
            string1 = ast.get_source_segment(code, node1)
            string2 = ast.get_source_segment(code, node2)
            # check to see if the code segments are the same
            if string1 == string2 and equal == True:
                return True
    # if we get to else- one of the tests failed and the nodes are not equal- return False
    else:
        return False
'''

