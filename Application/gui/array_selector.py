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
    width, height = 400, 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Large fonts
    font_label = ("Helvetica", 16, "bold")
    font_button = ("Helvetica", 14)

    app_device = tk.StringVar(root, value='demo')

    tk.Label(root, text="Choose Array Type:", font=font_label).pack(pady=20)
    tk.Button(root, text="Line Array", font=font_button, width=20, height=2, command=choose_line).pack(pady=5)
    tk.Button(root, text="Rectangular Array", font=font_button, width=20, height=2, command=choose_rect).pack(pady=5)

    # Device selector
    tk.Label(root, text="Select Controller:", font=font_label).pack(pady=(20, 5))

    frame = tk.Frame(root)
    frame.pack()

    tk.Radiobutton(frame, text="Demo", variable=app_device, value="demo", font=font_button).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame, text="Mac", variable=app_device, value="mac", font=font_button).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame, text="Pi", variable=app_device, value="pi", font=font_button).pack(side=tk.LEFT, padx=10)

    root.mainloop()

    return selection, app_device.get()
