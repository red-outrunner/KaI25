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
        self.root.title("Ubomvu Calendar")
        self.root.geometry("1000x800")  # Adjust width for sidebar

        self.selected_date = datetime.now().date()
        self.events = {}  # Dictionary to store events

        self.create_widgets()
        self.draw_calendar()
        self.update_sidebar()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(pady=20)

        # Calendar Section
        self.calendar_frame = ttk.Frame(self.frame)
        self.calendar_frame.grid(row=0, column=0, rowspan=2, padx=(0, 20))

        self.lbl_month_year = ttk.Label(self.calendar_frame, text='', font=('Helvetica', 14))
        self.lbl_month_year.grid(row=0, column=0, columnspan=7)

        self.prev_month_btn = ttk.Button(self.calendar_frame, text='<< Prev', command=self.prev_month)
        self.prev_month_btn.grid(row=0, column=0)

        self.next_month_btn = ttk.Button(self.calendar_frame, text='Next >>', command=self.next_month)
        self.next_month_btn.grid(row=0, column=6)

        # Create labels for the days of the week
        self.day_labels = [
            ttk.Label(self.calendar_frame, text=day, width=4, relief="solid")
            for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ]
        for i, label in enumerate(self.day_labels):
            label.grid(row=1, column=i)

        # Create a list to store the calendar buttons
        self.calendar_buttons = []

        # Sidebar Section
        self.sidebar_frame = ttk.Frame(self.frame)
        self.sidebar_frame.grid(row=0, column=1, rowspan=2, sticky="ns")

        self.sidebar_label = ttk.Label(self.sidebar_frame, text="Upcoming Events", font=('Helvetica', 12))
        self.sidebar_label.pack(pady=10)

        self.sidebar_events_list = tk.Listbox(self.sidebar_frame, width=30, height=10)
        self.sidebar_events_list.pack(pady=5)

        self.sidebar_events_list.bind("<<ListboxSelect>>", self.sidebar_event_selected)

        # Create a popup window for the event toolbox
        self.event_toolbox_popup = tk.Toplevel(self.root)
        self.event_toolbox_popup.withdraw()  # Hide it initially
        self.event_toolbox_popup.title("Event Toolbox")

        # Add Event Button
        self.add_event_btn = ttk.Button(self.event_toolbox_popup, text="Add Event", command=lambda: self.add_event(self.selected_date))
        self.add_event_btn.pack(pady=5)

        # Edit Events Button
        self.edit_event_btn = ttk.Button(self.event_toolbox_popup, text="Edit Events", command=lambda: self.edit_events(self.selected_date))
        self.edit_event_btn.pack(pady=5)

        # Delete Events Button
        self.delete_event_btn = ttk.Button(self.event_toolbox_popup, text="Delete Events", command=lambda: self.delete_events(self.selected_date))
        self.delete_event_btn.pack(pady=5)

    def draw_calendar(self):
        month = self.selected_date.month
        year = self.selected_date.year
        self.lbl_month_year.config(text=f'{datetime.strftime(self.selected_date, "%B %Y")}')

        # Clear existing buttons
        for button in self.calendar_buttons:
            button.destroy()
        self.calendar_buttons = []

        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()
        days_in_month = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total_days = days_in_month.day

        row = 0
        col = start_day

        for day in range(1, total_days + 1):
            date = datetime(year, month, day)
            events_on_day = self.events.get(date, [])
            event_text = "\n".join(event.description for event in events_on_day)

            # Create a button for each day
            button = tk.Button(
                self.calendar_frame,
                text=str(day),
                command=lambda d=date: self.show_events_for_date(d),
                width=4,
                relief="solid",
            )
            button.grid(row=row + 1, column=col)
            button.bind("<Button-3>", lambda event, b=button, d=date: self.show_event_toolbox_popup(d, b))  # Pass button
            self.calendar_buttons.append(button)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def prev_month(self):
        self.selected_date = self.selected_date - timedelta(days=1)
        self.draw_calendar()
        self.update_sidebar()

    def next_month(self):
        self.selected_date = (self.selected_date + timedelta(days=32)).replace(day=1)
        self.draw_calendar()
        self.update_sidebar()

    def show_events_for_date(self, date):
        self.selected_date = date  # Update selected date
        self.update_sidebar()

        events_on_day = self.events.get(date, [])
        if events_on_day:
            event_text = "\n".join(event.description for event in events_on_day)
            messagebox.showinfo(f"Events on {date.strftime('%Y-%m-%d')}", event_text)
        else:
            messagebox.showinfo(f"Events on {date.strftime('%Y-%m-%d')}", "No events scheduled for this day.")

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
            self.update_sidebar()

    def show_event_toolbox_popup(self, date, button):
        self.selected_date = date  # Update selected date
        self.event_toolbox_popup.deiconify()  # Show the popup
        self.event_toolbox_popup.geometry(f"+{self.root.winfo_rootx() + self.calendar_frame.winfo_x() + button.winfo_x()}+{self.root.winfo_rooty() + self.calendar_frame.winfo_y() + button.winfo_y()}")  # Position it near the button

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
            self.update_sidebar()
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
                    self.update_sidebar()
            else:
                delete_choice = messagebox.askyesno("Delete Event", "Are you sure you want to delete all events on this date?")
                if delete_choice:
                    del self.events[date]
                    self.draw_calendar()
                    self.update_sidebar()
        else:
            messagebox.showinfo("No Events", "There are no events on this date.")

    def update_sidebar(self):
        self.sidebar_events_list.delete(0, tk.END)  # Clear existing events

        # Get upcoming events
        upcoming_events = []
        for date, events in sorted(self.events.items()):
            if date >= self.selected_date:
                for event in events:
                    upcoming_events.append(f"{date.strftime('%Y-%m-%d')} - {event.description}")

        # Add upcoming events to the sidebar listbox
        for event in upcoming_events:
            self.sidebar_events_list.insert(tk.END, event)

    def sidebar_event_selected(self, event):
        selection = self.sidebar_events_list.curselection()
        if selection:
            selected_event = self.sidebar_events_list.get(selection[0])
            date_str, description = selected_event.split(" - ")
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            self.show_events_for_date(selected_date)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = CalendarApp(root)
    app.run()
