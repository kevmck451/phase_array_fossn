




import customtkinter as ctk
from PIL import ImageTk
import tkinter as tk
import subprocess
from PIL import Image
import sys

from Application.controller.event_states import Event



# Settings Window
class Human_Op_Mode_Window(ctk.CTk):
    def __init__(self, event_handler, array_config, device_config):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.array_config = array_config
        self.device_config = device_config

        # Computer Icon
        # print(self.device_config.main_window_icon)
        # img = Image.open(self.device_config.main_window_icon)
        # icon = ImageTk.PhotoImage(img)
        # self.tk.call('wm', 'iconphoto', self._w, icon)

        # Main Setup ------------------------------------------------------------
        self.title(f'Human Operational Mode: {self.array_config.title}')


        # Get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (self.device_config.settings_window_width / 2))
        center_y = int((screen_height / 2) - (self.device_config.settings_window_height / 2))
        self.geometry(f'{self.device_config.settings_window_width}x{self.device_config.settings_window_height}+{center_x}+{center_y}')
        self.minsize(self.device_config.settings_min_window_width, self.device_config.settings_min_window_height)


        self.Main_Frame = Top_Frame(self, event_handler)
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


class Top_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.parent = parent

        self.event_handler = event_handler

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(padx=self.parent.device_config.x_pad_main, pady=self.parent.device_config.y_pad_main, sticky='nsew')
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
        frame.grid_columnconfigure(0, weight=1)  # Single column


