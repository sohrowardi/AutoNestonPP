import pyautogui
import time
import os
import pyperclip  # New import for clipboard operations
import keyboard  # New import for detecting key presses
import threading  # New import for threading

# Global variable to control the loop
stop_program = False

def monitor_esc_key():
    global stop_program
    while True:
        if keyboard.is_pressed('esc'):
            stop_program = True
            print("Program stopped by user.")
            break
        time.sleep(0.1)

def select_txt_file(directory):
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

    if not txt_files:
        print("No .txt files found in the directory.")
        return None

    if len(txt_files) == 1:
        return txt_files[0]

    print("Multiple .txt files found. Please select one:")
    for i, file in enumerate(txt_files):
        print(f"{i + 1}: {file}")

    while True:
        try:
            choice = int(input("Enter the number of the file you want to select: ")) - 1
            if 0 <= choice < len(txt_files):
                return txt_files[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

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
    
    for subtitle in subtitles[start_line:]:
        if stop_program:
            break

        print(f"Processing subtitle: {subtitle}")

        # Select the clip (Assuming 'd' selects the clip)
        pyautogui.press('d')
        time.sleep(0.5)  # Adjusted wait for the clip to be selected

        # Nest the clip (Assuming '2' nests the clip)
        pyautogui.press('2')
        time.sleep(0.8)  # Adjusted wait for the nesting to start

        # Copy the subtitle to the clipboard
        pyperclip.copy(subtitle)
        
        # Paste the copied subtitle
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)  # Wait for the text to be entered

        # Confirm the name change (Assuming 'Enter' confirms)
        pyautogui.press('enter')
        time.sleep(0.5)  # Adjusted wait for the nesting process to complete

        # Move to the next clip (Assuming 'Down Arrow' moves to the next clip)
        pyautogui.press('down')
        time.sleep(0.5)  # Adjusted wait before proceeding to the next iteration

    print("All subtitles processed.")

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
