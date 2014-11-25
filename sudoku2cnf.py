#!/usr/bin/env python

from __future__ import print_function
import numpy
import random
import sys
from itertools import combinations, product
from cStringIO import StringIO
import subprocess


MINISAT_EXEC = "minisat/minisat"
TMP_INPUT = "sudoku_cnf.txt"
TMP_OUTPUT = "minisat_out.txt"

def pos2variable(size, row, column, val):
    variable = val + (column * size) + (row * size * size)
    return variable + 1


def var2pos(variable, size):
    variable = abs(variable) - 1
    value = variable % size
    variable = variable / size
    column = variable % size
    row = variable / size
    return row, column, value


def random_sudoku(size):
    def valid_row_values(sudoku, row):
        row = sudoku[row - 1, :]
        row_vals = row[row != 0]
        all_vals = numpy.arange(1, size + 1)
        return numpy.setdiff1d(all_vals, row_vals)

    def valid_col_values(sudoku, col):
        col = sudoku[:, col - 1]
        col_vals = col[col != 0]
        all_vals = numpy.arange(1, size + 1)
        return numpy.setdiff1d(all_vals, col_vals)

    def valid_box_values(sudoku, row, col):
        box_size = int(size ** 0.5)
        box_row = ((row - 1) / box_size) * box_size
        box_col = ((col - 1) / box_size) * box_size
        box = sudoku[box_row:box_row + box_size, box_col:box_col + box_size]
        box = numpy.array(box).flatten()
        box_vals = box[box != 0]
        all_vals = numpy.arange(1, size + 1)
        return numpy.setdiff1d(all_vals, box_vals)

    def valid_values(sudoku, row, col):
        row_vals = valid_row_values(sudoku, row)
        col_vals = valid_col_values(sudoku, col)
        box_vals = valid_box_values(sudoku, row, col)
        valid_vals = numpy.intersect1d(row_vals, col_vals)
        return numpy.intersect1d(valid_vals, box_vals)

    ###
    sudoku = numpy.zeros((size, size))
    for i in xrange(size):
        r1 = valid_values(sudoku, 1, i + 1)
        sudoku[0, i] = random.choice(r1)
        c1 = valid_values(sudoku, i + 1, 1)
        sudoku[i, 0] = random.choice(c1)
        d1 = valid_values(sudoku, i + 1, i + 1)
        sudoku[i, i] = random.choice(d1)
    return sudoku


def draw_result(sat_output, size):
    result = None
    with open(sat_output, "r") as f:
        ans = f.readline().strip()
        assert ans == "SAT"
        result = map(int, f.readline().strip().split())
        del result[-1]

    sudoku = [[0 for _ in xrange(size)] for _ in xrange(size)]
    for v in result:
        if v < 0:
            continue

        row, col, value = var2pos(v, size)
        assert sudoku[row][col] == 0
        sudoku[row][col] = value + 1

    for i in xrange(size):
        for j in xrange(size):
            print("%2d " % sudoku[i][j], end="")
        print("")


def reduction1(sudoku):
    size = len(sudoku)
    box_size = int(size ** 0.5)
    variables = size ** 3
    buffer = StringIO()
    clauses = 0

    ###
    buffer.write('c initial conditions (clause type 3)\n')
    for row in xrange(size):
        for col in xrange(size):
            val = int(sudoku[row, col])
            if val != 0:
                buffer.write("%d 0\n" % pos2variable(size, row, col, val - 1))
                clauses += 1

    ###
    buffer.write('c each cell has a certain number (clause type 1)\n')
    for row in xrange(size):
        for col in xrange(size):
            for val in xrange(size):
                variable = pos2variable(size, row, col, val)
                buffer.write('%d ' % variable)
            buffer.write('0\n')
            clauses += 1

    ###
    buffer.write('c sudoku rule for rows (clause type 2)\n')
    for row in xrange(size):
        for val in xrange(size):
            for col_1, col_2 in combinations(xrange(size), 2):
                variable1 = pos2variable(size, row, col_1, val)
                variable2 = pos2variable(size, row, col_2, val)
                buffer.write("-%d -%d 0\n" % (variable1, variable2))
                clauses += 1

    ###
    buffer.write('c sudoku rule for columns (clause type 2)\n')
    for col in xrange(size):
        for val in xrange(size):
            for row_1, row_2 in combinations(xrange(size), 2):
                variable1 = pos2variable(size, row_1, col, val)
                variable2 = pos2variable(size, row_2, col, val)
                buffer.write("-%d -%d 0\n" % (variable1, variable2))
                clauses += 1

    ###
    buffer.write('c sudoku rule for boxes (clause type 2)\n')
    for box_id in xrange(size):
        box_row = (box_id % box_size) * box_size
        box_col = (box_id / box_size) * box_size

        for val in xrange(size):
            for row_1, row_2 in product(xrange(box_row, box_row + box_size),
                                        repeat=2):
                for col_1, col_2 in product(xrange(box_col, box_col + box_size),
                                            repeat=2):
                    if row_1 == row_2 and col_1 == col_2:
                        continue

                    variable_1 = pos2variable(size, row_1, col_1, val)
                    variable_2 = pos2variable(size, row_2, col_2, val)
                    buffer.write("-%d -%d 0\n" % (variable_1, variable_2))
                    clauses += 1

    with open(TMP_INPUT, "w") as cnf_file:
        cnf_file.write("p cnf %d %d\n" % (variables, clauses))
        cnf_file.write(buffer.getvalue())


def reduction2(sudoku):
    size = len(sudoku)
    box_size = int(size ** 0.5)
    variables = size ** 3
    buffer = StringIO()
    clauses = 0

    ###
    buffer.write('c initial conditions (clause type 3)\n')
    for row in xrange(size):
        for col in xrange(size):
            val = int(sudoku[row, col])
            if val != 0:
                buffer.write("%d 0\n" % pos2variable(size, row, col, val - 1))
                clauses += 1

    ###
    buffer.write('c each cell has a certain number (clause type 1)\n')
    for row in xrange(size):
        for col in xrange(size):
            for val_1, val_2 in combinations(xrange(size), 2):
                variable_1 = pos2variable(size, row, col, val_1)
                variable_2 = pos2variable(size, row, col, val_2)
                buffer.write('-%d -%s 0\n' % (variable_1, variable_2))
                clauses += 1

    ###
    buffer.write('c sudoku rule for rows (clause type 2)\n')
    for row in xrange(size):
        for val in xrange(size):
            for col in xrange(size):
                variable = pos2variable(size, row, col, val)
                buffer.write('%d ' % variable)
            buffer.write('0\n')
            clauses += 1

    ###
    buffer.write('c sudoku rule for columns (clause type 2)\n')
    for col in xrange(size):
        for val in xrange(size):
            for row in xrange(size):
                variable = pos2variable(size, row, col, val)
                buffer.write('%d ' % variable)
            buffer.write('0\n')
            clauses += 1

    ###
    buffer.write('c sudoku rule for boxes (clause type 2)\n')
    for box_id in xrange(size):
        box_row = (box_id % box_size) * box_size
        box_col = (box_id / box_size) * box_size

        for val in xrange(size):
            for row in xrange(box_row, box_row + box_size):
                for col in xrange(box_col, box_col + box_size):
                    variable = pos2variable(size, row, col, val)
                    buffer.write('%d ' % variable)

            buffer.write('0\n')
            clauses += 1

    with open(TMP_INPUT, "w") as cnf_file:
        cnf_file.write("p cnf %d %d\n" % (variables, clauses))
        cnf_file.write(buffer.getvalue())


def run_minisat(input_file, output_file):
    cmd = [MINISAT_EXEC, input_file, output_file]
    subprocess.call(cmd)


def main():
    if len(sys.argv) != 3:
        print("Usage sudoku2cnf.py [1|2] size", file=sys.stderr)
        return 1

    red_type = sys.argv[1]
    size = int(sys.argv[2])
    if int(size ** 0.5) ** 2 != size:
        print("Size should be a squared number", file=sys.stderr)
        return 1
    if red_type not in ["1", "2"]:
        print("Reduction type could be either 1 or 2", file=sys.stderr)
        return 1

    sudoku = random_sudoku(size)
    if red_type == "1":
        reduction1(sudoku)
    else:
        reduction2(sudoku)

    run_minisat(TMP_INPUT, TMP_OUTPUT)
    draw_result(TMP_OUTPUT, size)

    return 0

if __name__ == '__main__':
    main()
