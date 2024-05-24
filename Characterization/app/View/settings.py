from tkinter import PhotoImage
import customtkinter as ctk
import tkinter as tk
import numpy as np
import warnings

import app.View.configuration as configuration
from app.Controller.events import Event



# Settings Window
class Settings_Window(ctk.CTk):
    def __init__(self, event_handler, initial_values):
        super().__init__()
        ctk.set_appearance_mode("light")
        # Computer Icon

        # Main Setup ------------------------------------------------------------
        self.title(configuration.settings_window_title)

        # Get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (configuration.settings_window_width / 2))
        center_y = int((screen_height / 2) - (configuration.settings_window_height / 2))
        self.geometry(f'{configuration.settings_window_width}x{configuration.settings_window_height}+{center_x}+{center_y}')
        self.minsize(configuration.settings_min_window_width, configuration.settings_min_window_height)


        self.Main_Frame = Settings_Frame(self, event_handler, initial_values)
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


class Settings_Frame(ctk.CTkFrame):
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
        frame.grid_rowconfigure(0, weight=1)  # Row for the load button
        frame.grid_rowconfigure(1, weight=1)  # Row for the load button
        frame.grid_rowconfigure(2, weight=1)  # Row for the load button
        frame.grid_rowconfigure(3, weight=1)  # Row for the load button
        frame.grid_rowconfigure(4, weight=1)  # Row for the load button
        frame.grid_rowconfigure(5, weight=1)  # Row for the load button
        frame.grid_rowconfigure(6, weight=1)  # Row for the load button
        frame.grid_rowconfigure(7, weight=1)  # Row for the load button
        frame.grid_rowconfigure(8, weight=1)  # Row for the load button
        frame.grid_columnconfigure(0, weight=1)  # Single column

        # Stimulus Dropdown Box
        dropdown_values_stim = [f'Stimulus Start Number: {x}' for x in range(1, 101)]
        self.option_var_stim = tk.StringVar(value=dropdown_values_stim[0])  # Set initial value to the prompt text
        self.dropdown_stim = ctk.CTkOptionMenu(frame, variable=self.option_var_stim, values=dropdown_values_stim,
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.dropdown_fg_color,
                                               dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_stim.grid(row=0, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                sticky='nsew')

        # Load Stim Button
        self.load_stim_button = ctk.CTkButton(frame, text='Load Stim',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color,
                                              hover_color=configuration.button_hover_color,
                                              command=lambda: self.event_handler(Event.SET_STIM_NUMBER))
        self.load_stim_button.grid(row=1, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')



        # Time bw Samples Dropdown Box
        dropdown_values_time_bw_samp = [f'Time bw Samples: {x} sec' for x in np.arange(0, 4.5, 0.5)]
        value_list = [x for x in np.arange(0, 4.5, 0.5)]
        init_index_time = 0
        for i, value in enumerate(value_list):
            # print(str(self.initial_value[0]), str(value))
            if str(self.initial_value[0]) == str(value):
                init_index_time = i

        self.option_var_time_bw_samp = tk.StringVar(value=dropdown_values_time_bw_samp[init_index_time])  # Set initial value
        self.dropdown_time_bw_samp = ctk.CTkOptionMenu(frame, variable=self.option_var_time_bw_samp,
                                                       values=dropdown_values_time_bw_samp,
                                                       font=(configuration.main_font_style, configuration.main_font_size),
                                                       fg_color=configuration.dropdown_fg_color,
                                                       dropdown_hover_color=configuration.dropdown_hover_color)
        self.dropdown_time_bw_samp.grid(row=2, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                        sticky='nsew')

        # Load Stim Button
        self.save_default_bw_time = ctk.CTkButton(frame, text='Change Default',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color,
                                              hover_color=configuration.button_hover_color,
                                              command=lambda: self.event_handler(Event.SET_DEFAULT_BW_TIME))
        self.save_default_bw_time.grid(row=3, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')


        # IP Settings
        ip_addresses = ['0.0.0.0', '192.168.1.253', '141.225.179.76']
        dropdown_values_ip = [f'IP Address: {x}' for x in ip_addresses]
        init_index_ip = 0
        for i, value in enumerate(ip_addresses):
            if str(self.initial_value[1]) == str(value):
                init_index_ip = i
        self.option_var_ip_address = tk.StringVar(value=dropdown_values_ip[init_index_ip])  # Set initial value to the prompt text
        self.dropdown_ip_address = ctk.CTkOptionMenu(frame, variable=self.option_var_ip_address, values=dropdown_values_ip,
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.dropdown_fg_color,
                                               dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_ip_address.grid(row=4, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                sticky='nsew')

        # IP Button
        self.load_ip_button = ctk.CTkButton(frame, text='Change Default',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color,
                                              hover_color=configuration.button_hover_color,
                                              command=lambda: self.event_handler(Event.SET_IP_ADDRESS))
        self.load_ip_button.grid(row=5, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # Port Settings
        port_nums = ['12345', '99999', '86868']
        dropdown_values_port = [f'Port Number: {x}' for x in port_nums]
        init_index_port = 0
        for i, value in enumerate(port_nums):
            if str(self.initial_value[2]) == str(value):
                init_index_port = i
        self.option_var_port = tk.StringVar(value=dropdown_values_port[init_index_port])  # Set initial value to the prompt text
        self.dropdown_port = ctk.CTkOptionMenu(frame, variable=self.option_var_port, values=dropdown_values_port,
                                               font=(configuration.main_font_style, configuration.main_font_size),
                                               fg_color=configuration.dropdown_fg_color,
                                               dropdown_hover_color=configuration.button_hover_color)
        self.dropdown_port.grid(row=6, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                sticky='nsew')

        # Load Stim Button
        self.load_port_button = ctk.CTkButton(frame, text='Change Default',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.button_fg_color,
                                              hover_color=configuration.button_hover_color,
                                              command=lambda: self.event_handler(Event.SET_PORT_NUM))
        self.load_port_button.grid(row=7, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')

        # Calibration Button
        self.calibration_button = ctk.CTkButton(frame, text='Calibrate Speakers',
                                              font=(configuration.main_font_style, configuration.main_font_size),
                                              fg_color=configuration.pause_fg_color,
                                              hover_color=configuration.pause_hover_color,
                                              command=lambda: self.event_handler(Event.CALIBRATION))
        self.calibration_button.grid(row=8, column=0, padx=configuration.x_pad_setting, pady=configuration.y_pad_setting,
                                   sticky='nsew')