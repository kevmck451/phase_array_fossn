


from app.Model.tdt_hardware.TDT_manager import TDT_Circuit
from app.Model.vr_hardware.VR_manager import VR_Headset_Hardware
from app.Model.data_manager import circuit_data
from app.Controller.experiment_state import Experiment
from app.View.settings import Settings_Window
from app.View.calibration import Calibration_Window
from app.Controller.utilities import CSVFile_Experiment
from app.Controller.utilities import CSVFile_Settings
from app.Controller.utilities import CSVFile_Calibration
from app.Controller.utilities import time_class
from app.Controller.events import Event

from enum import Enum, auto
from threading import Thread
import numpy as np
import time
import threading



class Controller:
    def __init__(self):
        self.app_state = State.IDLE
        self.sample_names_list = list
        self.audio_samples_list = list
        self.channel_list = list
        self.loaded_experiment_name = str
        self.experiment_loaded = False
        self.tdt_hardware = TDT_Circuit()
        self.vr_hardware = VR_Headset_Hardware()
        self.experiment = Experiment()
        self.warmup = Experiment()
        self.stop_flag_raised = False
        self.pause_flag_raised = False
        self.settings_file = CSVFile_Settings()
        self.gain_defaults = CSVFile_Calibration()
        self.audio_loading = False

    def set_gui(self, gui):
        self.gui = gui

    # These are the gate keepers for whether or not to perform the action
    def handle_event(self, event):
        # Connect to TDT Hardware:
        if event == Event.TDT_CONNECT:
            if self.app_state == State.IDLE:
                self.app_state = State.TDT_INITIALIZING
                self.start_tdt_hardware()

        # Disconnect from TDT Hardware
        elif event == Event.TDT_DISCONNECT:
            if self.app_state == State.IDLE:
                self.app_state = State.TDT_INITIALIZING
                self.tdt_hardware.disconnect_hardware()
                self.gui.Main_Frame.toggle_tdt_button()
                self.app_state = State.IDLE

        # Load Experiment: FINISHED
        elif event == Event.LOAD_EXPERIMENT:
            if self.app_state == State.IDLE:
                selected_value = self.gui.Main_Frame.option_var_exp.get()

                if selected_value != 'Select an Experiment':
                    if selected_value == self.loaded_experiment_name:
                        self.gui.Main_Frame.warning_popup_general(message='Experiment already Loaded')
                    else:
                        self.loaded_experiment_name = selected_value
                        self.app_state = State.LOADING_EXPERIMENT
                        self.load_experiment(selected_value)
                else:
                    if selected_value == 'Select an Experiment':
                        self.gui.Main_Frame.warning_popup_general(message='Need to select an Experiment')

        # Start Warmup:
        elif event == Event.START_WARMUP:
            if self.app_state == State.IDLE:
                self.start_warmup()

        # END Warmup:
        elif event == Event.END_WARMUP:
            if self.app_state == State.WARMUP_RUNNING:
                self.stop_flag_raised = True
                # self.end_warmup()
                self.app_state = State.IDLE

        # Start Experiment:
        elif event == Event.START_EXPERIMENT:
            if self.app_state == State.IDLE:
                if self.gui.Main_Frame.option_var_exp.get() == 'Select an Experiment':
                    self.gui.Main_Frame.warning_popup_general(message='Need to select an Experiment')
                elif self.experiment_loaded == False:
                    self.gui.Main_Frame.warning_popup_general(message='No Experiment Loaded')
                elif self.gui.Main_Frame.option_var_exp.get() != self.loaded_experiment_name:
                    self.gui.Main_Frame.warning_popup_general(message='Loaded Experiment doesnt\nmatch Selected Experiment')
                else:
                    self.start_experiment()

        # End Experiment:
        elif event == Event.END_EXPERIMENT:
            if self.app_state == State.EXPERIMENT_RUNNING or \
                    self.app_state == State.EXPERIMENT_PAUSED:
                if self.gui.Main_Frame.pause_button_state == False:
                    self.gui.Main_Frame.toggle_pause_button()
                self.app_state = State.EXPERIMENT_ENDED
                self.stop_flag_raised = True

        # Pause Experiment:
        elif event == Event.PAUSE:
            if self.app_state == State.EXPERIMENT_RUNNING:
                self.gui.Main_Frame.toggle_pause_button()
                self.app_state = State.EXPERIMENT_PAUSED
                self.pause_flag_raised = True

        # Resume Experiment:
        elif event == Event.RESUME:
            if self.app_state == State.EXPERIMENT_PAUSED:
                self.gui.Main_Frame.toggle_pause_button()
                self.app_state = State.EXPERIMENT_RUNNING
                self.pause_flag_raised = False

        # Load from Specific Stimulus Number:
        elif event == Event.SETTINGS:
            if self.app_state == State.EXPERIMENT_PAUSED or \
                    self.app_state == State.IDLE or \
                    self.app_state == State.EXPERIMENT_ENDED:
                init_tbs = self.settings_file.get_setting('time bw samples')
                init_ip = self.settings_file.get_setting('ip address')
                init_port = self.settings_file.get_setting('port')
                self.settings_window = Settings_Window(self.handle_event, [init_tbs, init_ip, init_port])
                self.settings_window.mainloop()

        # Load from Specific Stimulus Number:
        elif event == Event.CALIBRATION:
            if self.app_state == self.app_state == State.IDLE or \
                    self.app_state == State.EXPERIMENT_ENDED:
                init_gain = self.gain_defaults.get_setting('gain')
                init_gain_sub = self.gain_defaults.get_setting('gain sub')
                init_speaker = self.gain_defaults.get_setting('speaker')
                self.calibration_window = Calibration_Window(self.handle_event, [init_gain, init_gain_sub, init_speaker])
                self.calibration_window.mainloop()

        elif event == Event.PLAY_CALIBRATION_SAMPLE:
            task_thread = Thread(target=self.play_calibration_sample, daemon=True)
            task_thread.start()

        # Get Current Stim Number to Display
        elif event == Event.STIM_NUMBER:
            # set gui variable from experiment variable
            if self.app_state == State.WARMUP_RUNNING:
                self.gui.Main_Frame.current_stim_number = self.warmup.current_stim_number
            elif self.app_state == State.EXPERIMENT_RUNNING:
                self.gui.Main_Frame.current_stim_number = self.experiment.current_stim_number

        # Get Current Channel Number to Display
        elif event == Event.CHANNEL_NUMBER:
            # set gui variable from experiment variable
            if self.app_state == State.WARMUP_RUNNING:
                self.gui.Main_Frame.current_speaker_projecting_number = self.warmup.current_speaker_projecting
            elif self.app_state == State.EXPERIMENT_RUNNING:
                self.gui.Main_Frame.current_speaker_projecting_number = self.experiment.current_speaker_projecting

        # Get Current Channel Selected to Display
        elif event == Event.CHANNEL_SEL_NUMBER:
            # set gui variable from experiment variable
            self.gui.Main_Frame.current_speaker_selected_number = self.vr_hardware.selected_speaker

        # Reset Experiment Conditions
        elif event == Event.RESET_EXPERIMENT:
            self.reset_experiment()
            self.app_state = State.IDLE

        # Set Stim Number from Settings
        elif event == Event.SET_STIM_NUMBER:
            value = self.settings_window.Main_Frame.option_var_stim.get()
            value = int(value.split(':')[1].strip())
            self.experiment.current_index = value - 1
            self.experiment.update_current_stim_number(self.experiment.current_index)

        # Set default time between samples value
        elif event == Event.SET_DEFAULT_BW_TIME:
            # get value selected and set default
            value = self.settings_window.Main_Frame.option_var_time_bw_samp.get()
            value = float(value.split(':')[1].strip().split(' ')[0])
            self.settings_file.set_default_setting('time bw samples', value)

        # Set default IP address
        elif event == Event.SET_IP_ADDRESS:
            # get value selected and set default
            value = self.settings_window.Main_Frame.option_var_ip_address.get()
            value = str(value.split(':')[1].strip())
            self.settings_file.set_default_setting('ip address', value)

        # Set default Port address
        elif event == Event.SET_PORT_NUM:
            # get value selected and set default
            value = self.settings_window.Main_Frame.option_var_port.get()
            value = str(value.split(':')[1].strip())
            self.settings_file.set_default_setting('port', value)

        # Get Initial Time before Samples
        elif event == Event.GET_INITIAL_TBS:
            # get default values
            self.settings_window.Main_Frame.initial_value = self.settings_file.get_setting('time bw samples')

        # Connect to VR Hardware:
        elif event == Event.VR_CONNECT:
            if self.app_state == State.IDLE:
                self.app_state = State.VR_INITIALIZING
                self.start_vr_hardware()

        # Disconnect VR Hardware
        elif event == Event.VR_DISCONNECT:
            if self.app_state == State.IDLE:
                self.app_state = State.VR_INITIALIZING
                self.vr_hardware.disconnect_hardware()
                # self.gui.Main_Frame.stop_vr_hardware_connection_status()
                self.gui.Main_Frame.toggle_vr_button()
                self.app_state = State.IDLE

        # Get headset status
        elif event == Event.VR_CONNECTION:
            # event to update connection status
            self.gui.Main_Frame.vr_connection = self.vr_hardware.headset_state

        # Window Closing Actions
        elif event == Event.ON_CLOSE:
            if self.vr_hardware.headset_state:
                self.vr_hardware.disconnect_hardware()
            if self.tdt_hardware.circuit_state:
                self.tdt_hardware.disconnect_hardware()

        # Loading Box was Closed
        elif event == Event.STOP_LOADING:
            if self.app_state == State.TDT_INITIALIZING:
                self.tdt_hardware.initialize = False
            if self.app_state == State.VR_INITIALIZING:
                self.vr_hardware.initialize = False
            if self.app_state == State.LOADING_EXPERIMENT:
                self.audio_loading = False

    # Action Functions ------------------------------
    def start_vr_hardware(self):
        self.gui.Main_Frame.manage_loading_audio_popup(text='Waiting for Connection...', show=True)
        load_thread = Thread(target=self.wait_for_vr_connection, daemon=True)
        load_thread.start()

    def wait_for_vr_connection(self):
        connection_time = time_class('connection_time')
        self.vr_hardware.initialize = True
        load_thread = Thread(target=self.vr_hardware.connect_hardware,
                             args=(self.settings_file.get_setting('ip address'),
                                   self.settings_file.get_setting('port')),
                             daemon=True)
        load_thread.start()
        wait_time = 20
        while self.vr_hardware.headset_state == False:
            if self.vr_hardware.initialize == False:
                break
            if connection_time.reaction_time() > wait_time:
                print(f'connection timed out at {wait_time} secs')
                break

        self.gui.Main_Frame.close_loading_popup()
        if self.vr_hardware.headset_state:
            # self.gui.Main_Frame.vr_hardware_connection_status()
            self.gui.Main_Frame.toggle_vr_button()
        else:
            if self.vr_hardware.initialize:
                self.gui.Main_Frame.warning_popup_general(message='connection could not be made')

        self.vr_hardware.initialize = False
        self.app_state = State.IDLE

    def start_tdt_hardware(self):
        self.gui.Main_Frame.manage_loading_audio_popup(text='Waiting for Connection...', show=True)
        load_thread = Thread(target=self.wait_for_tdt_connection, daemon=True)
        load_thread.start()

    def wait_for_tdt_connection(self):
        connection_time = time_class('connection_time')
        self.tdt_hardware.initialize = True
        load_thread = Thread(target=self.tdt_hardware.connect_hardware, daemon=True)
        load_thread.start()
        wait_time = 40
        while self.tdt_hardware.circuit_state == False:
            if self.tdt_hardware.initialize == False:
                break
            if connection_time.reaction_time() > wait_time:
                print(f'connection timed out at {wait_time} secs')
                break

        self.gui.Main_Frame.close_loading_popup()
        if self.tdt_hardware.circuit_state:
            self.gui.Main_Frame.toggle_tdt_button()
        else:
            if self.tdt_hardware.initialize:
                self.gui.Main_Frame.warning_popup_general(message='connection could not be made')

        self.tdt_hardware.initialize = False
        self.app_state = State.IDLE

    def load_experiment(self, selected_value):
        exp_num = selected_value.split(' ')[1]
        self.sample_names_list = circuit_data.load_audio_names(exp_num)
        self.audio_loading = True
        self.gui.Main_Frame.manage_loading_audio_popup(text="Loading audio samples, please wait...", show=True)
        load_thread = Thread(target=self.load_audio_samples, args=(exp_num,), daemon=True)
        load_thread.start()

    def load_audio_samples(self, experiment_id):
        self.audio_samples_list = circuit_data.load_audio_samples(experiment_id)
        self.channel_list = circuit_data.load_channel_numbers(experiment_id)

        if self.audio_loading:
            self.experiment.set_audio_channel_list(self.audio_samples_list, self.channel_list)
            self.experiment_loaded = True
            self.gui.Console_Frame.update_console_box(self.sample_names_list, experiment=experiment_id)
            self.gui.Main_Frame.close_loading_popup()
            self.app_state = State.IDLE
            self.audio_loading = False

    def start_warmup(self):
        self.app_state = State.WARMUP_RUNNING
        self.gui.Main_Frame.toggle_warmup_button()
        warmup_audio, warmup_channels = circuit_data.load_warmup_data()
        self.warmup.set_audio_channel_list(warmup_audio, warmup_channels)
        self.warmup.experiment_in_progress = False

        self.warmup.current_index = 0
        self.warmup.max_index = 4
        self.vr_hardware.selected_speaker = 0
        self.vr_hardware.num_selections = 0
        self.warmup.update_current_stim_number(self.warmup.current_index)
        # self.vr_hardware.get_vr_input()
        self.gui.Main_Frame.update_stim_number()
        self.gui.Main_Frame.update_speaker_projecting_number()
        self.gui.Main_Frame.update_speaker_selected_number()
        self.gui.Main_Frame.update_warmup_test_displays()

        task_thread = Thread(target=self.perform_warmup_round, daemon=True)
        task_thread.start()

    def perform_warmup_round(self):
        while self.warmup.current_index <= self.warmup.max_index:
            if self.warmup.experiment_in_progress == False:
                self.warmup.experiment_in_progress = True

                audio_sample = self.warmup.audio_sample_list[self.warmup.current_index]
                channel_num = self.warmup.channel_list[self.warmup.current_index]
                self.warmup.current_speaker_projecting = channel_num

                stop_event = threading.Event()

                if self.tdt_hardware.circuit_state == False:
                    audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample_computer,
                                          args=(audio_sample, float(self.settings_file.get_setting('time bw samples'))),
                                          daemon=True)

                else:
                    audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample,
                                          args=(audio_sample, channel_num, float(self.settings_file.get_setting('time bw samples'))),
                                          daemon=True)

                if self.vr_hardware.headset_state:
                    vr_thread = Thread(target=self.vr_hardware.update_vr_input_values, args=(stop_event,), daemon=True)
                else:
                    vr_thread = Thread(target=self.vr_hardware.update_vr_input_values_NC, args=(stop_event,), daemon=True)

                audio_thread.start()
                vr_thread.start()

                audio_thread.join()
                stop_event.set()
                vr_thread.join()

                self.vr_hardware.selected_speaker = 0

                # time.sleep(self.settings_file.get_setting('time bw samples'))
                self.warmup.current_index += 1
                if self.warmup.current_index < 6:
                    self.warmup.update_current_stim_number(self.warmup.current_index)
                self.warmup.experiment_in_progress = False
            if self.stop_flag_raised: break

        self.end_warmup()

    def end_warmup(self):
        self.warmup.current_index = ''
        self.warmup.current_speaker_projecting = ''
        self.warmup.current_speaker_selected = ''
        self.gui.Main_Frame.stop_update_stim_number()
        self.gui.Main_Frame.stop_update_speaker_projecting_number()
        self.gui.Main_Frame.stop_update_speaker_selected_number()
        self.gui.Main_Frame.stop_update_warmup_test_displays()
        self.gui.Main_Frame.reset_warmup_tests()
        self.gui.Main_Frame.toggle_warmup_button()
        self.stop_flag_raised = False
        self.gui.Main_Frame.reset_metadata_displays()
        self.app_state = State.IDLE

    def start_experiment(self):
        self.app_state = State.EXPERIMENT_RUNNING
        self.gui.Main_Frame.toggle_start_button()
        selected_value = self.gui.Main_Frame.option_var_exp.get().split(' ')[1]
        self.output_file = CSVFile_Experiment(selected_value)
        self.warmup.set_audio_channel_list(self.audio_samples_list, self.channel_list)
        self.experiment.experiment_in_progress = False
        self.experiment.max_index = 99
        self.vr_hardware.selected_speaker = 0
        self.vr_hardware.num_selections = 0
        self.experiment.update_current_stim_number(self.experiment.current_index)
        self.gui.Main_Frame.start_experiment_timer()
        self.gui.Main_Frame.update_stim_number()
        self.gui.Main_Frame.update_speaker_projecting_number()
        self.gui.Main_Frame.update_speaker_selected_number()
        self.gui.Main_Frame.update_console_display()
        task_thread = Thread(target=self.perform_experiment_rounds, daemon=True)
        task_thread.start()

    def perform_experiment_rounds(self):
        while self.experiment.current_index <= self.experiment.max_index:
            if self.experiment.experiment_in_progress == False:
                reaction_timer = time_class('reaction timer')
                if self.experiment.current_index < 101:
                    self.experiment.update_current_stim_number(self.experiment.current_index)
                self.experiment.experiment_in_progress = True

                audio_sample = self.experiment.audio_sample_list[self.experiment.current_index]
                channel_num = self.experiment.channel_list[self.experiment.current_index]
                self.experiment.current_speaker_projecting = channel_num

                stop_event = threading.Event()

                if self.tdt_hardware.circuit_state == False:
                    audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample_computer,
                                          args=(audio_sample, float(self.settings_file.get_setting('time bw samples'))),
                                          daemon=True)

                else:
                    audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample,
                                          args=(audio_sample, channel_num, float(self.settings_file.get_setting('time bw samples'))),
                                          daemon=True)

                if self.vr_hardware.headset_state:
                    vr_thread = Thread(target=self.vr_hardware.update_vr_input_values,
                                       args=(stop_event, ), kwargs={'reaction_timer': reaction_timer},
                                       daemon=True)
                else:
                    vr_thread = Thread(target=self.vr_hardware.update_vr_input_values_NC,
                                       args=(stop_event, ), kwargs={'reaction_timer': reaction_timer},
                                       daemon=True)

                audio_thread.start()
                vr_thread.start()
                audio_thread.join()
                stop_event.set()
                vr_thread.join()

                # Get VR Response
                speaker_selected = self.vr_hardware.selected_speaker
                reaction_time = self.vr_hardware.time_selection_given
                num_selections = self.vr_hardware.num_selections
                self.output_file.write_row_at(int(self.experiment.current_index),
                                              [self.experiment.current_stim_number, audio_sample.name, channel_num,
                                               speaker_selected,
                                               reaction_time, num_selections])

                self.vr_hardware.selected_speaker = 0
                self.vr_hardware.num_selections = 0
                self.experiment.current_index += 1
                self.experiment.experiment_in_progress = False
            if self.pause_flag_raised:
                self.pause_experiment()
            if self.stop_flag_raised: break

        self.end_experiment()

    def end_experiment(self):
        self.experiment.current_index = 0
        self.app_state = State.EXPERIMENT_ENDED
        self.experiment.current_index = ''
        self.experiment.current_speaker_projecting = ''
        self.experiment.current_speaker_selected = ''
        self.gui.Main_Frame.stop_experiment_timer()
        self.gui.Main_Frame.stop_update_stim_number()
        self.gui.Main_Frame.stop_update_speaker_projecting_number()
        self.gui.Main_Frame.stop_update_speaker_selected_number()
        self.gui.Main_Frame.stop_update_console_display()
        self.gui.Main_Frame.toggle_start_button()
        self.stop_flag_raised = False
        self.pause_flag_raised = False

    def reset_experiment(self):
        self.gui.Main_Frame.toggle_start_button()
        self.gui.Console_Frame.reset_console_box()
        self.gui.Main_Frame.reset_metadata_displays()
        self.gui.Main_Frame.reset_dropdown_box()
        self.experiment_loaded = False
        self.loaded_experiment_name = 'Select an Experiment'
        self.gui.Main_Frame.reset_metadata_displays()

    def pause_experiment(self):
        while self.pause_flag_raised and self.app_state == State.EXPERIMENT_PAUSED:
            time.sleep(0.1)

    def play_calibration_sample(self):
        speaker = int(self.calibration_window.Main_Frame.option_var_speaker.get().split(' ')[1])
        gain = int(self.calibration_window.Main_Frame.option_var_gain.get().split(' ')[1])
        gain_sub = np.round(float(self.calibration_window.Main_Frame.option_var_gain_sub.get()), 2)
        total_gain = gain + gain_sub
        time = int(self.calibration_window.Main_Frame.option_var_times.get().split(' ')[1])
        audio_sample = circuit_data.load_calibration_sample(time)


        # function to play sample with those arguments
        if self.tdt_hardware.circuit_state == False:
            audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample_computer,
                                  args=(audio_sample, None), daemon=True)

        else:
            audio_thread = Thread(target=self.tdt_hardware.trigger_audio_sample,
                                  args=(audio_sample, speaker, None), kwargs={'gain':total_gain},
                                  daemon=True)

        audio_thread.start()


# Define the states using an enumeration
class State(Enum):
    VR_INITIALIZING = auto()
    TDT_INITIALIZING = auto()
    IDLE = auto()
    LOADING_EXPERIMENT = auto()
    WARMUP_RUNNING = auto()
    EXPERIMENT_RUNNING = auto()
    EXPERIMENT_PAUSED = auto()
    EXPERIMENT_ENDED = auto()
    SHUTTING_DOWN = auto()
    SETTINGS_OPEN = auto()





