
from Application.gui.window_main import Main_Window
from Application.controller.controller import Controller
from Application.controller.detector_log import Detector_Log

from Temp_Sensor.client import Sender_Client
from Recorder.RecordAudio import Audio_Recorder







if __name__ == "__main__":


    temp_sensor = Sender_Client(name='macbook')
    audio_recorder = Audio_Recorder()

    controller = Controller()

    gui = Main_Window(controller.handle_event)
    detector_log = Detector_Log(controller.handle_event)

    controller.add_peripherals(temp_sensor, audio_recorder, gui)

    gui.mainloop()
