


from Application.controller.event_states import Event

import customtkinter as ctk
from PIL import ImageTk
import tkinter as tk
import subprocess
from PIL import Image
import sys


class Main_Window(ctk.CTk):
    def __init__(self, event_handler, array_config, configuration):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.event_handler = event_handler
        self.array_config = array_config
        self.device_config = configuration

        # Computer Icon
        self.img = Image.open(configuration.main_window_icon)
        icon = ImageTk.PhotoImage(self.img)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        if configuration.device_type == 'pi' and sys.platform != 'darwin':
            self.attributes('-fullscreen', True)

        # Main Setup ------------------------------------------------------------
        self.title(f'{self.device_config.window_title}: {self.array_config.title}')

        # Screen: can see window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (self.device_config.window_width / 2))
        center_y = int((screen_height / 2) - (self.device_config.window_height / 2))
        self.geometry(f'{self.device_config.window_width}x{self.device_config.window_height}+{center_x}+{center_y}')
        self.minsize(self.device_config.min_window_width, self.device_config.min_window_height)

        self.Top_Frame = Top_Frame(self, self.event_handler)
        self.Middle_Frame = Middle_Frame(self, self.event_handler)
        self.Bottom_Frame = Bottom_Frame(self, self.event_handler)

        # Configure grid rows with equal weight
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)

        self.Top_Frame.grid(row=0, column=0, sticky='nsew')
        self.Middle_Frame.grid(row=1, column=0, sticky='nsew')
        self.Bottom_Frame.grid(row=2, column=0, sticky='nsew')

        # Ending Procedures
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Escape>", self.on_close)
        self.bind("<Control-c>", self.on_close)

    def on_close(self, *args):
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
        configuration = self.parent.parent.device_config

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
        configuration = self.parent.parent.device_config
        self.fpga_connection_label = ctk.CTkLabel(frame, text="Microphone Connection Status", font=configuration.console_font_style)
        self.fpga_connection_label.pack(fill='both') # , expand=True
        self.fpga_status_label = ctk.CTkLabel(frame, text="Not Connected", text_color='red', font=configuration.console_font_style)
        self.fpga_status_label.pack(fill='both')  # , expand=True

    def rpi_connection_frame(self, frame):
        configuration = self.parent.parent.device_config
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
        configuration = self.parent.parent.device_config

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
        configuration = self.parent.parent.device_config
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

        self.chunk_time_entry = ctk.CTkEntry(button_frame, width=40, placeholder_text="1.0s", font=configuration.console_font_style_small)
        self.chunk_time_entry.grid(row=0, column=3, padx=5)

        entry_frame = ctk.CTkFrame(frame)
        entry_frame.pack(pady=10)

        self.project_name = ctk.CTkEntry(entry_frame, width=300, placeholder_text="Enter a Test Name, if desired...", font=configuration.button_font_style)
        self.project_name.pack()

    def load_audio_file(self):
        if self.parent.parent.device_config.device_type == 'mac':
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

        elif self.parent.parent.device_config.device_type == 'pi':
            try:
                from tkinter import filedialog
                audio_file_path = filedialog.askopenfilename(
                    title="Select Audio File",
                    filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.aac *.ogg *.m4a")]
                )

                if audio_file_path:
                    self.selected_audio_file = audio_file_path
                    print(f"Selected audio file: {self.selected_audio_file}")
                    self.event_handler(Event.LOAD_AUDIO)

            except Exception as e:
                print("File dialog failed:", e)

    def calibration_frame(self, frame):
        configuration = self.parent.parent.device_config
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

        self.calibration_time_entry = ctk.CTkEntry(button_frame, width=40, placeholder_text="60s", font=configuration.console_font_style_small)
        self.calibration_time_entry.grid(row=0, column=3, padx=5)

    def load_pca_file(self):
        if self.parent.parent.device_config.device_type == 'mac':
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
                    self.event_handler(Event.LOAD_CALIBRATION)

            except Exception as e:
                print("Folder dialog failed:", e)

        elif self.parent.parent.device_config.device_type == 'pi':
            try:
                from tkinter import filedialog
                folder_path = filedialog.askdirectory(
                    title="Select Folder Containing PCA Calibration Files"
                )

                if folder_path:
                    self.selected_pca_folder = folder_path
                    print(f"Selected PCA folder: {self.selected_pca_folder}")

                    self.event_handler(Event.LOAD_CALIBRATION)

            except Exception as e:
                print("Folder dialog failed:", e)

    def toggle_play(self):
        configuration = self.parent.parent.device_config
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
        configuration = self.parent.parent.device_config
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



class MicSelector(ctk.CTkFrame):
    def __init__(self, parent, shape, callback=None):
        super().__init__(parent)
        self.shape = shape  # (rows, cols)
        self.callback = callback  # Optional function to call on state change
        self.selected_mics = set()
        self.buttons = []

        mic_num = 0
        for r in range(shape[0]):
            row = []
            for c in range(shape[1]):
                text_display = f'{mic_num + 1} ' if mic_num + 1 < 10 else f'{mic_num + 1}'
                btn = ctk.CTkButton(self, text=text_display, width=5, height=5, corner_radius=2,
                                    font=("Arial", 9),
                                    fg_color="#444", hover_color="#888",
                                    command=lambda n=mic_num: self.toggle(n))
                btn.grid(row=r, column=c, padx=1, pady=1)
                row.append(btn)
                mic_num += 1
            self.buttons.append(row)

    def toggle(self, mic_index):
        if mic_index in self.selected_mics:
            self.selected_mics.remove(mic_index)
            self.set_color(mic_index, "#444")
        else:
            self.selected_mics.add(mic_index)
            self.set_color(mic_index, "#00aaff")
        if self.callback:
            self.callback()

    def set_color(self, mic_index, color):
        r, c = divmod(mic_index, self.shape[1])
        self.buttons[r][c].configure(fg_color=color)

    def get(self):
        return sorted(self.selected_mics)

    def rebuild(self, label_list, shape):
        # Set new shape
        self.shape = shape
        rows, cols = shape

        # Clear old widgets
        for row in self.buttons:
            for btn in row:
                btn.destroy()

        self.buttons = []
        self.selected_mics = set()

        mic_num = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if mic_num < len(label_list):
                    label = str(label_list[mic_num])
                else:
                    label = ""
                btn = ctk.CTkButton(self, text=label, width=5, height=5, corner_radius=2,
                                    font=("Arial", 9),
                                    fg_color="#444", hover_color="#888",
                                    command=lambda n=mic_num: self.toggle(n))
                btn.grid(row=r, column=c, padx=1, pady=1)
                row.append(btn)
                mic_num += 1
            self.buttons.append(row)

        # if label_list:
        #     self.toggle(0)

class Top_Middle_Right_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent
        configuration = self.parent.parent.device_config

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
        configuration = self.parent.parent.device_config
        self.clock_display = ctk.CTkLabel(
            frame, text="00:00", font=configuration.console_font_style_large
        )
        self.clock_display.pack(pady=5)

        self.real_time_checkbox_variable = ctk.BooleanVar(value=True)

        self.real_time_checkbox = ctk.CTkCheckBox(frame, text="Real-Time",
                                                  variable=self.real_time_checkbox_variable,
                                                  fg_color=configuration.bluelight_fg_color,
                                                  hover_color=configuration.bluelight_hover_color, font=configuration.button_font_style)
        self.real_time_checkbox.pack(pady=5)

        self.play_external_button = ctk.CTkButton(frame, text="Start External Audio",
                                          fg_color=configuration.purple_fg_color,
                                          hover_color=configuration.purple_hover_color,
                                          command=lambda: self.event_handler(Event.START_EXTERNAL_PLAY),
                                          font=configuration.button_font_style)
        self.play_external_button.pack(pady=5)

        self.stream_location = ctk.CTkSegmentedButton(
            frame,
            values=["Raw", "Beam", "Pro"],
            font=configuration.button_font_style,
            height=28,
            command=lambda value: self.event_handler(Event.CHANGE_EXTERNAL_PLAYER)
        )
        self.stream_location.set("Raw")
        self.stream_location.pack(pady=(10, 5))


        self.mic_selector = MicSelector(frame, shape=[self.parent.parent.array_config.rows, self.parent.parent.array_config.cols],
                                        callback=lambda: self.event_handler(Event.CHANGE_EXTERNAL_PLAYER_CHANNELS))
        self.mic_selector.pack(pady=5)



        # self.human_op_mode_button = ctk.CTkButton(frame, text="Human Op Mode",
        #                                           fg_color=configuration.bluelight_fg_color,
        #                                           hover_color=configuration.bluelight_hover_color,
        #                                           command=lambda: self.event_handler(Event.START_HUMAN_OP_MODE),
        #                                           font=configuration.button_font_style)
        # self.human_op_mode_button.pack(pady=5)

    def toggle_play_external_button(self):
        configuration = self.parent.parent.device_config
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
        configuration = self.parent.parent.device_config

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
        configuration = self.parent.parent.device_config
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
        self.configuration = self.parent.parent.device_config

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Left
        self.grid_columnconfigure(1, weight=1)  # Center
        self.grid_columnconfigure(2, weight=0)  # Right

        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_columnconfigure(0, weight=1)

        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        center_frame.rowconfigure(1, weight=1)  # Let row 1 (image) expand
        center_frame.grid_columnconfigure(0, weight=1)

        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        self.detector_frame(left_frame)
        self.heatmap_frame(center_frame)
        self.classification(right_frame)

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
        self.anomaly_data = [0] * len(self.directions)

        self.start_heatmap_updates()
        self.start_updates()

    def detector_frame(self, frame):
        self.detector_label = ctk.CTkLabel(frame, text="Beamformed PCA Detector Output", font=self.configuration.console_font_style)
        self.detector_label.grid(row=0, column=0, sticky='ew')

        self.canvas_left_width = self.configuration.detector_canvas_width
        self.canvas_left = tk.Canvas(frame, bg="#333333",
                                     width=self.canvas_left_width,
                                     height=self.configuration.detector_canvas_height)
        self.canvas_left.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        self.canvas_left.master.grid_propagate(False)

    def heatmap_frame(self, frame):
        self.heatmap_title = ctk.CTkLabel(frame, text="Time Series Heatmap of Anomalies", font=self.configuration.console_font_style)
        self.heatmap_title.grid(row=0, column=0, sticky='ew')

        # New: Image container
        self.heatmap_canvas = tk.Label(frame, bg="black",
                                       width=self.configuration.heatmap_canvas_width,
                                       height=self.configuration.heatmap_canvas_height)
        self.heatmap_canvas.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        self.heatmap_canvas.master.grid_propagate(False)

    def classification(self, frame):
        self.classifier_label = ctk.CTkLabel(frame, text="Sound Classifier", font=self.configuration.console_font_style)
        self.classifier_label.grid(row=0, column=0, sticky='ew')

        # Create a subframe to hold the icons
        icon_frame = ctk.CTkFrame(frame, fg_color="transparent")
        icon_frame.grid(row=1, column=0)

        size = 40
        horizontal_pad = self.configuration.classification_horizontal_pad

        self.icons = {
            'drone': ctk.CTkImage(Image.open(self.configuration.drone_icon), size=(size, size)),
            'plane': ctk.CTkImage(Image.open(self.configuration.plane_icon), size=(size, size)),
            'tank': ctk.CTkImage(Image.open(self.configuration.tank_icon), size=(size, size)),
            'generator': ctk.CTkImage(Image.open(self.configuration.generator_icon), size=(size, size)),
            'car': ctk.CTkImage(Image.open(self.configuration.car_icon), size=(size, size)),
        }

        for icon in self.icons.values():
            label = ctk.CTkLabel(icon_frame, image=icon, text="")
            label.pack(side="left", padx=horizontal_pad, pady=5)

    def draw_bar_chart(self):
        font_size = 9

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
        self.Center_Frame = Bottom_Center_Frame(self, self.event_handler)
        self.Middle_Center_Frame = Bottom_Middle_Center_Frame(self, self.event_handler)
        self.Middle_Frame = Bottom_Middle_Frame(self, self.event_handler)
        self.Right_Frame = Bottom_Right_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space
        self.columnconfigure(1, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(2, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(3, weight=1)  # Right column with x/3 of the space
        self.columnconfigure(4, weight=1)  # Right column with x/3 of the space

        # Place the frames using grid
        self.Left_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        self.Middle_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1
        self.Middle_Center_Frame.grid(row=0, column=2, sticky='nsew')  # Right frame in column 1
        self.Center_Frame.grid(row=0, column=3, sticky='nsew')  # Right frame in column 1
        self.Right_Frame.grid(row=0, column=4, sticky='nsew')  # Right frame in column 1


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
        configuration = self.parent.parent.device_config
        # Beamform Settings Label
        self.beamform_settings_label = ctk.CTkLabel(self, text="Beamform Settings", font=configuration.console_font_style)
        self.beamform_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # — Thetas container (fills columns 0–2 of the parent) —
        thetas_frame = ctk.CTkFrame(self)
        thetas_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
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
        config = self.parent.parent.array_config
        if self.enable_thetas.get():
            # reset back to your θ‑defaults
            self.ltheta_entry.configure(state="normal")
            self.ltheta_entry.delete(0, tk.END)
            self.ltheta_entry.insert(0, str(config.Ltheta))

            self.rtheta_entry.configure(state="normal")
            self.rtheta_entry.delete(0, tk.END)
            self.rtheta_entry.insert(0, str(config.Rtheta))

            self.theta_inc_var.set(str(config.increment))
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
        config = self.parent.parent.array_config
        if self.enable_phis.get():
            # reset back to your φ‑defaults (here both 0)
            self.lphi_entry.configure(state="normal")
            self.lphi_entry.delete(0, tk.END)
            self.lphi_entry.insert(0, str(config.Lphi))

            self.rphi_entry.configure(state="normal")
            self.rphi_entry.delete(0, tk.END)
            self.rphi_entry.insert(0, str(config.Rphi))

            self.phi_inc_var.set(str(config.phi_increment))
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


class Bottom_Middle_Center_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Label
        self.grid_rowconfigure(1, weight=0)  # Visual selector
        self.grid_rowconfigure(2, weight=0)  # Slider
        self.grid_rowconfigure(3, weight=0)  # Tick labels
        self.grid_rowconfigure(4, weight=1)  # Empty space below
        self.grid_rowconfigure(5, weight=1)  # Empty space below
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.heatmap_settings_frame()

    def heatmap_settings_frame(self):
        configuration = self.parent.parent.device_config
        self.heatmap_settings_label = ctk.CTkLabel(
            self, text="Heatmap Settings", font=configuration.console_font_style
        )
        self.heatmap_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=(10, 5))

        # Slim visual selector (no vertical stretching)
        self.visual_selector = ctk.CTkSegmentedButton(
            self,
            values=["Visual 1", "Visual 2", "Visual 3", "Visual 4"],
            # command=self.handle_visual_selection,
            font=configuration.button_font_style,
            height=28  # reduce the button height directly
        )
        self.visual_selector.set("Visual 1")
        self.visual_selector.grid(row=1, column=0, columnspan=3, pady=(0, 10), padx=40, sticky='ew')

        # Slider with value label
        self.value_slider = ctk.CTkSlider(
            self,
            from_=1,
            to=200,
            number_of_steps=200,
            command=self.update_slider_label
        )
        self.value_slider.set(100)
        self.value_slider.grid(row=2, column=0, columnspan=5, padx=10, pady=(0, 2), sticky="ew")

        # Slider tick labels below
        self.slider_min_label = ctk.CTkLabel(self, text="Less Sensitive", font=configuration.console_font_style_small)
        self.slider_mid_label = ctk.CTkLabel(self, text="|", font=configuration.console_font_style_small)
        self.slider_max_label = ctk.CTkLabel(self, text="More Sensitive", font=configuration.console_font_style_small)

        self.slider_min_label.grid(row=3, column=0, sticky="w", padx=10)
        self.slider_mid_label.grid(row=3, column=1, sticky="n")
        self.slider_max_label.grid(row=3, column=2, sticky="e", padx=10)

        self.heatmap_anom_settings_label = ctk.CTkLabel(
            self, text="Anomaly Max/Sensitivity Settings", font=configuration.button_font_style
        )
        self.heatmap_anom_settings_label.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=10, pady=(10, 5))

        # Slim visual selector (no vertical stretching)
        self.hp_max_selector = ctk.CTkSegmentedButton(
            self,
            values=["global", "local"],
            # command=self.handle_visual_selection,
            font=configuration.button_font_style,
            height=28  # reduce the button height directly
        )
        self.hp_max_selector.set("global")
        self.hp_max_selector.grid(row=5, column=0, pady=(0, 10), padx=40, sticky='ew')

        self.hp_max_options = ctk.CTkSegmentedButton(
            self,
            values=["1", "2", "3", "4", "5"],
            font=configuration.button_font_style,
            height=28
        )
        self.hp_max_options.set("2")
        self.hp_max_options.grid(row=5, column=2, pady=(0, 10), padx=(5, 40), sticky='ew')

    def handle_visual_selection(self, value):
        print(f"Selected: {value}")

    def update_slider_label(self, value):
        pass  # Or add live value updating if you want an extra label



class Bottom_Middle_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent
        self.array_config = self.parent.parent.array_config

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Row for the top label
        self.grid_rowconfigure(1, weight=1)  # Row for the settings
        self.grid_rowconfigure(2, weight=1)  # Row for the settings
        self.grid_rowconfigure(3, weight=1)  # Row for the settings
        self.grid_rowconfigure(4, weight=1)  # Row for the settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.hp_bottom_cutoff_freq = self.array_config.beam_mix_1.processing_chain.get('hp')
        self.ds_new_sr = self.array_config.beam_mix_1.processing_chain.get('ds')
        self.center_freq = self.array_config.beam_mix_1.center_frequency
        self.beam_mix_num_mics = self.array_config.beam_mix_1.num_mics
        self.beam_mix_spcaing = self.array_config.beam_mix_1.mic_spacing
        self.current_beam_mix = self.array_config.beam_mix_1

        self.beam_mix_settings_frame()

    def beam_mix_settings_frame(self):
        configuration = self.parent.parent.device_config

        self.beam_mix_settings_label = ctk.CTkLabel(self, text="Beam Mixture Options", font=configuration.console_font_style)
        self.beam_mix_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        self.beam_mixture_selector = ctk.CTkSegmentedButton(
            self,
            values=["Mix 1", "Mix 2", "Mix 3", "Mix 4"],
            font=configuration.button_font_style,
            height=28,
            command=lambda value: self.event_handler(Event.CHANGE_BEAM_MIXTURE)
        )
        self.beam_mixture_selector.set("Mix 1")
        self.beam_mixture_selector.grid(row=1, column=0, columnspan=3, pady=(10, 5), sticky='nsew')

        self.beam_mix_settings_label = ctk.CTkLabel(self,
                                                    text=f'Center: {self.center_freq}Hz   |   #Mics: {self.beam_mix_num_mics}   |   Sp: {self.beam_mix_spcaing}m',
                                                    font=configuration.console_font_style)
        self.beam_mix_settings_label.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # DS: New Sample Rate
        self.ds_new_sr_label = ctk.CTkLabel(self, text="DS (Hz): ", font=configuration.console_font_style)
        self.ds_new_sr_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)
        self.ds_new_sr_entry = ctk.CTkEntry(self, width=100, font=configuration.button_font_style)
        self.ds_new_sr_entry.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        self.ds_new_sr_set_button = ctk.CTkButton(self, text="Set", command=self.set_ds_new_sr, font=configuration.button_font_style)
        self.ds_new_sr_set_button.grid(row=3, column=2, sticky='w', padx=10, pady=5)
        self.ds_new_sr_entry.insert(0, f'{self.ds_new_sr}')  # Default value

        # HP: Bottom Cutoff Frequency
        self.hp_bottom_cutoff_freq_label = ctk.CTkLabel(self, text="HP (Hz): ", font=configuration.console_font_style)
        self.hp_bottom_cutoff_freq_label.grid(row=4, column=0, sticky='e', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_entry = ctk.CTkEntry(self, width=100, font=configuration.button_font_style)
        self.hp_bottom_cutoff_freq_entry.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_set_button = ctk.CTkButton(self, text="Set", command=self.set_hp_bottom_cutoff_freq, font=configuration.button_font_style)
        self.hp_bottom_cutoff_freq_set_button.grid(row=4, column=2, sticky='w', padx=10, pady=5)
        self.hp_bottom_cutoff_freq_entry.insert(0, f'{self.hp_bottom_cutoff_freq}')  # Default value

    def update_center_freq_label(self):
        mix = self.beam_mixture_selector.get()
        mix_config = {
            'Mix 1': self.array_config.beam_mix_1,
            'Mix 2': self.array_config.beam_mix_2,
            'Mix 3': self.array_config.beam_mix_3,
            'Mix 4': self.array_config.beam_mix_4,
        }

        self.current_beam_mix = mix_config.get(mix)


        self.center_freq = self.current_beam_mix.center_frequency
        self.hp_bottom_cutoff_freq = self.current_beam_mix.processing_chain.get('hp')
        self.ds_new_sr = self.current_beam_mix.processing_chain.get('ds')
        self.beam_mix_num_mics = self.current_beam_mix.num_mics
        self.beam_mix_spacing = self.current_beam_mix.mic_spacing

        self.ds_new_sr_entry.delete(0, 'end')
        self.ds_new_sr_entry.insert(0, f'{self.ds_new_sr}')

        self.hp_bottom_cutoff_freq_entry.delete(0, 'end')
        self.hp_bottom_cutoff_freq_entry.insert(0, f'{self.hp_bottom_cutoff_freq}')

        self.beam_mix_settings_label.configure(
            text=f'Center: {self.center_freq}Hz   |   #Mics: {self.beam_mix_num_mics}   |   Sp: {self.beam_mix_spacing}m'
        )

    def set_hp_bottom_cutoff_freq(self):
        hp_bottom_cutoff_freq = self.hp_bottom_cutoff_freq_entry.get()
        if hp_bottom_cutoff_freq:
            print(f"HP Bottom Cutoff Frequency set to: {hp_bottom_cutoff_freq}")

    def set_ds_new_sr(self):
        ds_new_sr = self.ds_new_sr_entry.get()
        if ds_new_sr:
            print(f"DS New Sample Rate set to: {ds_new_sr}")


class Bottom_Center_Frame(ctk.CTkFrame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.parent = parent

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)  # Settings label
        self.grid_rowconfigure(1, weight=0)  # Wind Bias label
        self.grid_rowconfigure(2, weight=0)  # Wind Bias inputs + button
        self.grid_rowconfigure(3, weight=0)  # Edge Suppression label
        self.grid_rowconfigure(4, weight=0)  # Edge Suppression inputs + button
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)  # for the buttons

        # Wind bias defaults
        self.default_scale_factor = "0.9"
        self.default_margin_bias = "0.5"
        self.default_theta_ratio = "0.7"

        # Edge suppression defaults
        self.default_edge_width = "4"
        self.default_suppression_factor = "0.5"
        self.box_width = 20

        self.detector_settings_frame()

    def detector_settings_frame(self):
        configuration = self.parent.parent.device_config

        self.settings_label = ctk.CTkLabel(
            self, text="Anomaly Filtering Settings", font=configuration.console_font_style
        )
        self.settings_label.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

        # Row 1: Labels for wind bias inputs + section label at end
        self.scale_factor_label = ctk.CTkLabel(self, text="Scale Factor", font=configuration.console_font_style_small)
        self.scale_factor_label.grid(row=1, column=0, padx=5, pady=2, sticky='ew')

        self.margin_bias_label = ctk.CTkLabel(self, text="Margin Bias", font=configuration.console_font_style_small)
        self.margin_bias_label.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        self.theta_ratio_label = ctk.CTkLabel(self, text="Theta Ratio", font=configuration.console_font_style_small)
        self.theta_ratio_label.grid(row=1, column=2, padx=5, pady=2, sticky='ew')

        self.wind_bias_label = ctk.CTkLabel(self, text="Wind Bias Removal", font=configuration.console_font_style_small)
        self.wind_bias_label.grid(row=1, column=3, padx=5, pady=2, sticky='ew')

        self.scale_factor_entry = ctk.CTkEntry(self, width=self.box_width, font=configuration.button_font_style)
        self.scale_factor_entry.insert(0, self.default_scale_factor)
        self.scale_factor_entry.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        self.margin_bias_entry = ctk.CTkEntry(self, width=self.box_width, font=configuration.button_font_style)
        self.margin_bias_entry.insert(0, self.default_margin_bias)
        self.margin_bias_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        self.theta_ratio_entry = ctk.CTkEntry(self, width=self.box_width, font=configuration.button_font_style)
        self.theta_ratio_entry.insert(0, self.default_theta_ratio)
        self.theta_ratio_entry.grid(row=2, column=2, padx=5, pady=5, sticky='ew')

        self.set_bias_button = ctk.CTkButton(self, text="Set Bias",
                                             command=lambda: self.event_handler(Event.UPDATE_ANOMALY_SETTINGS),
                                             font=configuration.button_font_style)
        self.set_bias_button.grid(row=2, column=3, padx=5, pady=5, sticky='ew')

        # Row 3: Labels for edge suppression inputs + section label at end
        self.edge_width_label = ctk.CTkLabel(self, text="Edge Width", font=configuration.console_font_style_small)
        self.edge_width_label.grid(row=3, column=1, padx=5, pady=2, sticky='ew')

        self.suppression_factor_label = ctk.CTkLabel(self, text="Sup. Factor", font=configuration.console_font_style_small)
        self.suppression_factor_label.grid(row=3, column=2, padx=5, pady=2, sticky='ew')

        self.edge_suppression_label = ctk.CTkLabel(self, text="Edge Suppression", font=configuration.console_font_style_small)
        self.edge_suppression_label.grid(row=3, column=3, padx=5, pady=2, sticky='ew')

        self.edge_width_entry = ctk.CTkEntry(self, width=self.box_width, font=configuration.button_font_style)
        self.edge_width_entry.insert(0, self.default_edge_width)
        self.edge_width_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        self.suppression_factor_entry = ctk.CTkEntry(self, width=self.box_width, font=configuration.button_font_style)
        self.suppression_factor_entry.insert(0, self.default_suppression_factor)
        self.suppression_factor_entry.grid(row=4, column=2, padx=5, pady=5, sticky='ew')

        self.set_edge_button = ctk.CTkButton(self, text="Set Edge",
                                             command=lambda: self.event_handler(Event.UPDATE_ANOMALY_SETTINGS),
                                             font=configuration.button_font_style)
        self.set_edge_button.grid(row=4, column=3, padx=5, pady=5, sticky='ew')


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

        self.max_anomaly_value = 2500 # 1500 # 50
        self.anomaly_threshold_value = 2 # 3 # 8
        self.box_width = 60

        self.pca_detector_settings_frame()

    def pca_detector_settings_frame(self):
        configuration = self.parent.parent.device_config

        # Number of Components Label
        self.pca_detector_settings_label = ctk.CTkLabel(self, text="PCA Detector Settings", font=configuration.console_font_style)
        self.pca_detector_settings_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        self.num_components_label = ctk.CTkLabel(
            self, text="# Comps:", font=configuration.console_font_style
        )
        self.num_components_label.grid(row=1, column=0, sticky='e', padx=(10, 5), pady=5)

        self.num_components_selector = ctk.CTkSegmentedButton(
            self,
            values=["3", "4", "5", "6"],
            command=self.set_num_components,
            font=configuration.button_font_style,
            height=28
        )
        self.num_components_selector.set("3")
        self.num_components_selector.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=5, sticky='ew')

        # anomaly threshold value Label
        self.anomaly_threshold_value_label = ctk.CTkLabel(
            self, text="Anom Thres:", font=configuration.console_font_style
        )
        self.anomaly_threshold_value_label.grid(row=2, column=0, sticky='e', padx=(10, 5), pady=5)

        self.anomaly_threshold_selector = ctk.CTkSegmentedButton(
            self,
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            command = self.set_anomaly_threshold_value,
            font=configuration.button_font_style,
            height=28
        )
        self.anomaly_threshold_selector.set("1")
        self.anomaly_threshold_selector.grid(row=2, column=1, columnspan=2, padx=(5, 10), pady=5, sticky='ew')

        self.max_anomaly_value_label = ctk.CTkLabel(
            self, text="Max Anom:", font=configuration.console_font_style
        )
        self.max_anomaly_value_label.grid(row=3, column=0, sticky='e', padx=(10, 5), pady=5)

        self.max_anomaly_value_slider = ctk.CTkSlider(
            self,
            from_=50,
            to=3500,
            number_of_steps=(3500 - 50) // 10,  # step size of 10
            orientation="horizontal",
            width=200
        )
        self.max_anomaly_value_slider.set(2800)
        self.max_anomaly_value_slider.grid(row=3, column=1, padx=(5, 10), pady=5, sticky='ew')

        self.max_anomaly_value_display = ctk.CTkLabel(
            self,
            text="2800",
            font=configuration.button_font_style,
            width=50,
            anchor="w"
        )
        self.max_anomaly_value_display.grid(row=3, column=2, padx=(5, 10), pady=5, sticky='w')

        def update_max_anomaly_label(value):
            rounded = int(round(value / 10) * 10)
            self.max_anomaly_value_display.configure(text=str(rounded).rjust(4))

        self.max_anomaly_value_slider.configure(command=update_max_anomaly_label)

        self.normalization_checkbox = ctk.CTkCheckBox(self, text="Normalization", font=configuration.button_font_style)
        self.normalization_checkbox.deselect()
        self.normalization_checkbox.grid(row=5, column=0, columnspan=4, pady=10)

    def set_num_components(self, value):
        num_components = self.num_components_selector.get()
        if num_components:
            print(f"Number of components set to: {num_components}")
            self.event_handler(Event.SET_NUM_COMPS)

    def set_anomaly_threshold_value(self, value):
        self.anomaly_threshold_value = self.anomaly_threshold_selector.get()
        if self.anomaly_threshold_value:
            print(f"Max Anomaly Value set to: {self.anomaly_threshold_value}")
            self.event_handler(Event.SET_ANOMALY_THRESHOLD_VALUE)
