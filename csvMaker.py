import tempASTkeystroke
import depthGraph
import pandas as pd
import csv
import ast


# https://stackoverflow.com/questions/67184001/get-depth-of-an-abstract-syntax-tree-in-python
def get_tree_height(tree):
    # This is a generic recursive algorithm
    return 1 + max((get_tree_height(child) for child in ast.iter_child_nodes(tree)),
                       default=0)


# prepare data for csv
def get_data(students, assigns, file_name):
    data = []
    grades_df = pd.read_csv('students.csv', index_col=0)
    for student_num in students:
        for assign_num in assigns:
            row = []
            student = "Student" + str(student_num)
            assignment = "Assign" + str(assign_num)
            studentassignment = student + assignment
            # print(studentassignment)
            row.append(student)
            row.append(assignment)
            # get grade
            assign_grades = grades_df[[assignment]].copy()
            d = assign_grades.loc["Student" + str(student_num)]
            d_value = d[0]
            row.append(d_value)
            # get depths
            df = pd.read_csv('keystrokes.csv')
            # a = df[(df.SubjectID == student) & (df.AssignmentID == assignment)]
            # unique = a.CodeStateSection.unique()
            a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == file_name)].copy()
            a = a[a.EventType == 'File.Edit'].copy()
            a.loc[a.InsertText.isna(), 'InsertText'] = ''
            a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
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
                monotinictiy = depthGraph.get_monotinicity(heights)
                row.append(monotinictiy)
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
            #print(row)

            data.append(row)
    return data


# help with making csvs in python:
# https://www.pythontutorial.net/python-basics/python-write-csv-file/
def make_csv(students, assigns, file_name, csv_name):
    header = ['Student', 'Assignment', 'Grade', 'Height', 'Monotinicity', 'ATM', 'Skew', 'Depths List', 'Height ATM', 'Height Skew',
              'Height List']
    data = get_data(students, assigns, file_name)
    #with open('ast_metrics_with_skew.csv', 'w', encoding='UTF8', newline='') as f:
    with open(csv_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write multiple rows
        writer.writerows(data)
        # close the file
        f.close()


assignments = [6, 7, 8, 9, 10, 11, 12, 13]
file_name = "task1.py"
# assignments = [6]
students = []
for i in range(1, 45):
    students.append(i)
make_csv(students, assignments, file_name, "ast_metrics_with_monotonicity.csv")



