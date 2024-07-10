import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import re

# Define the Event class
class Event:
    def __init__(self, description, repeat_interval="None"):
        self.description = description
        self.repeat_interval = repeat_interval
        self.repeat_count = 0

# Define the CalendarApp class  

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
        self.calendar_view.bind("<Double-1>", self.show_event_toolbox)
        self.calendar_view.bind("<Button-3>", self.show_event_toolbox)

    def draw_calendar(self):
        month = self.selected_date.month
        year = self.selected_date.year
        self.lbl_month_year.config(text=f'{datetime.strftime(self.selected_date, "%B %Y")}')

        for item in self.calendar_view.get_children():
            self.calendar_view.delete(item)

        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()
        days_in_month = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total_days = days_in_month.day

        row = []
        for i in range(start_day):
            row.append('')

        for day in range(1, total_days + 1):
            date = datetime(year, month, day)
            events_on_day = self.events.get(date, [])
            event_text = "\n".join(event.description for event in events_on_day)
            row.append((day, event_text)) 
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
        # click and highlight the selected date
        for item in self.calendar_view.selection():
            self.calendar_view.selection_remove(item)
        item = self.calendar_view.identify_row(event.y)
        self.calendar_view.selection_add(item)

        # Get the selected date then open a widget to add_event
        self.select_date(event)

    def select_date(self, event):
        item = self.calendar_view.selection()[0]
        day, events = self.calendar_view.item(item, 'values')[:2]  # Get day and events

        if day != '':
            # Clean the day variable
            day = day.strip()  # Remove leading/trailing whitespace
            day = re.sub(r'\D', '', day)  # Remove non-numeric characters

            try:
                selected_date = datetime(self.selected_date.year, self.selected_date.month, int(day))
                self.add_event(selected_date)
            except ValueError:
                messagebox.showerror("Invalid Date", "Please select a valid date.")
    
    def repeat_event(self, event, date):
        if event.repeat_interval == "Daily":
            next_date = date + timedelta(days=1)
        elif event.repeat_interval == "Monthly":
            next_date = date.replace(month=date.month + 1, day=min(date.day, (date + timedelta(days=32)).replace(day=1).day - 1)) # Handle month rollover
        elif event.repeat_interval == "Yearly":
            next_date = date.replace(year=date.year + 1)
        else:
            return  # No repetition needed
        
        if next_date <= self.selected_date.replace(day=1) + timedelta(days=31): # Check if still in current month
            self.events.setdefault(next_date, []).append(event)
            self.repeat_event(event, next_date)

    def add_event(self, date):
        event_description = simpledialog.askstring("Event Description", "Enter event description:")
        if event_description:
            repeat_interval = simpledialog.askstring("Repeat Interval", "Enter repeat interval (daily, monthly, yearly, or none):") or "None"

            new_event = Event(event_description, repeat_interval.lower())
            self.events.setdefault(date, []).append(new_event)
            self.repeat_event(new_event, date)  # Handle repetition
            self.draw_calendar()

    def show_event_toolbox(self, event):
        item = self.calendar_view.selection()[0]
        day, events = self.calendar_view.item(item, 'values')[:2]  # Get day and events
        
        if day != '':
            selected_date = datetime(self.selected_date.year, self.selected_date.month, int(day))
            self.show_event_toolbox_widget(selected_date)

    def show_event_toolbox_widget(self, date):
        # Create a new top-level window for the toolbox
        toolbox_window = tk.Toplevel(self.root)
        toolbox_window.title("Event Toolbox")

        # Add Event Button
        add_event_btn = ttk.Button(toolbox_window, text="Add Event", command=lambda: self.add_event(date))
        add_event_btn.pack(pady=5)

        # Edit Events Button
        edit_event_btn = ttk.Button(toolbox_window, text="Edit Events", command=lambda: self.edit_events(date))
        edit_event_btn.pack(pady=5)

        # Delete Events Button
        delete_event_btn = ttk.Button(toolbox_window, text="Delete Events", command=lambda: self.delete_events(date))
        delete_event_btn.pack(pady=5)

    def edit_events(self, date):
        # Implement editing events for a specific date
        if date in self.events:
            event_list = self.events[date]
            for i, event in enumerate(event_list):
                event_description, repeat_interval = event
                new_description = simpledialog.askstring("Edit Event", f"Current description: {event_description}\nNew description:")
                if new_description:
                    event_list[i] = (new_description, repeat_interval)
            self.draw_calendar()
        else:
            messagebox.showinfo("No Events", "There are no events on this date.")

    def delete_events(self, date):
        # Implement deleting events for a specific date
        if date in self.events:
            event_list = self.events[date]
            if len(event_list) > 1:
                event_to_delete = simpledialog.askstring("Delete Event", "Enter the event description to delete:")
                if event_to_delete:
                    for i, event in enumerate(event_list):
                        if event[0] == event_to_delete:
                            del event_list[i]
                            break
                    self.draw_calendar()
            else:
                delete_choice = messagebox.askyesno("Delete Event", "Are you sure you want to delete all events on this date?")
                if delete_choice:
                    del self.events[date]
                    self.draw_calendar()
        else:
            messagebox.showinfo("No Events", "There are no events on this date.")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = CalendarApp(root)
    app.run()
