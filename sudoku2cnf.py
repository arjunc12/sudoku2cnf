import numpy
import random
from sys import argv

def pos2variable(size, row, column, val):
    varPerRow = size*size
    varPerCol = size
    x = row * varPerRow
    x += column * varPerCol
    x += val
    return x + 1

def valid_row_values(sudoku, row, size):
    row = sudoku[row - 1, :]
    row_vals = row[row != 0]
    all_vals = numpy.arange(1, size + 1)
    return numpy.setdiff1d(all_vals, row_vals)

def valid_col_values(sudoku, col, size):
    col = sudoku[:, col - 1]
    col_vals = col[col != 0]
    all_vals = numpy.arange(1, size + 1)
    return numpy.setdiff1d(all_vals, col_vals)
    
def valid_box_values(sudoku, row, col, size):
    box_size = int(size ** 0.5)
    box_row = ((row - 1) / box_size) * box_size
    box_col = ((col - 1) / box_size) * box_size
    box = sudoku[box_row:box_row + box_size, box_col:box_col + box_size]
    box = numpy.array(box).flatten()
    box_vals = box[box != 0]
    all_vals = numpy.arange(1, size + 1)
    return numpy.setdiff1d(all_vals, box_vals)

def valid_values(sudoku, row, col, size):
    row_vals = valid_row_values(sudoku, row, size)
    col_vals = valid_col_values(sudoku, col, size)
    box_vals = valid_box_values(sudoku, row, col, size)
    valid_vals = numpy.intersect1d(row_vals, col_vals)
    return numpy.intersect1d(valid_vals, box_vals)

def random_sudoku(size):
    sudoku = numpy.zeros((size, size))
    for i in xrange(size):
        r1 = valid_values(sudoku, 1, i + 1, size)
        sudoku[0, i] = random.choice(r1)
        c1 = valid_values(sudoku, i + 1, 1, size)
        sudoku[i, 0] = random.choice(c1)
        d1 = valid_values(sudoku, i + 1, i + 1, size)
        sudoku[i, i] = random.choice(d1)
    return sudoku

def reduction1(sudoku):
    size = len(sudoku)
    box_size = int(size ** 0.5)
    variables = size ** 3
    temp_file = open('temp.txt', 'w')
    clauses = 0

    for row in xrange(size):
        for col in xrange(size):
            val = sudoku[row, col]
            if val != 0:
                temp_file.write("%d 0\n" % pos2variable(size, row, col, val))
                for row2 in xrange(size):
                    if row2 != row:
                        variable = pos2variable(size, row2, col, val)
                        temp_file.write("-%d 0\n" % variable)
                        clauses += 1
                for col2 in xrange(size):
                    if col2 != col:
                        variable = pos2variable(size, row, col2, val)
                        temp_file.write("-%d 0\n" % variable)
                        clauses += 1
                box_row = (row / box_size) * box_size
                box_col = (col / box_size) * box_size
                for i in xrange(box_row, box_row + box_size):
                    for j in xrange(box_col, box_col + box_size):
                        if i != row and j != col:
                            variable = pos2variable(size, i, j, val)
                            temp_file.write("-%d 0\n" % variable)
                            clauses += 1


    for row in xrange(size):
        for col in xrange(size):
            for val in xrange(size):
                variable = pos2variable(size, row, col, val)
                temp_file.write("%d" %variable)
                if val != size - 1:
                    temp_file.write(" ")
                clauses += 1
            temp_file.write(' 0\n')
    
    for row in xrange(size):
        for col1 in xrange(size):
            for col2 in xrange(col1 + 1, size):
                for val in xrange(size):
                    variable1 = pos2variable(size, row, col1, val)
                    variable2 = pos2variable(size, row, col2, val)
                    temp_file.write("-%d -%d 0\n" % (variable1, variable2))
                    clauses += 1
    
    for col in xrange(size):
        for row1 in xrange(size):
            for row2 in xrange(row1 + 1, size):
                for val in xrange(size):
                    variable1 = pos2variable(size, row1, col, val)
                    variable2 = pos2variable(size, row2, col, val)
                    temp_file.write("-%d -%d 0\n" % (variable1, variable2))
                    clauses += 1

    for box in xrange(size):
        box_row = (box / box_size) * box_size
        box_col = (box % box_size) * box_size
        for row1 in xrange(box_row, box_row + box_size):
            for col1 in xrange(box_col, box_col + box_size):
                for row2 in xrange(box_row, box_row + box_size):
                    for col2 in xrange(box_col, box_col + box_size):
                        if row1 != row2 and col1 != col2:
                            for num in xrange(size):
                                variable1 = pos2variable(size, row1, col1, num)
                                variable2 = pos2variable(size, row2, col2, num)
                                temp_file.write("-%d -%d 0\n" % (variable1, variable2))
                                clauses += 1

    cnf_file = open("sudoku_cnf.txt", "w")
    cnf_file.write("p cnf %d %d\n" % (variables, clauses))
    temp_file.close()
    for line in open("temp.txt", 'r'):
        cnf_file.write(line)
    cnf_file.close()


def reduction2(sudoku):
    size = len(sudoku)
    box_size = int(size ** 0.5)
    variables = size ** 3
    temp_file = open('temp.txt', 'w')
    clauses = 0

    for row in xrange(size):
        for col in xrange(size):
            val = sudoku[row, col]
            if val != 0:
                temp_file.write("%d 0\n" % pos2variable(size, row, col, val))
                for row2 in xrange(size):
                    if row2 != row:
                        variable = pos2variable(size, row2, col, val)
                        temp_file.write("-%d 0\n" % variable)
                        clauses += 1
                for col2 in xrange(size):
                    if col2 != col:
                        variable = pos2variable(size, row, col2, val)
                        temp_file.write("-%d 0\n" % variable)
                        clauses += 1
                box_row = (row / box_size) * box_size
                box_col = (col / box_size) * box_size
                for i in xrange(box_row, box_row + box_size):
                    for j in xrange(box_col, box_col + box_size):
                        if i != row and j != col:
                            variable = pos2variable(size, i, j, val)
                            temp_file.write("-%d 0\n" % variable)
                            clauses += 1

    for row in xrange(size):
        for col in xrange(size):
            for val in xrange(size):
                variable = pos2variable(size, row, col, val)
                temp_file.write("%d" %variable)
                if val != size - 1:
                    temp_file.write(" ") 
                clauses += 1
            temp_file.write(' 0\n')
    
    for row in xrange(size):
        for val in xrange(size):
            for col in xrange(size):
                variable = pos2variable(size, row, col, val)    
                temp_file.write("%d" % variable)
                if col != size - 1:
                    temp_file.write(" ")
                clauses += 1
            temp_file.write(" 0\n")

    
    for col in xrange(size):
        for val in xrange(size):
            for row in xrange(size):
                variable = pos2variable(size, row, col, val)    
                temp_file.write("%d" % variable)
                if row != size - 1:
                    temp_file.write(" ")
                clauses += 1
            temp_file.write(" 0\n")

    for box in xrange(size):
        box_row = (box / box_size) * box_size
        box_col = (box % box_size) * box_size
        for val in xrange(size):
            for row in xrange(box_row, box_row + box_size):
                for col in xrange(box_col, box_col + box_size):
                    variable = pos2variable(size, row, col, val)
                    temp_file.write("%d" % variable)
                    if row != box_row + box_size - 1 and col != box_col + box_size - 1:
                        temp_file.write(" ")
                    clauses += 1
            temp_file.write(" 0\n")

    cnf_file = open("sudoku_cnf2.txt", "w")
    cnf_file.write("p cnf %d %d\n" % (variables, clauses))
    temp_file.close()
    for line in open("temp.txt", 'r'):
        cnf_file.write(line)
    cnf_file.close()

if __name__ == '__main__':
    size = int(argv[1])
    sudoku = random_sudoku(size)
    reduction1(sudoku)
    reduction2(sudoku)
