    
import tkinter
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Treeview
from enum import Enum

from sys_util_core.file_utils import LogSystem

# Singleton instance for the Tk root window
_root_instance = None
_mainloop_running = False

def get_root():
    global _root_instance, _mainloop_running
    if _root_instance is None:
        _root_instance = tkinter.Tk()
        _root_instance.withdraw()  # Hide the main window initially
    return _root_instance

def get_mainloop():
    global _mainloop_running
    root = get_root()
    if not _mainloop_running:
        try:
            _mainloop_running = True
            root.mainloop()
        finally:
            _mainloop_running = False  # mainloop 종료 시 플래그 리셋

class GuiType(Enum):
    MSG_BOX = "msg_box"
    FILE_DLG = "file_dialog"
    INPUT_DLG = "input_dialog"
    CONFIRM_DLG = "confirm_dialog"
    COLOR_DLG = "color_dialog"
    SAVE_FILE_DLG = "save_file_dialog"
    POPUP_CTT_MENU = "popup_context_menu"
    SCROLL_TEXT_WND = "scroll_text_window"
    PROGRESS_BAR_WND = "progress_bar_window"
    TREE_VIEW_WND = "tree_view_window"
    CANVAS_WND = "canvas_window"
    TOPLEVEL_SUB_WND = "toplevel_sub_window"
    MAIN_WND = "main_window"


def show_msg_box(message, title="Info"):
    try:        
        root = get_root()
        tkinter.messagebox.showinfo(title, message)
    except Exception as e:
        LogSystem.log_error(f"show_msg_box error: {e}")

def show_file_dialog(title="Select a file") -> str:
    try:
        root = get_root()
        file_path = filedialog.askopenfilename(title=title)
        return file_path
    except Exception as e:
        LogSystem.log_error(f"show_file_dialog error: {e}")
        return ""

def show_input_dialog(prompt="Please enter something:", title="Input") -> str:
    try:
        root = get_root()
        user_input = tkinter.simpledialog.askstring(title, prompt)
        return user_input
    except Exception as e:
        LogSystem.log_error(f"show_input_dialog error: {e}")
        return None

def show_confirm_dialog(message="Do you want to proceed?", title="Confirm") -> bool:
    try:
        root = get_root()
        result = tkinter.messagebox.askyesno(title, message)
        return result
    except Exception as e:
        LogSystem.log_error(f"show_confirm_dialog error: {e}")
        return False

def show_color_dialog(title="Choose a color") -> str:
    try:
        root = get_root()
        color_code = tkinter.colorchooser.askcolor(title=title)[1]
        return color_code
    except Exception as e:
        LogSystem.log_error(f"show_color_dialog error: {e}")
        return ""

def show_save_file_dialog(title="Save file as") -> str:
    try:
        root = get_root()
        file_path = filedialog.asksaveasfilename(title=title)
        return file_path
    except Exception as e:
        LogSystem.log_error(f"show_save_file_dialog error: {e}")
        return ""

def show_popup_context_menu(root, options=None):
    try:
        root = get_root()
        if options is None:
            options = [("Option 1", None), ("Option 2", None), ("Exit", root.quit)]

        def popup(event):
            popup_menu.post(event.x_root, event.y_root)

        popup_menu = tkinter.Menu(root, tearoff=0)
        for label, command in options:
            if label == "separator":
                popup_menu.add_separator()
            else:
                popup_menu.add_command(label=label, command=command)

        root.bind("<Button-3>", popup)
        root.deiconify()
        get_mainloop()
        
    except Exception as e:
        LogSystem.log_error(f"show_popup_context_menu error: {e}")

def show_scroll_text_window(title="Scroll Text Window"):
    try:
        root = get_root()
        top = tkinter.Toplevel(root)
        top.title(title)
        text_area = tkinter.Text(top, wrap="word")
        scroll_bar = tkinter.Scrollbar(top, command=text_area.yview)
        text_area.configure(yscrollcommand=scroll_bar.set)
        text_area.pack(side="left", fill="both", expand=True)
        scroll_bar.pack(side="right", fill="y")

    except Exception as e:
        LogSystem.log_error(f"show_scroll_text_window error: {e}")

def show_progress_bar_window(progress_value=50, title="Progress Bar Window"):
    try:
        root = get_root()
        top = tkinter.Toplevel(root)
        top.title(title)
        progress = Progressbar(top, orient="horizontal", length=200, mode="determinate")
        progress.pack(pady=20)
        progress["value"] = progress_value

    except Exception as e:
        LogSystem.log_error(f"show_progress_bar_window error: {e}")

def show_tree_view_window(columns=("one", "two"), items=None, title="Tree View Window"):
    try:
        if items is None:
            items = [("", "end", "Item 1", ("Value 1", "Value 2"))]
        root = get_root()
        top = tkinter.Toplevel(root)
        top.title(title)
        tree = Treeview(top)
        tree["columns"] = columns
        tree.heading("#0", text="Item")
        for col in columns:
            tree.heading(col, text=f"Column {col}")
        for parent, index, text, values in items:
            tree.insert(parent, index, text=text, values=values)
        tree.pack(fill="both", expand=True)

    except Exception as e:
        LogSystem.log_error(f"show_tree_view_window error: {e}")

def show_canvas_window(width=200, height=100, shapes=None, title="Canvas Window"):
    try:
        if shapes is None:
            shapes = [("rectangle", (50, 25, 150, 75), {"fill": "blue"})]

        root = get_root()
        root.title(title)
        canvas = tkinter.Canvas(root, width=width, height=height)
        canvas.pack()
        for shape, coords, options in shapes:
            getattr(canvas, f"create_{shape}")(*coords, **options)
        root.deiconify()
        get_mainloop()

    except Exception as e:
        LogSystem.log_error(f"show_canvas_window error: {e}")

def show_toplevel_window(message="This is a Toplevel window", title="TopLevel Window"):
    try:
        root = get_root()
        top = tkinter.Toplevel(root)
        top.title(title)
        tkinter.Label(top, text=message).pack()

    except Exception as e:
        LogSystem.log_error(f"show_toplevel_window error: {e}")

def show_main_window(message="This is the main window", title="Main Window"):
    try:
        root = get_root()
        root.deiconify()
        root.title(title)
        tkinter.Label(root, text=message).pack()
        get_mainloop()

    except Exception as e:
        LogSystem.log_error(f"show_main_window error: {e}")

