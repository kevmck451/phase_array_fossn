
from Application.gui.window_main import Main_Window
from Application.controller.controller import Controller
from Application.engine.array.AudioStream import Mic_Array
from Application.engine.temp_sensor.client import Sender_Client
from Application.gui.array_selector import get_array_selection



# ssh -L 7654:192.168.1.201:2048 admin@192.168.1.1


if __name__ == "__main__":

    selection, app_device = get_array_selection()

    if selection == 'RECT':
        from Application.engine.array import array_config_RECT as array_config
    else: from Application.engine.array import array_config_LINE as array_config

    if app_device == 'mac' or app_device == 'other':
        from Application.gui import configuration as device_config
    if app_device == 'pi':
        from Application.gui import configuration_pi as device_config

    temp_sensor = Sender_Client(name='macbook')
    audio_realtime = Mic_Array(array_config)

    controller = Controller(array_config, app_device)

    gui = Main_Window(controller.handle_event, array_config, device_config)

    controller.add_peripherals(temp_sensor, audio_realtime, gui)

    gui.mainloop()
