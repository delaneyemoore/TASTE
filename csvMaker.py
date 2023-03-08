import tempASTkeystroke
import depthGraph
import pandas as pd
import csv
import ast
global file_groups
file_groups = {
        "Assign6": ['task1.py', 'task2.py'],
        "Assign7": ['task1.py', 'task2.py', 'chessboard.py'],
        "Assign8": ['task1.py', 'pattern.py'],
        "Assign9": ['task1.py', 'tak2.py', 'blobber.py'],
        "Assign10": ['task1.py', 'wordinator.py'],
        "Assign11": ['task1.py', 'orbian.py'],
        "Assign12": ['task1.py', 'task2.py', 'task3.py', 'gronkyutil.py', 'deck.py', 'card.py'],
        "Assign13": ['task1.py', 'memorycard.py', 'gameboard.py', 'memory_starter.py']
    }


# https://stackoverflow.com/questions/67184001/get-depth-of-an-abstract-syntax-tree-in-python
def get_tree_height(tree):
    # This is a generic recursive algorithm
    return 1 + max((get_tree_height(child) for child in ast.iter_child_nodes(tree)),
                       default=0)


def get_file_group(assignment, filename):
    possible_files = file_groups[assignment]
    for file in possible_files:
        if filename == file:
            return file
        elif filename.casefold() == file:
            return file
    return 'unknown'


def get_df(student, assignment, file):
    # df = pd.read_csv('keystrokes.csv')
    df = pd.read_csv('keystrokesAssign10NEW3_2.csv')
    a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file)].copy()
    # a = a[(a.EventType == 'File.Edit') | (a.EventType == 'X-Copy') | (a.EventType == 'X-Paste')].copy()
    a = a[a.EventType == 'File.Edit'].copy()
    a.loc[a.InsertText.isna(), 'InsertText'] = ''
    a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
    return a


# prepare data for csv
def get_rows(student_num, assign_num, grades_df):
    # student = "Student" + str(student_num)
    # assignment = "Assign" + str(assign_num)
    # studentassignment = student + assignment
    files = get_files(student_num, assign_num)
    studentassignment = student_num + assign_num
    # files = ["calc.py"]
    rows = []
    for file_name in files:
        row = []
        #row.append(student)
        #row.append(assignment)
        row.append(student_num)
        row.append(assign_num)
        row.append(file_name)
        # need to add following metrics for each assignment file
        # # keystrokes
        # % of compilable states over the whole development (look at notebook from Edwards)
        # # of comments
        # monotonicity of AST behavior chart (from edwards) (can represent deletions and commenting)
        # get file group
        group = get_file_group(assign_num, file_name)
        row.append(group)
        # row.append("calc.py")
        # get grade
        assign_grades = grades_df[[assign_num]].copy()
        try:
            d = assign_grades.loc[student_num]
            d_value = d[0]
            row.append(d_value)
        except:
            row.append(0.0)
        # row.append(0.0)
        # get depths
        # a = get_df(student, assignment, file_name)
        a = get_df(student_num, assign_num, file_name)
        results = tempASTkeystroke.write_code_from_csv(a)
        code = results[0]
        values = results[1]
        depths, heights = tempASTkeystroke.create(values, code, studentassignment)
        # get height
        try:
            tree = ast.parse(code)
            height = get_tree_height(tree) - 1
        except:
            height = 0
        row.append(height)
        # get skew
        if depths == 0 or height == 0:
            row.append(None)
            row.append(None)
            row.append(None)
        else:
            depths.remove(depths[0])
            monotonicity = depthGraph.get_monotonicity(depths)
            row.append(monotonicity)
            atm = depthGraph.get_area_score(depths)
            row.append(atm)
            skew = depthGraph.get_skew(depths)
            row.append(skew)
            row.append(depths)
        if heights == 0 or height == 0:
            row.append(None)
            row.append(None)
            row.append(None)
        else:
            heights.remove(heights[0])
            atm = depthGraph.get_area_score(heights)
            row.append(atm)
            skew = depthGraph.get_skew(heights)
            row.append(skew)
            row.append(heights)
        rows.append(row)
        print(row)
    return rows


def get_data(students, assigns):
    data = []
    grades_df = pd.read_csv('students.csv', index_col=0)
    # students1 = students[:44]
    # students2 = students[44:]
    for student_num in students:
        for assign_num in assigns:
            rows = get_rows(student_num, assign_num, grades_df)
            for row in rows:
                data.append(row)
    # only for keystrokes with assign10
    # for student_num in students2:
        # rows = get_rows(student_num, "Assign10", grades_df)
        # for row in rows:
            # data.append(row)
    return data


def get_files(student, assignment):
    files = []
    df = pd.read_csv('keystrokesAssign10NEW3_2.csv')
    a = df[(df.SubjectID == student) & (df.AssignmentID == assignment)]
    unique = a.CodeStateSection.unique()
    for name in unique:
        if type(name) == str:
            fg = get_file_group(assignment, name)
            if fg != 'unknown':
                df = get_df(student, assignment, name)
                if not df.empty:
                    files.append(name)
    return files


# help with making csvs in python:
# https://www.pythontutorial.net/python-basics/python-write-csv-file/
def make_csv(students, assigns, csv_name):
    header = ['Student', 'Assignment', 'FileName', 'FileGroup', 'Grade', 'Height', 'Monotonicity', 'ATM', 'Skew', 'Depths List', 'Height ATM', 'Height Skew',
              'Height List']
    data = get_data(students, assigns)
    # with open('ast_metrics_with_skew.csv', 'w', encoding='UTF8', newline='') as f:
    with open(csv_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write multiple rows
        writer.writerows(data)
        # close the file
        f.close()


df = pd.read_csv('keystrokesAssign10NEW3_2.csv')
students = df.SubjectID.unique()
# students = students[32:]
students = ["StudentArithmeticCopyPaste"]
assignments = ["Assign10"]
# assign_num = "Assign10"
# file_name = "wordinator.py"
# students = students[44:]
# assignments = ["Assign6", "Assign7", "Assign8", "Assign9", "Assign10", "Assign11", "Assign12", "Assign13"]
# file_name = "task1.py"
# assignments = [6]
# students = []
# for i in range(1, 45):
#    students.append(i)
'''
for student_num in students:
    studentassignment = student_num + assign_num
    a = get_df(student_num, assign_num, file_name)
    results = tempASTkeystroke.write_code_from_csv2(a)
    code = results[0]
    values = results[1]
    depths, heights = tempASTkeystroke.create(values, code, studentassignment)'''
make_csv(students, assignments, "scratch.csv")



