# by weo fuzile
# ubomvu
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ubomvu Calendar Application")
        self.root.geometry("600x600")

        self.selected_date = datetime.now().date()
        self.events = {}  # Dictionary to store events

        self.create_widgets()
        self.draw_calendar()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(pady=20)

        self.lbl_month_year = ttk.Label(self.frame, text='', font=('Helvetica', 14))
        self.lbl_month_year.grid(row=0, column=1, columnspan=5)

        self.prev_month_btn = ttk.Button(self.frame, text='<< Prev', command=self.prev_month)
        self.prev_month_btn.grid(row=0, column=0)

        self.next_month_btn = ttk.Button(self.frame, text='Next >>', command=self.next_month)
        self.next_month_btn.grid(row=0, column=6)

        self.calendar_view = ttk.Treeview(self.frame, height=7, columns=['1', '2', '3', '4', '5', '6', '7'], show='headings')
        self.calendar_view.grid(row=1, column=0, columnspan=7)

        self.calendar_view.heading('1', text='Mon')
        self.calendar_view.heading('2', text='Tue')
        self.calendar_view.heading('3', text='Wed')
        self.calendar_view.heading('4', text='Thu')
        self.calendar_view.heading('5', text='Fri')
        self.calendar_view.heading('6', text='Sat')
        self.calendar_view.heading('7', text='Sun')

        self.calendar_view.bind("<Button-1>", self.date_click)
        self.calendar_view.bind("<Button-3>", self.show_toolbox)

    def draw_calendar(self):
        month = self.selected_date.month
        year = self.selected_date.year
        self.lbl_month_year.config(text=f'{datetime.strftime(self.selected_date, "%B %Y")}')

        # Clear previous items in the calendar
        for item in self.calendar_view.get_children():
            self.calendar_view.delete(item)

        # Calculate the starting day of the month
        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()  # 0 = Monday, 6 = Sunday

        # Calculate number of days in the month
        days_in_month = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total_days = days_in_month.day

        # Fill the calendar with days
        row = []
        for i in range(start_day):
            row.append('')

        for day in range(1, total_days + 1):
            events_on_day = self.events.get(datetime(year, month, day), [])
            row.append((day, events_on_day))
            if len(row) == 7:
                self.calendar_view.insert('', 'end', values=row)
                row = []

        if row:
            self.calendar_view.insert('', 'end', values=row)

    def prev_month(self):
        self.selected_date = self.selected_date - timedelta(days=1)
        self.draw_calendar()

    def next_month(self):
        self.selected_date = (self.selected_date + timedelta(days=32)).replace(day=1)
        self.draw_calendar()

    def date_click(self, event):
        item = self.calendar_view.selection()[0]
        day = self.calendar_view.item(item, 'values')[0]

        if day != '':
            selected_date = datetime(self.selected_date.year, self.selected_date.month, int(day))
            self.add_event(selected_date)

    def add_event(self, date):
        event_description = simpledialog.askstring("Event Description", "Enter event description:")
        if event_description:
            repeat_choice = messagebox.askyesno("Repeat Event", "Do you want to repeat this event?")
            if repeat_choice:
                repeat_options = ['None', 'Daily', 'Monthly', 'Yearly']
                repeat_interval = simpledialog.askstring("Repeat Interval", "Enter repeat interval (daily, monthly or yearly):")
                if repeat_interval in repeat_options:
                    self.events.setdefault(date, []).append((event_description, repeat_interval))
                else:
                    messagebox.showwarning("Invalid Input", "Please enter a valid repeat interval.")
            else:
                self.events.setdefault(date, []).append((event_description, 'None'))
            self.draw_calendar()

    def show_toolbox(self, event):
        item = self.calendar_view.selection()[0]
        day = self.calendar_view.item(item, 'values')[0]

        if day != '':
            selected_date = datetime(self.selected_date.year, self.selected_date.month, int(day))
            self.show_event_toolbox(selected_date)

    def show_event_toolbox(self, date):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Add Event", command=lambda: self.add_event(date))
        menu.add_command(label="Edit Events", command=lambda: self.edit_events(date))
        menu.add_command(label="Delete Events", command=lambda: self.delete_events(date))

        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def edit_events(self, date):
        # Implement editing events for a specific date
        pass

    def delete_events(self, date):
        # Implement deleting events for a specific date
        pass

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = CalendarApp(root)
    app.run()
