import numpy as np
from PIL import Image
from Board import Board

doepfer_measurements = {1:5.00, 2:9.80, 3:15, 4: 20.00, 6: 30.00, 8: 40.30, 10:50.50, 12:60.60, 14:70.80, 16:80.90,
                        18:91.30, 20:101.30, 21:106.68, 22:111.76, 28:142.24, 42:213.36}

def print_drill_map(module_width):
    print('Module width =', str(module_width) + 'HP,', 'which is', str(doepfer_measurements[module_width]), 'mm.')

# pixels per mm
ppmm = Board.ppi*0.0393701

def create_outline(board, padding, stroke):
    pixel_width = board.width * ppmm
    i_pixel_width = int(pixel_width)
    #TODO handle if too many holes in stripboard and board is >128.5 OR if it's > 112 or so
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

def drill_outline_px(pixels, r, thickness, mid_x, mid_y):
    mid_x = int(mid_x)
    mid_y = int(mid_y)

    # print('mid_xy', mid_x, mid_y)
    for i in range(thickness-1):
        radius = r+i
        for y in range(radius*2+1):
            for x in range(radius*2+1):
                rx = x-radius
                ry = y-radius
                if (rx * rx + ry * ry > radius * radius - radius and rx * rx + ry * ry < radius * radius + radius):
                    pixels[mid_y+ry][mid_x+rx] = (0, 0, 0)
                # if (rx * rx + ry * ry <= radius * radius):
                #     pixels[mid_y+ry][mid_x+rx] = (0, 0, 0)


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
            comp.global_drill_offsets = (x_zero + comp.x_offset * 2.54 + comp.drill_offsets[0],
                                         y_zero + comp.y_offset * 2.54 + comp.drill_offsets[1])

def create_drill_guide(board, padding, stroke, radius, display):
    pixels = create_outline(board, padding, stroke)
    drills = get_drill_positions(board)
    for br in board.board_rows:
        for comp in br.row:
            drill_mark_px(pixels, radius, padding + comp.global_drill_offsets[0] * ppmm,
                          padding + comp.global_drill_offsets[1] * ppmm)
            drill_outline_px(pixels, int((comp.drill_diameters / 2) * ppmm)-stroke//2, stroke,
                             padding + comp.global_drill_offsets[0] * ppmm,
                             padding + comp.global_drill_offsets[1] * ppmm)
            # drill_outline_px(pixels, int((comp.drill_diameters / 2) * ppmm)+1,
            #                  padding + comp.global_drill_offsets[0] * ppmm,
            #                  padding + comp.global_drill_offsets[1] * ppmm)

    # convert pixels to numpy array
    return pixels
    # numpy_array = np.array(pixels, dtype=np.uint8)
    #
    # # create image from pix array
    # output_image = Image.fromarray(numpy_array)
    # output_image.save('panel.bmp')
    # output_image.save('panel.pdf', resolution=Board.ppi, title="Eurorack Panel", author="Eurodrill v0.1")
    #
    # if(display):
    #     im = Image.open("panel.bmp")
    #     im.show()