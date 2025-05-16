import tkinter as tk
import sys

def get_array_selection():
    selection = None

    def choose_rect():
        nonlocal selection
        selection = 'RECT'
        root.destroy()

    def choose_line():
        nonlocal selection
        selection = 'LINE'
        root.destroy()

    def on_close():
        sys.exit(0)

    root = tk.Tk()
    root.title("Select Array Configuration")

    # Make the window big
    width, height = 400, 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Large fonts
    font_label = ("Helvetica", 16, "bold")
    font_button = ("Helvetica", 14)

    tk.Label(root, text="Choose Array Type:", font=font_label).pack(pady=20)
    tk.Button(root, text="Line Array", font=font_button, width=20, height=2, command=choose_line).pack(pady=5)
    tk.Button(root, text="Rectangular Array", font=font_button, width=20, height=2, command=choose_rect).pack(pady=5)


    root.mainloop()

    return selection
