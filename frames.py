from datetime import datetime
from tkcalendar import Calendar
from tkinter import *
from tkinter import messagebox
import shelve

BACKGROUND_COLOR = '#696969'
radio_state = IntVar()
radio_state2 = IntVar()

today = datetime.now()  # .strftime("%m/%d/%Y")

this_month = f'0{today.month}' if today.month < 10 else f'{today.month}'
this_day = f'0{today.day}' if today.day < 10 else f'{today.day}'
pixela_today = f"{today.year}{this_month}{this_day}"

try:
    with shelve.open(filename='user_options') as sf:
        DATE_PATTERN = sf['date_pattern']
except (FileNotFoundError, KeyError):
    DATE_PATTERN = 'mm/dd/yyyy'  # program starts in american format


class DateFrame(Frame):
    """
     DateFrame class creates:
    | ◉ Today     ○ Pick Date  |      # Pick Date displays a calendar
    |    Date: 04/06/2021      |
    """
    def __init__(self, root):
        self.root = root
        super().__init__(self.root, bg=BACKGROUND_COLOR)
        self.date_pattern = DATE_PATTERN
        self.date_to_pixela = pixela_today  # '20210406'
        self.calendar = Calendar(self, font='Arial 8', background='#000080',
                                 showweeknumbers=False,
                                 weekendforeground='#000000',
                                 weekendbackground='#ffffff',
                                 date_pattern=self.date_pattern,
                                 othermonthwebackground='#ffffff',
                                 othermonthbackground='#ffffff')
        # ◉Today
        self.today = Radiobutton(self, command=self.set_today,
                                 text="Today ", value=0,
                                 variable=radio_state,
                                 bg=BACKGROUND_COLOR )
        self.today.grid(row=0, column=0, sticky='w')

        # ◉Pick Date
        self.pick_date = Radiobutton(self, command=self.show_calendar,
                                     text="Pick Date", value=1,
                                     variable=radio_state,
                                     bg=BACKGROUND_COLOR)
        self.pick_date.grid(row=0, column=1, sticky='w')

        # Date:  {04/06/2021}
        Label(self, text="Date: ", bg=BACKGROUND_COLOR, padx=10).grid(row=1, column=0)
        self.main_date = Label(self, text="", bg=BACKGROUND_COLOR, font=('Arial', 12, 'bold'))
        self.main_date.grid(row=1, column=1, sticky='w')

        self.set_today()  # output today's date right away

    def change_date_pattern(self, option):  # to be used by Options in MainMenu
        self.date_pattern = option
        self.calendar = Calendar(self, font='Arial 8', background='#000080',
                                 showweeknumbers=False,
                                 weekendforeground='#000000',
                                 weekendbackground='#ffffff',
                                 date_pattern=option,
                                 othermonthwebackground='#ffffff',
                                 othermonthbackground='#ffffff')

        keep_format = messagebox.askyesno(
            title="Keep Format",
            message="Do you wish to keep this date format \n"
                    "for the next times you open this program?")
        if keep_format:
            with shelve.open(filename="user_options") as sf:
                sf["date_pattern"] = option

        self.set_today()

    def display(self, date):
        self.calendar.grid_forget()
        self.main_date.config(text=date)

    def set_today(self):
        self.date_to_pixela = pixela_today  # set back TODAY for pixe.la and display it
        if self.date_pattern == 'mm/dd/yyyy':
            self.display(today.strftime("%m/%d/%Y"))
        elif self.date_pattern == 'dd/mm/yyyy':
            self.display(today.strftime("%d/%m/%Y"))
        else:
            self.display(today.strftime("%Y/%m/%d"))

    def show_calendar(self):  # displays new date label, at every click, and hides calendar
        self.calendar.grid(row=2, column=0, columnspan=2, sticky='w')

        def format_day_from_calendar(event):  # won't work without "event" (?)
            date = self.get_pixela_date_from_calendar()
            self.display(date)

        self.calendar.bind("<<CalendarSelected>>", format_day_from_calendar)

    def get_pixela_date_from_calendar(self):
        get_date = self.calendar.get_date()     # format retrieved depends on self.date_pattern
        date = get_date.split('/')
        if self.date_pattern == 'mm/dd/yyyy':
            self.date_to_pixela = ''.join([date[2], date[0], date[1]])
        elif self.date_pattern == 'dd/mm/yyyy':
            self.date_to_pixela = ''.join([date[2], date[1], date[0]])
        else:  # asian
            self.date_to_pixela = ''.join(date)
        return get_date


class TimeFrame(Frame):
    """
    TimeFrame class creates:
     |◉Input Time   ○Record             or      | ○Input Time   ◉Record
     |Time Spent:( ) ( ) hours & min            |Time Spent:00:00 ⏺️⏸️⏹️
    """

    def __init__(self, root):
        self.root = root
        self.total_time_recorded = 0  # in seconds
        self.timer = self.root.after(1000, self.stop_counting)
        super().__init__(self.root, bg=BACKGROUND_COLOR)

        # ◉Input Time
        self.input_time_radio_button = Radiobutton(self, text="Input Time", command=self.input_time_option,
                                                   variable=radio_state2, value=0, bg=BACKGROUND_COLOR)
        self.input_time_radio_button.grid(row=0, column=0, pady=(20, 0), sticky='e')

        # ◉Record
        self.record_time_radio_button = Radiobutton(self, text="Record", command=self.record_option,
                                                    variable=radio_state2, value=1, bg=BACKGROUND_COLOR)
        self.record_time_radio_button.grid(row=0, column=2, pady=(20, 0), sticky='w')

        # ------------------------------ FRAME for hours/minutes entries ----------------------------------#
        #  Time Spent:{( ) ( ) hours & min}
        self.entry_frame = Frame(self, bg=BACKGROUND_COLOR)
        Label(self.entry_frame, text="Time Spent: ", bg=BACKGROUND_COLOR).grid(row=1, column=0)
        self.hours_entry = Entry(self.entry_frame, width=5, justify="right")
        self.hours_entry.grid(row=1, column=1, sticky='w')

        self.minutes_entry = Entry(self.entry_frame, width=5, justify="right")
        self.minutes_entry.grid(row=1, column=2, padx=5)
        Label(self.entry_frame, text="hours & min", bg=BACKGROUND_COLOR).grid(row=1, column=3, sticky='w')

        # ------------------------------ FRAME for recording buttons -------------------------------------#
        # Time Spent:{00:00:00 ⏺️⏸️⏹️}
        self.record_frame = Frame(self, bg=BACKGROUND_COLOR)
        Label(self.record_frame, text="Time Spent: ", bg=BACKGROUND_COLOR).grid(row=1, column=0)
        self.elapsed_time = Label(self.record_frame, text="00:00:00",
                                  font=('Arial', 12, 'bold'), bg=BACKGROUND_COLOR)
        self.elapsed_time.grid(row=1, column=1)

        self.start_button = Button(self.record_frame, text="⏺", command=self.start_counting)
        self.start_button.grid(row=1, column=2, padx=(5, 0))

        self.pause_button = Button(self.record_frame, text="⏸", command=self.pause_counting)
        self.pause_button.grid(row=1, column=3)

        self.stop_button = Button(self.record_frame, text="⏹", command=self.stop_counting)
        self.stop_button.grid(row=1, column=4)

        self.input_time_option()

    def input_time_option(self):
        self.record_frame.grid_forget()
        self.entry_frame.grid(row=1, column=0, columnspan=4)
        self.stop_counting()
        self.minutes_entry.delete(0, END)
        self.minutes_entry.insert(0, "0")

    def record_option(self):
        self.entry_frame.grid_forget()
        self.record_frame.grid(row=1, column=0, columnspan=4)
        self.hours_entry.delete(0, END)
        self.minutes_entry.delete(0, END)
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')

    def start_counting(self):
        # to avoid bugs if user clicks record button multiple times
        self.start_button.config(state='disabled')
        self.pause_button.config(state='active')
        self.stop_button.config(state='active')

        time_hour = self.total_time_recorded // 3600
        time_min = (self.total_time_recorded // 60) - 60 * time_hour
        time_sec = self.total_time_recorded % 60
        hours = f'0{time_hour}' if time_hour < 10 else f'{time_hour}'
        mins = f'0{time_min}' if time_min < 10 else f'{time_min}'
        secs = f'0{time_sec}' if time_sec < 10 else f'{time_sec}'
        text = f'{hours}:{mins}:{secs}'

        self.elapsed_time.config(text=text, fg='#00FF00')
        self.total_time_recorded += 1
        self.timer = self.root.after(1000, self.start_counting)

    def pause_counting(self):
        self.root.after_cancel(self.timer)
        self.total_time_recorded -= 1  # to avoid retrieving elapsed time with a 1 second more bug :/
        self.start_button.config(state='active')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='active')
        self.elapsed_time.config(fg='white')

    def stop_counting(self):
        self.root.after_cancel(self.timer)
        self.total_time_recorded = 0
        self.elapsed_time.config(text="00:00:00")
        self.elapsed_time.config(fg='black')
        self.start_button.config(state='active')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')

    def get_pixela_time(self):  # to be used by the button "Create" in main.py, hands back seconds
        hours_from_entry, minutes_from_entry = self.hours_entry.get(), self.minutes_entry.get()
        if hours_from_entry or minutes_from_entry:
            try:
                hours = abs(int(hours_from_entry) * 3600)
            except ValueError:
                self.hours_entry.delete(0, END)
                ok = messagebox.askokcancel(
                    title="Hours Invalid Input",
                    message="You have entered a non-numeric input "
                            "for hours. May the amount of hours spent "
                            "be considered 0?")
                if ok:
                    hours = 0
                    self.hours_entry.insert(0, "0")
                else:
                    return None
            try:
                mins = abs(int(minutes_from_entry) * 60)
            except ValueError:
                self.minutes_entry.delete(0, END)
                ok = messagebox.askokcancel(
                    title="Minutes Invalid Input",
                    message="You have entered a non-numeric input "
                            "for minutes. May the amount of minutes spent "
                            "be considered 0?")
                if ok:
                    mins = 0
                    self.minutes_entry.insert(0, "0")
                else:
                    return None

            return hours + mins
        else:
            return self.total_time_recorded


class InputFrame(Frame):
    """Creates simple input area {Input Quantity: (   ) unit}"""

    def __init__(self, root, unit):
        self.root = root
        self.unit = unit
        super().__init__(self.root, bg=BACKGROUND_COLOR)

        Label(self, text="Input Quantity: ", bg=BACKGROUND_COLOR).grid(row=0, column=0, pady=(10, 0))
        self.amount_entry = Entry(self, width=10, justify="right", bg='white')
        self.amount_entry.grid(row=0, column=1, pady=(10, 0), padx=(5, 0))
        Label(self, text=unit, bg=BACKGROUND_COLOR).grid(row=0, column=2, pady=(10, 0))
        self.amount_entry.focus()

    def get_quantity(self):
        try:
            quantity = float(self.amount_entry.get())
        except ValueError:
            self.amount_entry.delete(0, END)
            ok = messagebox.askokcancel(
                title="Invalid Input for Quantity",
                message="You have entered a non-numeric input "
                        "for Quantity. May the quantity "
                        "be considered 0?")
            if ok:
                self.amount_entry.insert(0, "0")
                return 0
        else:
            return quantity

