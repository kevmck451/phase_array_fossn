from tkinter import PhotoImage
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
import warnings
from tkinter import ttk

import app.View.configuration as configuration
from app.Controller.events import Event
from app.Controller.utilities import time_class



class Main_Window(ctk.CTk):
    def __init__(self, event_handler):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.event_handler = event_handler

        # Computer Icon
        img = Image.open(configuration.main_window_icon)
        icon = ImageTk.PhotoImage(img)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        # Main Setup ------------------------------------------------------------
        self.title(configuration.window_title)

        # Get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (configuration.window_width / 2))
        center_y = int((screen_height / 2) - (configuration.window_height / 2))
        self.geometry(f'{configuration.window_width}x{configuration.window_height}+{center_x}+{center_y}')
        self.minsize(configuration.min_window_width, configuration.min_window_height)

        self.Console_Frame = Console_Frame(self)
        self.Main_Frame = Main_Frame(self, self.Console_Frame, self.event_handler)

        # Grid configuration
        self.columnconfigure(0, weight=1)  # Left column with 2/3 of the space
        self.columnconfigure(1, weight=1)  # Right column with 1/3 of the space

        # Place the frames using grid
        self.Main_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        self.Console_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1

        # Ending Procedures
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Perform any cleanup or process termination steps here
        # For example, safely terminate any running threads, save state, release resources, etc.

        self.event_handler(Event.ON_CLOSE)

        self.destroy()


class Console_Frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.group_number = 0

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)  # Configure the column to expand

        self.console_box(main_frame)

    def console_box(self, frame):

        # Experiment Metadata Info Box (Title)
        self.main_info_label = ctk.CTkLabel(frame, text="Sample Audio Order:", font=configuration.console_font_style)
        self.main_info_label.grid(row=0, column=0, padx=configuration.console_x_pad, pady=configuration.console_y_pad, sticky='ew')

        self.stim_labels = [ctk.CTkLabel(frame, text=f"Stim {i}:", font=configuration.console_font_style) for i in range(1, 21)]
        for i, label in enumerate(self.stim_labels):
            label.grid(row=i + 1, column=0, padx=configuration.console_x_pad, pady=configuration.console_y_pad, sticky='w')

        # Configure the rows to not expand
        for i in range(21):
            frame.grid_rowconfigure(i, weight=0)

    def update_console_box(self, new_data, experiment, **kwargs):
        text_color = kwargs.get('text_color', 'black')
        number = kwargs.get('number', None)
        bg_color = kwargs.get('bg_color', None)

        self.main_info_label.configure(text=f"Sample Audio Order: Experiment {experiment}")
        for i, data in enumerate(new_data):
            if i + 1 == number:
                self.stim_labels[i].configure(text=f"Stim {number}: {str(data).title()} ", text_color=text_color,
                                               bg_color='#B8B9B8')
            elif bg_color is not None:
                self.stim_labels[i].configure(text=f"Stim {i + 1}: {str(data).title()} ", text_color='black',
                                               bg_color=bg_color)
            else:
                self.stim_labels[i].configure(text=f"Stim {i + 1}: {str(data).title()} ", text_color='black')

    def reset_console_box(self):
        self.main_info_label.configure(text="Sample Audio Order:")
        for i, label in enumerate(self.stim_labels):
            label.configure(text=f"Stim {i + 1}:", text_color='black', bg_color='#CFCFCF', image='')



class Main_Frame(ctk.CTkFrame):
    def __init__(self, parent, console_frame, event_handler):
        super().__init__(parent)
        self.console_frame = console_frame
        self.event_handler = event_handler

        self.warmup_button_state = True
        self.start_button_state = 0
        self.pause_button_state = True
        self.previous_group_state = 0
        self.vr_button_state = 0
        self.tdt_button_state = 0

        self.update_timer_id = None
        self.update_stim_num_id = None
        self.update_speaker_proj_id = None
        self.update_speaker_sel_id = None
        self.update_test_displays_id = None
        self.update_console_displays_id = None
        self.vr_hardware_id = None


        self.current_stim_number = ''
        self.current_speaker_projecting_number = ''
        self.current_speaker_selected_number = ''
        self.vr_connection = bool

        self.playing_icon = PhotoImage(file=configuration.playing_icon_filepath)
        self.playing_icon_s = PhotoImage(file=configuration.playing_icon_s_filepath)
        self.start_icon = PhotoImage(file=configuration.start_icon_filepath)
        self.stop_icon = PhotoImage(file=configuration.stop_icon_filepath)
        self.pause_icon = PhotoImage(file=configuration.pause_icon_filepath)
        self.load_icon = PhotoImage(file=configuration.load_icon_filepath)
        self.settings_icon = PhotoImage(file=configuration.settings_icon_filepath)
        self.reset_icon = PhotoImage(file=configuration.reset_icon_filepath)
        warnings.filterwarnings('ignore', category=UserWarning, module='customtkinter.*')

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')

        # Hardware Status & Load Experiment Widgets
        top_left_frame = ctk.CTkFrame(top_frame)
        top_left_frame.grid(row=0, column=0, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')
        top_right_frame = ctk.CTkFrame(top_frame)
        top_right_frame.grid(row=0, column=1, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')

        # Configure the grid of the top_frame
        top_frame.grid_columnconfigure(0, weight=1, uniform='col')  # First column
        top_frame.grid_columnconfigure(1, weight=1, uniform='col')  # Second column
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Middle Frame
        middle_frame = ctk.CTkFrame(self)
        middle_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')

        # Creating and placing sub-frames for each column in the middle_frame
        middle_frame_1 = ctk.CTkFrame(middle_frame)
        middle_frame_1.grid(row=0, column=0, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')
        middle_frame_2 = ctk.CTkFrame(middle_frame)
        middle_frame_2.grid(row=0, column=1, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')

        # Configure the grid of the middle_frame
        middle_frame.grid_columnconfigure(0, weight=1, uniform='col')  # First column
        middle_frame.grid_columnconfigure(1, weight=1, uniform='col')  # Second column
        middle_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Bottom Frame
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')

        # Bottom Frame Left and Right Cells
        bottom_left_frame = ctk.CTkFrame(bottom_frame)
        bottom_left_frame.grid(row=0, column=0, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')
        bottom_right_frame = ctk.CTkFrame(bottom_frame)
        bottom_right_frame.grid(row=0, column=1, padx=configuration.x_pad_1, pady=configuration.y_pad_1, sticky='nsew')

        # Configure the grid of the bottom_frame
        bottom_frame.grid_columnconfigure(0, weight=1, uniform='col')  # Left column
        bottom_frame.grid_columnconfigure(1, weight=1, uniform='col')  # Right column
        bottom_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)  # Top row
        self.grid_rowconfigure(1, weight=1)  # Middle row
        self.grid_rowconfigure(2, weight=1)  # Bottom row
        self.grid_columnconfigure(0, weight=1, uniform='col')  # Single column

        self.hardware_connection_frames(top_left_frame)
        self.select_experiment_frame(top_right_frame)
        self.warmup_frames(middle_frame_1)
        self.start_stop_frames(middle_frame_2)
        self.experiment_metadata_frames_1(bottom_left_frame)
        self.experiment_metadata_frames_2(bottom_right_frame)

    # FRAMES ---------------------------------------------
    def hardware_connection_frames(self, frame):
        # Configure the grid for the frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # TDT Connection Status
        self.tdt_status = ctk.CTkLabel(frame, text=configuration.connection_status_TDT, text_color=configuration.not_connected_color,
                                       font=(configuration.main_font_style, configuration.main_font_size))
        self.tdt_status.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        # TDT Reset Button
        self.TDT_button = ctk.CTkButton(frame, text='Connect',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color, command=lambda: self.event_handler(Event.TDT_CONNECT))
        self.TDT_button.grid(row=0, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        # VR Connection Status
        self.vr_status = ctk.CTkLabel(frame, text=configuration.connection_status_VR, text_color=configuration.not_connected_color,
                                      font=(configuration.main_font_style, configuration.main_font_size))
        self.vr_status.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        # VR Reset Button
        self.VR_button = ctk.CTkButton(frame, text='Connect',
                                             font=(configuration.main_font_style, configuration.main_font_size),
                                             fg_color=configuration.button_fg_color, command=lambda: self.event_handler(Event.VR_CONNECT))
        self.VR_button.grid(row=1, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

    def select_experiment_frame(self, frame):
        # Configure the grid for the frame
        frame.grid_rowconfigure(0, weight=1)  # Row for the dropdown box
        frame.grid_rowconfigure(1, weight=1)  # Row for the load button
        frame.grid_columnconfigure(0, weight=1)  # Single column

        # Dropdown Box
        dropdown_values_exp = ['Select an Experiment'] + [f'Experiment {x}' for x in range(1, 21)]
        self.option_var_exp = tk.StringVar(value=dropdown_values_exp[0])  # Set initial value to the prompt text
        self.dropdown_exp = ctk.CTkOptionMenu(frame, variable=self.option_var_exp, values=dropdown_values_exp,
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.dropdown_fg_color, dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_exp.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')


        # Load Experiment Button
        self.experiment_button = ctk.CTkButton(frame, text='Load Experiment',
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.button_fg_color,
                                               image=self.load_icon, command=lambda: self.event_handler(Event.LOAD_EXPERIMENT))
        self.experiment_button.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

    def warmup_frames(self, frame):
        frame.grid_rowconfigure(0, weight=1)  # Row for the dropdown box
        frame.grid_rowconfigure(1, weight=1)  # Row for the load button
        frame.grid_rowconfigure(2, weight=1)  # Row for the load button
        frame.grid_rowconfigure(3, weight=1)  # Row for the load button
        frame.grid_rowconfigure(4, weight=1)  # Row for the load button
        frame.grid_rowconfigure(5, weight=1)  # Row for the load button
        frame.grid_columnconfigure(0, weight=1)  # Single column

        # Sub Sub Frame of Warm Up ----------------------------------------
        self.warmup_button = ctk.CTkButton(frame, text="Play Warmup",
                                           font=(configuration.main_font_style, configuration.main_font_size),
                                           fg_color=configuration.start_fg_color, hover_color=configuration.start_hover_color,
                                           image=self.start_icon, command=lambda: self.event_handler(Event.START_WARMUP))
        self.warmup_button.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        self.warmup_test_1 = ctk.CTkLabel(frame, text='Test 1', text_color=configuration.warmup_test_color,
                                          font=(configuration.main_font_style, configuration.main_font_size))
        self.warmup_test_1.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.warmup_test_2 = ctk.CTkLabel(frame, text='Test 2', text_color=configuration.warmup_test_color,
                                          font=(configuration.main_font_style, configuration.main_font_size))
        self.warmup_test_2.grid(row=2, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.warmup_test_3 = ctk.CTkLabel(frame, text='Test 3', text_color=configuration.warmup_test_color,
                                          font=(configuration.main_font_style, configuration.main_font_size))
        self.warmup_test_3.grid(row=3, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.warmup_test_4 = ctk.CTkLabel(frame, text='Test 4', text_color=configuration.warmup_test_color,
                                          font=(configuration.main_font_style, configuration.main_font_size))
        self.warmup_test_4.grid(row=4, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.warmup_test_5 = ctk.CTkLabel(frame, text='Test 5', text_color=configuration.warmup_test_color,
                                          font=(configuration.main_font_style, configuration.main_font_size))
        self.warmup_test_5.grid(row=5, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

    def start_stop_frames(self, frame):

        frame.grid_rowconfigure(0, weight=1)  # Row for the load button
        frame.grid_rowconfigure(1, weight=1)  # Row for the load button
        frame.grid_rowconfigure(2, weight=1)  # Row for the load button
        frame.grid_columnconfigure(0, weight=1)  # Single column

        self.start_button = ctk.CTkButton(frame, text='Start Experiment', font=(configuration.main_font_style, configuration.main_font_size),
                                          fg_color=configuration.start_fg_color, hover_color=configuration.start_hover_color,
                                          image=self.start_icon, command=lambda: self.event_handler(Event.START_EXPERIMENT))
        self.start_button.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        self.pause_button = ctk.CTkButton(frame, text='Pause',
                                          font=(configuration.main_font_style, configuration.main_font_size),
                                          fg_color=configuration.button_fg_color,
                                          hover_color=configuration.button_hover_color,
                                          image=self.pause_icon, command=lambda: self.event_handler(Event.PAUSE))
        self.pause_button.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        self.settings_button = ctk.CTkButton(frame, text='Settings', font=(configuration.main_font_style, configuration.main_font_size),
                                        fg_color=configuration.pause_fg_color, hover_color=configuration.pause_hover_color,
                                        image=self.settings_icon, command=lambda: self.event_handler(Event.SETTINGS))
        self.settings_button.grid(row=2, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')


    def experiment_metadata_frames_1(self, frame):

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        self.current_stimulus_label = ctk.CTkLabel(frame, text='Current Simulus #:',font=(configuration.main_font_style, configuration.main_font_size))
        self.current_stimulus_label.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.current_stimulus_display = ctk.CTkLabel(frame, text='None',font=(configuration.main_font_style, configuration.main_font_size))
        self.current_stimulus_display.grid(row=0, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        self.total_time_label = ctk.CTkLabel(frame, text='Total Time:', font=(configuration.main_font_style, configuration.main_font_size))
        self.total_time_label.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.total_time_display = ctk.CTkLabel(frame, text='00:00',font=(configuration.main_font_style, configuration.main_font_size))
        self.total_time_display.grid(row=1, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

    def experiment_metadata_frames_2(self, frame):

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        self.speaker_projected_label = ctk.CTkLabel(frame, text='Speaker Projecting:', font=(configuration.main_font_style, configuration.main_font_size))
        self.speaker_projected_label.grid(row=0, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.speaker_projected_display = ctk.CTkLabel(frame, text='None', font=(configuration.main_font_style, configuration.main_font_size))
        self.speaker_projected_display.grid(row=0, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

        self.selection_made_label = ctk.CTkLabel(frame, text='Speaker Selected:', font=(configuration.main_font_style, configuration.main_font_size))
        self.selection_made_label.grid(row=1, column=0, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')
        self.selection_made_display = ctk.CTkLabel(frame, text='None',font=(configuration.main_font_style, configuration.main_font_size))
        self.selection_made_display.grid(row=1, column=1, padx=configuration.x_pad_2, pady=configuration.y_pad_2, sticky='nsew')

    # POP UP WINDOWS -------------------------------------------
    def manage_loading_audio_popup(self, text, show=False):
        if show:
            self.loading_popup = tk.Toplevel(self)
            self.loading_popup.title("Loading")
            window_width = 400
            window_height = 100
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            center_x = int((screen_width / 2) - (window_width / 2))
            center_y = int((screen_height / 2) - (window_height / 2))
            self.loading_popup.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
            tk.Label(self.loading_popup, text=text, font=("default_font", 16)).pack(
                pady=10)
            # Configure style for a larger progress bar
            style = ttk.Style(self.loading_popup)
            style.theme_use('clam')  # or 'default', 'classic', 'alt', etc.
            style.configure("Larger.Horizontal.TProgressbar",
                            troughcolor='#D3D3D3',
                            bordercolor='#D3D3D3',
                            background='#00008B',  # Dark Blue color
                            lightcolor='#00008B',  # Adjust if needed
                            darkcolor='#00008B',  # Adjust if needed
                            thickness=30)  # Customize thickness

            self.progress = ttk.Progressbar(self.loading_popup, orient="horizontal", length=250, mode="indeterminate",
                                            style="Larger.Horizontal.TProgressbar")
            self.progress.pack(pady=10)
            self.progress.start()

            def on_close():
                # Perform any necessary cleanup
                self.event_handler(Event.STOP_LOADING)
                self.progress.stop()
                self.loading_popup.destroy()

            self.loading_popup.protocol("WM_DELETE_WINDOW", on_close)

        else:
            if self.loading_popup:
                self.progress.stop()
                self.loading_popup.destroy()

    def close_loading_popup(self):
        try:
            self.manage_loading_audio_popup(text='', show=False)
        except:
            pass

    def warning_popup_general(self, message):
        message_popup = tk.Toplevel(self)
        message_popup.title("Message")
        window_width = 400
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        message_popup.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Display the message
        tk.Label(message_popup, text=message, font=("default_font", 16)).pack(pady=20)

        # OK button to close the pop-up
        ok_button = tk.Button(message_popup, text="OK", background="#D3D3D3", padx=10, pady=10,
                              command=message_popup.destroy)
        ok_button.pack(pady=10)

    # BUTTON TOGGLE STATES ------------------------
    def toggle_warmup_button(self):
        if self.warmup_button_state:
            self.warmup_button.configure(text="End Warmup",
                                               fg_color=configuration.stop_fg_color,
                                               hover_color=configuration.stop_hover_color,
                                               image=self.stop_icon,
                                               command=lambda: self.event_handler(Event.END_WARMUP))
            self.warmup_button_state = False
        else:
            self.warmup_button.configure(text="Play Warmup",
                                               fg_color=configuration.start_fg_color,
                                               hover_color=configuration.start_hover_color,
                                               image=self.start_icon,
                                               command=lambda: self.event_handler(Event.START_WARMUP))
            self.warmup_button_state = True

    def toggle_start_button(self):
        if self.start_button_state == 0:
            self.start_button.configure(text="End Experiment",
                                               fg_color=configuration.stop_fg_color,
                                               hover_color=configuration.stop_hover_color,
                                               image=self.stop_icon,
                                               command=lambda: self.event_handler(Event.END_EXPERIMENT))
            self.start_button_state += 1
        elif self.start_button_state == 1:
            self.start_button.configure(text="Reset Experiment",
                                               fg_color=configuration.reset_fg_color,
                                               hover_color=configuration.reset_hover_color,
                                               image=self.reset_icon,
                                               command=lambda: self.event_handler(Event.RESET_EXPERIMENT))
            self.start_button_state += 1

        else:
            self.start_button.configure(text="Start Experiment",
                                        fg_color=configuration.start_fg_color,
                                        hover_color=configuration.start_hover_color,
                                        image=self.start_icon,
                                        command=lambda: self.event_handler(Event.START_EXPERIMENT))
            self.start_button_state = 0

    def toggle_pause_button(self):
        if self.pause_button_state:
            self.pause_button.configure(text="Resume",
                                               fg_color=configuration.start_fg_color,
                                               hover_color=configuration.start_hover_color,
                                               image=self.start_icon,
                                               command=lambda: self.event_handler(Event.RESUME))
            self.pause_button_state = False
        else:
            self.pause_button.configure(text="Pause",
                                               fg_color=configuration.button_fg_color,
                                               hover_color=configuration.button_hover_color,
                                               image=self.pause_icon,
                                               command=lambda: self.event_handler(Event.PAUSE))
            self.pause_button_state = True

    def toggle_vr_button(self):
        if self.vr_button_state == 0:
            self.vr_status.configure(text=configuration.connection_status_VR_C,
                                     text_color=configuration.connected_color)
            self.VR_button.configure(text='Disconnect',
                                     fg_color=configuration.stop_fg_color, hover_color=configuration.stop_hover_color,
                                     command=lambda: self.event_handler(Event.VR_DISCONNECT))
            self.vr_button_state += 1
        else:
            self.vr_status.configure(text=configuration.connection_status_VR,
                                     text_color=configuration.not_connected_color)
            self.VR_button.configure(text='Connect',
                                     fg_color=configuration.button_fg_color, hover_color=configuration.button_hover_color,
                                     command=lambda: self.event_handler(Event.VR_CONNECT))
            self.vr_button_state = 0

    def toggle_tdt_button(self):
        if self.tdt_button_state == 0:
            self.tdt_status.configure(text=configuration.connection_status_TDT_C,
                                     text_color=configuration.connected_color)
            self.TDT_button.configure(text='Disconnect',
                                     fg_color=configuration.stop_fg_color, hover_color=configuration.stop_hover_color,
                                     command=lambda: self.event_handler(Event.TDT_DISCONNECT))
            self.tdt_button_state += 1
        else:
            self.tdt_status.configure(text=configuration.connection_status_TDT,
                                     text_color=configuration.not_connected_color)
            self.TDT_button.configure(text='Connect',
                                     fg_color=configuration.button_fg_color, hover_color=configuration.button_hover_color,
                                     command=lambda: self.event_handler(Event.TDT_CONNECT))
            self.tdt_button_state = 0

    # RESET DISPLAYS ------------------------
    def reset_metadata_displays(self):
        self.current_stimulus_display.configure(text='None')
        self.speaker_projected_display.configure(text='None')
        self.selection_made_display.configure(text='None')
        self.total_time_display.configure(text='00:00')

    def reset_dropdown_box(self):
        self.option_var_exp.set('Select an Experiment')

    # UPDATE METADATA FRAMES ------------------------
    def start_experiment_timer(self):
        self.experiment_total_time_object = time_class('Experiment Total Time')
        self.update_experiment_timer()

    def update_experiment_timer(self):
        time = self.experiment_total_time_object.stats()
        self.total_time_display.configure(text=time)
        self.update_timer_id = self.after(100, self.update_experiment_timer)

    def stop_experiment_timer(self):
        if self.update_timer_id:
            self.after_cancel(self.update_timer_id)
            self.update_timer_id = None

    def update_stim_number(self):
        self.event_handler(Event.STIM_NUMBER)
        stim_num = self.current_stim_number
        self.current_stimulus_display.configure(text=stim_num)
        self.update_stim_num_id = self.after(100, self.update_stim_number)

    def stop_update_stim_number(self):
        if self.update_stim_num_id:
            self.after_cancel(self.update_stim_num_id)
            self.update_stim_num_id = None

    def update_speaker_projecting_number(self):
        self.event_handler(Event.CHANNEL_NUMBER)
        text = self.current_speaker_projecting_number
        self.speaker_projected_display.configure(text=text)
        self.update_speaker_proj_id = self.after(100, self.update_speaker_projecting_number)

    def stop_update_speaker_projecting_number(self):
        if self.update_speaker_proj_id:
            self.after_cancel(self.update_speaker_proj_id)
            self.update_speaker_proj_id = None

    def update_speaker_selected_number(self):
        self.event_handler(Event.CHANNEL_SEL_NUMBER)
        if self.current_speaker_selected_number == 0 or 'hb' in self.current_speaker_selected_number: text = ''
        else: text = self.current_speaker_selected_number
        self.selection_made_display.configure(text=text)
        self.update_speaker_sel_id = self.after(10, self.update_speaker_selected_number)

    def stop_update_speaker_selected_number(self):
        if self.update_speaker_sel_id:
            self.after_cancel(self.update_speaker_sel_id)
            self.update_speaker_sel_id = None

    # WARM UP TEST VIEWS ------------------------
    def reset_warmup_tests(self):
        self.warmup_test_1.configure(text='Test 1', bg_color=configuration.warmup_neutral_bg_color, image='')
        self.warmup_test_2.configure(text='Test 2', bg_color=configuration.warmup_neutral_bg_color, image='')
        self.warmup_test_3.configure(text='Test 3', bg_color=configuration.warmup_neutral_bg_color, image='')
        self.warmup_test_4.configure(text='Test 4', bg_color=configuration.warmup_neutral_bg_color, image='')
        self.warmup_test_5.configure(text='Test 5', bg_color=configuration.warmup_neutral_bg_color, image='')

    def update_warmup_test_displays(self):
        self.event_handler(Event.VR_INPUT)
        # selection = self.something
        # if selection == self.speaker projecting
            # change text color to match

        if self.current_stim_number == '1':
            self.warmup_test_1.configure(text='   Test 1',
                                         bg_color=configuration.warmup_playing_bg_color, image=self.playing_icon, compound='left')
        elif self.current_stim_number == '2':
            self.warmup_test_1.configure(text='Test 1', image='')
            self.warmup_test_2.configure(text='   Test 2',
                                         bg_color=configuration.warmup_playing_bg_color, image=self.playing_icon, compound='left')
        elif self.current_stim_number == '3':
            # self.warmup_test_1.configure(text='Test 1', image='')
            self.warmup_test_2.configure(text='Test 2', image='')
            self.warmup_test_3.configure(text='   Test 3',
                                         bg_color=configuration.warmup_playing_bg_color, image=self.playing_icon, compound='left')
        elif self.current_stim_number == '4':
            # self.warmup_test_1.configure(text='Test 1', image='')
            # self.warmup_test_2.configure(text='Test 2', image='')
            self.warmup_test_3.configure(text='Test 3', image='')
            self.warmup_test_4.configure(text='   Test 4',
                                         bg_color=configuration.warmup_playing_bg_color, image=self.playing_icon, compound='left')
        elif self.current_stim_number == '5':
            # self.warmup_test_1.configure(text='Test 1', image='')
            # self.warmup_test_2.configure(text='Test 2', image='')
            # self.warmup_test_3.configure(text='Test 3', image='')
            self.warmup_test_4.configure(text='Test 4', image='')
            self.warmup_test_5.configure(text='   Test 5',
                                         bg_color=configuration.warmup_playing_bg_color, image=self.playing_icon, compound='left')
        else:
            self.warmup_test_1.configure(bg_color=configuration.warmup_neutral_bg_color, image='')
            self.warmup_test_2.configure(bg_color=configuration.warmup_neutral_bg_color, image='')
            self.warmup_test_3.configure(bg_color=configuration.warmup_neutral_bg_color, image='')
            self.warmup_test_4.configure(bg_color=configuration.warmup_neutral_bg_color, image='')
            self.warmup_test_5.configure(bg_color=configuration.warmup_neutral_bg_color, image='')

        self.update_test_displays_id = self.after(100, self.update_warmup_test_displays)

    def stop_update_warmup_test_displays(self):
            if self.update_test_displays_id:
                self.after_cancel(self.update_test_displays_id)
                self.update_test_displays_id = None

    # EXPERIMENT VIEWS ------------------------
    def update_console_display(self):
        get_group_number = lambda index: (int(index)-1) // 5
        self.console_frame.group_number = get_group_number(self.current_stim_number)
        if self.console_frame.group_number != 21:
            self.console_frame.stim_labels[self.previous_group_state].configure(image='')
            self.console_frame.stim_labels[self.console_frame.group_number].configure(image=self.playing_icon_s, compound='right')

        self.previous_group_state = self.console_frame.group_number
        self.update_console_displays_id = self.after(100, self.update_console_display)

    def stop_update_console_display(self):
        if self.update_console_displays_id:
            self.after_cancel(self.update_console_displays_id)
            self.update_console_displays_id = None

    # VR HARDWARE VIEWS
    def vr_hardware_connection_status(self):
        self.event_handler(Event.VR_CONNECTION)

        if self.vr_connection:
            self.vr_button_state = 1
            self.toggle_vr_button()
        else:
            self.vr_button_state = 0
            self.toggle_vr_button()

        self.vr_hardware_id = self.after(1000, self.vr_hardware_connection_status)

    def stop_vr_hardware_connection_status(self):
        if self.vr_hardware_id:
            self.after_cancel(self.vr_hardware_id)
            self.vr_hardware_id = None

