from enum import Enum
from Component import Component
from BoardRow import BoardRow
doepfer_measurements = {1:5.00, 2:9.80, 3:15, 4: 20.00, 6: 30.00, 8: 40.30, 10:50.50, 12:60.60, 14:70.80, 16:80.90,
                        18:91.30, 20:101.30, 21:106.68, 22:111.76, 28:142.24, 42:213.36}

class Board:
    # component_type
    def __init__(self):
        self.pad_width = 0
        self.pad_height = 0

    def __init__(self, hp, available_vertical_pads):
        self.hp = hp
        self.doepfer_hp = hp
        while self.doepfer_hp not in doepfer_measurements:
            self.doepfer_hp = self.doepfer_hp + 1
            if (self.doepfer_hp > 100):
                print('Something has gone wrong. Could not find a module width that fit.')
                quit()
        self.width = doepfer_measurements[self.doepfer_hp]
        self.pad_width = 2*self.doepfer_hp - 1
        self.pad_height = available_vertical_pads

    def add_components(self, interpreted_input):
        self.board_rows = list()
        for row in interpreted_input:
            self.board_rows.append(BoardRow(row[0], row[1], self.pad_width))

    def arrange(self):
        self.total_component_heights = 0
        for br in self.board_rows:
            self.total_component_heights += br.height
        self.empty_rows = self.pad_height - self.total_component_heights
        self.between_pads = self.empty_rows//(len(self.board_rows)-1)
        self.top_bottom_pads = self.empty_rows - (self.between_pads*(len(self.board_rows)-1))
        self.top_pads = self.top_bottom_pads>>1
        self.bottom_pads = self.top_pads
        if(self.top_pads+self.bottom_pads != self.top_bottom_pads):
            self.top_pads+=1
        count = 0
        component_pads = 0
        for br in self.board_rows:
            br.set_y_offset(self.top_pads+component_pads+(count*self.between_pads))
            br.set_component_offsets()
            component_pads += br.height
            count+=1

    def print_stats(self):
        print('empty pads =', self.empty_rows)
        print('pads between =', self.between_pads)
        print('remaining for top/bot =', self.top_bottom_pads)
        print('top pads =', self.top_pads)
        print('bottom_pads =', self.bottom_pads)

    def print_rows(self):
        for board_row in self.board_rows:
            print(board_row)


    def __str__(self):
        info = ('Module width = ' + str(self.hp) + 'HP, which is ' + str(doepfer_measurements[self.hp]) + 'mm.\n'
                'The mounting board is ' + str(self.pad_width) + ' pads wide and ' + str(self.pad_height) + ' tall.')
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