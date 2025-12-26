# Standard Library Imports
import os, sys, ctypes
import time
from datetime import datetime
from enum import Enum
from typing import Optional

import tkinter
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Treeview

from sys_util_core.jcommon import SingletonBase
from sys_util_core.jsystems import JLogger, JTracer

"""
"""
class ErrorSystemManager(Exception): pass
class SystemManager(SingletonBase):
    def launch_proper(self, admin: bool = False, level: int = None, log_file_fullpath: Optional[str] = None):
        JLogger().start_logger(level, log_file_fullpath)
        JTracer().start()
        self.ensure_admin_running(required=admin)


    def exit_proper(self, msg=None, is_proper=False):
        if msg == None:
            msg = "process completed properly" if is_proper else "process finished with errors"
        if is_proper:
            JLogger().log_info(msg, 1)
            GuiManager().show_msg_box(msg, None)
            JTracer().stop()
            JLogger().end_logger(is_proper)
            sys.exit(0)
        else:
            JLogger().log_error(msg)
            GuiManager().show_msg_box(msg, None)
            JTracer().stop()
            JLogger().end_logger(is_proper)
            sys.exit(1)

    def ensure_admin_running(self, required: bool) -> bool: # 운영체제에 따라 관리자 권한 확인
        if os.name == 'posix':  # Unix 계열 (Linux, macOS)
            is_window = False
            is_admin_current = os.getuid() == 0
        elif os.name == 'nt':  # Windows
            is_window = True
            is_admin_current = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            is_window = False
            is_admin_current = False

        if is_window:
            # 권한 상태 확인 및 처리
            required_level = "관리자" if required else "일반 사용자"            
            if is_admin_current == required: # 요구 권한 일치
                msg = f"{required_level} 권한으로 실행 중입니다."
                JLogger().log_info(msg)
                return True
            else: # 권한 불일치
                msg = f"이 스크립트는 {required_level} 권한으로 실행되어야 합니다. {required_level} 권한으로 다시 실행하세요."
                self.exit_proper(msg)
        else:
            msg = "지원되지 않는 운영체제입니다."
            self.exit_proper(msg)
            
"""
"""
class ErrorGuiManager(Exception): pass
class GuiManager(SingletonBase):
    def __init__(self):
        if not hasattr(self, "initialized"):
            # init flag
            self.initialized = True

            # root
            self.root = tkinter.Tk()
            self.root.withdraw()

            # mainloop
            self.mainloop_running = False

    def run_mainloop(self):
        self.root.mainloop_running = True
        self.root.mainloop()
        
    class GuiType(Enum):
        MSG_BOX = "message_box" # 모달
        FILE_DLG = "file_dialog" # 모달
        INPUT_DLG = "input_dialog" # 모달
        CONFIRM_DLG = "confirm_dialog" # 모달
        COLOR_DLG = "color_dialog" # 모달
        SAVE_FILE_DLG = "save_file_dialog" # 모달
        POPUP_CTT_MENU = "popup_context_menu" # 논모달
        SCROLL_TEXT_WND = "scroll_text_window" # 논모달
        PROGRESS_BAR_WND = "progress_bar_window" # 논모달
        TREE_VIEW_WND = "tree_view_window" # 논모달
        CANVAS_WND = "canvas_window" # 논모달
        TOPLEVEL_SUB_WND = "toplevel_sub_window" # 논모달
        MAIN_WND = "main_window" # 논모달

    def show_msg_box(self, message: str, title: Optional[str] = "Info"):
        try:
            is_for_end = (True if title == None else False)
            cur_time_hms = JLogger().get_end_time_str_ymdhms(False, True) if is_for_end else JLogger().get_cur_time_str_ymdhms(False, True)
            stt_time_ymdhms = JLogger().get_stt_time_str_ymdhms(True, True)
            _title = "End of Process" if title == None else title

            _title = f"{_title} ({stt_time_ymdhms}→{cur_time_hms}, ... {JLogger().elapsed_time_f(end=is_for_end):.2f}s)"
            self.root.attributes('-topmost', True)  # 메시지 박스를 최상위로 설정
            tkinter.messagebox.showinfo(_title, message)
            self.root.attributes('-topmost', False)  # 최상위 설정 해제
            
        except Exception as e:
            JLogger().log_error(f"show_msg_box error: {e}")

    def show_file_dialog(self, title: str = "Select a file") -> str:
        try:
            file_path = filedialog.askopenfilename(title=title)
            return file_path
        except Exception as e:
            JLogger().log_error(f"show_file_dialog error: {e}")
            return ""

    def show_input_dialog(self, prompt: str = "Please enter something:", title: str = "Input") -> str:
        try:
            user_input = tkinter.simpledialog.askstring(title, prompt)
            return user_input
        except Exception as e:
            JLogger().log_error(f"show_input_dialog error: {e}")
            return None

    def show_confirm_dialog(self, message: str = "Do you want to proceed?", title: str = "Confirm") -> bool:
        try:
            result = tkinter.messagebox.askyesno(title, message)
            return result
        except Exception as e:
            JLogger().log_error(f"show_confirm_dialog error: {e}")
            return False

    def show_color_dialog(self, title: str = "Choose a color") -> str:
        try:
            color_code = tkinter.colorchooser.askcolor(title=title)[1]
            return color_code
        except Exception as e:
            JLogger().log_error(f"show_color_dialog error: {e}")
            return ""

    def show_save_file_dialog(self, title: str = "Save file as") -> str:
        try:
            file_path = filedialog.asksaveasfilename(title=title)
            return file_path
        except Exception as e:
            JLogger().log_error(f"show_save_file_dialog error: {e}")
            return ""

    def show_popup_context_menu(self, root, options=None):
        try:
            if options is None:
                options = [("Option 1", None), ("Option 2", None), ("Exit", self.root.quit)]

            def popup(event):
                popup_menu.post(event.x_root, event.y_root)

            popup_menu = tkinter.Menu(root, tearoff=0)
            for label, command in options:
                if label == "separator":
                    popup_menu.add_separator()
                else:
                    popup_menu.add_command(label=label, command=command)

            self.root.bind("<Button-3>", popup)
            self.root.deiconify()
            self.root.mainloop()

        except Exception as e:
            JLogger().log_error(f"show_popup_context_menu error: {e}")

    def show_scroll_text_window(self, title: str = "Scroll Text Window"):
        try:
            top = tkinter.Toplevel(self.root)
            top.title(title)
            text_area = tkinter.Text(top, wrap="word")
            scroll_bar = tkinter.Scrollbar(top, command=text_area.yview)
            text_area.configure(yscrollcommand=scroll_bar.set)
            text_area.pack(side="left", fill="both", expand=True)
            scroll_bar.pack(side="right", fill="y")

        except Exception as e:
            JLogger().log_error(f"show_scroll_text_window error: {e}")

    def show_progress_bar_window(self, progress_value: int = 50, title: str = "Progress Bar Window"):
        try:
            top = tkinter.Toplevel(self.root)
            top.title(title)
            progress = Progressbar(top, orient="horizontal", length=200, mode="determinate")
            progress.pack(pady=20)
            progress["value"] = progress_value

        except Exception as e:
            JLogger().log_error(f"show_progress_bar_window error: {e}")

    def show_tree_view_window(self, columns=("one", "two"), items=None, title: str = "Tree View Window"):
        try:
            if items is None:
                items = [("", "end", "Item 1", ("Value 1", "Value 2"))]
            top = tkinter.Toplevel(self.root)
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
            JLogger().log_error(f"show_tree_view_window error: {e}")

    def show_canvas_window(self, width: int = 200, height: int = 100, shapes=None, title: str = "Canvas Window"):
        try:
            if shapes is None:
                shapes = [("rectangle", (50, 25, 150, 75), {"fill": "blue"})]

            self.root.title(title)
            canvas = tkinter.Canvas(self.root, width=width, height=height)
            canvas.pack()
            for shape, coords, options in shapes:
                getattr(canvas, f"create_{shape}")(*coords, **options)
            self.root.deiconify()
            self.run_mainloop()

        except Exception as e:
            JLogger().log_error(f"show_canvas_window error: {e}")

    def show_toplevel_window(self, message: str = "This is a Toplevel window", title: str = "TopLevel Window"):
        try:
            top = tkinter.Toplevel(self.root)
            top.title(title)
            tkinter.Label(top, text=message).pack()

        except Exception as e:
            JLogger().log_error(f"show_toplevel_window error: {e}")

    def show_main_window(self, message: str = "This is the main window", title: str = "Main Window"):
        try:
            self.root.deiconify()
            self.root.title(title)
            tkinter.Label(self.root, text=message).pack()
            self.run_mainloop()
            
        except Exception as e:
            JLogger().log_error(f"show_main_window error: {e}")

