from Component import Component, ComponentType


class BoardRow:
    def __init__(self):
        pass

    def __init__(self, num, component_type, pad_width):
        self.blank_pad = '-'
        self.row = list()
        self.height = 0
        self.pad_width = pad_width
        for i in range(num):
            comp = Component(component_type)
            self.height = max(self.height, comp.height)
            self.row.append(Component(component_type))
        components_pad_width = 0
        comp_count = 0
        for comp in self.row:
            components_pad_width += comp.pad_width
            if comp_count != len(self.row)-1:
                components_pad_width+=comp.padding
            comp_count += 1
        self.x_offset = (self.pad_width - components_pad_width) >> 1

    def is_jack_row(self):
        for component in self.row:
            if component.component_type != ComponentType.PJ398SM:
                return False
        return True

    def set_component_offsets(self):
        lines = list()
        x_offset = self.x_offset
        for component in self.row:
            component.x_offset = x_offset
            component.y_offset = self.y_offset
            x_offset = x_offset + component.pad_width + component.padding

    def set_y_offset(self, y):
        self.y_offset = y

    def __str__(self):
        lines = list()
        for i in range(self.height):
            line_string = list()
            for i in range(self.pad_width):
                line_string.append(self.blank_pad)
            lines.append(line_string)
        x_offset = self.x_offset
        caps = False
        for component in self.row:
            for coords in component.solder_points:
                if(caps):
                    lines[coords[1]][coords[0]+x_offset] = component.marker.upper()
                else:
                    lines[coords[1]][coords[0] + x_offset] = component.marker.lower()
            x_offset = x_offset + component.pad_width + component.padding
            caps = not caps
        output_string = ''
        for i in range(self.height):
            output_string += ''.join(lines[i])
            if (i != self.height-1):
                output_string += '\n'
        return output_string