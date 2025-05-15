
from enum import Enum, auto


# Define the events
class Event(Enum):
    ON_CLOSE = auto()
    UPDATE_BEAM_DIRECTIONS = auto()
    START_RECORDER = auto()
    STOP_RECORDER = auto()
    LOAD_AUDIO = auto()
    PCA_CALIBRATION = auto()
    LOAD_CALIBRATION = auto()
    STOP_PCA_CALIBRATION = auto()
    SET_TEMP = auto()
    SET_MAX_ANOMALY_VALUE = auto()
    ANOMALY_DETECTED = auto()
    SET_ANOMALY_THRESHOLD_VALUE = auto()
    LOG_DETECTION = auto()
    START_EXTERNAL_PLAY = auto()
    STOP_EXTERNAL_PLAY = auto()
    DUMMY_BUTTON = auto()





# Define the states using an enumeration
class State(Enum):
    IDLE = auto()
    SHUTTING_DOWN = auto()
    SETTINGS_OPEN = auto()
    RUNNING = auto()
    CALIBRATING = auto()