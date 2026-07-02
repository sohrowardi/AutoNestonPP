import pyautogui
import time
import os
import sys
import pyperclip
import keyboard
import threading
import tkinter as tk
from tkinter import Listbox

# Global variables to control the loop
stop_program = False
AUTOSAVE_INTERVAL = 200  # Save every N processed clips

def monitor_esc_key():
    global stop_program
    while True:
        if keyboard.is_pressed('esc'):
            stop_program = True
            print("Program stopped by user.")
            break
        time.sleep(0.1)

def find_matching_txt_file(directory):
    # Find all .srt files in the directory
    srt_files = [f for f in os.listdir(directory) if f.endswith('.srt')]
    
    # Find the corresponding .txt file for each .srt file
    for srt_file in srt_files:
        txt_file = srt_file.replace('.srt', '.txt')
        if txt_file in os.listdir(directory):
            return txt_file
    
    # If no matching .txt file found, return None
    return None

def select_txt_file(directory):
    # Try to find a matching .txt file first
    matching_file = find_matching_txt_file(directory)
    if matching_file:
        return matching_file

    # If no matching .txt file found, ask user to select a file
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

    if not txt_files:
        print("No .txt files found in the directory.")
        return None

    if len(txt_files) == 1:
        return txt_files[0]

    # Show GUI popup for file selection
    selected_file = [None]
    
    def on_select():
        selection = listbox_widget.curselection()
        if selection:
            selected_file[0] = txt_files[selection[0]]
            root.destroy()
    
    def on_double_click(event):
        selection = listbox_widget.curselection()
        if selection:
            selected_file[0] = txt_files[selection[0]]
            root.destroy()
    
    root = tk.Tk()
    root.title("Select .txt File")
    root.geometry("400x300")
    
    # Create listbox
    listbox_widget = Listbox(root, width=50)
    listbox_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Add files to listbox
    for file in txt_files:
        listbox_widget.insert(tk.END, file)
    
    # Bind double-click event
    listbox_widget.bind('<Double-Button-1>', on_double_click)
    
    # Create Select button
    select_btn = tk.Button(root, text="Select", command=on_select)
    select_btn.pack(pady=5)
    
    root.mainloop()
    
    return selected_file[0]

def read_lines_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def get_starting_line(subtitles):
    while True:
        try:
            start_line = input(f"Enter the line number to start from (default is 1): ")
            if start_line == "":
                start_line = 1
            else:
                start_line = int(start_line)
                
            if 1 <= start_line <= len(subtitles):
                confirmation = input(f"Start from line {start_line}: '{subtitles[start_line - 1]}'? (yes/no, default is yes): ").strip().lower()
                if confirmation == '' or confirmation == 'yes':
                    return start_line
            else:
                print(f"Invalid line number. Please enter a number between 1 and {len(subtitles)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def perform_save():
    print("Saving progress...")
    pyautogui.hotkey('ctrl', 's')
    time.sleep(10)


def automate_premiere_pro(file_path):
    global stop_program
    subtitles = read_lines_from_file(file_path)
    
    if not subtitles:
        print("No subtitles found.")
        return

    start_line = get_starting_line(subtitles) - 1  # Adjust for 0-based index

    # Give user time to switch focus to Premiere Pro
    print("Switch to Adobe Premiere Pro. You have 5 seconds.")
    time.sleep(5)
    
    for line_number, subtitle in enumerate(subtitles[start_line:], start=start_line):
        if stop_program:
            break

        print(f"Processing subtitle (Line {line_number + 1}): {subtitle}")

        # Select the clip (Assuming 'd' selects the clip)
        pyautogui.press('d')
        time.sleep(0.5)  # Adjusted wait for the clip to be selected
        if stop_program:
            break

        # Nest the clip (Assuming '2' nests the clip)
        pyautogui.press('2')
        time.sleep(0.8)  # Adjusted wait for the nesting to start
        if stop_program:
            break

        # Copy the subtitle to the clipboard
        pyperclip.copy(subtitle)
        
        # Paste the copied subtitle
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)  # Wait for the text to be entered
        if stop_program:
            break

        # Confirm the name change (Assuming 'Enter' confirms)
        pyautogui.press('enter')
        time.sleep(0.5)  # Adjusted wait for the nesting process to complete
        if stop_program:
            break

        # Move to the next clip (Assuming 'Down Arrow' moves to the next clip)
        pyautogui.press('down')
        time.sleep(0.5)  # Adjusted wait before proceeding to the next iteration

        if (line_number - start_line + 1) % AUTOSAVE_INTERVAL == 0:
            perform_save()

    if stop_program:
        print("Stop requested. Performing final save before exiting...")
    else:
        print("All subtitles processed. Performing final save and exiting...")

    perform_save()
    print("Final save complete. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    # Start the thread to monitor the "esc" key
    esc_thread = threading.Thread(target=monitor_esc_key)
    esc_thread.start()

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Select the .txt file
    txt_file = select_txt_file(script_dir)
    
    if txt_file:
        txt_file_path = os.path.join(script_dir, txt_file)
        print(f"Found file: {txt_file_path}")
        automate_premiere_pro(txt_file_path)
    else:
        print("No .txt file selected. Exiting.")
