import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.simpledialog as simpledialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class HabitTrackerApp:
    def __init__(self, root):
        self.habits = {}
        self.root = root
        self.setup_main_window()
        self.create_widgets()
        self.refresh_habit_list()
        self.update_date()

    def setup_main_window(self):
        self.root.title("Habit Tracker")
        self.root.geometry("800x800")
        self.root.configure(bg="#f0f0f0")

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.habits_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        self.graph_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        
        self.notebook.add(self.habits_tab, text="Habits")
        self.notebook.add(self.graph_tab, text="Progress Graph")

        # Main container in habits tab
        self.main_container = tk.Frame(self.habits_tab, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Date display
        self.date_label = tk.Label(
            self.main_container,
            font=("Helvetica", 12),
            bg="#e0e0e0",
            relief=tk.RAISED,
            padx=10,
            pady=5
        )
        self.date_label.pack(fill=tk.X, pady=(0, 10))

        # Habits container
        self.habit_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        self.habit_frame.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        self.button_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, pady=10)

        # Add habit button
        self.add_habit_button = tk.Button(
            self.button_frame,
            text="Add New Habit",
            command=self.add_habit,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        )
        self.add_habit_button.pack(side=tk.LEFT, padx=5)

        # Clear all button
        self.clear_all_button = tk.Button(
            self.button_frame,
            text="Clear All",
            command=self.clear_all_habits,
            bg="#f44336",
            fg="white",
            padx=20,
            pady=5
        )
        self.clear_all_button.pack(side=tk.RIGHT, padx=5)

        # Graph setup
        self.setup_graph()

    def update_date(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label.config(text=f"Today's Date: {current_date}")
        self.root.after(1000, self.update_date)  # Update every second

    def add_habit(self):
        habit_name = simpledialog.askstring("Add Habit", "Enter habit name:")
        if habit_name:
            if habit_name in self.habits:
                messagebox.showwarning("Warning", "Habit already exists!")
                return
            self.habits[habit_name] = {
                "streak": 0,
                "last_completed": None,
                "completion_dates": {}
            }
            self.refresh_habit_list()
            self.update_graph()

    def clear_all_habits(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all habits?"):
            self.habits.clear()
            self.refresh_habit_list()
            self.update_graph()

    def refresh_habit_list(self):
        # Clear existing habits
        for widget in self.habit_frame.winfo_children():
            widget.destroy()

        # Create header
        headers = ["Habit Name", "Current Streak", "Last Completed", "Action"]
        for col, header in enumerate(headers):
            label = tk.Label(
                self.habit_frame,
                text=header,
                font=("Helvetica", 10, "bold"),
                bg="#e0e0e0",
                padx=10,
                pady=5
            )
            label.grid(row=0, column=col, sticky="ew", padx=2)

        # Add habits
        for row, (habit_name, habit_data) in enumerate(self.habits.items(), start=1):
            # Habit name
            tk.Label(
                self.habit_frame,
                text=habit_name,
                bg="#f0f0f0"
            ).grid(row=row, column=0, padx=5, pady=2)

            # Streak
            tk.Label(
                self.habit_frame,
                text=str(habit_data["streak"]),
                bg="#f0f0f0"
            ).grid(row=row, column=1, padx=5, pady=2)

            # Last completed
            tk.Label(
                self.habit_frame,
                text=habit_data["last_completed"] or "Never",
                bg="#f0f0f0"
            ).grid(row=row, column=2, padx=5, pady=2)

            # Complete button
            tk.Button(
                self.habit_frame,
                text="Complete",
                command=lambda h=habit_name: self.mark_completed(h),
                bg="#2196F3",
                fg="white"
            ).grid(row=row, column=3, padx=5, pady=2)

    def setup_graph(self):
        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_graph(self):
        self.ax.clear()
        
        if not self.habits:
            self.ax.text(0.5, 0.5, 'No habits to display', 
                        horizontalalignment='center',
                        verticalalignment='center')
            self.canvas.draw()
            return

        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') 
                for x in range(7)][::-1]
        
        for habit_name, habit_data in self.habits.items():
            streaks = []
            current_streak = 0
            
            for date in dates:
                if habit_data.get('completion_dates', {}).get(date):
                    current_streak += 1
                else:
                    current_streak = 0
                streaks.append(current_streak)
            
            self.ax.plot(dates, streaks, marker='o', label=habit_name, linewidth=2)

        self.ax.set_title('Daily Habit Progress')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Streak Count')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        
        plt.setp(self.ax.get_xticklabels(), rotation=45)
        self.fig.tight_layout()
        
        self.canvas.draw()

    def mark_completed(self, habit_name):
        today = datetime.now().strftime("%Y-%m-%d")
        habit_data = self.habits.get(habit_name)
        
        if not habit_data:
            messagebox.showerror("Error", f'Habit "{habit_name}" not found.')
            return

        if habit_data.get("last_completed") == today:
            messagebox.showinfo("Already Completed", f'You already completed "{habit_name}" today!')
            return

        if 'completion_dates' not in habit_data:
            habit_data['completion_dates'] = {}
        
        habit_data['completion_dates'][today] = True
        habit_data["last_completed"] = today

        if habit_data["last_completed"]:
            last_date = datetime.strptime(habit_data["last_completed"], "%Y-%m-%d")
            days_difference = (datetime.now() - last_date).days
            
            if days_difference > 1:
                habit_data["streak"] = 1
                messagebox.showinfo("Streak Reset", "Streak reset due to missed day(s).")
            else:
                habit_data["streak"] += 1
        else:
            habit_data["streak"] = 1

        self.refresh_habit_list()
        self.update_graph()
        messagebox.showinfo("Success", f'Habit "{habit_name}" completed! Current streak: {habit_data["streak"]} days')

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
