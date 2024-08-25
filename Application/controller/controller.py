
from Application.gui.settings import Settings_Window
from Application.controller.event_states import Event
from Application.controller.event_states import State


class Controller:
    def __init__(self):
        self.app_state = State.IDLE
        self.gui = None
        self.temp_sensor = None
        self.audio_recorder = None


    def add_peripherals(self, temp_sensor, audio_recorder, gui):
        self.temp_sensor = temp_sensor
        self.audio_recorder = audio_recorder
        self.gui = gui


    def handle_event(self, event):

        # Load from Specific Stimulus Number:
        if event == Event.SETTINGS:
            self.settings_window = Settings_Window(self.handle_event)
            self.settings_window.mainloop()

        elif event == Event.SETTINGS_BUTTON_1:
            print('SETTINGS BUTTON 1 PRESSED')

        elif event == Event.SETTINGS_BUTTON_2:
            print('SETTINGS BUTTON 2 PRESSED')

        elif event == Event.TAKE_PICTURE:
            print('TAKE PICTURE')

        elif event == Event.RECORD_VIDEO:
            print('RECORD VIDEO')

        elif event == Event.DUMMY_BUTTON:
            print('BUTTON PRESSED')