import numpy as np
from PIL import Image
from Board import Board

doepfer_measurements = {1:5.00, 2:9.80, 3:15, 4: 20.00, 6: 30.00, 8: 40.30, 10:50.50, 12:60.60, 14:70.80, 16:80.90,
                        18:91.30, 20:101.30, 21:106.68, 22:111.76, 28:142.24, 42:213.36}

def print_drill_map(module_width):
    print('Module width =', str(module_width) + 'HP,', 'which is', str(doepfer_measurements[module_width]), 'mm.')

def drill_map(module_width):
    while module_width not in doepfer_measurements:
        module_width = module_width + 1
        if (module_width > 100):
            print('Something has gone wrong. Could not find a module width that fit.')
            quit()

# pixels per mm
ppmm = 11.81103

def create_outline(board, padding, stroke):
    pixel_width = board.width * ppmm
    i_pixel_width = int(pixel_width)
    pixel_height = 128.5 * ppmm
    i_pixel_height = int(pixel_height)

    pixels = list()
    # Add top padding
    for i in range(padding - (stroke // 2)):
        row = list()
        for j in range(i_pixel_width + 2 * padding):
            row.append((255, 255, 255))
        pixels.append(row)

    # Top stroke line
    for i in range(stroke):
        row = list()
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        for j in range(i_pixel_width + stroke):
            row.append((0, 0, 0))
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        pixels.append(row)
    # end top padding

    # core
    for i in range(i_pixel_height):
        row = list()
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        for j in range((stroke)):
            row.append((0, 0, 0))
        for j in range(i_pixel_width - (stroke)):
            row.append((255, 255, 255))
        for j in range((stroke)):
            row.append((0, 0, 0))
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        pixels.append(row)
    # end core

    # add bottom padding
    # Bot stroke line
    for i in range(stroke):
        row = list()
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        for j in range(i_pixel_width + stroke):
            row.append((0, 0, 0))
        for j in range(padding - (stroke // 2)):
            row.append((255, 255, 255))
        pixels.append(row)

    for i in range(padding - (stroke // 2)):
        row = list()
        for j in range(i_pixel_width + 2 * padding):
            row.append((255, 255, 255))
        pixels.append(row)
    # end bottom padding

    return pixels

def drill_mark_px(pixels, radius, mid_x, mid_y):
    mid_x = int(mid_x)
    mid_y = int(mid_y)
    for y in range(radius*2+1):
        for x in range(radius*2+1):
            rx = x-radius
            ry = y-radius
            if (rx * rx + ry * ry <= radius * radius):
                pixels[mid_y+ry][mid_x+rx] = (0, 0, 0)


def get_drill_positions(board):
    x_center = board.width/2
    y_center = 128.5/2
    x_zero = x_center - (board.pad_width//2) * 2.54
    y_zero = y_center - (board.pad_height // 2) * 2.54
    if (board.pad_width % 2 == 0):
        x_zero = x_zero + (2.54 / 2)
    if (board.pad_height % 2 == 0):
        y_zero = y_zero + (2.54 / 2)
    drill_marks = list()
    for br in board.board_rows:
        for comp in br.row:
            drill_marks.append( (x_zero+comp.x_offset*2.54+comp.drill_offsets[0],
                                 y_zero+comp.y_offset*2.54+comp.drill_offsets[1]) )
    return drill_marks

def create_drill_guide(board, padding, stroke, radius):
    pixels = create_outline(board, padding, stroke)
    drills = get_drill_positions(board)
    for drill in drills:
        drill_mark_px(pixels, radius, padding+drill[0]*ppmm, padding+drill[1]*ppmm)

    # convert pixels to numpy array
    numpy_array = np.array(pixels, dtype=np.uint8)

    # create image from pix array
    output_image = Image.fromarray(numpy_array)
    output_image.save('board.png')

    # im = Image.open("board.png")
    # im.show()