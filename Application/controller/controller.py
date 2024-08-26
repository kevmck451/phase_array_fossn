
from Mic_Array.Beamform.beamform_realtime import Beamform
from Mic_Array.Processing.process_realtime import Processing
from Mic_Array.PCA.pca_realtime import PCA_Detection


from Application.gui.settings import Settings_Window
from Application.controller.event_states import Event
from Application.controller.event_states import State


from threading import Thread
import time


class Controller:
    def __init__(self):
        self.app_state = State.IDLE

        self.gui = None
        self.temp_sensor = None
        self.audio_recorder = None

        self.beamformer = None
        self.thetas = [-90,-80,-70,-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90]
        self.phis = [0]  # azimuth angle: neg is below and pos is above
        self.temperature = None
        self.beamforming_thread = None
        self.beamform_running = False

        self.processor = None

        self.pca_detector = None


    def add_peripherals(self, temp_sensor, audio_recorder, gui):
        self.temp_sensor = temp_sensor
        self.audio_recorder = audio_recorder
        self.gui = gui

    # ---------------------------------
    # BEAMFORMING ---------------------
    # ---------------------------------
    def beamform_setup(self):
        if not self.temp_sensor.connected:
            answer = input('Temp Sensor not Connected\nWant to enter temp manually? y or n ')
            if answer == 'n': pass
            else: self.temperature = input('Enter Temp(F): ')
            self.beamformer = Beamform(self.thetas, self.phis, self.temperature)

    def beamform_start(self):
        self.beamforming_thread = Thread(target=self.beamform, daemon=False).start()
        self.beamform_running = True

    def beamform(self):
        while self.beamform_running:
            if not self.audio_recorder.queue.empty():
                print()
                print('BEAMFORMING------------------')
                print(f'Audio Stream Queue Size: {self.audio_recorder.queue.qsize()}')
                current_audio_data = self.audio_recorder.queue.get()
                print(f'Current Data Size: {current_audio_data.shape}')
                # -------------------------
                self.beamformer.beamform_data(current_audio_data)

            time.sleep(0.5)

    # ---------------------------------
    # PROCESSING ----------------------
    # ---------------------------------
    def processor_setup(self):
        self.processor = Processing()

    # ---------------------------------
    # PCA DETECTOR --------------------
    # ---------------------------------
    def pca_detector_setup(self):
        self.processor = PCA_Detection()



    def handle_event(self, event):

        # Load from Specific Stimulus Number:
        if event == Event.SETTINGS:
            self.settings_window = Settings_Window(self.handle_event)
            self.settings_window.mainloop()

        elif event == Event.START_RECORDER:
            print('START_RECORDER BUTTON PRESSED')
            if self.audio_recorder.audio_receiver.running is False:
                print('FPGA not connected')
                pass
            else: self.audio_recorder.start_recording()


        elif event == Event.DUMMY_BUTTON:
            print('BUTTON PRESSED')