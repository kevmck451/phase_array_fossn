


from Application.controller.event_states import Event
import Application.gui.configuration as configuration



import customtkinter as ctk





class Main_Window(ctk.CTk):
    def __init__(self, event_handler):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.event_handler = event_handler

        # Computer Icon
        # img = Image.open(configuration.main_window_icon)
        # icon = ImageTk.PhotoImage(img)
        # self.tk.call('wm', 'iconphoto', self._w, icon)

        # Main Setup ------------------------------------------------------------
        self.title(configuration.window_title)

        # Screen: full screen
        # self.attributes('-fullscreen', True)

        # Screen: can see window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (configuration.window_width / 2))
        center_y = int((screen_height / 2) - (configuration.window_height / 2))
        self.geometry(f'{configuration.window_width}x{configuration.window_height}+{center_x}+{center_y}')
        self.minsize(configuration.min_window_width, configuration.min_window_height)

        # -------------------------------
        # MAIN TWO LEVELS: TOP AND BOTTOM
        # -------------------------------
        self.Console_Frame = Console_Frame(self)
        self.Main_Frame = Main_Frame(self, self.Console_Frame, self.event_handler)

        # Configure grid rows with equal weight
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)

        # Place the frames using grid
        self.Console_Frame.grid(row=0, column=0, sticky='nsew')
        self.Main_Frame.grid(row=1, column=0, sticky='nsew')

        self.columnconfigure(0, weight=1)

        # Ending Procedures
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Escape>", self.close_application)
        self.bind("<Control-c>", self.close_application)

    def set_video_sender(self, video_server):
        self.video_sender = video_server

    def on_close(self):
        # Perform any cleanup or process termination steps here
        # For example, safely terminate any running threads, save state, release resources, etc.
        # self.matrix_mics.stop_stream()
        self.event_handler(Event.ON_CLOSE)
        self.destroy()

    def close_application(self, event=None):
        # Perform any cleanup or process termination steps here
        # Then close the application
        self.on_close()




# ---------------------------------------------------
# CONSOLE FRAME --------------------------------------
# ---------------------------------------------------
class Console_Frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(padx=configuration.x_pad_main, pady=configuration.y_pad_main, sticky='nsew')

        # Configure the columns and rows of main_frame to expand
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        self.console_box(main_frame)

    def console_box(self, frame):
        # Experiment Metadata Info Box (Title)
        self.title = ctk.CTkLabel(frame, text="FOSSN Phased Array", font=configuration.console_font_style)
        # Place the title in the third column, centered
        self.title.grid(row=0, column=0, padx=configuration.console_x_pad, pady=configuration.console_y_pad, sticky='nsew')

        self.main_info_label = ctk.CTkLabel(frame, text="University of Memphis", font=configuration.console_font_style)
        # Place the main info label in the third column, centered
        self.main_info_label.grid(row=1, column=0, padx=configuration.console_x_pad, pady=configuration.console_y_pad, sticky='nsew')




# ---------------------------------------------------
# MAIN FRAME --------------------------------------
# ---------------------------------------------------
class Main_Frame(ctk.CTkFrame):
    def __init__(self, parent, console_frame, event_handler):
        super().__init__(parent)
        self.console_frame = console_frame
        self.event_handler = event_handler
        self.parent = parent

        # self.Left_Frame = Left_Frame(self, self.event_handler)
        # self.Center_Frame = Video_Frame(self, self.event_handler)
        # self.Right_Frame = Right_Frame(self, self.event_handler)

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left column with x/3 of the space
        self.columnconfigure(1, weight=2)  # Right column with x/3 of the space
        self.columnconfigure(2, weight=1)  # Right column with x/3 of the space




        # Place the frames using grid
        # self.Left_Frame.grid(row=0, column=0, sticky='nsew')  # Left frame in column 0
        # self.Center_Frame.grid(row=0, column=1, sticky='nsew')  # Right frame in column 1
        # self.Right_Frame.grid(row=0, column=2, sticky='nsew')  # Right frame in column 1

