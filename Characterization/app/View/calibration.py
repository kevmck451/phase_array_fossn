from tkinter import PhotoImage
import customtkinter as ctk
import tkinter as tk
import numpy as np
import warnings

import app.View.configuration as configuration
from app.Controller.events import Event



# Settings Window
class Calibration_Window(ctk.CTk):
    def __init__(self, event_handler, initial_values):
        super().__init__()
        ctk.set_appearance_mode("light")
        # Computer Icon

        # Main Setup ------------------------------------------------------------
        self.title(configuration.calibration_window_title)

        # Get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (configuration.calibration_window_width / 2))
        center_y = int((screen_height / 2) - (configuration.calibration_window_height / 2) - 250)
        self.geometry(f'{configuration.calibration_window_width}x{configuration.calibration_window_height}+{center_x}+{center_y}')
        self.minsize(configuration.calibration_min_window_width, configuration.calibration_min_window_height)


        self.Main_Frame = Calibration_Frame(self, event_handler, initial_values)
        self.columnconfigure(0, weight=1)  # Left column with 2/3 of the spac
        self.rowconfigure(0, weight=1)  # Left column with 2/3 of the spac
        self.Main_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0

        # Ending Procedures
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Perform any cleanup or process termination steps here
        # For example, safely terminate any running threads, save state, release resources, etc.
        # print("Performing cleanup before exiting...")  # Replace this with actual cleanup code

        # End the application
        self.destroy()


class Calibration_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler, initial_values):
        super().__init__(parent)

        self.event_handler = event_handler
        self.initial_value = initial_values

        self.playing_icon = PhotoImage(file=configuration.playing_icon_filepath)
        self.start_icon = PhotoImage(file=configuration.start_icon_filepath)
        self.stop_icon = PhotoImage(file=configuration.stop_icon_filepath)
        self.pause_icon = PhotoImage(file=configuration.pause_icon_filepath)
        self.load_icon = PhotoImage(file=configuration.load_icon_filepath)
        self.settings_icon = PhotoImage(file=configuration.settings_icon_filepath)
        self.reset_icon = PhotoImage(file=configuration.reset_icon_filepath)
        warnings.filterwarnings('ignore', category=UserWarning, module='customtkinter.*')

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)  # Configure the column to expand
        self.grid_rowconfigure(0, weight=1)  # Configure the column to expand

        self.setting_frames(main_frame)

    def setting_frames(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(4, weight=1)
        frame.grid_columnconfigure(5, weight=1)
        frame.grid_rowconfigure(0, weight=1)



        # ----------------------------------------
        sample_options = ['Pink Noise']
        dropdown_values_sample = [f'{x}' for x in sample_options]
        self.option_var_sample = tk.StringVar(value=dropdown_values_sample[0])  # Set initial value to the prompt text
        self.dropdown_sample = ctk.CTkOptionMenu(frame, variable=self.option_var_sample, values=dropdown_values_sample,
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.dropdown_fg_color,
                                               dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_sample.grid(row=0, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                sticky='nsew')

        # ----------------------------------------
        time_options = [3, 5, 8, 10, 15, 20, 30]
        dropdown_values_times = [f'Time: {x}' for x in time_options]
        self.option_var_times = tk.StringVar(value=dropdown_values_times[2])  # Set initial value to the prompt text
        self.dropdown_times = ctk.CTkOptionMenu(frame, variable=self.option_var_times,
                                                  values=dropdown_values_times,
                                                  font=(configuration.main_font_style, configuration.main_font_size),
                                                  fg_color=configuration.dropdown_fg_color,
                                                  dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_times.grid(row=0, column=1, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # ----------------------------------------
        dropdown_values_speaker = [f'Speaker: {x}' for x in range(1, 10)]
        init_index_speaker = 0
        for i, value in enumerate(dropdown_values_speaker):
            if str(self.initial_value[1]) == str(value):
                init_index_speaker = i
        self.option_var_speaker = tk.StringVar(value=dropdown_values_speaker[init_index_speaker])  # Set initial value to the prompt text
        self.dropdown_speaker = ctk.CTkOptionMenu(frame, variable=self.option_var_speaker,
                                                  values=dropdown_values_speaker,
                                                  font=(configuration.main_font_style, configuration.main_font_size),
                                                  fg_color=configuration.dropdown_fg_color,
                                                  dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_speaker.grid(row=0, column=2, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # ----------------------------------------
        dropdown_values_gain = [f'Gain: {x}' for x in range(1, 21)]
        init_index_gain = 0
        for i, value in enumerate(time_options):
            if str(self.initial_value[1]) == str(value):
                init_index_gain = i
        self.option_var_gain = tk.StringVar(value=dropdown_values_gain[init_index_gain])  # Set initial value to the prompt text
        self.dropdown_gain = ctk.CTkOptionMenu(frame, variable=self.option_var_gain, values=dropdown_values_gain,
                                                  font=(configuration.main_font_style, configuration.main_font_size),
                                                  fg_color=configuration.dropdown_fg_color,
                                                  dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_gain.grid(row=0, column=3, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # ----------------------------------------
        dropdown_values_gain_sub = [f'{np.round(x,2)}' for x in np.arange(0, 1, 0.05)]
        self.option_var_gain_sub = tk.StringVar(value=dropdown_values_gain_sub[0])  # Set initial value to the prompt text
        self.dropdown_gain_sub = ctk.CTkOptionMenu(frame, variable=self.option_var_gain_sub, values=dropdown_values_gain_sub,
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.dropdown_fg_color,
                                               dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_gain_sub.grid(row=0, column=4, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                sticky='nsew')



        # ----------------------------------------
        self.play_pink_noise_button = ctk.CTkButton(frame, text='Play',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.start_fg_color,
                                              hover_color=configuration.start_hover_color,
                                              command=lambda: self.event_handler(Event.PLAY_CALIBRATION_SAMPLE))
        self.play_pink_noise_button.grid(row=0, column=5, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # ----------------------------------------
        self.store_values_button = ctk.CTkButton(frame, text='Save Values',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color,
                                              hover_color=configuration.button_hover_color,
                                              command=lambda: self.event_handler(Event.SET_DEFAULT_BW_TIME))
        self.store_values_button.grid(row=0, column=6, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')



