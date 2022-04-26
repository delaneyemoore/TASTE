import tempASTkeystroke
import depthGraph
import pandas as pd
import matplotlib.pyplot as plt
import ast


# develop scatterplot for metrics
def make_scatter(grades, metrics, assign_num, type):
    # set up data first
    assign_grades = grades[[assign_num]].copy()
    x = []
    y = []
    low = 2
    low_student = 0
    high = 0
    high_student = 0
    for i in metrics:
        x.append(metrics[i])
        if metrics[i] < low and metrics[i] != 0:
            low = metrics[i]
            low_student = i
        if metrics[i] > high:
            high = metrics[i]
            high_student = i
        y.append(assign_grades.loc["Student" + str(i)])
    print("Lowest " + type + "=" + "Student" + str(low_student) + " " + str(low))
    print("Highest " + type + "=" + "Student" + str(high_student) + " " + str(high))
    plt.figure(figsize=(20, 20))
    plt.scatter(x, y, c="blue")
    plt.title(type + " Metrics vs Grades " + assign_num)
    plt.xlabel("Metric Value")
    plt.ylabel("Grade")
    # To show the plot
    plt.savefig('scatterplots/Scatter' + type + assign_num + '.png', dpi=100)  # bbox_inches='tight'
    plt.close()


def get_code_df(student_number, assignment_number, file_name):
    student = "Student" + str(student_number)
    assignment = "Assign" + str(assignment_number)
    global studentassignment
    studentassignment = student + assignment
    # selection of student code to be
    df = pd.read_csv('keystrokes.csv')
    a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file_name)].copy()
    a = a[a.EventType == 'File.Edit'].copy()
    a.loc[a.InsertText.isna(), 'InsertText'] = ''
    a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
    return a


def create_scatter():
    assignment_number = 13
    # create loop that will go through each student for a given assignment
    # selection of student code to be
    df = pd.read_csv('keystrokes.csv')
    assignment = "Assign" + str(assignment_number)
    file_name = 'task1.py'
    # df["SubjectID"].replace("Student", "", regex=True)
    # main_df["SubjectID"].apply(lambda x: [item for item in x if item is in ['Student']])
    student_numbers = df.SubjectID.unique()
    student_numbers = [s.replace('Student', '') for s in student_numbers]
    area_dict = {}
    mid_dict = {}
    for s_num in student_numbers:
        student = "Student" + s_num
        a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file_name)].copy()
        a = a[a.EventType == 'File.Edit'].copy()
        a.loc[a.InsertText.isna(), 'InsertText'] = ''
        a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
        a.head()
        studentassignment = student + assignment
        print(studentassignment)
        results = tempASTkeystroke.write_code_from_csv(a)
        code = results[0]
        values = results[1]
        # Build an AST and Depth graphs
        if a.empty:
            area_met = 0
            mid_met = 0
        else:
            metrics = tempASTkeystroke.create(values, code, studentassignment)
            area_met = metrics[0]
            mid_met = metrics[1]
        area_dict[s_num] = area_met
        mid_dict[s_num] = mid_met
    grades_df = pd.read_csv('students.csv', index_col=0)
    make_scatter(grades_df, area_dict, assignment, "Area")
    make_scatter(grades_df, mid_dict, assignment, "Midline")


def write_code_and_trees(a):
    code = ''
    values = []
    counter = 0
    compilable_states = 0
    # keystroke #, index = cs #
    keystrokes = []
    # ast obj, index = cs #
    trees = []
    values_per_tree = []
    code_per_tree = []
    # write out code and find creation values for each character
    for index, row in a.iterrows():
        i = int(row.SourceLocation)
        # Delete code
        code = code[:i] + code[i + len(row.DeleteText):]
        if row.DeleteText != '':
            delete = len(row.DeleteText)
            pop_list = []
            for char in range(delete):
                pop_list.append(i)
                i += 1
            for j in range(len(pop_list) - 1, -1, -1):
                values.pop(j)
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
        try:
            # attempt to build an intermediate AST
            tree = ast.parse(code)
            # if successful, add to compilable state counter and add cs, tree, and keystroke ind to appropriate dict
            compilable_states += 1
            keystrokes.append(counter)
            trees.append(tree)
            values_per_tree.append(values)
            code_per_tree.append(code)
            # set up variables for building tree visual
        except Exception:
            # if we can not build tree, the state is not compilable and we keep writing code
            pass
    return trees, values, code, values_per_tree, code_per_tree


def create_intermediate_trees(student_number, assignment_number, file_name):
    studentassign = "Student" + str(student_number) + "Assign" + str(assignment_number)
    a = get_code_df(student_number, assignment_number, file_name)
    results = write_code_and_trees(a)
    trees = results[0]
    values = results[1]
    code = results[2]
    tree_values = results[3]
    tree_codes = results[4]
    tree_node = ast.parse(code)
    nodes = []
    edges = []
    compilable_states = []
    label_dict = {}
    # call appropriate functions to build and visualize tree
    tempASTkeystroke.build_temp_ast_intermediate(code, None, tree_node, 0, nodes, edges, label_dict, compilable_states, trees, values, tree_values, tree_codes)
    tempASTkeystroke.build_graph_intermediate(nodes, edges, label_dict, compilable_states, studentassign)


create_intermediate_trees(1, 6, 'task1.py')
# create_scatter()
