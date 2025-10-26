#!/usr/bin/env python3
# The above line allows this file to be executed directly in Unix-like systems (Linux/Mac)
# by typing: ./task_cli.py instead of python3 task_cli.py

import json
import os
import sys
from datetime import datetime

# The name of the JSON file that will store all tasks.
TASKS_FILE = "tasks.json"

# =====================================================
#                  UTILITY FUNCTIONS
# =====================================================

def load_tasks():
    """
    Reads the tasks from the JSON file.
    - If the file doesn't exist, return an empty list.
    - If the file exists but is corrupted (invalid JSON), also return an empty list.
    """
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    """
    Saves the given list of task dictionaries into the JSON file.
    Uses pretty-printing (indent=4) for readability.
    """
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def get_next_id(tasks):
    """
    Generates a new task ID.
    - If no tasks exist, start at 1.
    - Otherwise, take the maximum current ID and add 1.
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def get_task_by_id(tasks, task_id):
    """
    Searches for and returns a task dictionary with the given ID.
    If not found, returns None.
    """
    return next((task for task in tasks if task["id"] == task_id), None)

# =====================================================
#                      COMMANDS
# =====================================================

def add_task(description):
    """
    Adds a new task to the list with default status 'todo'.
    Also records timestamps for creation and last update.
    """
    tasks = load_tasks()
    new_task = {
        "id": get_next_id(tasks),
        "description": description,
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {new_task['id']})")

def update_task(task_id, description):
    """
    Updates the description of an existing task by ID.
    If task not found, prints an error message.
    """
    tasks = load_tasks()
    task = get_task_by_id(tasks, task_id)
    if not task:
        print(f"Error: Task with ID {task_id} not found.")
        return
    task["description"] = description
    task["updatedAt"] = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"Task {task_id} updated successfully.")

def delete_task(task_id):
    """
    Deletes a task with the given ID from the JSON file.
    If ID doesn’t exist, prints an error.
    """
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task["id"] != task_id]
    if len(new_tasks) == len(tasks):
        print(f"Error: Task with ID {task_id} not found.")
        return
    save_tasks(new_tasks)
    print(f"Task {task_id} deleted successfully.")

def mark_task(task_id, status):
    """
    Changes the status of a task to 'in-progress' or 'done'.
    Also updates the last updated timestamp.
    """
    tasks = load_tasks()
    task = get_task_by_id(tasks, task_id)
    if not task:
        print(f"Error: Task with ID {task_id} not found.")
        return
    if status not in ["in-progress", "done"]:
        print("Error: Invalid status. Use 'in-progress' or 'done'.")
        return
    task["status"] = status
    task["updatedAt"] = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"Task {task_id} marked as {status}.")

def list_tasks(status=None):
    """
    Lists tasks to the terminal.
    - If no status is specified, show all tasks.
    - If a status is given (e.g., 'todo'), filter tasks accordingly.
    """
    tasks = load_tasks()

    # Filter by status if provided
    if status:
        tasks = [t for t in tasks if t["status"] == status]
        if not tasks:
            print(f"No tasks found with status '{status}'.")
            return
    elif not tasks:
        print("No tasks found.")
        return

    # Print all matching tasks in a readable format
    for task in tasks:
        print(
            f"[{task['id']}] {task['description']} "
            f"(status: {task['status']}, updated: {task['updatedAt']})"
        )

# =====================================================
#                   MAIN CLI HANDLER
# =====================================================

def main():
    """
    Entry point for the CLI.
    Parses command-line arguments using sys.argv.
    Routes commands to their corresponding handler functions.
    """
    if len(sys.argv) < 2:
        # If no command is provided, print usage instructions
        print("Usage: task-cli <command> [arguments]")
        print("Commands: add, update, delete, mark-in-progress, mark-done, list")
        sys.exit(1)

    command = sys.argv[1]  # The first argument after the script name

    # ------------------ ADD COMMAND ------------------
    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: task-cli add <description>")
        else:
            add_task(" ".join(sys.argv[2:]))

    # ------------------ UPDATE COMMAND ------------------
    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: task-cli update <id> <new description>")
        else:
            try:
                task_id = int(sys.argv[2])
                update_task(task_id, " ".join(sys.argv[3:]))
            except ValueError:
                print("Error: Task ID must be a number.")

    # ------------------ DELETE COMMAND ------------------
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: task-cli delete <id>")
        else:
            try:
                delete_task(int(sys.argv[2]))
            except ValueError:
                print("Error: Task ID must be a number.")

    # ------------------ MARK IN PROGRESS ------------------
    elif command == "mark-in-progress":
        if len(sys.argv) < 3:
            print("Usage: task-cli mark-in-progress <id>")
        else:
            try:
                mark_task(int(sys.argv[2]), "in-progress")
            except ValueError:
                print("Error: Task ID must be a number.")

    # ------------------ MARK DONE ------------------
    elif command == "mark-done":
        if len(sys.argv) < 3:
            print("Usage: task-cli mark-done <id>")
        else:
            try:
                mark_task(int(sys.argv[2]), "done")
            except ValueError:
                print("Error: Task ID must be a number.")

    # ------------------ LIST COMMAND ------------------
    elif command == "list":
        # If just 'list' → show all tasks
        # If 'list done/todo/in-progress' → filter
        if len(sys.argv) == 2:
            list_tasks()
        else:
            status = sys.argv[2]
            valid = ["todo", "done", "in-progress"]
            if status not in valid:
                print(f"Error: Invalid status '{status}'. Valid: {', '.join(valid)}")
            else:
                list_tasks(status)

    # ------------------ UNKNOWN COMMAND ------------------
    else:
        print(f"Unknown command: {command}")

# This ensures main() runs only when script is executed directly,
# not when imported as a module elsewhere.
if __name__ == "__main__":
    main()
