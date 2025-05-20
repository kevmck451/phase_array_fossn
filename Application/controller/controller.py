

from Application.engine.array.AudioStreamSimulator import AudioStreamSimulator
from Application.engine.array.external_play import External_Player
from Application.engine.filters.audio import Audio
from Application.engine.beamform.beamform import Beamform
from Application.engine.filters.processor import Processing
from Application.engine.detectors.pca_calculator import PCA_Calculator
from Application.engine.detectors.detector import Detector
from Application.engine.detectors.heatmap import Heatmap
from Application.engine.calibration_parallel import Calibration_All

from Application.controller.detector_log import Detector_Log
from Application.controller.heatmap_log import Heatmap_Log
from Application.controller.temp_log import Temp_Log
from Application.controller.event_states import Event
from Application.controller.event_states import State

from Application.gui.human_op_mode import Human_Op_Mode_Window


from datetime import datetime
from threading import Thread
from pathlib import Path
import numpy as np
import filecmp
import shutil
import queue
import time
import os


class Controller:
    def __init__(self, array_config, app_device):
        self.app_device = app_device
        self.app_state = State.IDLE

        self.array_config = array_config
        self.gui = None
        self.temp_sensor = None
        self.mic_array = None
        self.update_peripheral_thread = Thread(target=self.update_peripheral_states, daemon=True)
        self.mic_array_simulator = None
        self.audio_streamer = None
        self.audio_loaded = False
        self.audio_stream_running = False
        self.chunk_size_seconds = 1
        self.realtime = True
        self.calibrate_timer_iterator = 0

        self.calibration_time = 60
        self.calibrate_start_time = 0
        self.use_external_calibration = False

        self.thetas = self.array_config.default_theta_directions
        self.phis = [0]  # azimuth angle: neg is below and pos is above
        self.temperature = 90
        self.beam_mix_selection = self.array_config.beam_mix_1
        self.beamformer = Beamform(self.thetas, self.phis, self.temperature, self.array_config, self.beam_mix_selection)
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
        self.calibration_baselines_all = None

        self.heatmap = Heatmap()

        self.bar_chart_updater_thread = None
        self.bar_chart_updater_running = False

        self.external_player = None
        self.use_external_audio = False
        self.stream_location = None
        self.stream_stereo_mono = None
        self.stream_channels = None

        self.data_logger = None
        self.heatmap_logger = None
        self.temp_logger = None

        self.queue_check_time = 0.01

        self.color_pink = (255, 0, 150)
        self.color_light_blue = (0, 150, 255)

        self.last_time_stamp = None
        self.last_anomaly_locations = []

        self.project_directory_base_path = None
        self.calibration_filepath = None
        self.audio_filepath = None
        self.anom_filepath = None
        self.temp_filepath = None
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
                # self.gui.Top_Frame.Left_Frame.fpga_connection = self.temp_sensor.connected
                self.gui.Top_Frame.Left_Frame.current_temp = '-'

            if self.temp_sensor.connected and not self.temp_sensor.temp_sensor_connected:
                self.gui.Top_Frame.Right_Frame.insert_text(f'Pi Connected but Temp Sensor is Not', 'red')
                self.gui.Top_Frame.Left_Frame.current_temp = '-'

            if not self.audio_loaded:
                if self.app_state == State.RUNNING:
                    if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
                        if not self.temp_sensor.connected or not self.mic_array.audio_receiver.connected:
                            self.mic_array.record_running = False
                            self.gui.Top_Frame.Right_Frame.insert_text(f'Network Disconnected', 'red')
                            self.handle_event(Event.STOP_RECORDER)


            time.sleep(0.5)

    def setup_project_directory(self):
        if self.app_device == 'mac':
            self.project_directory_base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Field_Tests'
        elif self.app_device == 'pi':
            self.project_directory_base_path = '/home/pi/Field_Tests'
        else: self.project_directory_base_path = './Field_Tests'

        current_datetime = datetime.now().strftime('%-m-%d-%y %-I.%M%p').lower()
        self.project_directory_path = os.path.join(self.project_directory_base_path,
                                                   f'{current_datetime} {self.array_config.directory_name}')
        os.makedirs(self.project_directory_path, exist_ok=True)

    def create_directory(self, option):
        current_time = datetime.now().strftime('%-I.%M%p').lower()

        project_name = self.gui.Top_Frame.Center_Frame.project_name.get()
        if project_name != '':
            print(f'Project Name: {project_name}')
            self.project_directory_path = os.path.join(self.project_directory_path, project_name)
            os.makedirs(self.project_directory_path, exist_ok=True)

        if option == 'cal':
            self.calibration_filepath = f'{self.project_directory_path}/Calibration_'
            filepath = self.calibration_filepath + current_time
            self.calibration_filepath = filepath
            os.makedirs(filepath, exist_ok=True)
        elif option == 'audio':
            self.audio_filepath = f'{self.project_directory_path}/Audio_'
            filepath = self.audio_filepath + current_time
            self.audio_filepath = filepath
            os.makedirs(filepath, exist_ok=True)
        elif option == 'anomaly':
            self.anom_filepath = f'{self.project_directory_path}/Anomaly_'
            filepath = self.anom_filepath + current_time
            self.anom_filepath = filepath
            os.makedirs(filepath, exist_ok=True)
            self.data_logger = Detector_Log(self.anom_filepath, self.thetas)
            self.heatmap_logger = Heatmap_Log(self.anom_filepath)
        elif option == 'temp':
            self.temp_filepath = f'{self.project_directory_path}/Temp_'
            filepath = self.temp_filepath + current_time
            self.temp_filepath = filepath
            os.makedirs(filepath, exist_ok=True)
            self.temp_logger = Temp_Log(self.temp_filepath)


    # ---------------------------------
    # AUDIO COLLECTION ----------------
    # ---------------------------------
    def audio_setup(self):
        if self.audio_loaded:
            self.audio_streamer = self.mic_array_simulator
            self.mic_array_simulator.realtime = self.realtime
            self.mic_array_simulator.stop_flag = False
            if self.gui.Top_Frame.Center_Frame.pca_save_checkbox_variable.get():
                if self.app_state == State.CALIBRATING:
                    self.mic_array_simulator.record_audio = True
                    self.create_directory('cal')
                    self.mic_array_simulator.save_path = self.calibration_filepath

            self.mic_array_simulator.start_stream()

            if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
                if self.app_state == State.RUNNING:
                    self.create_directory('anomaly')

        else:
            self.audio_streamer = self.mic_array
            if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
                self.mic_array.record_audio = True
                if self.app_state == State.CALIBRATING:
                    self.create_directory('cal')
                    self.mic_array.start_recording(self.calibration_filepath)
                elif self.app_state == State.RUNNING:
                    self.create_directory('anomaly')
                    self.create_directory('audio')
                    self.create_directory('temp')
                    self.mic_array.start_recording(self.audio_filepath)
            else:
                self.mic_array.record_audio = False
                self.mic_array.start_recording(None)

    def audio_simulation(self, filepath):
        import soundfile as sf
        info = sf.info(str(filepath))
        if info.channels != self.array_config.num_mics:
            self.gui.Top_Frame.Right_Frame.insert_text(f'File Contains {info.channels} chs and App is for {self.array_config.num_mics}', self.color_pink)
            self.gui.Top_Frame.Right_Frame.insert_text(f'Is this a mistake?', self.color_pink)
        audio = Audio(filepath=filepath, num_channels=self.array_config.num_mics)
        self.mic_array_simulator = AudioStreamSimulator(audio, self.chunk_size_seconds)

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
        self.beamforming_thread = Thread(target=self.beamform_start, daemon=True)
        self.beamforming_thread.start()

    def beamform_start(self):
        while self.beamform_running:
            if not self.audio_streamer.queue.empty():
                # print('BEAMFORMING------------------')
                current_audio_data = self.audio_streamer.queue.get()
                # print(f'Audio Data Size: {current_audio_data.shape}')
                self.beamformer.beamform_data(current_audio_data)

            if self.realtime:
                time.sleep(self.queue_check_time)

    # ---------------------------------
    # PROCESSING ----------------------
    # ---------------------------------
    def processor_setup(self):
        self.processor.queue = queue.Queue()
        self.processor_running = True
        self.processor_thread = Thread(target=self.processor_start, daemon=True)
        self.processor_thread.start()

    def processor_start(self):
        while self.processor_running:
            if not self.beamformer.queue.empty():
                # print('PROCESSING------------------')
                current_data = self.beamformer.queue.get()
                # print(f'Beamform Data Size: {current_data.shape}')
                self.processor.process_data(current_data)

            if self.realtime:
                time.sleep(self.queue_check_time)

    # ---------------------------------
    # PCA CALCULATOR ------------------
    # ---------------------------------
    def pca_calculation_setup(self):
        self.pca_calculator.queue = queue.Queue()
        self.pca_calculator_running = True
        self.pca_calculator_thread = Thread(target=self.pca_calculation_start, daemon=True)
        self.pca_calculator_thread.start()

    def pca_calculation_start(self):
        while self.pca_calculator_running:
            if not self.processor.queue.empty():
                # print('PCA CALCULATING ----------')
                current_data = self.processor.queue.get()
                # print(f'Processor Data Size: {current_data.shape}')
                self.pca_calculator.process_chunk(current_data)

            if self.realtime:
                time.sleep(self.queue_check_time)

    # ---------------------------------
    # DETECTOR  -----------------------
    # ---------------------------------
    def detector_setup(self):
        self.detector.queue = queue.Queue()
        self.detector_running = True
        self.detector_thread = Thread(target=self.detector_start, daemon=True)
        self.detector_thread.start()

    def detector_start(self):
        while self.detector_running:
            if not self.pca_calculator.queue.empty():
                # print('DETECTING----------')
                current_data = self.pca_calculator.queue.get()
                # print(f'PCA Data Size: {current_data.shape}')
                self.detector.detect_anomalies(current_data)
                # self.detector.detect_anomalies_simulation(current_data)

            if self.realtime:
                time.sleep(self.queue_check_time)

    # ---------------------------------
    # GUI BAR CHART UPDATER -----------
    # ---------------------------------
    def bar_chart_updater_setup(self):
        self.bar_chart_updater_running = True
        self.bar_chart_updater_thread = Thread(target=self.bar_chart_updater_start, daemon=True)
        self.bar_chart_updater_thread.start()
        if self.realtime:
            self.gui.Middle_Frame.Center_Frame.start_updates()

    def bar_chart_updater_start(self):
        while self.bar_chart_updater_running:
            if not self.detector.queue.empty():
                # print('GUI BAR CHART UPDATING----------')

                current_anomaly_data = self.detector.queue.get()
                self.heatmap.update(self.thetas, current_anomaly_data)
                cmap = self.gui.Bottom_Frame.Middle_Center_Frame.visual_selector.get()
                vert_max = self.gui.Bottom_Frame.Middle_Center_Frame.value_slider.get()
                image = self.heatmap.render_heatmap_image(cmap, vert_max)

                if self.realtime:
                    # give anomaly data to bar chart
                    self.gui.Middle_Frame.Center_Frame.anomaly_data = current_anomaly_data
                    # give anomaly data to heatmap

                    self.gui.Middle_Frame.Center_Frame.next_heatmap_image = image

                # save data if box checked
                if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
                    self.data_logger.log_data(current_anomaly_data)

                    if self.heatmap_logger and self.heatmap.should_log:
                        self.heatmap_logger.save_heatmap_image(image, "rolling")
                        self.heatmap.should_log = False

                    if not self.audio_loaded:
                        self.temp_logger.log_data(self.temp_sensor.current_temp)


            if not self.realtime and self.app_state is State.CALIBRATING:
                self.calibrate_timer_iterator += 1

            if self.realtime:
                # check if sim audio is finished
                if self.audio_loaded:
                    if not self.mic_array_simulator.running:
                        self.handle_event(Event.STOP_RECORDER)

                time.sleep(self.chunk_size_seconds/2)

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
        self.external_audio()

    def stop_all_queues(self):
        if self.audio_loaded:
            self.mic_array_simulator.stop_flag = True
            if self.gui.Top_Frame.Center_Frame.save_checkbox_audio.get():
                if self.app_state == State.CALIBRATING:
                    self.mic_array_simulator.save_audio()
        if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
            self.mic_array.record_running = False
        self.beamform_running = False
        self.processor_running = False
        self.pca_calculator_running = False
        self.detector_running = False
        self.bar_chart_updater_running = False
        self.gui.Middle_Frame.Center_Frame.stop_updates()

    def calibrate_timer(self):

        if self.realtime:
            current_time = time.time()
            while (current_time - self.calibrate_start_time) < self.calibration_time:
                # print(self.detector.baseline_means)
                # print(self.detector.baseline_calculated)
                time.sleep(0.1)
                current_time = time.time()
            if self.app_state == State.CALIBRATING:
                self.handle_event(Event.STOP_PCA_CALIBRATION)
        else:
            while self.calibrate_timer_iterator < self.calibration_time:
                time.sleep(0.001)

            self.handle_event(Event.STOP_PCA_CALIBRATION)
            self.calibrate_timer_iterator = 0

    def wait_for_start(self):
        if self.realtime:
            while self.app_state != State.IDLE:
                time.sleep(0.1)
            self.handle_event(Event.START_RECORDER)
        else:
            while self.app_state != State.CALIBRATING:
                time.sleep(0.001)
            self.handle_event(Event.START_RECORDER)

    def remove_directory_if_empty(self):
        if os.path.exists(self.project_directory_path):
            for subdir in os.listdir(self.project_directory_path):
                full_subdir_path = os.path.join(self.project_directory_path, subdir)
                if os.path.isdir(full_subdir_path):
                    if not os.listdir(full_subdir_path):
                        os.rmdir(full_subdir_path)

            if not os.listdir(self.project_directory_path):
                os.rmdir(self.project_directory_path)

    def external_audio(self):
        if self.use_external_audio:
            self.audio_streamer.send_to_external_audio_stream = True
            self.beamformer.send_to_external_audio_stream = True
            self.processor.send_to_external_audio_stream = True
            self.external_player = External_Player(self.audio_streamer, self.beamformer, self.processor, self.array_config)
            self.external_player.stream_location = self.gui.Top_Frame.Center_Right_Frame.stream_location.get()
            self.stream_channels = self.gui.Top_Frame.Center_Right_Frame.mic_selector.get()
            self.external_player.start()

    def calibration_baseline_loader(self):
        mix_key = (
            self.beam_mix_selection.name
            if self.beam_mix_selection.name in self.calibration_baselines_all
            else "Mix 1")

        mix_data = self.calibration_baselines_all[mix_key]
        means = mix_data["means"]
        stds = mix_data["stds"]
        thetas_1 = list(range(-90, 91, 2))
        thetas_2 = list(range(-90, 91, 5))
        orig_thetas = sorted(set(thetas_1 + thetas_2))

        # Create mapping from angle to row index
        theta_to_idx = {theta: i for i, theta in enumerate(orig_thetas)}

        # Extract only the rows that match thetas in self.thetas
        indices = [theta_to_idx[theta] for theta in self.thetas]
        self.detector.baseline_means = means[indices]
        self.detector.baseline_stds = stds[indices]

        self.gui.Top_Frame.Right_Frame.insert_text(
            'Baseline calibration loaded successfully', 'green'
        )

    # ---------------------------------
    # EVENT HANDLER -------------------
    # ---------------------------------
    def handle_event(self, event):

        if event == Event.ON_CLOSE:
            if self.gui.Top_Frame.Center_Frame.pca_save_checkbox_variable.get():
                self.mic_array.record_running = False
                self.gui.Top_Frame.Right_Frame.insert_text('Audio File Saved', 'green')
            self.stop_all_queues()
            self.temp_sensor.close_connection()
            self.mic_array.audio_receiver.close_connection()
            self.app_state = State.IDLE

            self.remove_directory_if_empty()

        elif event == Event.LOAD_AUDIO:
            self.audio_loaded = True
            filepath = self.gui.Top_Frame.Center_Frame.selected_audio_file
            self.audio_simulation(filepath)
            self.gui.Top_Frame.Right_Frame.insert_text(f'Audio File Loaded: {Path(filepath).stem}.wav', 'green')

        elif event == Event.LOAD_CALIBRATION:
            self.detector.baseline_calculated = True
            self.use_external_calibration = True
            # check to determine to load the one just run inside project
            # self.create_directory('cal')
            # or that its from a filepath
            # source = the folder you just picked in the GUI
            if self.use_external_calibration:
                src = self.gui.Top_Frame.Center_Frame.selected_pca_folder

                # no guard/return here—assume src is valid
                folder_name = os.path.basename(os.path.normpath(src))

                # build dst under your project base
                dst_root = self.project_directory_path
                os.makedirs(dst_root, exist_ok=True)

                # this is where the entire folder will live
                dst = os.path.join(dst_root, folder_name)
                os.makedirs(dst, exist_ok=True)

                # copy _all_ files from src → dst
                for fname in os.listdir(src):
                    s = os.path.join(src, fname)
                    d = os.path.join(dst, fname)
                    # only overwrite if missing or changed
                    if not os.path.exists(d) or not filecmp.cmp(s, d, shallow=False):
                        shutil.copy2(s, d)

                print(f"Copied calibration folder '{folder_name}' into:\n    {dst}")

            # now load just the .npy files out of that new subfolder
            try:
                baselines = {}
                for fname in os.listdir(dst):
                    if not fname.lower().endswith('.npy'):
                        continue
                    mix = fname.split('_')[0]
                    param = fname.split('_')[-1].split('.')[0]  # 'means' or 'stds'
                    baselines.setdefault(mix, {})[param] = np.load(os.path.join(dst, fname))

                self.calibration_baselines_all = baselines
                # print(self.calibration_baselines_all)
                self.calibration_baseline_loader()

            except Exception as e:
                self.gui.Top_Frame.Right_Frame.insert_text(
                    f'Error loading calibration: {e}', 'red'
                )

        elif event == Event.START_RECORDER:
            self.realtime = self.gui.Top_Frame.Center_Right_Frame.real_time_checkbox_variable.get()
            if not self.realtime:
                self.gui.Top_Frame.Right_Frame.insert_text(f'App is analyzing & storing Data. Please Wait', self.color_light_blue)
            self.gui.Top_Frame.Center_Right_Frame.reset_clock()
            entry_val = self.gui.Top_Frame.Center_Frame.chunk_time_entry.get()
            if entry_val.isdigit():
                self.chunk_size_seconds = int(entry_val)
                self.mic_array.chunk_size_sec = self.chunk_size_seconds
                self.mic_array.audio_receiver.chunk_secs = self.chunk_size_seconds

            if not self.mic_array.audio_receiver.running and not self.audio_loaded:
                self.gui.Top_Frame.Right_Frame.insert_text(f'Phased Array not connected and No Audio is Loaded', 'red')
                print('FPGA not connected')
            elif self.app_state != State.IDLE:
                self.gui.Top_Frame.Right_Frame.insert_text('App State must be Idle', self.color_pink)
            else:
                if not self.detector.baseline_calculated:
                    self.handle_event(Event.PCA_CALIBRATION)
                    Thread(target=self.wait_for_start, daemon=True).start()
                else:
                    self.app_state = State.RUNNING
                    self.gui.Top_Frame.Center_Frame.toggle_play()
                    self.start_all_queues()
                    # if self.realtime:
                    self.gui.Top_Frame.Center_Right_Frame.start_recording()

        elif event == Event.STOP_RECORDER:
            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_play()
            if self.gui.Top_Frame.Center_Frame.pca_save_checkbox_variable.get():
                if not self.audio_loaded:
                    self.mic_array.record_running = False
                    self.gui.Top_Frame.Right_Frame.insert_text('Audio File Saved', 'green')
            if self.gui.Top_Frame.Center_Frame.audio_save_checkbox_variable.get():
                cmap = self.gui.Bottom_Frame.Middle_Center_Frame.visual_selector.get()
                vert_max = self.gui.Bottom_Frame.Middle_Center_Frame.value_slider.get()
                final_image = self.heatmap.render_heatmap_image(cmap, vert_max)
                if final_image is not None:
                    self.heatmap_logger.save_heatmap_image(final_image, "final")
            self.stop_all_queues()
            self.gui.Middle_Frame.Center_Frame.stop_updates()
            self.remove_directory_if_empty()
            self.setup_project_directory()
            self.gui.Top_Frame.Center_Right_Frame.stop_recording()

            if not self.realtime:
                self.gui.Top_Frame.Right_Frame.insert_text(f'App is finished analyzing', 'green')

            if self.use_external_audio: self.external_player.stop()

        elif event == Event.PCA_CALIBRATION:
            entry_val = self.gui.Top_Frame.Center_Frame.calibration_time_entry.get()
            if entry_val.isdigit():
                self.calibration_time = int(entry_val)

            if not self.mic_array.audio_receiver.running and not self.audio_loaded:
                self.gui.Top_Frame.Right_Frame.insert_text(f'Array not connected and No Audio is Loaded', 'red')
            else:
                self.app_state = State.CALIBRATING
                self.gui.Top_Frame.Center_Frame.toggle_calibrate()
                self.detector.baseline_calculated = False
                self.gui.Top_Frame.Right_Frame.insert_text('Detector Calibration Started', self.color_light_blue)
                self.gui.Top_Frame.Right_Frame.insert_text(f'Press Stop to End Early: {self.calibration_time}s calibration started', self.color_light_blue)
                self.start_all_queues()
                # i think now, only the streamer needs to be started really.
                # only current config is in memory, if real time settings changed, another config will need to be loaded in to match new shape
                # having the real time calibration is just doing an unnecessary process since it's already being calculated
                # self.audio_setup()
                self.Calibration_Class = Calibration_All(self.audio_streamer, self.temperature, self.array_config, self.calibration_filepath)

                self.calibrate_start_time = time.time()
                Thread(target=self.calibrate_timer, daemon=True).start()
                self.gui.Top_Frame.Center_Right_Frame.start_calibration(self.calibration_time)

        elif event == Event.STOP_PCA_CALIBRATION:
            self.stop_all_queues()
            self.detector.baseline_calculated = True
            # flush all queues
            while not self.audio_streamer.queue.empty():
                self.audio_streamer.queue.get()
            while not self.beamformer.queue.empty():
                self.beamformer.queue.get()
            while not self.processor.queue.empty():
                self.processor.queue.get()
            while not self.pca_calculator.queue.empty():
                self.pca_calculator.queue.get()
            while not self.detector.queue.empty():
                self.detector.queue.get()

            if self.gui.Top_Frame.Center_Frame.pca_save_checkbox_variable.get(): # todo what if not checked, it wont stop
                self.Calibration_Class.stop_everything()
                self.handle_event(Event.LOAD_CALIBRATION)
                self.gui.Top_Frame.Right_Frame.insert_text('Calibration Saved', 'green')

                # if self.audio_loaded:
                #     if self.app_state == State.CALIBRATING:
                #         self.mic_array_simulator.save_audio()
                #         np.save(f'{self.calibration_filepath}/baseline_means.npy', self.detector.baseline_means)
                #         np.save(f'{self.calibration_filepath}/baseline_stds.npy', self.detector.baseline_stds)
                #         print(f'Baseline stats saved in folder: {self.calibration_filepath}')
                #         self.gui.Top_Frame.Right_Frame.insert_text('Calibration Saved', 'green')
                # else:
                #     self.mic_array.record_running = False
                #     np.save(f'{self.calibration_filepath}/baseline_means.npy', self.detector.baseline_means)
                #     np.save(f'{self.calibration_filepath}/baseline_stds.npy', self.detector.baseline_stds)
                #     print(f'Baseline stats saved in folder: {self.calibration_filepath}')
                #     self.gui.Top_Frame.Right_Frame.insert_text('Calibration Saved', 'green')

            self.app_state = State.IDLE
            self.gui.Top_Frame.Center_Frame.toggle_calibrate()
            self.gui.Top_Frame.Right_Frame.insert_text('Detector Calibration Successful', 'green')
            self.calibrate_start_time = 0

            if self.use_external_audio: self.external_player.stop()

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
                # self.gui.Top_Frame.Right_Frame.insert_text(
                #     f'{current_time_stamp}: ANOMALY DETECTED AT {current_anomaly_locations}',
                #     'red'
                # )
                self.last_time_stamp = current_time_stamp
                self.last_anomaly_locations = current_anomaly_locations.copy()

        elif event == Event.UPDATE_BEAM_DIRECTIONS:
            if self.app_state == State.IDLE:
                Ltheta = int(self.gui.Bottom_Frame.Left_Frame.ltheta_entry.get())
                Rtheta = int(self.gui.Bottom_Frame.Left_Frame.rtheta_entry.get())
                increment = int(self.gui.Bottom_Frame.Left_Frame.theta_inc_var.get())
                phi = int(self.gui.Bottom_Frame.Left_Frame.lphi_entry.get())
                theta_list = list(range(Ltheta, Rtheta + 1, increment))

                self.phis = [phi]
                self.beamformer.phis = [phi]
                self.thetas = theta_list
                self.beamformer.thetas = self.thetas
                self.beamformer.update_parameters(self.beam_mix_selection)
                self.processor.processing_chain = self.beam_mix_selection.processing_chain
                self.calibration_baseline_loader()

                self.gui.Middle_Frame.Center_Frame.directions = self.thetas
                self.gui.Middle_Frame.Center_Frame.anomaly_data = [0] * len(self.thetas)
                self.gui.Top_Frame.Right_Frame.insert_text(f'Theta: ({Ltheta}, {Rtheta}, {increment}) | Phi: {phi}', self.color_pink)

        elif event == Event.START_EXTERNAL_PLAY:
            self.use_external_audio = True
            self.gui.Top_Frame.Center_Right_Frame.toggle_play_external_button()
            self.gui.Top_Frame.Right_Frame.insert_text(f'External Player Activated', 'green')

            if self.app_state == State.RUNNING or self.app_state == State.CALIBRATING:
                self.audio_streamer.send_to_external_audio_stream = True
                self.beamformer.send_to_external_audio_stream = True
                self.processor.send_to_external_audio_stream = True
                self.external_player = External_Player(self.audio_streamer, self.beamformer, self.processor, self.array_config)
                self.external_player.stream_location = self.gui.Top_Frame.Center_Right_Frame.stream_location.get()
                self.external_player.start()

        elif event == Event.STOP_EXTERNAL_PLAY:
            self.use_external_audio = False
            self.audio_streamer.send_to_external_audio_stream = False
            self.beamformer.send_to_external_audio_stream = False
            self.processor.send_to_external_audio_stream = False
            self.external_player.stop()
            self.gui.Top_Frame.Center_Right_Frame.toggle_play_external_button()

        elif event == Event.CHANGE_EXTERNAL_PLAYER:
            self.stream_location = self.gui.Top_Frame.Center_Right_Frame.stream_location.get()

            if self.stream_location == 'Raw':
                shape = (self.beam_mix_selection.rows, self.beam_mix_selection.cols)
                labels = [f'{i + 1} ' if i + 1 < 10 else f'{i + 1}' for i in range(shape[0] * shape[1])]
                self.gui.Top_Frame.Center_Right_Frame.mic_selector.rebuild(labels, shape)
            else:
                self.gui.Top_Frame.Center_Right_Frame.mic_selector.rebuild(self.thetas, (1, len(self.thetas)))

            if self.external_player is not None:
                self.external_player.stream_location = self.stream_location
                self.external_player.selected_channels = self.gui.Top_Frame.Center_Right_Frame.mic_selector.get()

        elif event == Event.CHANGE_EXTERNAL_PLAYER_CHANNELS:
            self.stream_channels = self.gui.Top_Frame.Center_Right_Frame.mic_selector.get()

            if self.external_player is not None:
                self.external_player.selected_channels = self.stream_channels

        elif event == Event.START_HUMAN_OP_MODE:
            print('Human Operation Mode')
            self.settings_window = Human_Op_Mode_Window(self.handle_event, self.array_config, self.gui.device_config)
            self.settings_window.mainloop()

        elif event == Event.CHANGE_BEAM_MIXTURE:
            self.gui.Bottom_Frame.Middle_Frame.update_center_freq_label()
            self.beam_mix_selection = self.gui.Bottom_Frame.Middle_Frame.current_beam_mix
            self.beamformer.update_parameters(self.beam_mix_selection)
            self.processor.processing_chain = self.beam_mix_selection.processing_chain
            self.calibration_baseline_loader()

        elif event == Event.DUMMY_BUTTON:
            # dummy button
            print('BUTTON PRESSED')































