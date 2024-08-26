
from enum import Enum, auto


# Define the events
class Event(Enum):
    ON_CLOSE = auto()
    SETTINGS = auto()
    START_RECORDER = auto()
    STOP_RECORDER = auto()
    SETTINGS_BUTTON_1 = auto()
    SETTINGS_BUTTON_2 = auto()
    DUMMY_BUTTON = auto()





# Define the states using an enumeration
class State(Enum):
    IDLE = auto()
    SHUTTING_DOWN = auto()
    SETTINGS_OPEN = auto()
    DEMO_IN_PROGRESS = auto()