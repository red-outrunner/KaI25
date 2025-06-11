import sys
import os
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCalendarWidget, QListWidget, QInputDialog,
    QMessageBox, QSplitter, QListWidgetItem
)
from PyQt6.QtGui import QFont, QColor, QBrush, QTextCharFormat
from PyQt6.QtCore import Qt, QDate

# Define the Event class (remains the same)
class Event:
    def __init__(self, description, repeat_interval="None"):
        self.description = description
        self.repeat_interval = repeat_interval

class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ubomvu Calendar (PyQt6)")
        self.setGeometry(100, 100, 1200, 800)

        # --- Database Initialization ---
        self.db_file = 'calendar.db'
        self.init_db()
        self.events = self.load_events_from_db()

        # --- Main UI Setup ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Use a splitter to make calendar and sidebar resizable
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        self.create_calendar_section()
        self.create_sidebar_section()

        # Initial population of UI
        self.update_sidebar()
        self.highlight_dates_with_events()

    def create_calendar_section(self):
        """Creates the left-hand side of the UI with the calendar."""
        calendar_container = QWidget()
        calendar_layout = QVBoxLayout(calendar_container)

        # --- Calendar Widget ---
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Connect signals to slots (event handlers)
        self.calendar.clicked[QDate].connect(self.date_clicked)
        self.calendar.currentPageChanged.connect(self.month_changed)

        calendar_layout.addWidget(self.calendar)
        self.splitter.addWidget(calendar_container)

    def create_sidebar_section(self):
        """Creates the right-hand side of the UI with the event list."""
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)

        # --- Upcoming Events Label ---
        sidebar_label = QLabel("Upcoming Events")
        sidebar_label.setFont(QFont('Helvetica', 14, QFont.Weight.Bold))
        sidebar_layout.addWidget(sidebar_label)

        # --- Events List Widget ---
        self.event_list_widget = QListWidget()
        self.event_list_widget.itemDoubleClicked.connect(self.edit_event_from_list)
        sidebar_layout.addWidget(self.event_list_widget)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(self.add_event)

        self.delete_event_btn = QPushButton("Delete Event")
        self.delete_event_btn.clicked.connect(self.delete_event)

        button_layout.addWidget(self.add_event_btn)
        button_layout.addWidget(self.delete_event_btn)
        sidebar_layout.addLayout(button_layout)

        self.splitter.addWidget(sidebar_container)

    # --- Event Handlers (Slots) ---

    def date_clicked(self, qdate):
        """Handles when a user clicks a date on the calendar."""
        self.update_sidebar_for_date(qdate)

    def month_changed(self):
        """Handles when the user navigates to a new month."""
        self.highlight_dates_with_events()

    def add_event(self):
        """Adds a new event for the currently selected date."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")

        text, ok = QInputDialog.getText(self, 'Add Event', f'Enter event description for {date_str}:')
        if ok and text:
            py_date = selected_date.toPyDate()
            event = Event(text)
            if py_date not in self.events:
                self.events[py_date] = []
            self.events[py_date].append(event)

            self.save_event_to_db(py_date, event)
            self.update_sidebar()
            self.highlight_dates_with_events()

    def delete_event(self):
        """Deletes the selected event from the list."""
        selected_items = self.event_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an event from the list to delete.")
            return

        selected_item = selected_items[0]
        event_text = selected_item.text()
        date_str = event_text.split(" - ")[0]
        description = event_text.split(" - ")[1]
        py_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        reply = QMessageBox.question(self, 'Delete Event', f'Are you sure you want to delete this event?\n\n"{description}"',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from local dictionary
            self.events[py_date] = [e for e in self.events[py_date] if e.description != description]
            if not self.events[py_date]:
                del self.events[py_date]

            # Remove from database
            self.delete_event_from_db(py_date, description)

            # Update UI
            self.update_sidebar()
            self.highlight_dates_with_events()

    def edit_event_from_list(self, item):
        """Edits an event when it's double-clicked in the list."""
        event_text = item.text()
        date_str, old_description = event_text.split(" - ")
        py_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        new_description, ok = QInputDialog.getText(self, 'Edit Event', 'Enter the new description:', text=old_description)

        if ok and new_description and new_description != old_description:
            # Update local dictionary
            for event in self.events[py_date]:
                if event.description == old_description:
                    event.description = new_description
                    break

            # Update database by deleting old and inserting new
            self.delete_event_from_db(py_date, old_description)
            self.save_event_to_db(py_date, Event(new_description))

            # Update UI
            self.update_sidebar()

    # --- UI Update Methods ---

    def highlight_dates_with_events(self):
        """Applies a bold format to dates in the calendar that have events."""
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold)

        for date, event_list in self.events.items():
            if event_list:
                qdate = QDate(date.year, date.month, date.day)
                self.calendar.setDateTextFormat(qdate, fmt)

        # Reset format for dates with no events
        # A more optimized way would be to track removed events
        # For simplicity, we can just clear formats and re-apply
        all_dates_in_view = [self.calendar.dateTextFormat(QDate(self.calendar.yearShown(), self.calendar.monthShown(), day)) for day in range(1, 32)]

        clean_format = QTextCharFormat() # Default format
        for day in range(1, 32):
            try:
                qdate = QDate(self.calendar.yearShown(), self.calendar.monthShown(), day)
                if qdate.toPyDate() not in self.events:
                    self.calendar.setDateTextFormat(qdate, clean_format)
            except ValueError:
                continue # Handles non-existent dates like Feb 30

    def update_sidebar(self):
        """Updates the sidebar to show all upcoming events."""
        self.event_list_widget.clear()
        today = datetime.now().date()
        upcoming_events = []
        for date, events_list in sorted(self.events.items()):
            if date >= today:
                for event in events_list:
                    upcoming_events.append((date, event.description))

        for date, description in upcoming_events:
            item = QListWidgetItem(f"{date.strftime('%Y-%m-%d')} - {description}")
            self.event_list_widget.addItem(item)

    def update_sidebar_for_date(self, qdate):
        """Updates the sidebar to show events for a specific date."""
        self.event_list_widget.clear()
        py_date = qdate.toPyDate()

        if py_date in self.events:
            for event in self.events[py_date]:
                item = QListWidgetItem(f"{py_date.strftime('%Y-%m-%d')} - {event.description}")
                self.event_list_widget.addItem(item)
        else:
             self.event_list_widget.addItem("No events for this date.")

    # --- Database Methods (mostly unchanged) ---
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                event_date TEXT NOT NULL,
                description TEXT NOT NULL,
                repeat_interval TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_events_from_db(self):
        events = {}
        if not os.path.exists(self.db_file): return events
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT event_date, description, repeat_interval FROM events")
            for row in cursor.fetchall():
                event_date = datetime.strptime(row[0], "%Y-%m-%d").date()
                event = Event(row[1], row[2])
                if event_date not in events:
                    events[event_date] = []
                events[event_date].append(event)
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading events: {e}")
        return events

    def save_event_to_db(self, date, event):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (event_date, description, repeat_interval) VALUES (?, ?, ?)",
                           (date.strftime("%Y-%m-%d"), event.description, event.repeat_interval))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error saving event: {e}")

    def delete_event_from_db(self, date, description):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE event_date = ? AND description = ?",
                           (date.strftime("%Y-%m-%d"), description))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error deleting event: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = CalendarApp()
    main_win.show()
    sys.exit(app.exec())
