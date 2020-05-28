import sys
import numpy as np
import time
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
        while(vertical_pads == 0):
            input_pads = input('How many vertical pads on your board? Leave blank to use 43 (Tayda SKU: A-2384)\n')
            if(input_pads == ''):
                vertical_pads = 43
            else:
                vertical_pads = int(input_pads)
        # print("This many vertical pads:", vertical_pads)
        print('Enter the layout of your module, followed by a blank line when done.',
              'For example, if it has three pots stacked vertically',
              'followed by 1 jack on a row, followed by 2 jacks on a row, you would enter this:')
        print('\np\np\np\nt\ntt\n\n')
        input_rows = list()
        ti = input('')
        while ti != '':
            input_rows.append(ti)
            ti = input('')

        jacks_only = True
        for inp in input_rows:
            if(inp != 't'):
                jacks_only = False
                break

        if(jacks_only):
            scrunch = False
        else:
            answer = ''
            while (answer.lower() != 'y' and answer.lower() != 'n'):
                print(answer)
                print('Should the jacks be scrunched at the bottom (to save room for knobs)? Enter y/n:')
                answer = input('')
            if (answer.lower() == 'y'):
                scrunch = True
            else:
                scrunch = False
    else:
        input_rows = list()
        input_rows.append('pppp')
        input_rows.append('pppp')
        input_rows.append('ppp')
        # input_rows.append('t')
        # input_rows.append('t')
        input_rows.append('pppp')
        input_rows.append('tttttt')
        # input_rows.append('t')
        # input_rows.append('t')
        input_rows.append('ttttttt')
        # input_rows.append('j')
        scrunch = True
        module_width = 16
        vertical_pads = 43
    print('Creating drill guide...')
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
    # drill_mapper.drill_map(module_width)
    board = Board(module_width, vertical_pads, scrunch)
    board.add_components(interpreted)
    return board


def main():
    # TODO: stripboard vs padboard
    show_image = False
    available_vertical_pads = 0
    if('debug' in sys.argv):
        show_image = True
        # available_vertical_pads = 0
    board = handle_io(available_vertical_pads, False)
    # board.arrange()
    padding = 30
    stroke = 6
    pnpx = drill_mapper.create_drill_guide(board, padding, stroke, 5, show_image)
    pdpx = board.create_pad_image(stroke)
    # print(len(pnpx), len(pnpx[0]), len(pdpx), len(pdpx[0]))
    diff = len(pnpx) - len(pdpx)
    for i in range(len(pnpx)):
        for p in range(300):
            pnpx[i].append((255,255,255))

    pdw = len(pdpx[0])
    pdh = len(pdpx)
    half_rem = diff//2
    for i in range(half_rem):
        for p in range(pdw):
            pnpx[i].append((255,255,255))
    for i in range(pdh):
        for p in range(pdw):
            pnpx[i+half_rem].append(pdpx[i][p])
    for i in range((diff//2)+(diff%2)):
        for p in range(pdw):
            pnpx[i+half_rem+pdh].append((255,255,255))

    #padding
    for i in range(len(pnpx)):
        for p in range(padding):
            pnpx[i].append((255,255,255))

    # print(board)

    numpy_array = np.array(pnpx, dtype=np.uint8)
    output_image = Image.fromarray(numpy_array)
    # TODO: if the image is too large to be printed on one sheet of paper, print on 2+
    saved = False
    msg_delivered = False
    while not saved:
        try:
            output_image.save('panel_board.pdf', resolution=Board.ppi, title="Eurorack Panel & Board", author="AutoEuroDrill v0.1")
            saved = True
        except:
            saved = False
            if not msg_delivered:
                print("The file was unable to be saved. Check if the PDF is open and close it if so.")
                msg_delivered = True
            else:
                time.sleep(.1)

    output_image.save('panel_board_preview.bmp')
    im = Image.open("panel_board_preview.bmp")
    im.show()
    print(board)


if __name__ == '__main__':
    # TODO: try the following inputs. Pots are not aligned well
    # p
    # pp
    # tt
    # ttt
    main()
