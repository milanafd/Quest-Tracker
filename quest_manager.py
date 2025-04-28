import tkinter as tk
from tkinter import messagebox
import os
import json
import shutil
from datetime import datetime, timedelta

# Define the directory to store quests, named with the current date
def get_quest_dir():
    today = datetime.now().strftime("%Y-%m-%d")
    quest_dir = os.path.join("quests", today)
    os.makedirs(quest_dir, exist_ok=True)
    return quest_dir

QUESTS_DIR = get_quest_dir()

# Helper function to clean filenames
def clean_filename(filename):
    return filename.replace(" ", "_").replace("'", "").replace('"', "").replace("/", "_")

# Task List
tasks = []
task_id_counter = 1

def save_quests():
    for task in tasks:
        task_filename = os.path.join(QUESTS_DIR, f"{clean_filename(task['name'])}.json")
        task_data = {
            "id": task['id'],
            "name": task['name'],
            "status": task['status'],
            "log": task.get("log", "")
        }
        with open(task_filename, "w") as f:
            json.dump(task_data, f)

def find_latest_day_with_quests():
    quests_root = "quests"
    today_str = datetime.now().strftime("%Y-%m-%d")

    for folder_name in sorted(os.listdir(quests_root), reverse=True):
        folder_path = os.path.join(quests_root, folder_name)
        if os.path.isdir(folder_path) and folder_name < today_str:
            has_json = any(f.endswith(".json") for f in os.listdir(folder_path))
            if has_json:
                return folder_path
    return None

def load_quests():
    global tasks, task_id_counter
    tasks.clear()

    today_has_quests = any(f.endswith(".json") for f in os.listdir(QUESTS_DIR))

    if today_has_quests:
        for filename in os.listdir(QUESTS_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(QUESTS_DIR, filename), "r") as f:
                    task_data = json.load(f)
                    if task_data['status'] != "Quest completed":
                        tasks.append(task_data)
                        task_id_counter = max(task_id_counter, task_data['id'] + 1)
    else:
        latest_dir = find_latest_day_with_quests()
        if latest_dir:
            for filename in os.listdir(latest_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(latest_dir, filename), "r") as f:
                        task_data = json.load(f)
                        if task_data['status'] != "Quest completed":
                            tasks.append(task_data)
                            task_id_counter = max(task_id_counter, task_data['id'] + 1)
                            # Copy the quest's .txt log file forward if it exists
                            old_log_file = os.path.join(latest_dir, f"{clean_filename(task_data['name'])}.txt")
                            new_log_file = os.path.join(QUESTS_DIR, f"{clean_filename(task_data['name'])}.txt")
                            if os.path.exists(old_log_file):
                                shutil.copy2(old_log_file, new_log_file)
            save_quests()

    update_task_list()

def add_task():
    task_name = entry_task.get()
    if task_name:
        global task_id_counter
        task = {"id": task_id_counter, "name": task_name, "status": "Quest not completed", "log": ""}
        tasks.append(task)
        task_id_counter += 1
        entry_task.delete(0, tk.END)
        update_task_list()
        save_quests()
    else:
        messagebox.showwarning("Input Error", "Quest name cannot be empty!")

def complete_task():
    selected_task_index = listbox.curselection()
    if selected_task_index:
        task_index = selected_task_index[0]
        task = tasks[task_index]
        task["status"] = "Quest completed"
        update_task_list()
        save_quests()
    else:
        messagebox.showwarning("Selection Error", "Please select a Quest to complete!")

def uncomplete_task():
    selected_task_index = listbox.curselection()
    if selected_task_index:
        task_index = selected_task_index[0]
        task = tasks[task_index]
        if task["status"] == "Quest completed":
            task["status"] = "Quest not completed"
            update_task_list()
            save_quests()
        else:
            messagebox.showwarning("Status Error", "This Quest is not completed yet!")
    else:
        messagebox.showwarning("Selection Error", "Please select a quest to uncomplete!")

def update_task_list():
    listbox.delete(0, tk.END)
    for index, task in enumerate(tasks):
        task_display = f"ID: {task['id']} - {task['name']} - {task['status']}"
        listbox.insert(tk.END, task_display)
        if task['status'] == "Quest completed":
            listbox.itemconfig(index, {'bg': 'lightgreen'})

def update_log():
    selected_task_index = listbox.curselection()
    if selected_task_index:
        task_index = selected_task_index[0]
        task = tasks[task_index]
        log_entry = text_log.get("1.0", tk.END).strip()
        if log_entry:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_text = f"[{timestamp}] {log_entry}\n"
            task["log"] += log_text
            save_quests()

            quest_log_file = os.path.join(QUESTS_DIR, f"{clean_filename(task['name'])}.txt")
            with open(quest_log_file, "a") as quest_log:
                quest_log.write(log_text)

# UI Setup
root = tk.Tk()
root.title("Quest Tracker")

frame = tk.Frame(root)
frame.pack(pady=10)

label_task = tk.Label(frame, text="Quest:")
label_task.grid(row=0, column=0, padx=5)

entry_task = tk.Entry(frame, width=30)
entry_task.grid(row=0, column=1, padx=5)

button_add_task = tk.Button(frame, text="Add Quest", command=add_task)
button_add_task.grid(row=0, column=2, padx=5)

listbox = tk.Listbox(root, width=70, height=10)
listbox.pack(pady=10)

button_complete_task = tk.Button(frame, text="Complete Quest", command=complete_task)
button_complete_task.grid(row=2, column=1, pady=10)

button_uncomplete_task = tk.Button(frame, text="Uncomplete Quest", command=uncomplete_task)
button_uncomplete_task.grid(row=3, column=1, pady=10)

text_log = tk.Text(root, width=70, height=5)
text_log.pack(pady=5)

button_update_log = tk.Button(root, text="Update Quest Log", command=update_log)
button_update_log.pack(pady=5)

load_quests()
root.mainloop()

#v 1.4 was written with ChatGPT
