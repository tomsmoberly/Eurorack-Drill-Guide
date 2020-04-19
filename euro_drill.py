import sys
import numpy as np
from PIL import Image
import drill_mapper
from Component import Component
from Component import ComponentType
from Board import Board


def interpret_input(inp):
    interpreted = list()
    for row in inp:
        row = row.lower()
        if 't' in row:
            interpreted.append((row.count('t'), ComponentType.PJ398SM))
        if 'p' in row:
            interpreted.append((row.count('p'), ComponentType.POT))
    return interpreted


def handle_io(vertical_pads, dummy_data):
    if not dummy_data:
        print('If you have a module width in HP already decided, enter it now. Leave blank to let program determine size.')
        module_width = input('')
        if (module_width != ''):
            module_width = int(module_width)
        else:
            module_width = 0
        print('Enter the layout of your module, followed by a blank line when done.',
              'For example, if it has three pots stacked vertically',
              'followed by 1 jack on a row, followed by 2 jacks on a row, you would enter this:')
        print('\np\np\np\nj\njj\n\n')
        input_rows = list()
        ti = input('')
        while ti != '':
            input_rows.append(ti)
            ti = input('')
    else:
        input_rows = list()
        # input_rows.append('p')
        input_rows.append('p')
        input_rows.append('p')
        # input_rows.append('p')
        input_rows.append('t')
        input_rows.append('tt')
        input_rows.append('t')
        input_rows.append('tt')
        # input_rows.append('j')
        module_width = 0
    interpreted = interpret_input(input_rows)
    if (module_width == 0):
        for i in interpreted:
            if (i[1] == ComponentType.PJ398SM):
                r_size = i[0] * 2
                if (r_size > module_width):
                    module_width = r_size
            if (i[1] == ComponentType.POT):
                r_size = i[0] * 2 + 1
                if (r_size > module_width):
                    module_width = r_size
            # print(i[0], i[1])
    drill_mapper.drill_map(module_width)
    board = Board(module_width, vertical_pads)
    board.add_components(interpreted)
    return board


def main():
    if('debug' in sys.argv):
        print('debug')
        return
    available_vertical_pads = 41
    board = handle_io(available_vertical_pads, True)
    board.arrange()
    # board.print_rows()
    drill_mapper.create_drill_guide(board, 30, 2, 5)
    print(board)

if __name__ == '__main__':
    main()
