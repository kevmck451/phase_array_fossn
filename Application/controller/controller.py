
from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio

from Mic_Array.Beamform.beamform_realtime import Beamform
from Mic_Array.Processing.process_realtime import Processing
from Mic_Array.PCA.pca_realtime import PCA_Calculator
from Mic_Array.Detector.detector_realtime import Detector


from Application.controller.event_states import Event
from Application.controller.event_states import State


from threading import Thread
import queue
import time



class Controller:
    def __init__(self):
        self.app_state = State.IDLE

        self.gui = None
        self.temp_sensor = None
        self.audio_recorder = None
        self.thetas = [-90,-80,-70,-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90]
        self.phis = [0]  # azimuth angle: neg is below and pos is above
        self.temperature = 90
        self.beamformer = Beamform(self.thetas, self.phis, self.temperature)
        self.beamforming_thread = None
        self.beamform_running = False

        self.processor = Processing()
        self.processor_thread = None
        self.processor_running = False

        self.pca_calculator = PCA_Calculator()
        self.pca_calculator_thread = None
        self.pca_calculator_running = False

        self.detector = Detector()
        self.detector_thread = None
        self.detector_running = False

        self.bar_chart_updater_thread = None
        self.bar_chart_updater_running = False

        self.queue_check_time = 0.1

        self.color_pink = (255, 0, 150)
        self.color_light_blue = (0, 150, 255)


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
                self.beamformer.temperature_current = self.temperature
        else:
            print('Manual Temp Entry')
            self.gui.Top_Frame.Right_Frame.insert_text(f'Using Temp: {self.temperature}', self.color_pink)

        self.beamformer.queue = queue.Queue()
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
        self.processor.queue = queue.Queue()
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
    # PCA CALCULATOR ------------------
    # ---------------------------------
    def pca_calculation_setup(self):
        self.pca_calculator.queue = queue.Queue()
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
        self.detector.queue = queue.Queue()
        self.detector_running = True
        self.detector_thread = Thread(target=self.detector_start, daemon=True).start()

    def detector_start(self):
        while self.detector_running:
            if not self.pca_calculator.queue.empty():
                # print('DETECTING----------')
                current_data = self.pca_calculator.queue.get()
                # print(f'Current Data Size: {current_data.shape}')
                # self.detector.detect_anomalies(current_data)
                self.detector.detect_anomalies_simulation(current_data)

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
    # START / STOP QUEUES ------------
    # ---------------------------------
    def start_all_queues(self):
        self.sim_stream.start_stream()
        self.beamform_setup()
        self.processor_setup()
        self.pca_calculation_setup()
        self.detector_setup()
        self.bar_chart_updater_setup()

    def stop_all_queues(self):
        self.audio_recorder.record_running = False
        self.beamform_running = False
        self.processor_running = False
        self.pca_calculator_running = False
        self.detector_running = False
        self.bar_chart_updater_running = False
        self.gui.Middle_Frame.Center_Frame.stop_updates()

    def calibrate_timer(self):
        time.sleep(self.detector.baseline_calibration_time)
        if self.app_state == State.CALIBRATING:
            self.handle_event(Event.STOP_PCA_CALIBRATION)

    def wait_for_start(self):
        while self.app_state != State.IDLE:
            time.sleep(0.5)
        self.handle_event(Event.START_RECORDER)

    # ---------------------------------
    # EVENT HANDLER -------------------
    # ---------------------------------
    def handle_event(self, event):

        if event == Event.ON_CLOSE:
            self.stop_all_queues()
            self.temp_sensor.close_connection()
            self.audio_recorder.audio_receiver.close_connection()
            self.app_state = State.IDLE

        elif event == Event.START_RECORDER:
            # if self.audio_recorder.audio_receiver.running is False:
            #     print('FPGA not connected')
            if self.app_state != State.IDLE:
                self.gui.Top_Frame.Right_Frame.insert_text('App State must be Idle', self.color_pink)
            else:
                if not self.detector.baseline_calculated:
                    self.handle_event(Event.PCA_CALIBRATION)
                    Thread(target=self.wait_for_start, daemon=True).start()
                else:
                    self.start_all_queues()
                    self.app_state = State.RUNNING
                    self.gui.Top_Frame.Center_Frame.toggle_play()

        elif event == Event.STOP_RECORDER:
            self.gui.Top_Frame.Center_Frame.toggle_play()
            self.app_state = State.IDLE
            self.stop_all_queues()
            self.gui.Middle_Frame.Center_Frame.stop_updates()

        elif event == Event.PCA_CALIBRATION:
            self.app_state = State.CALIBRATING
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()
            self.detector.baseline_calculated = False
            self.gui.Top_Frame.Right_Frame.insert_text('Detector Calibration Started', self.color_light_blue)
            self.start_all_queues()
            Thread(target=self.calibrate_timer, daemon=True).start()

        elif event == Event.STOP_PCA_CALIBRATION:
            self.stop_all_queues()
            self.detector.baseline_calculated = True
            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()
            self.gui.Top_Frame.Right_Frame.insert_text('Detector Calibration Successful', 'green')
            self.app_state = State.IDLE

        elif event == Event.SET_TEMP:
            self.temperature = int(self.gui.Bottom_Frame.Left_Frame.temp_value)
            if self.app_state == State.RUNNING:
                self.beamformer.temperature_current = self.temperature
            self.gui.Top_Frame.Right_Frame.insert_text(f'Temp Set Successful: {self.temperature}', 'green')

        elif event == Event.SET_MAX_ANOMALY_VALUE:
            self.detector.max_value = int(self.gui.Bottom_Frame.Right_Frame.max_anomaly_value)
            self.gui.Top_Frame.Right_Frame.insert_text(f'Max Anomaly Value Set Successful: {self.detector.max_value}', 'green')

        elif event == Event.LOG_DETECTION:
            print('logging detection')
            self.gui.Top_Frame.Right_Frame.insert_text('ALERT!!! SOMETHING HAS BEEN DETECTED at X direction', 'red')

        elif event == Event.DUMMY_BUTTON:
            print('BUTTON PRESSED')




