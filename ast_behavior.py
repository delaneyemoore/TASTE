import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import ast
import pandas as pd


df = pd.read_csv('keystrokes.csv')
a8 = df[(df.AssignmentID == 'Assign8') & (df.CodeStateSection == 'pattern.py')].copy()


def str_node(node):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)


class V():
    def __init__(self):
        self.max_level = 0
        self.num_nodes = 0
    def ast_visit(self, node, do_print=False, level=0):
        self.num_nodes += 1
        self.max_level = max(self.max_level, level)
        if do_print:
            print('  ' * level + str_node(node))
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.ast_visit(item, do_print, level=level+1)
            elif isinstance(value, ast.AST):
                self.ast_visit(value, do_print, level=level+1)


def get_ast_size(tree):
    v = V()
    v.ast_visit(tree)
    return v.num_nodes, v.max_level


def get_ast_sizes(df):
    s = ''
    sizes = [0]
    densities = [0]
    for _,row in df[df.EventType=='File.Edit'].iterrows():
        i = int(row.SourceLocation)
        insert = '' if pd.isna(row.InsertText) else row.InsertText
        delete = '' if pd.isna(row.DeleteText) else row.DeleteText
        s = s[:i] + insert + s[i+len(delete):]
        try:
            tree = ast.parse(s)
            n, m = get_ast_size(tree)
            sizes = sizes + [n]
            densities = densities + [n/float(m)]
        except:
            sizes = sizes + [0]
            densities = densities + [0]
    return sizes, densities


sizes = {}
densities = {}
subjects = a8.SubjectID.unique()#["Student1", "Student2", "Student3", "Student4", "Student5", "Student6"]
for subjectID in subjects:
    test = a8[(a8.SubjectID == subjectID)]
    s, d = get_ast_sizes(test)
    sizes[subjectID] = s
    densities[subjectID] = d

students100 = ['Student23', 'Student17', 'Student29', 'Student10']#, 'Student15']
students100 = students100#[2:4]
plt.figure(figsize=[20,5])
for subjectID in students100:
    y = sizes[subjectID]
    y = [y_ if y_ > 0 else np.nan for y_ in y]
    x = range(len(y))
#     sns.lineplot(data=None, x=x, y=y)#, labels=students100)
    plt.plot(x, y)
plt.legend(labels=students100)
plt.xticks(range(0, 5500, 250), rotation=90)
f = 24
plt.title('AST behavior')
plt.xlabel('Event number')
plt.ylabel('AST node count')
# plt.title('AST behavior', fontsize=f)
# plt.xlabel('Event number', fontsize=f)
# plt.ylabel('AST node count', fontsize=f)
plt.rcParams.update({'font.size': f})
plt.tight_layout()
plt.savefig('ast-evolution.pdf')