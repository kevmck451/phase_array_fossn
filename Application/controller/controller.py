
from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio

from Mic_Array.Beamform.beamform_realtime import Beamform
from Mic_Array.Processing.process_realtime import Processing
from Mic_Array.PCA.pca_realtime import PCA_Calculator
from Mic_Array.Detector.detector_realtime import Detector


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

        self.processor = Processing()
        self.processor_thread = None
        self.processor_running = False

        self.pca_calculator = None
        self.pca_calculator_thread = None
        self.pca_calculator_running = False

        self.detector = None
        self.detector_thread = None
        self.detector_running = False

        self.bar_chart_updater_thread = None
        self.bar_chart_updater_running = False

        self.queue_check_time = 0.1

        base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
        filename = 'cars_drive_by_150m'
        filepath = f'{base_path}/Tests/17_outdoor_testing/{filename}.wav'
        audio = Audio(filepath=filepath, num_channels=48)
        chunk_size_seconds = 1
        self.sim_stream = AudioStreamSimulator(audio, chunk_size_seconds)

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
        self.beamform_running = True
        self.beamforming_thread = Thread(target=self.beamform_start, daemon=True).start()

    def beamform_start(self):
        while self.beamform_running:
            if not self.sim_stream.queue.empty():
                # print('BEAMFORMING------------------')
                current_audio_data = self.sim_stream.queue.get()
                # print(f'Current Data Size: {current_audio_data.shape}')
                self.beamformer.beamform_data(current_audio_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # PROCESSING ----------------------
    # ---------------------------------
    def processor_setup(self):
        self.processor_running = True
        self.processor_thread = Thread(target=self.processor_start, daemon=True).start()

    def processor_start(self):
        while self.processor_running:
            if not self.beamformer.queue.empty():
                # print('PROCESSING------------------')
                current_data = self.beamformer.queue.get()
                # print(f'Current Data Size: {current_data.shape}')
                self.processor.process_data(current_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # PCA CALCULATOR --------------------
    # ---------------------------------
    def pca_calculation_setup(self):
        self.pca_calculator = PCA_Calculator()
        self.pca_calculator_running = True
        self.pca_calculator_thread = Thread(target=self.pca_calculation_start, daemon=True).start()

    def pca_calculation_start(self):
        # while (data := self.processor.queue.get()):
        #     self.pca_calculator.process_chunk(data)
        # self.pca_calculator.queue.put(None)
        while self.pca_calculator_running:
            if not self.processor.queue.empty():
                # print('PCA CALCULATING ----------')
                current_data = self.processor.queue.get()
                # print(f'Current Data Size: {current_data.shape}')
                self.pca_calculator.process_chunk(current_data)
            time.sleep(self.queue_check_time)

    # ---------------------------------
    # DETECTOR  -----------------------
    # ---------------------------------
    def detector_setup(self):
        self.detector = Detector()
        self.detector_running = True
        self.detector_thread = Thread(target=self.detector_start, daemon=True).start()

    def detector_start(self):
        while self.detector_running:
            if not self.pca_calculator.queue.empty():
                # print('DETECTING----------')
                current_data = self.pca_calculator.queue.get()
                # print(f'Current Data Size: {current_data.shape}')
                self.detector.detect_anomalies(current_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # GUI BAR CHART UPDATER -----------
    # ---------------------------------
    def bar_chart_updater_setup(self):
        self.bar_chart_updater_running = True
        self.bar_chart_updater_thread = Thread(target=self.bar_chart_updater_start, daemon=True).start()
        self.gui.Middle_Frame.Center_Frame.start_updates()

    def bar_chart_updater_start(self):
        while self.bar_chart_updater_running:
            if not self.detector.queue.empty():
                # print('GUI BAR CHART UPDATING----------')
                self.gui.Middle_Frame.Center_Frame.anomaly_data = self.detector.queue.get()

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
            self.pca_calculator_running = False
            self.detector_running = False
            self.bar_chart_updater_running = False
            self.gui.Middle_Frame.Center_Frame.stop_updates()
            self.temp_sensor.close_connection()
            self.audio_recorder.audio_receiver.close_connection()
            self.app_state = State.IDLE

        elif event == Event.START_RECORDER:
            # print('START_RECORDER BUTTON PRESSED')
            self.gui.Top_Frame.Center_Frame.toggle_play()
            # if self.audio_recorder.audio_receiver.running is False:
            #     print('FPGA not connected')
            # if self.app_state != State.IDLE:
            #     print('App State must be Idle')
            # else:
            #     self.app_state = State.RUNNING
            #     self.audio_recorder.start_recording()
            #     self.beamform_setup()
            #     self.processor_setup()
            #     self.pca_calculation_setup()

            self.sim_stream.start_stream()
            self.beamform_setup()
            self.processor_setup()
            self.pca_calculation_setup()
            self.detector_setup()
            self.bar_chart_updater_setup()

        elif event == Event.STOP_RECORDER:
            # print('STOP_RECORDER BUTTON PRESSED')
            self.gui.Top_Frame.Center_Frame.toggle_play()
            self.app_state = State.IDLE
            self.audio_recorder.record_running = False
            self.beamform_running = False
            self.processor_running = False
            self.pca_calculator_running = False
            self.detector_running = False
            self.bar_chart_updater_running = False
            self.gui.Middle_Frame.Center_Frame.stop_updates()


        elif event == Event.PCA_CALIBRATION:
            print('Starting PCA Calibration')
            self.app_state = State.CALIBRATING
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()
            self.gui.Top_Frame.Right_Frame.insert_text('ALERT!!! SOMETHING HAS BEEN DETECTED at X direction', 'red')


        elif event == Event.STOP_PCA_CALIBRATION:
            print('Stopping PCA Calibration')
            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()

        elif event == Event.LOG_DETECTION:
            print('logging detection')
            self.gui.Top_Frame.Right_Frame.insert_text('ALERT!!! SOMETHING HAS BEEN DETECTED at X direction', 'red')

        elif event == Event.DUMMY_BUTTON:
            print('BUTTON PRESSED')




