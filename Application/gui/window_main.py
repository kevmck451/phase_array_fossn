


from Application.controller.event_states import Event
import Application.gui.configuration as configuration


import customtkinter as ctk
import tkinter as tk
import sys



class Main_Window(ctk.CTk):
    def __init__(self, event_handler):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.event_handler = event_handler

        # Main Setup ------------------------------------------------------------
        self.title(configuration.window_title)

        # Screen: can see window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (configuration.window_width / 2))
        center_y = int((screen_height / 2) - (configuration.window_height / 2))
        self.geometry(f'{configuration.window_width}x{configuration.window_height}+{center_x}+{center_y}')
        self.minsize(configuration.min_window_width, configuration.min_window_height)

        self.Top_Frame = Top_Frame(self, self.event_handler)
        self.Middle_Frame = Middle_Frame(self, self.event_handler)
        self.Bottom_Frame = Bottom_Frame(self, self.event_handler)

        # Configure grid rows with equal weight
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.Top_Frame.grid(row=0, column=0, sticky='nsew')
        self.Middle_Frame.grid(row=1, column=0, sticky='nsew')
        self.Bottom_Frame.grid(row=2, column=0, sticky='nsew')

        # Ending Procedures
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Escape>", self.on_close)
        self.bind("<Control-c>", self.on_close)

    def on_close(self):
        # Perform any cleanup or process termination steps here
        # For example, safely terminate any running threads, save state, release resources, etc.
        # self.matrix_mics.stop_stream()
        self.event_handler(Event.ON_CLOSE)
        self.destroy()

# --------------------------------------------------------------------------------------------------
# TOP FRAME ----------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
class Top_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        self.Left_Frame = Top_Left_Frame(self, self.event_handler)
        self.Center_Frame = Top_Middle_Frame(self, self.event_handler)
        self.Right_Frame = Top_Right_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space
        self.columnconfigure(1, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(2, weight=1)  # Right column with x/3 of the space

        # Place the frames using grid
        self.Left_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        self.Center_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1
        self.Right_Frame.grid(row=0, column=2, sticky='nsew')  # Right frame in column 1

class Top_Left_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Bottom Frame
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        bottom_frame.grid_rowconfigure(0, weight=1, uniform='row')


        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.fpga_connection_frame(top_frame)
        self.rpi_connection_frame(bottom_frame)


    # FRAMES ---------------------------------------------
    def fpga_connection_frame(self, frame):
        self.fpga_connection_label = ctk.CTkLabel(frame, text="Microphone Connection Status", font=configuration.console_font_style)
        self.fpga_connection_label.pack(fill='both') # , expand=True

    def rpi_connection_frame(self, frame):
        self.rpi_connection_label = ctk.CTkLabel(frame, text="Temp Sensor Connection Status", font=configuration.console_font_style)
        self.rpi_connection_label.pack(fill='both') # , expand=True

class Top_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        self.playing = False
        self.calibrating = False

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Bottom Frame
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        bottom_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.start_frame(top_frame)
        self.calibration_frame(bottom_frame)


    # FRAMES ---------------------------------------------
    def start_frame(self, frame):
        self.start_label = ctk.CTkLabel(frame, text="Start/Stop Recording, Beamforming, Processing, and PCA Detecting", font=configuration.console_font_style)
        self.start_label.pack(fill='both')  # , expand=True

        self.start_button = ctk.CTkButton(frame, text="Start",
                                         fg_color=configuration.start_fg_color,
                                         hover_color=configuration.start_hover_color,
                                         command=lambda: self.event_handler(Event.START_RECORDER))
        self.start_button.pack(pady=5)

    def calibration_frame(self, frame):
        self.calibration_label = ctk.CTkLabel(frame, text="Baseline Calibration for PCA Detector", font=configuration.console_font_style)
        self.calibration_label.pack(fill='both')  # , expand=True

        self.calibrate_button = ctk.CTkButton(frame, text="Calibrate PCA",
                                          fg_color=configuration.start_fg_color,
                                          hover_color=configuration.start_hover_color,
                                          command=lambda: self.event_handler(Event.PCA_CALIBRATION))
        self.calibrate_button.pack(pady=5)

    def toggle_play(self):
        if self.playing:
            self.start_button.configure(text="Start",
                                       fg_color=configuration.start_fg_color,
                                       hover_color=configuration.start_hover_color,
                                       command=lambda: self.event_handler(Event.START_RECORDER))
            self.playing = False
            # Placeholder for stopping audio
        else:
            self.start_button.configure(text="Stop",
                                       fg_color=configuration.stop_fg_color,
                                       hover_color=configuration.stop_hover_color,
                                       command=lambda: self.event_handler(Event.STOP_RECORDER))
            self.playing = True

    def toggle_calibrate(self):
        if self.calibrating:
            self.calibrate_button.configure(text="Calibrate PCA",
                                        fg_color=configuration.start_fg_color,
                                        hover_color=configuration.start_hover_color,
                                        command=lambda: self.event_handler(Event.PCA_CALIBRATION))
            self.calibrating = False
        else:
            self.calibrate_button.configure(text="Stop Calibration",
                                        fg_color=configuration.stop_fg_color,
                                        hover_color=configuration.stop_hover_color,
                                        command=lambda: self.event_handler(Event.STOP_PCA_CALIBRATION))
            self.calibrating = True

class Top_Right_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Top Frame
        main_frame = ctk.CTkFrame(self)
        # main_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # main_frame.grid_rowconfigure(0, weight=1, uniform='row')
        main_frame.pack(fill='both', expand=True, padx=configuration.x_pad_main, pady=configuration.y_pad_main)

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)  # Top row
        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.console_frame(main_frame)

        sys.stdout = self

        print('Attempting to Connect with Temp Server')
        print('Attempting to Connect with FPGA Server')


    # FRAMES ---------------------------------------------
    def console_frame(self, frame):
        self.console_label = ctk.CTkLabel(frame, text="Output Console", font=configuration.console_font_style)
        self.console_label.pack(side=tk.TOP, fill=tk.X)

        # Create a Text widget for console output
        self.console_text = tk.Text(frame, wrap=tk.WORD, state='disabled', height=10)
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the Text widget
        scrollbar = tk.Scrollbar(frame, command=self.console_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.config(yscrollcommand=scrollbar.set)

    def write(self, message):
        # Insert text into the Text widget and scroll to the end
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, message)
        self.console_text.config(state='disabled')
        self.console_text.yview(tk.END)

    def flush(self):
        pass


# --------------------------------------------------------------------------------------------------
# MIDDLE FRAMES ------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

class Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        self.Center_Frame = Main_Middle_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space

        # Place the frames using grid
        self.Center_Frame.grid(row=0, column=0, sticky='nsew')

class Main_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        middle_frame = ctk.CTkFrame(self)
        middle_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)  # Top row
        self.grid_columnconfigure(0, weight=1)

        self.detector_frame(middle_frame)

    # FRAMES ---------------------------------------------
    def detector_frame(self, frame):
        self.detector_label = ctk.CTkLabel(frame, text="Beamformed PCA Detector Output", font=configuration.console_font_style)
        self.detector_label.pack(fill='both')  # , expand=True



# --------------------------------------------------------------------------------------------------
# BOTTOM FRAMES ------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
class Bottom_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        self.Left_Frame = Bottom_Left_Frame(self, self.event_handler)
        self.Center_Frame = Bottom_Middle_Frame(self, self.event_handler)
        self.Right_Frame = Bottom_Right_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space
        self.columnconfigure(1, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(2, weight=1)  # Right column with x/3 of the space

        # Place the frames using grid
        self.Left_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        self.Center_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1
        self.Right_Frame.grid(row=0, column=2, sticky='nsew')  # Right frame in column 1

class Bottom_Left_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # # Middle Frame
        # middle_frame = ctk.CTkFrame(self)
        # middle_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # middle_frame.grid_rowconfigure(1, weight=1, uniform='row')
        #
        # # Bottom Frame
        # bottom_frame = ctk.CTkFrame(self)
        # bottom_frame.grid(row=2, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # bottom_frame.grid_rowconfigure(2, weight=1, uniform='row')

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.beamform_settings_frame(top_frame)

    # FRAMES ---------------------------------------------
    def beamform_settings_frame(self, frame):
        self.beamform_settings_label = ctk.CTkLabel(frame, text="Beamform Settings", font=configuration.console_font_style)
        self.beamform_settings_label.pack(fill='both')  # , expand=True

        self.thetas_label = ctk.CTkLabel(frame, text="Thetas", font=configuration.console_font_style)
        self.thetas_label.pack(fill='both')  # , expand=True

        self.phis_label = ctk.CTkLabel(frame, text="Phis", font=configuration.console_font_style)
        self.phis_label.pack(fill='both')  # , expand=True

        self.manual_temp_entry_label = ctk.CTkLabel(frame, text="Manual Temp Entry", font=configuration.console_font_style)
        self.manual_temp_entry_label.pack(fill='both')  # , expand=True



class Bottom_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # # Middle Frame
        # middle_frame = ctk.CTkFrame(self)
        # middle_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # middle_frame.grid_rowconfigure(1, weight=1, uniform='row')
        #
        # # Bottom Frame
        # bottom_frame = ctk.CTkFrame(self)
        # bottom_frame.grid(row=2, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # bottom_frame.grid_rowconfigure(2, weight=1, uniform='row')

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.processing_settings_frame(top_frame)

    # FRAMES ---------------------------------------------
    def processing_settings_frame(self, frame):
        self.processing_settings_label = ctk.CTkLabel(frame, text="Processing Settings", font=configuration.console_font_style)
        self.processing_settings_label.pack(fill='both')  # , expand=True

        self.processing_chain_label = ctk.CTkLabel(frame,
                                                   text="Processing Chain: Noise Reduction, High Pass, Normalization, Down Sampling",
                                                   font=configuration.console_font_style)
        self.processing_chain_label.pack(fill='both')  # , expand=True

        self.nr_std_threshold_label = ctk.CTkLabel(frame, text="NR: STD Threshold", font=configuration.console_font_style)
        self.nr_std_threshold_label.pack(fill='both')  # , expand=True

        self.hp_bottom_cutoff_freq_label = ctk.CTkLabel(frame, text="HP: Bottom Cutoff Frequency", font=configuration.console_font_style)
        self.hp_bottom_cutoff_freq_label.pack(fill='both')  # , expand=True

        self.nm_percentage_label = ctk.CTkLabel(frame, text="NM: Percentage", font=configuration.console_font_style)
        self.nm_percentage_label.pack(fill='both')  # , expand=True

        self.ds_new_sr_label = ctk.CTkLabel(frame, text="DS: New Sample Rate", font=configuration.console_font_style)
        self.ds_new_sr_label.pack(fill='both')  # , expand=True




class Bottom_Right_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Top Frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        top_frame.grid_rowconfigure(0, weight=1, uniform='row')

        # # Middle Frame
        # middle_frame = ctk.CTkFrame(self)
        # middle_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # middle_frame.grid_rowconfigure(1, weight=1, uniform='row')
        #
        # # Bottom Frame
        # bottom_frame = ctk.CTkFrame(self)
        # bottom_frame.grid(row=2, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
        # bottom_frame.grid_rowconfigure(2, weight=1, uniform='row')

        # Configure the grid rows and column for self
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform='col')

        self.pca_detector_settings_frame(top_frame)

    # FRAMES ---------------------------------------------
    def pca_detector_settings_frame(self, frame):
        self.pca_detector_settings_label = ctk.CTkLabel(frame, text="PCA Detector Settings", font=configuration.console_font_style)
        self.pca_detector_settings_label.pack(fill='both')  # , expand=True

        self.num_components_label = ctk.CTkLabel(frame, text="Number of Components", font=configuration.console_font_style)
        self.num_components_label.pack(fill='both')  # , expand=True

        self.threshold_multiplier_label = ctk.CTkLabel(frame, text="Threshold Multiplier", font=configuration.console_font_style)
        self.threshold_multiplier_label.pack(fill='both')  # , expand=True