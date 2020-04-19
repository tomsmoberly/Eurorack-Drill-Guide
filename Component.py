from enum import Enum


class ComponentType(Enum):
    PJ398SM = 1
    POT = 2

component_heights = {
    ComponentType.PJ398SM: 5,
    ComponentType.POT: 5
}

component_widths = {
    ComponentType.PJ398SM: 3,
    ComponentType.POT: 5
}

component_padding = {
    ComponentType.PJ398SM: 1,
    ComponentType.POT: 0
}

component_drill_offsets = {
    ComponentType.PJ398SM: (2.54, 4.517),
    ComponentType.POT: (5.08, 3.16)
}

component_solder_points = {
    ComponentType.PJ398SM: ( (1,0), (1,3), (1,4) ),
    ComponentType.POT: ( (1,4), (2,4), (3,4) )
}

# for rough printouts of solder pads
component_markers = {
    ComponentType.PJ398SM: 'T',
    ComponentType.POT: 'P'
}

class Component:
    def __init__(self):
        pass

    def __init__(self, component_type):
        self.component_type = component_type
        self.solder_points = component_solder_points[component_type]
        self.height = component_heights[component_type]
        self.pad_width = component_widths[component_type]
        self.padding = component_padding[component_type]
        self.drill_offsets = component_drill_offsets[component_type]
        self.marker = component_markers[component_type]

