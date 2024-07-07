from enum import IntEnum

class State(IntEnum):
    up = 0
    down = 1
    stopped_door_closed = 2
    stopped_door_opened = 3
    stopped_opening_door = 4
    stopped_closing_door = 5