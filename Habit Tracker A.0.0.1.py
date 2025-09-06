import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# ---------------- Habit Class ----------------
class Habit:
    def __init__(self, name):
        self.name = name
        self.completion_dates = set()  # Stores datetime.date objects
        self.streak = 0
        self.update_streak()

    def mark_completed(self):
        today = datetime.now().date()
        if today in self.completion_dates:
            return False
        self.completion_dates.add(today)
        self.update_streak()
        return True

    def update_streak(self):
        today = datetime.now().date()
        streak = 0
        day = today
        while day in self.completion_dates:
            streak += 1
            day -= timedelta(days=1)
        self.streak = streak

    def last_completed_str(self):
        if not self.completion_dates:
            return "Never"
        return max(self.completion_dates).strftime("%Y-%m-%d")

    def get_dates_for_graph(self, days=30):
        """Return a list of last `days` dates and streak values."""
        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(days)][::-1]
        streaks = []
        current_streak = 0
        for date in dates:
            if date in self.completion_dates:
                current_streak += 1
            else:
                current_streak = 0
            streaks.append(current_streak)
        return dates, streaks

# ---------------- Main App ----------------
class HabitTrackerApp:
    DATA_FILE = "habits.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        self.habits = {}  # name -> Habit object

        self.create_widgets()
        self.load_habits()
        self.refresh_habit_list()
        self.update_date()

    # ---------------- UI Setup ----------------
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        self.habits_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        self.graph_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.habits_tab, text="Habits")
        self.notebook.add(self.graph_tab, text="Progress Graph")

        # Habits tab
        self.main_container = tk.Frame(self.habits_tab, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Date display
        self.date_label = tk.Label(self.main_container, font=("Helvetica", 12),
                                   bg="#e0e0e0", relief=tk.RAISED, padx=10, pady=5)
        self.date_label.pack(fill=tk.X, pady=(0, 10))

        # Scrollable habit frame
        self.habit_canvas = tk.Canvas(self.main_container, bg="#f0f0f0")
        self.habit_frame = tk.Frame(self.habit_canvas, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.habit_canvas.yview)
        self.habit_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.habit_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.habit_canvas.create_window((0, 0), window=self.habit_frame, anchor='nw')
        self.habit_frame.bind("<Configure>", lambda e: self.habit_canvas.configure(scrollregion=self.habit_canvas.bbox("all")))

        # Buttons
        self.button_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, pady=10)

        self.add_habit_button = tk.Button(self.button_frame, text="Add New Habit", command=self.add_habit,
                                          bg="#4CAF50", fg="white", padx=20, pady=5)
        self.add_habit_button.pack(side=tk.LEFT, padx=5)

        self.clear_all_button = tk.Button(self.button_frame, text="Clear All", command=self.clear_all_habits,
                                          bg="#f44336", fg="white", padx=20, pady=5)
        self.clear_all_button.pack(side=tk.RIGHT, padx=5)

        # Graph setup
        self.fig = Figure(figsize=(8, 5))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------------- Date ----------------
    def update_date(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_label.config(text=f"Today's Date: {current_date}")
        self.root.after(1000, self.update_date)

    # ---------------- Habit Operations ----------------
    def add_habit(self):
        habit_name = simpledialog.askstring("Add Habit", "Enter habit name:")
        if habit_name:
            if habit_name in self.habits:
                messagebox.showwarning("Warning", "Habit already exists!")
                return
            self.habits[habit_name] = Habit(habit_name)
            self.refresh_habit_list()
            self.update_graph()
            self.save_habits()

    def clear_all_habits(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all habits?"):
            self.habits.clear()
            self.refresh_habit_list()
            self.update_graph()
            self.save_habits()

    def mark_completed(self, habit_name):
        habit = self.habits.get(habit_name)
        if not habit:
            messagebox.showerror("Error", f'Habit "{habit_name}" not found.')
            return

        if not habit.mark_completed():
            messagebox.showinfo("Already Completed", f'You already completed "{habit_name}" today!')
            return

        self.refresh_habit_list()
        self.update_graph()
        self.save_habits()
        messagebox.showinfo("Success", f'Habit "{habit_name}" completed! Current streak: {habit.streak} days')

    # ---------------- Habit List ----------------
    def refresh_habit_list(self):
        # Clear existing
        for widget in self.habit_frame.winfo_children():
            widget.destroy()

        headers = ["Habit Name", "Current Streak", "Last Completed", "Action"]
        for col, header in enumerate(headers):
            label = tk.Label(self.habit_frame, text=header, font=("Helvetica", 10, "bold"),
                             bg="#e0e0e0", padx=10, pady=5)
            label.grid(row=0, column=col, sticky="ew", padx=2)

        for row, (name, habit) in enumerate(self.habits.items(), start=1):
            tk.Label(self.habit_frame, text=name, bg="#f0f0f0").grid(row=row, column=0, padx=5, pady=2)
            tk.Label(self.habit_frame, text=str(habit.streak), bg="#f0f0f0").grid(row=row, column=1, padx=5, pady=2)
            tk.Label(self.habit_frame, text=habit.last_completed_str(), bg="#f0f0f0").grid(row=row, column=2, padx=5, pady=2)
            tk.Button(self.habit_frame, text="Complete", bg="#2196F3", fg="white",
                      command=lambda h=name: self.mark_completed(h)).grid(row=row, column=3, padx=5, pady=2)

    # ---------------- Graph ----------------
    def update_graph(self):
        self.ax.clear()
        if not self.habits:
            self.ax.text(0.5, 0.5, 'No habits to display',
                         horizontalalignment='center', verticalalignment='center', fontsize=14)
            self.canvas.draw()
            return

        for habit in self.habits.values():
            dates, streaks = habit.get_dates_for_graph(days=30)
            self.ax.plot(dates, streaks, marker='o', label=habit.name, linewidth=2)

        self.ax.set_title('Habit Progress (Last 30 Days)')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Streak')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        self.fig.autofmt_xdate()
        self.canvas.draw()

    # ---------------- Persistence ----------------
    def save_habits(self):
        data = {}
        for name, habit in self.habits.items():
            data[name] = [d.strftime("%Y-%m-%d") for d in habit.completion_dates]
        with open(self.DATA_FILE, "w") as f:
            json.dump(data, f)

    def load_habits(self):
        try:
            with open(self.DATA_FILE) as f:
                data = json.load(f)
            for name, dates in data.items():
                habit = Habit(name)
                habit.completion_dates = set(datetime.strptime(d, "%Y-%m-%d").date() for d in dates)
                habit.update_streak()
                self.habits[name] = habit
        except FileNotFoundError:
            pass

# ---------------- Run App ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
