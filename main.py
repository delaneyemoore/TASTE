import tempASTkeystroke as tempAST
import depthGraph as depth
import csvMaker
import os.path


# create CSV for keystroke explorer application
def create_csv(students, assignments, file_name):
    # students = []
    # for i in range(1, 45):
    #     students.append(i)
    # assignments = [6, 7, 8, 9, 10, 11, 12, 13]
    # file_name = "task1.py"
    csv_name = input("Please enter the csv file name: ")
    csv_name_parts = csv_name.split(".")
    if len(csv_name_parts) == 1:
        csv_name = csv_name + ".csv"
    else:
        if csv_name_parts[1] != "csv":
            csv_name = csv_name_parts[0] + ".csv"
    csvMaker.make_csv(students, assignments, file_name, csv_name)


def create_trees(students, assignments, file_name):
    for student_number in students:
        student = "Student" + str(student_number)
        for assignment_number in assignments:
            assignment = "Assign" + str(assignment_number)
    return 0


def create_depth_charts():
    return 0


def create_height_charts():
    return 0


def check_numbers(numbers):
    message = ""
    new_numbers = []
    if numbers[0] == 'r':
        try:
            low = int(numbers[1])
            high = int(numbers[2])
            for i in range(low, high + 1):
                new_numbers.append(i)
        except (RuntimeError, TypeError, NameError, IndexError, ValueError):
            return False, "The range for could not be interpreted, please try again.", new_numbers
    else:
        try:
            for val in numbers:
                new_numbers.append(int(val))
        except (RuntimeError, TypeError, NameError, IndexError, ValueError):
            return False, "Input could not be converted to integers, please try again.", new_numbers
    return True, message, new_numbers


# get input from user, call functions accordingly
cont = True
while cont:
    file_name = input("What is the keystroke file name? (enter 'q' to quit)")
    if file_name == "q":
        break
    if os.path.exists('readme.txt') is False:
        print("The file does not exist")
        continue
    student_numbers = input("Enter student numbers (for range begin input with 'r' and then the lowest value followed "
                            "by the largest value like so: 'r 1 45'):")
    student_numbers = student_numbers.split()
    status, s_print_message, students = check_numbers(student_numbers)
    if status is False:
        print(s_print_message)
        continue
    assignment_numbers = input("Enter assignment numbers (for range begin input with 'r' and then the lowest value "
                               "followed by the largest value like so: 'r 1 45'):")
    assignment_numbers = assignment_numbers.split()
    status, a_print_message, assignments = check_numbers(assignment_numbers)
    if status is False:
        print(a_print_message)
        continue
    options = input("What action would you like to perform? (you may choose more than one, space separated)"
                    "\n1: Create keystroke explorer CSV"
                    "\n2: Create TASTs"
                    "\n3: Create Depth Charts"
                    "\n4: Create Height Charts"
                    "\nq: Quit")
    options = options.split()
    num_calls = 0
    if options.includes('1'):
        print("Creating csv...")
        num_calls += 1
        create_csv(students, assignments, file_name)
    if options.includes('2'):
        print("Creating TASTs...")
        num_calls += 1
        create_trees()
    if options.includes('3'):
        print("Creating depth charts...")
        num_calls += 1
        create_depth_charts()
    if options.includes('4'):
        print("Creating height charts...")
        num_calls += 1
        create_height_charts()
    if options.includes('q'):
        print("Quit")
        cont = False
        num_calls += 1
    if num_calls == 0:
        print("The input provided was not entered correctly or was not an option, please try again.")




