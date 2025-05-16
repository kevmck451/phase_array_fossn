import os

def base_path(relative_path):
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_script_dir))
    return os.path.join(base_dir, relative_path)

# Main App Settings
window_title = 'University of Memphis Acoustic'

window_width = 1680 # 1400 # 3200 1400
window_height = 960 # 800  # 1200 800
min_window_width = window_width
min_window_height = window_height
x_pad_main = 2
y_pad_main = 2
x_pad_1 = 10
y_pad_1 = 10
x_pad_2 = 10
y_pad_2 = 10
main_font_style = "default_font"
small_font_size = 9
main_font_size = 18 #26
large_font_size = 54
button_font_size = 14

main_window_icon = base_path('docs/papa_icon.png')
playing_icon_filepath = base_path('docs/playing icon s.png')
playing_icon_s_filepath = base_path('docs/playing icon ss.png')
start_icon_filepath = base_path('docs/start icon s.png')
stop_icon_filepath = base_path('docs/stop icon s.png')
pause_icon_filepath = base_path('docs/pause icon s.png')
load_icon_filepath = base_path('docs/load icon s.png')
settings_icon_filepath = base_path('docs/settings icon s.png')
reset_icon_filepath = base_path('docs/reset icon s.png')



# Console Settings
console_x_pad = 5
console_y_pad = 1

console_font_style_small = (main_font_style, small_font_size)
console_font_style = (main_font_style, main_font_size)
console_font_style_large = (main_font_style, large_font_size)

button_font_style = (main_font_style, button_font_size)

# Main Frame Settings



# Color Options

# Start / Stop
start_fg_color="#2B881A"
start_hover_color='#389327'
stop_fg_color="#BD2E2E"
stop_hover_color='#C74343'

# Pause Frame
pause_fg_color = '#8F8F8F'
pause_hover_color = '#9E9E9E'


# Overlay Colors
green_fg_color="#2B881A"
green_hover_color='#389327'
red_fg_color="#BD2E2E"
red_hover_color='#C74343'
bluelight_fg_color = '#578CD5'
bluelight_hover_color = '#496FA3'

device_type = 'mac'

# Other Colors
gray_fg_color = '#8F8F8F'
gray_hover_color = '#9E9E9E'
darkgray_fg_color = '#4a4949'
darkgray_hover_color = '#5c5b5b'
purple_fg_color = '#8270E7'
purple_hover_color = '#8F7FE9'
blue_hover_color = '#0F5BB6'
blue_fg_color = '#0952AA'
not_connected_color = '#BD2E2E'
connected_color = '#2B881A'


# Settings Window
settings_window_title = 'Experiment Settings'
settings_window_width = 400
settings_window_height = 400
settings_min_window_width = 400
settings_min_window_height = 400
settings_window_icon_filepath = 'docs/settings window icon.png'
x_pad_setting = 5
y_pad_setting = 5


# Overlay Threshold Window
overlay_threshold_window_title = 'Overlay Threshold Adjustments'

row_weight = 0
column_weight = 0
