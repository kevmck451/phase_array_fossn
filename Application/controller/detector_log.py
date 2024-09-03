

from Application.controller.event_states import Event







class Detector_Log:

    def __init__(self, event_handler):
        self.event_handler = event_handler

        # time stamp, direction
        self.detection_log = None



    def alert_detection(self, direction):
        self.event_handler(Event.LOG_DETECTION)