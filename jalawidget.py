import tkinter as tk
import jdatetime
from tkinter import font, messagebox
import ctypes
import os
import subprocess
import sys
import traceback
import winreg

try:
    weekdays_fa = {
        'Saturday': 'شنبه',
        'Sunday': 'یک‌شنبه',
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه',
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه'
    }

    months_fa = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
        4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر',
        10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }

    gregorian_months = {
        1: 'January', 2: 'February', 3: 'March',
        4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September',
        10: 'October', 11: 'November', 12: 'December'
    }

    calendar_weekdays = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
    weekday_columns = {
        'Saturday': 0,
        'Sunday': 1,
        'Monday': 2,
        'Tuesday': 3,
        'Wednesday': 4,
        'Thursday': 5,
        'Friday': 6
    }

    AUTOSTART_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    AUTOSTART_VALUE_NAME = "JalaliDateWidget"

    def get_persian_date():
        today = jdatetime.date.today()
        weekday = weekdays_fa.get(today.strftime("%A"), today.strftime("%A"))
        day = today.day
        month = months_fa.get(today.month, today.month)
        year = today.year
        return f"{weekday} {day} {month} {year}"

    class PersianDateWidget:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("تاریخ امروز")
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", False)
            self.root.wm_attributes("-alpha", 0.85)
            self.root.configure(bg="#222222")
            self.calendar_window = None
            self.displayed_year = None
            self.displayed_month = None
            self.show_gregorian = tk.BooleanVar(value=False)
            self.start_with_windows = tk.BooleanVar(
                value=self.is_autostart_enabled()
            )
            self.has_moved = False

            # لیست فونت‌ها رو چاپ می‌کنیم (برای اطمینان)
            all_fonts = list(font.families())
            # print("Fonts installed:", all_fonts)

            font_name = "Vazirmatn FD Medium"
            if font_name not in all_fonts:
                print(f"Font '{font_name}' not found, using default font.")
                self.vazirmatn_font = font.Font(size=13)
            else:
                self.vazirmatn_font = font.Font(family=font_name, size=13)

            self.frame = tk.Frame(self.root, bg="#222222", bd=0)
            self.frame.pack(fill="both", expand=True)

            self.label = tk.Label(self.frame, text=get_persian_date(),
                                  font=self.vazirmatn_font, fg="white", bg="#222222", padx=10, pady=5)
            self.label.pack(side="left")

            # بدست آوردن عرض و ارتفاع پنجره پس از pack کردن
            self.root.update_idletasks()
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            # ابعاد صفحه نمایش
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # موقعیت پایین سمت راست با 20 پیکسل فاصله از لبه‌ها
            x = screen_width - window_width - 20
            y = screen_height - window_height - 50  # 50 برای پایین‌تر از نوار taskbar

            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # فعال کردن حرکت پنجره با موس
            self.frame.bind("<Button-1>", self.start_move)
            self.frame.bind("<B1-Motion>", self.do_move)
            self.frame.bind("<ButtonRelease-1>", self.finish_click)
            self.label.bind("<Button-1>", self.start_move)
            self.label.bind("<B1-Motion>", self.do_move)
            self.label.bind("<ButtonRelease-1>", self.finish_click)
            
            # اضافه کردن راست کلیک برای بستن ویجت
            self.frame.bind("<Button-3>", self.close_widget)
            self.label.bind("<Button-3>", self.close_widget)

            self.offset_x = 0
            self.offset_y = 0

            self.root.mainloop()

        def start_move(self, event):
            self.offset_x = event.x
            self.offset_y = event.y
            self.start_pointer_x = self.root.winfo_pointerx()
            self.start_pointer_y = self.root.winfo_pointery()
            self.has_moved = False

        def do_move(self, event):
            pointer_x = self.root.winfo_pointerx()
            pointer_y = self.root.winfo_pointery()
            if (abs(pointer_x - self.start_pointer_x) > 3 or
                    abs(pointer_y - self.start_pointer_y) > 3):
                self.has_moved = True
            x = self.root.winfo_pointerx() - self.offset_x
            y = self.root.winfo_pointery() - self.offset_y
            self.root.geometry(f"+{x}+{y}")

        def finish_click(self, event):
            if not self.has_moved:
                self.toggle_calendar()

        def toggle_calendar(self):
            if (self.calendar_window is not None and
                    self.calendar_window.winfo_exists()):
                self.close_calendar()
                return

            today = jdatetime.date.today()
            self.displayed_year = today.year
            self.displayed_month = today.month
            self.calendar_window = tk.Toplevel(self.root)
            self.calendar_window.overrideredirect(True)
            self.calendar_window.attributes("-topmost", True)
            self.calendar_window.configure(bg="#222222")
            self.render_calendar()

        def render_calendar(self):
            for child in self.calendar_window.winfo_children():
                child.destroy()

            today = jdatetime.date.today()

            previous_button = tk.Button(
                self.calendar_window,
                text="▶",
                command=lambda: self.change_month(-1),
                font=self.vazirmatn_font,
                fg="white",
                bg="#222222",
                activeforeground="#f4c542",
                activebackground="#333333",
                bd=0,
                cursor="hand2"
            )
            previous_button.grid(row=0, column=6, sticky="e", padx=4)

            settings_button = tk.Button(
                self.calendar_window,
                text="⚙",
                command=lambda: self.show_settings_menu(settings_button),
                font=self.vazirmatn_font,
                fg="#aaaaaa",
                bg="#222222",
                activeforeground="white",
                activebackground="#333333",
                bd=0,
                cursor="hand2"
            )
            settings_button.grid(row=0, column=1, sticky="w")

            title = tk.Label(
                self.calendar_window,
                text=f"{months_fa[self.displayed_month]} {self.displayed_year}",
                font=self.vazirmatn_font,
                fg="white",
                bg="#222222",
                pady=8
            )
            title.grid(row=0, column=2, columnspan=3, sticky="ew")

            next_button = tk.Button(
                self.calendar_window,
                text="◀",
                command=lambda: self.change_month(1),
                font=self.vazirmatn_font,
                fg="white",
                bg="#222222",
                activeforeground="#f4c542",
                activebackground="#333333",
                bd=0,
                cursor="hand2"
            )
            next_button.grid(row=0, column=0, sticky="w", padx=4)

            content_start_row = 1
            if self.show_gregorian.get():
                gregorian_range = self.get_gregorian_month_range(
                    self.displayed_year,
                    self.displayed_month
                )
                tk.Label(
                    self.calendar_window,
                    text=gregorian_range,
                    font=(self.vazirmatn_font.actual("family"), 9),
                    fg="#aaaaaa",
                    bg="#222222",
                    pady=2
                ).grid(row=1, column=0, columnspan=7, sticky="ew")
                content_start_row = 2

            for column, weekday in enumerate(calendar_weekdays):
                is_friday_header = column == 6
                tk.Label(
                    self.calendar_window,
                    text=weekday,
                    font=self.vazirmatn_font,
                    width=3,
                    fg="#ff6b6b" if is_friday_header else "#aaaaaa",
                    bg="#222222"
                ).grid(
                    row=content_start_row,
                    column=6 - column,
                    padx=2,
                    pady=2
                )

            first_day = jdatetime.date(
                self.displayed_year,
                self.displayed_month,
                1
            )
            start_column = weekday_columns[first_day.strftime("%A")]
            month_length = self.get_month_length(
                self.displayed_year,
                self.displayed_month
            )

            for day in range(1, month_length + 1):
                position = start_column + day - 1
                row = position // 7 + content_start_row + 1
                column = 6 - (position % 7)
                is_today = (
                    day == today.day and
                    self.displayed_month == today.month and
                    self.displayed_year == today.year
                )
                is_friday = jdatetime.date(
                    self.displayed_year,
                    self.displayed_month,
                    day
                ).strftime("%A") == "Friday"
                if is_today:
                    foreground = "#9b1c1c" if is_friday else "#222222"
                else:
                    foreground = "#ff6b6b" if is_friday else "white"
                cell_background = "#f4c542" if is_today else "#222222"

                day_cell = tk.Frame(
                    self.calendar_window,
                    bg=cell_background,
                    padx=2,
                    pady=1
                )
                day_cell.grid(row=row, column=column, padx=2, pady=2)

                day_label = tk.Label(
                    day_cell,
                    text=str(day),
                    font=self.vazirmatn_font,
                    width=3,
                    fg=foreground,
                    bg=cell_background,
                    padx=0,
                    pady=0
                )
                day_label.pack()

                clickable_widgets = [day_cell, day_label]
                if self.show_gregorian.get():
                    gregorian_day = jdatetime.date(
                        self.displayed_year,
                        self.displayed_month,
                        day
                    ).togregorian().day
                    gregorian_label = tk.Label(
                        day_cell,
                        text=str(gregorian_day),
                        font=(self.vazirmatn_font.actual("family"), 8),
                        width=3,
                        fg="#705600" if is_today else "#777777",
                        bg=cell_background,
                        padx=0,
                        pady=0
                    )
                    gregorian_label.pack()
                    clickable_widgets.append(gregorian_label)

                for widget in clickable_widgets:
                    widget.bind(
                        "<Button-1>",
                        lambda event: self.close_calendar()
                    )

            self.calendar_window.update_idletasks()
            calendar_width = self.calendar_window.winfo_width()
            calendar_height = self.calendar_window.winfo_height()
            x = self.root.winfo_x() + self.root.winfo_width() - calendar_width
            y = self.root.winfo_y() - calendar_height - 6
            if y < 0:
                y = self.root.winfo_y() + self.root.winfo_height() + 6
            self.calendar_window.geometry(f"+{max(0, x)}+{y}")

        def show_settings_menu(self, button):
            menu = tk.Menu(
                self.calendar_window,
                tearoff=False,
                font=self.vazirmatn_font,
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white"
            )
            menu.add_checkbutton(
                label="نمایش ماه میلادی",
                variable=self.show_gregorian,
                command=self.render_calendar
            )
            menu.add_separator()
            menu.add_checkbutton(
                label="اجرا با شروع ویندوز",
                variable=self.start_with_windows,
                command=self.set_autostart
            )
            menu.tk_popup(
                button.winfo_rootx(),
                button.winfo_rooty() + button.winfo_height()
            )

        @staticmethod
        def get_startup_command():
            if getattr(sys, "frozen", False):
                command_parts = [sys.executable]
            else:
                command_parts = [sys.executable, os.path.abspath(__file__)]
            return subprocess.list2cmdline(command_parts)

        @staticmethod
        def is_autostart_enabled():
            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    AUTOSTART_REGISTRY_PATH
                ) as key:
                    winreg.QueryValueEx(key, AUTOSTART_VALUE_NAME)
                return True
            except FileNotFoundError:
                return False

        def set_autostart(self):
            try:
                with winreg.CreateKey(
                    winreg.HKEY_CURRENT_USER,
                    AUTOSTART_REGISTRY_PATH
                ) as key:
                    if self.start_with_windows.get():
                        winreg.SetValueEx(
                            key,
                            AUTOSTART_VALUE_NAME,
                            0,
                            winreg.REG_SZ,
                            self.get_startup_command()
                        )
                    else:
                        try:
                            winreg.DeleteValue(key, AUTOSTART_VALUE_NAME)
                        except FileNotFoundError:
                            pass
            except OSError as error:
                self.start_with_windows.set(
                    self.is_autostart_enabled()
                )
                messagebox.showerror(
                    "خطا",
                    f"تنظیم اجرای خودکار ذخیره نشد:\n{error}"
                )

        def change_month(self, offset):
            self.displayed_year, self.displayed_month = self.shift_month(
                self.displayed_year,
                self.displayed_month,
                offset
            )
            self.render_calendar()

        @staticmethod
        def shift_month(year, month, offset):
            month_index = year * 12 + month - 1 + offset
            return divmod(month_index, 12)[0], divmod(month_index, 12)[1] + 1

        @staticmethod
        def get_gregorian_month_range(year, month):
            first_day = jdatetime.date(year, month, 1).togregorian()
            last_day = jdatetime.date(
                year,
                month,
                PersianDateWidget.get_month_length(year, month)
            ).togregorian()
            first_name = gregorian_months[first_day.month]
            last_name = gregorian_months[last_day.month]

            if first_day.month == last_day.month:
                return f"{first_name} {first_day.year}"
            if first_day.year == last_day.year:
                return f"{first_name} - {last_name} {first_day.year}"
            return (
                f"{first_name} {first_day.year} - "
                f"{last_name} {last_day.year}"
            )

        @staticmethod
        def get_month_length(year, month):
            for day in (31, 30, 29):
                try:
                    jdatetime.date(year, month, day)
                    return day
                except ValueError:
                    continue
            return 29

        def close_calendar(self):
            if (self.calendar_window is not None and
                    self.calendar_window.winfo_exists()):
                self.calendar_window.destroy()
            self.calendar_window = None
            
        def close_widget(self, event):
            self.close_calendar()
            self.root.destroy()

    if __name__ == "__main__":
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        PersianDateWidget()

except Exception as e:
    print("Error:", e)
    traceback.print_exc()
    input("Press Enter to exit...")
