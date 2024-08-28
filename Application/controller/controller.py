
from Mic_Array.Beamform.beamform_realtime import Beamform
from Mic_Array.Processing.process_realtime import Processing
from Mic_Array.PCA.pca_realtime import PCA_Detection


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
        self.processing_chain = None
        self.processor_thread = None
        self.processor_running = False

        self.pca_detector = None
        self.pca_detector_thread = None
        self.pca_detector_running = False

        self.queue_check_time = 0.1


    def add_peripherals(self, temp_sensor, audio_recorder, gui):
        self.temp_sensor = temp_sensor
        self.audio_recorder = audio_recorder
        self.gui = gui


    # ---------------------------------
    # BEAMFORMING ---------------------
    # ---------------------------------
    def beamform_setup(self):
        if self.temp_sensor.connected:
            if self.temp_sensor.current_temp is not None:
                self.temperature = self.temp_sensor.current_temp
        else:
            # get manually: pop window with entry
            print('Manual Temp Entry')
            self.temperature = 90

        self.beamformer = Beamform(self.thetas, self.phis, self.temperature)
        self.beamforming_thread = Thread(target=self.beamform_start, daemon=True).start()
        self.beamform_running = True

    def beamform_start(self):
        while self.beamform_running:
            if not self.audio_recorder.queue.empty():
                print()
                print('BEAMFORMING------------------')
                print(f'Audio Stream Queue Size: {self.audio_recorder.queue.qsize()}')
                current_audio_data = self.audio_recorder.queue.get()
                print(f'Current Data Size: {current_audio_data.shape}')
                # -------------------------
                self.beamformer.beamform_data(current_audio_data)

            time.sleep(self.queue_check_time)



    # ---------------------------------
    # PROCESSING ----------------------
    # ---------------------------------
    def processor_setup(self):
        self.processor = Processing()
        self.processing_chain = {'hp': 1000, 'nm': 100, 'ds': 6000}
        self.processor_thread = Thread(target=self.processor_start, daemon=True).start()
        self.processor_running = True

    def processor_start(self):
        while self.processor_running:
            if not self.beamformer.queue.empty():
                print()
                print('PROCESSING------------------')
                print(f'Beamforming Stream Queue Size: {self.audio_recorder.queue.qsize()}')
                current_data = self.audio_recorder.queue.get()
                print(f'Current Data Size: {current_data.shape}')
                # -------------------------
                self.processor.process_data(current_data)

            time.sleep(self.queue_check_time)



    # ---------------------------------
    # PCA DETECTOR --------------------
    # ---------------------------------
    def pca_detector_setup(self):
        self.pca_detector = PCA_Detection()
        self.pca_detector_thread = Thread(target=self.pca_detector_start, daemon=True).start()
        self.pca_detector_running = True

    def pca_detector_start(self):
        while self.pca_detector_running:
            if not self.processor.queue.empty():
                print('PCA DETECTING----------')
                print(f'Audio Stream Queue Size: {self.processor.queue.qsize()}')
                current_data = self.processor.queue.get()
                print(f'Current Data Size: {current_data.shape}')
                # -------------------------
                self.pca_detector.process_chunk(current_data)
                print(f'PCA Queue Size: {self.pca_detector.queue.qsize()}')
                if not self.pca_detector.queue.empty():
                    current_pca_data = self.pca_detector.queue.get()
                    print(f'PCA Data Type: {type(current_pca_data)}')
                    print(f'PCA Data Length: {len(current_pca_data)}')
                    print(f'PCA Data Shape at 0: {current_pca_data.get(0).shape}')
                print()
                print('=' * 40)
                print()
            time.sleep(self.queue_check_time)




    # ---------------------------------
    # EVENT HANDLER -------------------
    # ---------------------------------
    def handle_event(self, event):

        # Load from Specific Stimulus Number:
        if event == Event.ON_CLOSE:
            self.audio_recorder.record_running = False
            self.beamform_running = False
            self.processor_running = False
            self.pca_detector_running = False
            self.temp_sensor.close_connection()
            self.audio_recorder.audio_receiver.close_connection()
            self.app_state = State.IDLE

        elif event == Event.START_RECORDER:
            print('START_RECORDER BUTTON PRESSED')
            if self.audio_recorder.audio_receiver.running is False:
                print('FPGA not connected')
            if self.app_state != State.IDLE:
                print('App State must be Idle')
            else:
                self.app_state = State.RUNNING
                self.audio_recorder.start_recording()
                self.beamform_setup()
                self.processor_setup()
                self.pca_detector_setup()

        elif event == Event.STOP_RECORDER:
            print('STOP_RECORDER BUTTON PRESSED')
            self.app_state = State.IDLE
            self.audio_recorder.record_running = False
            self.beamform_running = False
            self.processor_running = False
            self.pca_detector_running = False


        elif event == Event.PCA_CALIBRATION:
            print('Starting PCA Calibration')
            self.app_state = State.CALIBRATING
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()

        elif event == Event.STOP_PCA_CALIBRATION:
            print('Stopping PCA Calibration')
            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()


        elif event == Event.DUMMY_BUTTON:
            print('BUTTON PRESSED')