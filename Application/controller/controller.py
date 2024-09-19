

from Mic_Array.Audio_Stream.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio

from Mic_Array.Beamform.beamform_realtime import Beamform
from Mic_Array.Processing.process_realtime import Processing
from Mic_Array.PCA.pca_realtime import PCA_Calculator
from Mic_Array.Detector.detector_realtime import Detector

from Application.controller.detector_log import Detector_Log

from Application.controller.event_states import Event
from Application.controller.event_states import State


from datetime import datetime
from threading import Thread
from pathlib import Path
import numpy as np
import queue
import time
import os


class Controller:
    def __init__(self):
        self.app_state = State.IDLE

        self.gui = None
        self.temp_sensor = None
        self.mic_array = None
        self.update_peripheral_thread = Thread(target=self.update_peripheral_states, daemon=True)
        self.mic_array_simulator = None
        self.audio_streamer = None
        self.audio_loaded = False
        self.audio_stream_running = False

        self.calibration_time = 5
        self.calibrate_start_time = 0
        self.thetas = [-90,-80,-70,-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90]
        self.phis = [0]  # azimuth angle: neg is below and pos is above
        self.temperature = 90
        self.beamformer = Beamform(self.thetas, self.phis, self.temperature)
        self.beamforming_thread = Thread(target=self.beamform_start, daemon=True)
        self.beamform_running = False

        self.processor = Processing()
        self.processor_thread = Thread(target=self.processor_start, daemon=True)
        self.processor_running = False

        self.pca_calculator = PCA_Calculator()
        self.pca_calculator_thread = Thread(target=self.pca_calculation_start, daemon=True)
        self.pca_calculator_running = False

        self.detector = Detector()
        self.detector_thread = Thread(target=self.detector_start, daemon=True)
        self.detector_running = False

        self.bar_chart_updater_thread = Thread(target=self.bar_chart_updater_start, daemon=True)
        self.bar_chart_updater_running = False

        self.data_logger = Detector_Log()

        self.queue_check_time = 0.1

        self.color_pink = (255, 0, 150)
        self.color_light_blue = (0, 150, 255)

        self.last_time_stamp = None
        self.last_anomaly_locations = []

        self.setup_project_directory()

    def add_peripherals(self, temp_sensor, mic_array, gui):
        self.temp_sensor = temp_sensor
        self.mic_array = mic_array
        self.gui = gui

        if self.mic_array.audio_receiver.connected:
            self.gui.Top_Frame.Left_Frame.fpga_connected()

        if self.temp_sensor.connected:
            self.gui.Top_Frame.Left_Frame.rpi_connected()
            self.gui.Top_Frame.Left_Frame.current_temp = self.temp_sensor.current_temp
            self.gui.Top_Frame.Left_Frame.update_current_temp()

        self.update_peripheral_thread.start()

    def update_peripheral_states(self):
        while True:
            self.gui.Top_Frame.Left_Frame.current_temp = self.temp_sensor.current_temp
            self.gui.Top_Frame.Left_Frame.fpga_connection = self.mic_array.audio_receiver.connected
            self.gui.Top_Frame.Left_Frame.temp_connection = self.temp_sensor.connected

            if not self.temp_sensor.connected:
                self.gui.Top_Frame.Left_Frame.fpga_connection = self.temp_sensor.connected
                self.gui.Top_Frame.Left_Frame.current_temp = '-'

            time.sleep(0.5)

    def setup_project_directory(self):
        self.project_directory_base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Field_Tests'
        current_datetime = datetime.now().strftime('%-m-%d-%y %-I.%M%p').lower()
        self.project_directory_path = os.path.join(self.project_directory_base_path, current_datetime)
        os.makedirs(self.project_directory_path, exist_ok=True)

    def project_directory_audio_anomalies(self):
        current_time = datetime.now().strftime('%-I.%M%p').lower()
        self.anom_filepath = f'{self.project_directory_path}/Anomaly_Log_{current_time}'
        self.record_filepath = f'{self.project_directory_path}/Audio_{current_time}'
        os.makedirs(self.anom_filepath, exist_ok=True)
        os.makedirs(self.record_filepath, exist_ok=True)

    # ---------------------------------
    # AUDIO COLLECTION ----------------
    # ---------------------------------
    def audio_setup(self):
        if self.audio_loaded:
            self.audio_streamer = self.mic_array_simulator
            self.mic_array_simulator.start_stream()
        else:
            self.audio_streamer = self.mic_array
            self.project_directory_audio_anomalies()
            self.mic_array.start_recording(self.record_filepath)

    def audio_simulation(self, filepath):
        # base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
        # filename = 'angel_sensitivity'
        # filepath = f'{base_path}/Tests/15_outdoor_testing/{filename}.wav'

        # filename = 'sweep_angel_100m'
        # filename = 'sweep_semi_100m'
        # filename = 'distance_160-50m'
        # filepath = f'{base_path}/Tests/17_outdoor_testing/{filename}.wav'

        # filename = '08-14-2024_03-57-51_chunk_1'
        # filepath = f'{base_path}/Tests/19_outdoor_testing/{filename}.wav'

        audio = Audio(filepath=filepath, num_channels=48)
        chunk_size_seconds = 1
        self.mic_array_simulator = AudioStreamSimulator(audio, chunk_size_seconds)

    # ---------------------------------
    # BEAMFORMING ---------------------
    # ---------------------------------
    def beamform_setup(self):
        if self.temp_sensor.connected:
            # print(f'Current Temp: {self.temp_sensor.current_temp}')
            if self.temp_sensor.current_temp is not None:
                self.temperature = self.temp_sensor.current_temp
                self.beamformer.temperature_current = self.temperature

        else:
            print('Manual Temp Entry')
            self.gui.Top_Frame.Right_Frame.insert_text(f'Using Temp: {self.temperature}', self.color_pink)

        self.beamformer.queue = queue.Queue()
        self.beamform_running = True
        self.beamforming_thread.start()

    def beamform_start(self):
        while self.beamform_running:
            if not self.audio_streamer.queue.empty():
                # print('BEAMFORMING------------------')
                current_audio_data = self.audio_streamer.queue.get()
                # print(f'Audio Data Size: {current_audio_data.shape}')
                self.beamformer.beamform_data(current_audio_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # PROCESSING ----------------------
    # ---------------------------------
    def processor_setup(self):
        self.processor.queue = queue.Queue()
        self.processor_running = True
        self.processor_thread.start()

    def processor_start(self):
        while self.processor_running:
            if not self.beamformer.queue.empty():
                # print('PROCESSING------------------')
                current_data = self.beamformer.queue.get()
                # print(f'Beamform Data Size: {current_data.shape}')
                self.processor.process_data(current_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # PCA CALCULATOR ------------------
    # ---------------------------------
    def pca_calculation_setup(self):
        self.pca_calculator.queue = queue.Queue()
        self.pca_calculator_running = True
        self.pca_calculator_thread.start()

    def pca_calculation_start(self):
        # while (data := self.processor.queue.get()):
        #     self.pca_calculator.process_chunk(data)
        # self.pca_calculator.queue.put(None)
        while self.pca_calculator_running:
            if not self.processor.queue.empty():
                # print('PCA CALCULATING ----------')
                current_data = self.processor.queue.get()
                # print(f'Processor Data Size: {current_data.shape}')
                self.pca_calculator.process_chunk(current_data)
            time.sleep(self.queue_check_time)

    # ---------------------------------
    # DETECTOR  -----------------------
    # ---------------------------------
    def detector_setup(self):
        self.detector.queue = queue.Queue()
        self.detector_running = True
        self.detector_thread.start()

    def detector_start(self):
        while self.detector_running:
            if not self.pca_calculator.queue.empty():
                # print('DETECTING----------')
                current_data = self.pca_calculator.queue.get()
                # print(f'PCA Data Size: {current_data.shape}')
                self.detector.detect_anomalies(current_data)
                # self.detector.detect_anomalies_simulation(current_data)

            time.sleep(self.queue_check_time)

    # ---------------------------------
    # GUI BAR CHART UPDATER -----------
    # ---------------------------------
    def bar_chart_updater_setup(self):
        self.bar_chart_updater_running = True
        self.bar_chart_updater_thread.start()
        self.gui.Middle_Frame.Center_Frame.start_updates()

    def bar_chart_updater_start(self):
        while self.bar_chart_updater_running:
            if not self.detector.queue.empty():
                # print('GUI BAR CHART UPDATING----------')
                self.gui.Middle_Frame.Center_Frame.anomaly_data = self.detector.queue.get()
                self.data_logger.log_data(self.gui.Middle_Frame.Center_Frame.anomaly_data)

            time.sleep(1)


    # ---------------------------------
    # START / STOP QUEUES ------------
    # ---------------------------------
    def start_all_queues(self):
        self.audio_setup()
        self.beamform_setup()
        self.processor_setup()
        self.pca_calculation_setup()
        self.detector_setup()
        self.bar_chart_updater_setup()

    def stop_all_queues(self):
        if self.audio_loaded:
            self.mic_array_simulator.running = False
        self.beamform_running = False
        self.processor_running = False
        self.pca_calculator_running = False
        self.detector_running = False
        self.bar_chart_updater_running = False
        self.gui.Middle_Frame.Center_Frame.stop_updates()

    def calibrate_timer(self):
        current_time = time.time()
        while (current_time - self.calibrate_start_time) < self.calibration_time:
            # print(self.detector.baseline_means)
            # print(self.detector.baseline_calculated)
            time.sleep(0.1)
            current_time = time.time()
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
            self.mic_array.audio_receiver.close_connection()
            self.app_state = State.IDLE

            if os.path.exists(self.project_directory_path):
                for subdir in os.listdir(self.project_directory_path):
                    full_subdir_path = os.path.join(self.project_directory_path, subdir)
                    if os.path.isdir(full_subdir_path):
                        if not os.listdir(full_subdir_path):
                            os.rmdir(full_subdir_path)

                if not os.listdir(self.project_directory_path):
                    os.rmdir(self.project_directory_path)

        elif event == Event.LOAD_AUDIO:
            self.audio_loaded = True
            filepath = self.gui.Top_Frame.Center_Frame.selected_audio_file
            self.audio_simulation(filepath)
            self.gui.Top_Frame.Right_Frame.insert_text(f'Audio File Loaded: {Path(filepath).stem}.wav', 'green')

        elif event == Event.LOAD_CALIBRATION:
            self.detector.baseline_calculated = True
            filepath_mean = self.gui.Top_Frame.Center_Frame.baseline_means_path
            filepath_stds = self.gui.Top_Frame.Center_Frame.baseline_stds_path

            try:
                self.detector.baseline_means = np.load(filepath_mean)
                self.detector.baseline_stds = np.load(filepath_stds)
                self.gui.Top_Frame.Right_Frame.insert_text(f'Baseline calibration loaded successfully', 'green')
            except FileNotFoundError:
                self.gui.Top_Frame.Right_Frame.insert_text(f'Files Not Found. Try Again', 'red')

        elif event == Event.START_RECORDER:
            if not self.mic_array.audio_receiver.running:
                print('FPGA not connected')
            elif self.app_state != State.IDLE:
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
            self.calibrate_start_time = time.time()
            Thread(target=self.calibrate_timer, daemon=True).start()

        elif event == Event.STOP_PCA_CALIBRATION:
            self.stop_all_queues()
            self.detector.baseline_calculated = True
            if self.gui.Top_Frame.Center_Frame.pca_save_checkbox_variable.get():
                current_time = datetime.now().strftime('%-I.%M%p').lower()
                folder_path = f'{self.project_directory_path}/PCA_Cal_{current_time}'
                os.makedirs(folder_path, exist_ok=True)
                np.save(f'{folder_path}/baseline_means.npy', self.detector.baseline_means)
                np.save(f'{folder_path}/baseline_stds.npy', self.detector.baseline_stds)
                print(f'Baseline stats saved in folder: {folder_path}')

            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()
            self.gui.Top_Frame.Right_Frame.insert_text('Detector Calibration Successful', 'green')
            self.app_state = State.IDLE
            self.calibrate_start_time = 0

        elif event == Event.SET_TEMP:
            self.temperature = int(self.gui.Bottom_Frame.Left_Frame.temp_value)
            self.beamformer.temperature_current = self.temperature
            self.gui.Top_Frame.Right_Frame.insert_text(f'Temp Set Successful: {self.temperature}', 'green')

        elif event == Event.SET_MAX_ANOMALY_VALUE:
            self.detector.max_value = int(self.gui.Bottom_Frame.Right_Frame.max_anomaly_value)
            self.gui.Middle_Frame.Center_Frame.max_anomalies = self.detector.max_value
            self.gui.Top_Frame.Right_Frame.insert_text(f'Max Anomaly Value Set Successful: {self.detector.max_value}', 'green')

        elif event == Event.SET_ANOMALY_THRESHOLD_VALUE:
            self.detector.anomaly_threshold = int(self.gui.Bottom_Frame.Right_Frame.anomaly_threshold_value)
            self.gui.Top_Frame.Right_Frame.insert_text(f'Max Anomaly Value Set Successful: {self.detector.anomaly_threshold}', 'green')

        elif event == Event.ANOMALY_DETECTED:
            current_time_stamp = datetime.now().strftime("%I:%M:%S %p")
            current_anomaly_locations = self.gui.Middle_Frame.Center_Frame.anomaly_list
            if current_time_stamp != self.last_time_stamp or current_anomaly_locations != self.last_anomaly_locations:
                self.gui.Top_Frame.Right_Frame.insert_text(
                    f'{current_time_stamp}: ANOMALY DETECTED AT {current_anomaly_locations}',
                    'red'
                )
                self.last_time_stamp = current_time_stamp
                self.last_anomaly_locations = current_anomaly_locations.copy()

        elif event == Event.LOG_DETECTION:
            print('logging detection')
            self.gui.Top_Frame.Right_Frame.insert_text('ALERT!!! SOMETHING HAS BEEN DETECTED at X direction', 'red')

        elif event == Event.DUMMY_BUTTON:
            # dummy button
            print('BUTTON PRESSED')




