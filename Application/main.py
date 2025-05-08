
from Application.gui.window_main import Main_Window
from Application.controller.controller import Controller
from Application.controller.detector_log import Detector_Log

from Temp_Sensor.client import Sender_Client
from Mic_Array.Audio_Stream.audio_stream_realtime import Mic_Array




# ssh -L 7654:192.168.1.201:2048 admin@192.168.1.1


if __name__ == "__main__":


    temp_sensor = Sender_Client(name='macbook')
    audio_realtime = Mic_Array()

    controller = Controller()

    gui = Main_Window(controller.handle_event)

    controller.add_peripherals(temp_sensor, audio_realtime, gui)

    gui.mainloop()
