


from Application.controller.event_states import Event
import Application.gui.configuration as configuration


import customtkinter as ctk
from PIL import ImageTk
import tkinter as tk
import subprocess


class Main_Window(ctk.CTk):
    def __init__(self, event_handler, array_config):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.event_handler = event_handler
        self.array_config = array_config

        # Main Setup ------------------------------------------------------------
        self.title(f'{configuration.window_title}: {self.array_config.title}')

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
        self.Center_Right_Frame = Top_Middle_Right_Frame(self, self.event_handler)
        self.Right_Frame = Top_Right_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space
        self.columnconfigure(1, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(2, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(3, weight=1)  # Right column with x/3 of the space

        # Place the frames using grid
        self.Left_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        self.Center_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1
        self.Center_Right_Frame.grid(row=0, column=2, sticky='nsew')  # Right frame in column 1
        self.Right_Frame.grid(row=0, column=3, sticky='nsew')  # Right frame in column 1


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

        self.current_temp = '-'
        self.fpga_connection = False
        self.temp_connection = False
        self.update_sample_time = 1000

        self.check_for_state_changes()


    # FRAMES ---------------------------------------------
    def fpga_connection_frame(self, frame):
        self.fpga_connection_label = ctk.CTkLabel(frame, text="Microphone Connection Status", font=configuration.console_font_style)
        self.fpga_connection_label.pack(fill='both') # , expand=True
        self.fpga_status_label = ctk.CTkLabel(frame, text="Not Connected", text_color='red', font=configuration.console_font_style)
        self.fpga_status_label.pack(fill='both')  # , expand=True

    def rpi_connection_frame(self, frame):
        self.rpi_connection_label = ctk.CTkLabel(frame, text="Temp Sensor Connection Status", font=configuration.console_font_style)
        self.rpi_connection_label.pack(fill='both') # , expand=True
        self.rpi_status_label = ctk.CTkLabel(frame, text="Not Connected", text_color='red', font=configuration.console_font_style)
        self.rpi_status_label.pack(fill='both')  # , expand=True
        self.current_temp_label = ctk.CTkLabel(frame, text="-", font=configuration.console_font_style)
        self.current_temp_label.pack(fill='both')  # , expand=True

    def fpga_connected(self):
        self.fpga_status_label.configure(text="Connected", text_color='green')

    def fpga_disconnected(self):
        self.fpga_status_label.configure(text="Not Connected", text_color='red')

    def rpi_connected(self):
        self.rpi_status_label.configure(text="Connected", text_color='green')

    def rpi_disconnected(self):
        self.rpi_status_label.configure(text="Not Connected", text_color='red')

    def update_current_temp(self):
        self.current_temp_label.configure(text=f'{self.current_temp}\u00B0 F')

    def check_for_state_changes(self):
        if self.fpga_connection:
            self.fpga_connected()
        else:
            self.fpga_disconnected()

        if self.temp_connection:
            self.rpi_connected()
        else:
            self.rpi_disconnected()

        self.update_current_temp()

        self.after(self.update_sample_time, self.check_for_state_changes)


class Top_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        self.playing = False
        self.calibrating = False
        self.project_name = ''

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
        self.start_label = ctk.CTkLabel(frame, text="Start/Stop Recording, Beamforming, Processing, and PCA Calculator", font=configuration.console_font_style)
        self.start_label.pack(fill='both')  # , expand=True

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=5)

        self.load_button_audio = ctk.CTkButton(button_frame, text="Load",
                                         fg_color=configuration.gray_fg_color,
                                         hover_color=configuration.gray_hover_color,
                                         command=self.load_audio_file, font=configuration.button_font_style)
        self.load_button_audio.grid(row=0, column=0, padx=5)

        self.start_button = ctk.CTkButton(button_frame, text="Start",
                                         fg_color=configuration.start_fg_color,
                                         hover_color=configuration.start_hover_color,
                                         command=lambda: self.event_handler(Event.START_RECORDER),
                                          font=configuration.button_font_style)
        self.start_button.grid(row=0, column=1, padx=5)

        self.audio_save_checkbox_variable = ctk.BooleanVar(value=True)

        self.save_checkbox_audio = ctk.CTkCheckBox(button_frame, text="Save",
                                             variable=self.audio_save_checkbox_variable,
                                             fg_color=configuration.bluelight_fg_color,
                                             hover_color=configuration.bluelight_hover_color, font=configuration.button_font_style)
        self.save_checkbox_audio.grid(row=0, column=2, padx=5)

        self.chunk_time_entry = ctk.CTkEntry(button_frame, width=40, placeholder_text="1.0s", font=configuration.button_font_style)
        self.chunk_time_entry.grid(row=0, column=3, padx=5)

        entry_frame = ctk.CTkFrame(frame)
        entry_frame.pack(pady=10)

        self.project_name = ctk.CTkEntry(entry_frame, width=300, placeholder_text="Enter a Test Name, if desired...", font=configuration.button_font_style)
        self.project_name.pack()

    def load_audio_file(self):
        try:
            script = '''
            set chosenFile to choose file with prompt "Select Audio File" of type {"public.audio"}
            set filePath to POSIX path of chosenFile
            return filePath
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            audio_file_path = result.stdout.strip()

            if audio_file_path:
                self.selected_audio_file = audio_file_path
                print(f"Selected audio file: {self.selected_audio_file}")
                self.event_handler(Event.LOAD_AUDIO)

        except Exception as e:
            print("File dialog failed:", e)

    def calibration_frame(self, frame):
        self.calibration_label = ctk.CTkLabel(frame, text="Baseline Calibration for Detector", font=configuration.console_font_style)
        self.calibration_label.pack(fill='both')  # , expand=True

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=5)


        self.load_button_pca = ctk.CTkButton(button_frame, text="Load",
                                         fg_color=configuration.gray_fg_color,
                                         hover_color=configuration.gray_hover_color,
                                         command=self.load_pca_file, font=configuration.button_font_style)
        self.load_button_pca.grid(row=0, column=0, padx=5)


        self.calibrate_button = ctk.CTkButton(button_frame, text="Calibrate PCA",
                                              fg_color=configuration.start_fg_color,
                                              hover_color=configuration.start_hover_color,
                                              command=lambda: self.event_handler(Event.PCA_CALIBRATION), font=configuration.button_font_style)
        self.calibrate_button.grid(row=0, column=1, padx=5)

        self.pca_save_checkbox_variable = ctk.BooleanVar(value=True)

        self.save_checkbox_pca = ctk.CTkCheckBox(button_frame, text="Save",
                                             variable=self.pca_save_checkbox_variable,
                                             fg_color=configuration.bluelight_fg_color,
                                             hover_color=configuration.bluelight_hover_color, font=configuration.button_font_style)
        self.save_checkbox_pca.grid(row=0, column=2, padx=5)

        self.calibration_time_entry = ctk.CTkEntry(button_frame, width=40, placeholder_text="60s", font=configuration.button_font_style)
        self.calibration_time_entry.grid(row=0, column=3, padx=5)

    def load_pca_file(self):
        try:
            script = '''
            set chosenFolder to choose folder with prompt "Select Folder Containing PCA Calibration Files"
            set folderPath to POSIX path of chosenFolder
            return folderPath
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            folder_path = result.stdout.strip()

            if folder_path:
                self.selected_pca_folder = folder_path
                print(f"Selected PCA folder: {self.selected_pca_folder}")

                self.baseline_means_path = f"{self.selected_pca_folder}/baseline_means.npy"
                self.baseline_stds_path = f"{self.selected_pca_folder}/baseline_stds.npy"

                self.event_handler(Event.LOAD_CALIBRATION)

        except Exception as e:
            print("Folder dialog failed:", e)

    def toggle_play(self):
        if self.playing:
            self.start_button.configure(text="Start",
                                       fg_color=configuration.start_fg_color,
                                       hover_color=configuration.start_hover_color,
                                       command=lambda: self.event_handler(Event.START_RECORDER), font=configuration.button_font_style)
            self.playing = False
            # Placeholder for stopping audio
        else:
            self.start_button.configure(text="Stop",
                                       fg_color=configuration.stop_fg_color,
                                       hover_color=configuration.stop_hover_color,
                                       command=lambda: self.event_handler(Event.STOP_RECORDER), font=configuration.button_font_style)
            self.playing = True

    def toggle_calibrate(self):
        if self.calibrating:
            self.calibrate_button.configure(text="Calibrate PCA",
                                        fg_color=configuration.start_fg_color,
                                        hover_color=configuration.start_hover_color,
                                        command=lambda: self.event_handler(Event.PCA_CALIBRATION), font=configuration.button_font_style)
            self.calibrating = False
        else:
            self.calibrate_button.configure(text="Stop Calibration",
                                        fg_color=configuration.stop_fg_color,
                                        hover_color=configuration.stop_hover_color,
                                        command=lambda: self.event_handler(Event.STOP_PCA_CALIBRATION), font=configuration.button_font_style)
            self.calibrating = True


class Top_Middle_Right_Frame(ctk.CTkFrame):
        def __init__(self, parent, event_handler):
            super().__init__(parent)
            self.event_handler = event_handler
            self.parent = parent

            # Top Frame
            top_frame = ctk.CTkFrame(self)
            top_frame.grid(row=0, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
            top_frame.grid_rowconfigure(0, weight=0, uniform='row')

            # Bottom Frame
            bottom_frame = ctk.CTkFrame(self)
            # bottom_frame.grid(row=1, column=0, padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')
            bottom_frame.grid_rowconfigure(0, weight=0)

            # Configure the grid rows and column for self
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=0)

            self.grid_columnconfigure(0, weight=1, uniform='col')

            self.clock_frame(top_frame)

            self.calibration_seconds = 0
            self.recording_seconds = 0
            self.calibration_running = False
            self.recording_running = False
            self.external_playing = False

        # FRAMES ---------------------------------------------
        def clock_frame(self, frame):
            self.clock_display = ctk.CTkLabel(
                frame, text="00:00", font=configuration.console_font_style_large
            )
            self.clock_display.pack(pady=5)

            # # Initialize clock state
            # self.calibration_seconds = 0
            # self.recording_seconds = 0
            # self.calibration_running = False
            # self.recording_running = False

            self.real_time_checkbox_variable = ctk.BooleanVar(value=True)

            self.real_time_checkbox = ctk.CTkCheckBox(frame, text="Real-Time",
                                                      variable=self.real_time_checkbox_variable,
                                                      fg_color=configuration.bluelight_fg_color,
                                                      hover_color=configuration.bluelight_hover_color, font=configuration.button_font_style)
            self.real_time_checkbox.pack(pady=5)

            # button_frame = ctk.CTkFrame(frame)
            # button_frame.pack(pady=5)

            self.play_external_button = ctk.CTkButton(frame, text="Start External Audio",
                                              fg_color=configuration.purple_fg_color,
                                              hover_color=configuration.purple_hover_color,
                                              command=lambda: self.event_handler(Event.START_EXTERNAL_PLAY),
                                              font=configuration.button_font_style)
            self.play_external_button.pack(pady=5)

        def toggle_play_external_button(self):
            if self.external_playing:
                self.play_external_button.configure(text="Activate External Audio",
                                            fg_color=configuration.purple_fg_color,
                                            hover_color=configuration.purple_hover_color,
                                            command=lambda: self.event_handler(Event.START_EXTERNAL_PLAY), font=configuration.button_font_style)
                self.external_playing = False
                # Placeholder for stopping audio
            else:
                self.play_external_button.configure(text="Stop External Audio",
                                            fg_color=configuration.darkgray_fg_color,
                                            hover_color=configuration.darkgray_hover_color,
                                            command=lambda: self.event_handler(Event.STOP_EXTERNAL_PLAY), font=configuration.button_font_style)
                self.external_playing = True

        def start_calibration(self, seconds):
            self.calibration_seconds = seconds
            self.calibration_running = True
            self.update_calibration_timer()

        def update_calibration_timer(self):
            if self.calibration_running and self.calibration_seconds > 0:
                self.calibration_seconds -= 1
                self.update_clock_display(self.calibration_seconds)
                self.after(1000, self.update_calibration_timer)
            else:
                self.calibration_running = False

        def start_recording(self):
            self.recording_seconds = 0
            self.recording_running = True
            self.update_recording_timer()

        def update_recording_timer(self):
            if self.recording_running:
                self.recording_seconds += 1
                self.update_clock_display(self.recording_seconds)
                self.after(1000, self.update_recording_timer)

        def stop_recording(self):
            self.recording_running = False

        def reset_clock(self):
            self.calibration_running = False
            self.recording_running = False
            self.calibration_seconds = 0
            self.recording_seconds = 0
            self.update_clock_display(0)

        def update_clock_display(self, seconds):
            mins = seconds // 60
            secs = seconds % 60
            prefix = "-" if self.calibration_running else ""
            self.clock_display.configure(text=f"{prefix}{mins:02}:{secs:02}")


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

        # sys.stdout = self

    # FRAMES ---------------------------------------------
    def console_frame(self, frame):
        self.console_label = ctk.CTkLabel(frame, text="Output Console", font=configuration.console_font_style)
        self.console_label.pack(side=tk.TOP, fill=tk.X)

        # Create a Text widget for console output
        self.console_text = tk.Text(frame, wrap=tk.WORD, state='disabled', height=10, width=40)
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

    def insert_text(self, text, color="white"):
        # Color Options:
        # 1. Standard Color Names:
        #    - "black", "white", "red", "green", "blue", "yellow", "cyan", "magenta",
        #      "gray", "orange", "purple", "brown", etc.
        # 2. Hexadecimal Color Codes (format: "#RRGGBB"):
        #    - Examples: "#000000" (black), "#FFFFFF" (white), "#FF0000" (red),
        #                "#00FF00" (green), "#0000FF" (blue), "#FFFF00" (yellow),
        #                "#FFA500" (orange), "#800080" (purple)
        # 3. RGB Tuples (format: (R, G, B) where R, G, B are integers from 0 to 255):
        #    - Examples: (0, 0, 0) (black), (255, 255, 255) (white), (255, 0, 0) (red),
        #                (0, 255, 0) (green), (0, 0, 255) (blue)

        if isinstance(color, tuple):
            # Convert RGB tuple to hex string
            color = self.rgb_to_hex(color)

        # Enable the Text widget temporarily to insert text
        self.console_text.config(state='normal')

        # Create a tag with the desired color
        self.console_text.tag_configure(color, foreground=color)

        # Insert the text with the tag
        self.console_text.insert(tk.END, text + "\n", color)

        # Disable the Text widget to make it read-only again
        self.console_text.config(state='disabled')

        # Scroll to the end of the Text widget
        self.console_text.see(tk.END)

    def rgb_to_hex(self, rgb):
        """Convert an (R, G, B) tuple to a hexadecimal color string."""
        return "#%02x%02x%02x" % rgb


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
        self.columnconfigure(0, weight=1)

        # Place the frames using grid
        self.Center_Frame.grid(row=0, column=0, sticky='nsew')

class Main_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Configure three-column layout explicitly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Left
        self.grid_columnconfigure(1, weight=1)  # Center
        self.grid_columnconfigure(2, weight=1)  # Right

        # Left frame for visual
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_columnconfigure(0, weight=1)

        # Center side
        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        center_frame.rowconfigure(1, weight=1)  # Let row 1 (image) expand
        center_frame.grid_columnconfigure(0, weight=1)


        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)


        # LEFT FRAME ------------------------------

        self.detector_label = ctk.CTkLabel(left_frame, text="Beamformed PCA Detector Output", font=configuration.console_font_style)
        self.detector_label.grid(row=0, column=0, sticky='ew')

        self.canvas_left_width = 560
        self.canvas_left = tk.Canvas(left_frame, bg="#333333", width=self.canvas_left_width, height=385)
        self.canvas_left.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        self.canvas_left.master.grid_propagate(False)


        self.draw_threshold_lines()

        self.updating = True  # Flag to control updates

        self.all_directions = self.parent.parent.array_config.default_theta_directions
        self.directions = self.all_directions[:]
        self.anomaly_list = []

        # Example data for the bar chart
        # self.anomaly_data = [0, 1, 0.5, 1, 1, 0.5, 2, 4, 5, 9, 6, 3, 2, 1, 1, 0.5, 1.5, 0.5, 1]  # Example data
        self.anomaly_data = list(0 for x in range(len(self.directions)))
        self.max_anomalies = 150  # Maximum possible anomalies
        self.thresholds = {
            'green': 30,  # Less than 30% anomalies
            'yellow': 60, # 30% to 60% anomalies
            'red': 100,   # More than 60% anomalies
        }

        self.next_heatmap_image = None
        self._heatmap_loop_started = False

        # CENTER FRAME ------------------------------
        self.heatmap_title = ctk.CTkLabel(center_frame, text="Time Series Heatmap of Anomalies", font=configuration.console_font_style)
        self.heatmap_title.grid(row=0, column=0, sticky='ew')

        # New: Image container
        self.heatmap_canvas = tk.Label(center_frame, bg="black", width=800, height=600)
        self.heatmap_canvas.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        self.heatmap_canvas.master.grid_propagate(False)

        # RIGHT FRAME ------------------------------
        self.classifier_label = ctk.CTkLabel(right_frame, text="Sound Classifier", font=configuration.console_font_style)
        self.classifier_label.grid(row=0, column=0, sticky='ew')

        self.anomaly_data = [0] * len(self.directions)

        self.start_heatmap_updates()
        self.start_updates()

    def draw_bar_chart(self):
        font_size = 10

        num_channels = len(self.anomaly_data)

        directions_to_draw = self.directions[:num_channels]

        self.canvas_left.delete("all")  # Clear the canvas_left
        self.draw_threshold_lines()  # Draw threshold lines

        canvas_width = self.canvas_left_width
        canvas_height = self.canvas_left.winfo_height()

        # Calculate bar width to evenly fill the canvas_left
        bar_width = canvas_width / num_channels

        chart_height = canvas_height * 0.8  # Use 80% of the height for the chart

        for i in range(num_channels):
            value = self.anomaly_data[i]

            # Determine the color based on the threshold
            percentage = (value / self.max_anomalies) * 100

            # Cap the bar height to 100% of chart height
            capped_percentage = min(percentage, 100)
            bar_height = (capped_percentage / 100) * chart_height

            if percentage < self.thresholds['green']:
                bar_color = 'green'
            elif percentage < self.thresholds['yellow']:
                bar_color = 'yellow'
            else:
                bar_color = 'red'
                self.anomaly_list.append(directions_to_draw[i])
                self.event_handler(Event.ANOMALY_DETECTED)

            # Calculate the position of each bar
            x1 = i * bar_width
            y1 = chart_height - bar_height
            x2 = x1 + bar_width - 2
            y2 = chart_height

            # Draw the bar
            self.canvas_left.create_rectangle(x1, y1, x2, y2, fill=bar_color)

            # Draw the direction label below the bar
            # self.canvas_left.create_text(x1 + bar_width / 2, chart_height + 20, text=f'{directions_to_draw[i]}\u00B0', anchor='n', font=("Arial", font_size))
            label_y = canvas_height - 60
            self.canvas_left.create_text(x1 + bar_width / 2, label_y, text=f'{directions_to_draw[i]}\u00B0', anchor='n', font=("Arial", font_size))

        self.anomaly_list.clear()
        # Draw the chart's axis
        self.canvas_left.create_line(0, chart_height, canvas_width, chart_height)

        self.canvas_left.config(scrollregion=(0, 0, canvas_width, canvas_height))

        self.after(500, self.draw_bar_chart)

    def draw_threshold_lines(self):
        # Clear any existing lines
        self.canvas_left.delete("threshold_lines")

        # Calculate canvas_left dimensions
        canvas_width = self.canvas_left.winfo_width()
        canvas_height = self.canvas_left.winfo_height()

        # Define thresholds as percentages
        threshold_percentages = {
            'yellow': 30,  # Example: 30% of the max value
            'red': 60  # Example: 60% of the max value
        }

        # Convert percentages to actual pixel positions based on bar height scaling
        chart_height = canvas_height * 0.8  # Use 80% of the height for the chart
        for color, percentage in threshold_percentages.items():
            # Calculate the position for the threshold line
            threshold_position = (percentage / 100) * chart_height
            # Draw the threshold line
            self.canvas_left.create_line(0, chart_height - threshold_position, canvas_width, chart_height - threshold_position,
                                         fill=color, dash=(4, 4), tags="threshold_lines")

    def start_updates(self):
        if getattr(self, "_chart_loop_started", False):
            # print("draw_bar_chart() loop already running.")
            return
        # print("starting draw_bar_chart() loop.")
        self._chart_loop_started = True
        self.updating = True
        self.draw_bar_chart()

    def stop_updates(self):
        self.anomaly_data = list(0 for x in range(len(self.directions)))
        self.updating = False

    def start_heatmap_updates(self):
        if self._heatmap_loop_started:
            return
        self._heatmap_loop_started = True
        self.update_heatmap_image()

    def update_heatmap_image(self):
        # print('Heatmap')
        if self.next_heatmap_image:
            image = self.next_heatmap_image
            photo = ImageTk.PhotoImage(image)
            self.heatmap_canvas.configure(image=photo)
            self.heatmap_canvas.image = photo
            self.next_heatmap_image = None

        self.after(500, self.update_heatmap_image)


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

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Row for the top label
        self.grid_rowconfigure(1, weight=1)  # Row for the settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.beamform_settings_frame()

        self.temp_value = None

    def beamform_settings_frame(self):
        # Beamform Settings Label
        self.beamform_settings_label = ctk.CTkLabel(self, text="Beamform Settings", font=configuration.console_font_style)
        self.beamform_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # — Thetas container (fills columns 0–2 of the parent) —
        thetas_frame = ctk.CTkFrame(self)
        thetas_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=2)
        # inside this frame we make 5 tiny columns
        for c in range(5):
            thetas_frame.grid_columnconfigure(c, weight=0)

        # checkbox + label + Lθ, Rθ, Δθ inside thetas_frame
        self.enable_thetas = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            thetas_frame, text="", variable=self.enable_thetas,
            command=self.toggle_thetas, font=configuration.button_font_style
        ).grid(row=0, column=0, sticky='w', padx=(0, 2))

        ctk.CTkLabel(
            thetas_frame, text="Theta:", font=configuration.console_font_style
        ).grid(row=0, column=1, sticky='w', padx=(0, 5))

        self.ltheta_entry = ctk.CTkEntry(
            thetas_frame, font=configuration.button_font_style, width=40
        )
        self.ltheta_entry.insert(0, f'{self.parent.parent.array_config.Ltheta}')
        self.ltheta_entry.grid(row=0, column=2, sticky='w', padx=(0, 2))

        self.rtheta_entry = ctk.CTkEntry(
            thetas_frame, font=configuration.button_font_style, width=40
        )
        self.rtheta_entry.insert(0, f'{self.parent.parent.array_config.Rtheta}')
        self.rtheta_entry.grid(row=0, column=3, sticky='w', padx=(0, 2))

        self.theta_inc_var = tk.StringVar(value=f'{self.parent.parent.array_config.increment}')
        self.theta_inc_seg = ctk.CTkSegmentedButton(
            thetas_frame,
            values=["10", "5", "2"],
            variable=self.theta_inc_var,
            width=60, font=configuration.button_font_style
        )
        self.theta_inc_seg.grid(row=0, column=4, sticky='w')

        # — Phis container (also fills columns 0–2) —
        phis_frame = ctk.CTkFrame(self)
        phis_frame.grid(
            row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=2
        )
        for c in range(5):
            phis_frame.grid_columnconfigure(c, weight=0)

        self.enable_phis = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            phis_frame, text="", variable=self.enable_phis,
            command=self.toggle_phis, font=configuration.button_font_style
        ).grid(row=0, column=0, sticky='w', padx=(0, 2))

        ctk.CTkLabel(
            phis_frame, text="Phi:", font=configuration.console_font_style
        ).grid(row=0, column=1, sticky='w', padx=(0, 5))

        self.lphi_entry = ctk.CTkEntry(
            phis_frame, font=configuration.button_font_style, width=40
        )
        self.lphi_entry.insert(0, "0")
        self.lphi_entry.grid(row=0, column=2, sticky='w', padx=(0, 2))

        self.rphi_entry = ctk.CTkEntry(
            phis_frame, font=configuration.button_font_style, width=40
        )
        self.rphi_entry.insert(0, "0")
        self.rphi_entry.grid(row=0, column=3, sticky='w', padx=(0, 2))

        self.phi_inc_var = tk.StringVar(value="10")
        self.phi_inc_seg = ctk.CTkSegmentedButton(
            phis_frame,
            values=["10", "5", "2"],
            variable=self.phi_inc_var,
            width=60, font=configuration.button_font_style
        )
        self.phi_inc_seg.grid(row=0, column=4, sticky='w')

        # Update Button (below theta and phi settings)
        self.update_thetas_button = ctk.CTkButton(
            self, text="Update",
            command=lambda: self.event_handler(Event.UPDATE_BEAM_DIRECTIONS), font=configuration.button_font_style
        )
        self.update_thetas_button.grid(row=3, column=0, columnspan=3, sticky='ew', padx=10, pady=(5, 10))

        # initialize visibility
        self.toggle_thetas()
        self.toggle_phis()

        # Temp Stuff -----------------------------------
        # Manual Temp Entry Frame
        manual_temp_frame = ctk.CTkFrame(self)
        manual_temp_frame.grid(row=4, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        # Center Container Frame
        center_frame = ctk.CTkFrame(manual_temp_frame)
        center_frame.pack(expand=True, padx=10, pady=5)

        # Manual Temp Entry Label, Entry Box, and Set Button
        self.manual_temp_entry_label = ctk.CTkLabel(center_frame, text="Manual Temp Entry", font=configuration.console_font_style)
        self.manual_temp_entry_label.pack(side='left', padx=(0, 5))  # Add space between label and entry

        # Entry Box
        self.manual_temp_entry = ctk.CTkEntry(center_frame, width=50, font=configuration.button_font_style)  # Adjust width to fit 3 digits
        self.manual_temp_entry.pack(side='left', padx=(0, 5))  # Add space between entry and button

        # Set Button
        self.set_button = ctk.CTkButton(center_frame, text="Set", command=self.set_temp, font=configuration.button_font_style)
        self.set_button.pack(side='left')

        # Default value for manual temperature entry
        self.manual_temp_entry.insert(0, "90")  # Set a default temperature value

    def set_temp(self):
        # Function to handle the 'Set' button click
        self.temp_value = self.manual_temp_entry.get()
        if self.temp_value != '':
            print(f"Temperature set to: {self.temp_value} F")
            self.event_handler(Event.SET_TEMP)

    def toggle_thetas(self):
        if self.enable_thetas.get():
            # reset back to your θ‑defaults
            self.ltheta_entry.configure(state="normal")
            self.ltheta_entry.delete(0, tk.END)
            self.ltheta_entry.insert(0, "-70")

            self.rtheta_entry.configure(state="normal")
            self.rtheta_entry.delete(0, tk.END)
            self.rtheta_entry.insert(0, "70")

            self.theta_inc_var.set("10")
            self.theta_inc_seg.configure(state="normal")
        else:
            # disable and set to 0
            for entry in (self.ltheta_entry, self.rtheta_entry):
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, "0")
                entry.configure(state="disabled")

            self.theta_inc_var.set("10")
            self.theta_inc_seg.configure(state="disabled")

    def toggle_phis(self):
        if self.enable_phis.get():
            # reset back to your φ‑defaults (here both 0)
            self.lphi_entry.configure(state="normal")
            self.lphi_entry.delete(0, tk.END)
            self.lphi_entry.insert(0, "0")

            self.rphi_entry.configure(state="normal")
            self.rphi_entry.delete(0, tk.END)
            self.rphi_entry.insert(0, "0")

            self.phi_inc_var.set("10")
            self.phi_inc_seg.configure(state="normal")
        else:
            # disable and set to 0
            for entry in (self.lphi_entry, self.rphi_entry):
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, "0")
                entry.configure(state="disabled")

            self.phi_inc_var.set("10")
            self.phi_inc_seg.configure(state="disabled")


class Bottom_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Row for the top label
        self.grid_rowconfigure(1, weight=1)  # Row for the settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.nr_std_threshold = 1.5
        self.hp_bottom_cutoff_freq = 1144
        self.nm_percentage = 100
        self.ds_new_sr = 6288



        self.processing_settings_frame()

    def processing_settings_frame(self):
        self.processing_settings_label = ctk.CTkLabel(self, text="Processing Settings", font=configuration.console_font_style)
        self.processing_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # NR: STD Threshold
        self.nr_std_threshold_label = ctk.CTkLabel(self, text="NR: STD Threshold (int): ", font=configuration.console_font_style)
        self.nr_std_threshold_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)
        self.nr_std_threshold_entry = ctk.CTkEntry(self, width=100)
        self.nr_std_threshold_entry.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        self.nr_std_threshold_set_button = ctk.CTkButton(self, text="Set", command=self.set_nr_std_threshold, font=configuration.button_font_style)
        self.nr_std_threshold_set_button.grid(row=1, column=2, sticky='w', padx=10, pady=5)
        self.nr_std_threshold_entry.insert(0, f'{self.nr_std_threshold}')  # Default value

        # HP: Bottom Cutoff Frequency
        self.hp_bottom_cutoff_freq_label = ctk.CTkLabel(self, text="HP: Bottom Cutoff Frequency (Hz): ", font=configuration.console_font_style)
        self.hp_bottom_cutoff_freq_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_entry = ctk.CTkEntry(self, width=100)
        self.hp_bottom_cutoff_freq_entry.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_set_button = ctk.CTkButton(self, text="Set", command=self.set_hp_bottom_cutoff_freq, font=configuration.button_font_style)
        self.hp_bottom_cutoff_freq_set_button.grid(row=2, column=2, sticky='w', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_entry.insert(0, f'{self.hp_bottom_cutoff_freq}')  # Default value

        # NM: Percentage
        self.nm_percentage_label = ctk.CTkLabel(self, text="NM: Percentage (%): ", font=configuration.console_font_style)
        self.nm_percentage_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)
        self.nm_percentage_entry = ctk.CTkEntry(self, width=100)
        self.nm_percentage_entry.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        self.nm_percentage_set_button = ctk.CTkButton(self, text="Set", command=self.set_nm_percentage, font=configuration.button_font_style)
        self.nm_percentage_set_button.grid(row=3, column=2, sticky='w', padx=10, pady=5)
        self.nm_percentage_entry.insert(0, f'{self.nm_percentage}')  # Default value

        # DS: New Sample Rate
        self.ds_new_sr_label = ctk.CTkLabel(self, text="DS: New Sample Rate (Hz): ", font=configuration.console_font_style)
        self.ds_new_sr_label.grid(row=4, column=0, sticky='e', padx=10, pady=5)
        self.ds_new_sr_entry = ctk.CTkEntry(self, width=100)
        self.ds_new_sr_entry.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        self.ds_new_sr_set_button = ctk.CTkButton(self, text="Set", command=self.set_ds_new_sr, font=configuration.button_font_style)
        self.ds_new_sr_set_button.grid(row=4, column=2, sticky='w', padx=10, pady=5)
        self.ds_new_sr_entry.insert(0, f'{self.ds_new_sr}')  # Default value

    def set_nr_std_threshold(self):
        nr_std_threshold = self.nr_std_threshold_entry.get()
        if nr_std_threshold:
            print(f"NR STD Threshold set to: {nr_std_threshold}")

    def set_hp_bottom_cutoff_freq(self):
        hp_bottom_cutoff_freq = self.hp_bottom_cutoff_freq_entry.get()
        if hp_bottom_cutoff_freq:
            print(f"HP Bottom Cutoff Frequency set to: {hp_bottom_cutoff_freq}")

    def set_nm_percentage(self):
        nm_percentage = self.nm_percentage_entry.get()
        if nm_percentage:
            print(f"NM Percentage set to: {nm_percentage}")

    def set_ds_new_sr(self):
        ds_new_sr = self.ds_new_sr_entry.get()
        if ds_new_sr:
            print(f"DS New Sample Rate set to: {ds_new_sr}")


class Bottom_Right_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Row for the top label
        self.grid_rowconfigure(1, weight=1)  # Row for the settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        self.max_anomaly_value = 50
        self.anomaly_threshold_value = 8
        self.pca_detector_settings_frame()

    def pca_detector_settings_frame(self):
        # Number of Components Label
        self.pca_detector_settings_label = ctk.CTkLabel(self, text="PCA Detector Settings", font=configuration.console_font_style)
        self.pca_detector_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        self.num_components_label = ctk.CTkLabel(self, text="Number of Components:", font=configuration.console_font_style)
        self.num_components_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)

        self.num_components_entry = ctk.CTkEntry(self, width=50)
        self.num_components_entry.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        self.num_components_entry.insert(0, "3")  # Default value

        self.num_components_set_button = ctk.CTkButton(self, text="Set", command=self.set_num_components, font=configuration.button_font_style)
        self.num_components_set_button.grid(row=1, column=2, sticky='w', padx=10, pady=5)

        # Threshold Multiplier Label
        self.threshold_multiplier_label = ctk.CTkLabel(self, text="Threshold Multiplier:", font=configuration.console_font_style)
        self.threshold_multiplier_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)

        self.threshold_multiplier_entry = ctk.CTkEntry(self, width=50)
        self.threshold_multiplier_entry.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        self.threshold_multiplier_entry.insert(0, "1.0")  # Default value

        self.threshold_multiplier_set_button = ctk.CTkButton(self, text="Set", command=self.set_threshold_multiplier, font=configuration.button_font_style)
        self.threshold_multiplier_set_button.grid(row=2, column=2, sticky='w', padx=10, pady=5)

        # anomaly threshold value Label
        self.anomaly_threshold_value_label = ctk.CTkLabel(self, text="Anomaly Threshold Value:", font=configuration.console_font_style)
        self.anomaly_threshold_value_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)

        self.anomaly_threshold_value_entry = ctk.CTkEntry(self, width=50)
        self.anomaly_threshold_value_entry.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        self.anomaly_threshold_value_entry.insert(0, f'{self.anomaly_threshold_value}')  # Default value

        self.anomaly_threshold_value_set_button = ctk.CTkButton(self, text="Set", command=self.set_anomaly_threshold_value, font=configuration.button_font_style)
        self.anomaly_threshold_value_set_button.grid(row=3, column=2, sticky='w', padx=10, pady=5)

        # max_anomaly_value Label
        self.max_anomaly_value_label = ctk.CTkLabel(self, text="Max Anomaly Value:", font=configuration.console_font_style)
        self.max_anomaly_value_label.grid(row=4, column=0, sticky='e', padx=10, pady=5)

        self.max_anomaly_value_entry = ctk.CTkEntry(self, width=50)
        self.max_anomaly_value_entry.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        self.max_anomaly_value_entry.insert(0, f'{self.max_anomaly_value}')  # Default value

        self.max_anomaly_value_set_button = ctk.CTkButton(self, text="Set", command=self.set_max_anomaly_value, font=configuration.button_font_style)
        self.max_anomaly_value_set_button.grid(row=4, column=2, sticky='w', padx=10, pady=5)

    def set_num_components(self):
        num_components = self.num_components_entry.get()
        if num_components:
            print(f"Number of components set to: {num_components}")

    def set_threshold_multiplier(self):
        threshold_multiplier = self.threshold_multiplier_entry.get()
        if threshold_multiplier:
            print(f"Threshold multiplier set to: {threshold_multiplier}")

    def set_anomaly_threshold_value(self):
        self.anomaly_threshold_value = self.anomaly_threshold_value_entry.get()
        if self.anomaly_threshold_value:
            print(f"Max Anomaly Value set to: {self.anomaly_threshold_value}")
            self.event_handler(Event.SET_ANOMALY_THRESHOLD_VALUE)

    def set_max_anomaly_value(self):
        self.max_anomaly_value = self.max_anomaly_value_entry.get()
        if self.max_anomaly_value:
            print(f"Max Anomaly Value set to: {self.max_anomaly_value}")
            self.event_handler(Event.SET_MAX_ANOMALY_VALUE)