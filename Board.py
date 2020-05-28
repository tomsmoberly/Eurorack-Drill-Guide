from enum import Enum
from Component import Component
import numpy as np
from PIL import Image
from BoardRow import BoardRow
doepfer_measurements = {1:5.00, 2:9.80, 3:15, 4: 20.00, 6: 30.00, 8: 40.30, 10:50.50, 12:60.60, 14:70.80, 16:80.90,
                        18:91.30, 20:101.30, 21:106.68, 22:111.76, 28:142.24, 42:213.36}

class Board:
    component_colors = [
        None,
        (171, 0, 255),  # p/magenta
        (0, 255, 0),  # g
        (0, 0, 255),  # b
        (255, 0, 0),  # red
        # (255, 128, 0),  # o, orange and yellow blend in too much
        (0, 220, 255)  # t
    ]

    c_board = (255, 240, 194)

    # c_stroke = (0, 0, 0)
    # c_copper = (213, 161, 93)

    c_copper = (193,145,81)
    c_stroke = (0//2 + c_copper[0]//2, 0//2 + c_copper[1]//2, 0//2 + c_copper[2]//2)
    # c_stroke = (0 // 2 + c_copper[0]*3 // 4, 0 // 2 + c_copper[1]*3 // 4, 0 // 2 + c_copper[2]*3 // 4)

    ppi = 300   # pixels per inch
    ppti = ppi//10   # pixels per tenth of an inch, more relevant because pad spacing is 0.1"
    # c_copper = (168, 117, 50)

    # component_type
    def __init__(self):
        self.pad_width = 0
        self.pad_height = 0

    def __init__(self, hp, available_vertical_pads, scrunch):
        self.scrunch = scrunch
        self.hp = hp
        self.doepfer_hp = hp
        while self.doepfer_hp not in doepfer_measurements:
            self.doepfer_hp = self.doepfer_hp + 1
            if (self.doepfer_hp > 100):
                print('Something has gone wrong. Could not find a module width that fit.')
                quit()
        # TODO: am I using the right width??
        self.width = doepfer_measurements[self.doepfer_hp]
        self.pad_width = 2*self.doepfer_hp - 1
        self.pad_height = available_vertical_pads

    def add_components(self, interpreted_input):
        self.board_rows = list()
        for row in interpreted_input:
            self.board_rows.append(BoardRow(row[0], row[1], self.pad_width))
        self.arrange()

    def arrange_vanilla(self):
        self.total_component_heights = 0
        jack_rows = 0
        for br in self.board_rows:
            self.total_component_heights += br.height
        self.empty_rows = self.pad_height - self.total_component_heights
        self.between_pads = self.empty_rows // (len(self.board_rows) - 1)
        self.top_bottom_pads = self.empty_rows - (self.between_pads * (len(self.board_rows) - 1))
        self.top_pads = self.top_bottom_pads >> 1
        self.bottom_pads = self.top_pads
        if (self.top_pads + self.bottom_pads != self.top_bottom_pads):
            self.top_pads += 1
        count = 0
        component_pads = 0
        for br in self.board_rows:
            br.set_y_offset(self.top_pads + component_pads + (count * self.between_pads))
            br.set_component_offsets()
            component_pads += br.height
            count += 1

    def arrange_scrunch(self, jack_rows):
        self.total_component_heights = 0
        for br in self.board_rows:
            self.total_component_heights += br.height
        self.empty_rows = self.pad_height - self.total_component_heights
        self.between_pads = self.empty_rows//(len(self.board_rows)-jack_rows)

        # TODO: put this extra space b/w jacks
        self.top_bottom_pads = self.empty_rows - (self.between_pads*(len(self.board_rows)-jack_rows))
        self.top_pads = self.top_bottom_pads>>1
        self.bottom_pads = self.top_pads
        if(self.top_pads+self.bottom_pads != self.top_bottom_pads):
            self.top_pads+=1
        count = 0
        jack_count = 0
        component_pads = 0
        for br in self.board_rows:
            if (br.is_jack_row()) :
                br.set_y_offset((self.pad_height) - self.bottom_pads - (jack_rows-jack_count)*5)
                br.set_component_offsets()
                jack_count+=1
            else:
                br.set_y_offset(self.top_pads+component_pads+(count*self.between_pads))
                br.set_component_offsets()
                component_pads += br.height
                count+=1

    def arrange(self):
        if(self.scrunch):
            jack_rows = 0
            for br in self.board_rows:
                if br.is_jack_row():
                    jack_rows += 1
            # TODO: only ask for scrunch if 2+ jrows
            if(jack_rows >= 2):
                self.arrange_scrunch(jack_rows)
            else:
                self.arrange_vanilla()
        else:
            self.arrange_vanilla()

        # Finally, track each hole and whether or not it is a solder joint.
        self.joints = [[0 for _ in range(self.pad_width)] for _ in range(self.pad_height)]
        # for i in range(self.pad_width):
        #     blank_row += '-'
        joint_no = 1
        xoff = 0
        yoff = 0
        # print(yoff, 'a')
        for i in range(self.top_pads):
            # output += blank_row + '\n'
            yoff+=1

            # print(yoff, 'b')
        jack_row = False
        for board_row in self.board_rows[:-1]:
            jack_row = board_row.is_jack_row()
            row = str(board_row)
            # print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            # print(row)
            for c in row:
                if(c == '\n'):
                    yoff+=1

                    # print(yoff, 'c')
                    xoff=0
                elif(c == board_row.blank_pad):
                    xoff += 1
                else:
                    if(c.isupper()):
                        self.joints[yoff][xoff] = -joint_no
                    else:
                        self.joints[yoff][xoff] = joint_no
                    xoff+=1
            xoff=0
            yoff+=1

            # print(yoff, 'd')
            if(not jack_row or not self.scrunch):
                for i in range(self.between_pads):
                    yoff+=1

            joint_no += 1
            if joint_no > len(Board.component_colors)-1:
                joint_no = 1
        # output+=str(self.board_rows[-1]) + '\n'
        row = str(self.board_rows[-1])
        # jack_row = self.board_rows[-1].is_jack_row()
        # print('-----------')
        # print(row)
        for c in row:
            if (c == '\n'):
                yoff += 1
                xoff = 0
            elif (c == self.board_rows[-1].blank_pad):
                xoff += 1
            else:
                if (c.isupper()):
                    self.joints[yoff][xoff] = -joint_no
                else:
                    self.joints[yoff][xoff] = joint_no
                xoff += 1
        # yoff += 1
        # xoff = 0
        # for i in range(self.bottom_pads):
        #     output += blank_row

    def print_stats(self):
        print('empty pads =', self.empty_rows)
        print('pads between =', self.between_pads)
        print('remaining for top/bot =', self.top_bottom_pads)
        print('top pads =', self.top_pads)
        print('bottom_pads =', self.bottom_pads)

    def print_rows(self):
        for board_row in self.board_rows:
            print(board_row)

    def mark_px(self, pixels, radius, mid_x, mid_y, color):
        mid_x = int(mid_x)
        mid_y = int(mid_y)
        # print('Mid x/y:', mid_x, mid_y)
        for y in range(radius * 2 + 1):
            for x in range(radius * 2 + 1):
                rx = x - radius
                ry = y - radius
                if (rx * rx + ry * ry <= radius * radius):
                    pixels[mid_y + ry][mid_x + rx] = color

    # def outline_px(self, pixels, radius, mid_x, mid_y, color):
    #     mid_x = int(mid_x)
    #     mid_y = int(mid_y)
    #     for y in range(radius * 2 + 1):
    #         for x in range(radius * 2 + 1):
    #             rx = x - radius
    #             ry = y - radius
    #             if (rx * rx + ry * ry > radius * radius - radius and rx * rx + ry * ry < radius * radius + radius):
    #                 pixels[mid_y + ry][mid_x + rx] = color
    #             # if (rx * rx + ry * ry <= radius * radius):
    #             #     pixels[mid_y+ry][mid_x+rx] = (0, 0, 0)

    def set_pad(self,pixels,x,y,joint_color):
        xoff = x*Board.ppti
        yoff = y*Board.ppti
        if(joint_color):
            c_hole = joint_color
        else:
            c_hole = (255,255,255)
        for i in range(Board.ppti):
            for j in range(Board.ppti // 10):
                pixels[j + yoff][i + xoff] = Board.c_board
        yoff = yoff+(Board.ppti // 10)
        for i in range(Board.ppti):
            pixels[yoff][i + xoff] = Board.c_stroke
        yoff += 1
        for i in range(Board.ppti):
            for j in range((Board.ppti*8//10) - 2):
                pixels[j + yoff][i + xoff] = Board.c_copper
        yoff = yoff + (Board.ppti*8 // 10) - 2
        for i in range(Board.ppti):
            pixels[yoff][i + xoff] = Board.c_stroke
        yoff += 1
        for i in range(Board.ppti):
            for j in range(Board.ppti // 10):
                pixels[j + yoff][i + xoff] = Board.c_board

        self.mark_px(pixels, Board.ppti//4+2, Board.ppti*x+(Board.ppti//2), Board.ppti*y+(Board.ppti//2), Board.c_stroke)

        self.mark_px(pixels, Board.ppti//4+1, Board.ppti*x+(Board.ppti//2), Board.ppti*y+(Board.ppti//2), c_hole)


    def create_pad_image(self, stroke):
        # ppi = 300
        width = self.pad_width*Board.ppti
        height = self.pad_height*Board.ppti
        pixels = [[(255,255,255) for _ in range(width)] for _ in range(height)]
        for i in range(self.pad_width):
            for j in range(self.pad_height):
                joint_no = self.joints[j][i]
                if (joint_no < 0):
                    raw_color = Board.component_colors[-joint_no]
                    color = ((0 + raw_color[0]) // 2, (0 + raw_color[1]) // 2, (0 + raw_color[2]) // 2)
                else:
                    color = Board.component_colors[joint_no]
                self.set_pad(pixels, i, j, color)

        pxh = len(pixels)
        pxw = len(pixels[0])
        sides = []
        for i in range(stroke):
            sides.append((0,0,0))
        for i in range(pxh):
            pixels[i] = sides + pixels[i] + sides
            # for p in range(stroke):
            #     pixels[i].append((0,0,0))
        #
        # new_pixels = []
        stroke_row = []
        top_bot = []
        for i in range(pxw+2*stroke):
            stroke_row.append((0,0,0))
        for i in range(stroke):
            top_bot.append(stroke_row)
        # for i in range
        return top_bot + pixels + top_bot
        # numpy_array = np.array(pixels, dtype=np.uint8)
        #
        # # create image from pix array
        # output_image = Image.fromarray(numpy_array)
        # output_image.save('pads.bmp')
        #
        # if (True):
        #     im = Image.open("pads.bmp")
        #     im.show()

    def __str__(self):

        info = ('Module width = ' + str(self.hp) + 'HP, which is ' + str(doepfer_measurements[self.hp]) + 'mm.\n'
                'The mounting board is ' + str(self.pad_width) + ' pads wide and ' + str(self.pad_height) + ' tall.')
        return info
        output = ''
        blank_row = ''
        for i in range(self.pad_width):
            blank_row += '-'
        for i in range(self.top_pads):
            output += blank_row + '\n'
        for board_row in self.board_rows[:-1]:
            output+= str(board_row) + '\n'
            for i in range(self.between_pads):
                output+=blank_row + '\n'
        output+=str(self.board_rows[-1]) + '\n'
        for i in range(self.bottom_pads):
            output += blank_row
        return info + '\n\n' + output

        # board_string = ''
        # for i in range(self.pad_height):
        #     for j in range(self.pad_width):
        #         board_string = board_string + 'O'
        #     board_string = board_string + '\n'
        # return info + '\n' + board_string