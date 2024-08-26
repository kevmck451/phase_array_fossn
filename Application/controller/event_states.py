
from enum import Enum, auto


# Define the events
class Event(Enum):
    ON_CLOSE = auto()
    SETTINGS = auto()
    START_RECORDER = auto()
    STOP_RECORDER = auto()
    DUMMY_BUTTON = auto()





# Define the states using an enumeration
class State(Enum):
    IDLE = auto()
    SHUTTING_DOWN = auto()
    SETTINGS_OPEN = auto()
    RUNNING = auto()