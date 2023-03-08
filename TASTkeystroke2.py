import pandas as pd
import tempASTkeystroke


def get_new_copyvalues(copyvalues, copytext, n, counter):
    new_values = []
    copy_counter = 0
    for i in range(len(n)):
        if n[i] != copytext[copy_counter]:
            new_values.append(counter)
        else:
            new_values.append(copyvalues[copy_counter])
            copy_counter += 1
    return new_values


def write_code_from_csv2(a):
    code = ''
    values = []
    counter = 0
    copytext = ""
    copyloc = 0
    copyvalues = []
    pasteloc = 0
    # write out code and find creation values for each character
    for index, row in a.iterrows():
        if row.EventType == "X-Copy":
            copytext = row["InsertText"]
            copylen = len(copytext)
            copyloc = int(row.SourceLocation)
            copyvalues = values[copyloc:(copyloc + copylen)]
        else:
            i = int(row.SourceLocation)
            # Delete code
            code = code[:i] + code[i + len(row.DeleteText):]
            values = values[:i] + values[i + len(row.DeleteText):]
            # Insert code
            m = len(row.InsertText)
            n = row.InsertText
            code = code[:i] + row.InsertText + code[i:]
            new_n = n.replace(" ", "")
            new_copytext = copytext.replace(" ", "")
            if row.InsertText != '':
                text = list(row.InsertText)
                if new_n == new_copytext and copytext != "":
                    if n != copytext:
                        copyvalues = get_new_copyvalues(copyvalues, copytext, n, counter)
                    print("paste")
                    for value in copyvalues:
                        values.insert(i, value)
                        i += 1
                else:
                    for t in text:
                        values.insert(i, counter)
                        i += 1
            # increase creation value counter
            counter += 1
        # this could be where we attempt to build an intermediate AST
    return code, values


"""student = "Student1"
assignment = "Assign6"
df = pd.read_csv('keystrokes.csv')
a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == "task1.py")].copy()
a = a[(a.EventType == 'File.Edit') | (a.EventType == 'X-Copy') | (a.EventType == 'X-Paste')].copy()
a.loc[a.InsertText.isna(), 'InsertText'] = ''
a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
code, values = write_code_from_csv2(a)"""
df = pd.read_csv('keystrokesOnlyAssign10_2_27.csv')
students = df.SubjectID.unique()
# students = students[32:]
students = ["StudentAirthmeticFirst2"]
assignment = "Assign10"
# df = pd.read_csv('keystrokesCalcUpdate2_10.csv')
# students = df.SubjectID.unique()
# assignment = "Calculator"
for student in students:
    a = df[(df.SubjectID == student) & (df.AssignmentID == assignment) & (df.CodeStateSection == "wordinator.py")].copy()
    unique = a.EventType.unique()
    a = a[(a.EventType == 'File.Edit') | (a.EventType == 'X-Copy') | (a.EventType == 'X-Paste')].copy()
    unique = a.EventType.unique()
    a.loc[a.InsertText.isna(), 'InsertText'] = ''
    a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
    code, values = write_code_from_csv2(a)
    a = a[a.EventType == 'File.Edit'].copy()
    a.loc[a.InsertText.isna(), 'InsertText'] = ''
    a.loc[a.DeleteText.isna(), 'DeleteText'] = ''
    results2 = tempASTkeystroke.write_code_from_csv(a)
    code2 = results2[0]
    values2 = results2[1]
    len1 = len(code)
    len2 = len(code2)
    if code2 == code:
        print("Code same")
    if values != values2:
        print("values different")
print("hi")


