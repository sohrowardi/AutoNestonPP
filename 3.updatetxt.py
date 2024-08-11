import os
import tkinter as tk
from tkinter import filedialog

def process_files(a_file_path, b_file_path):
    # Step 1: Read the main database file and store sentences with their numbers
    sentence_count = {}
    with open(a_file_path, 'r', encoding='utf-8') as a_file:
        for line in a_file:
            try:
                sentence, number = line.rsplit(' ', 1)
                number = int(number.strip('()\n'))  # Correctly strip parentheses and newline
                if sentence not in sentence_count:
                    sentence_count[sentence] = []
                sentence_count[sentence].append(number)
            except ValueError:
                # Handle lines that don't follow the expected format
                print(f"Skipping invalid line in {a_file_path}: {line.strip()}")

    # Step 2: Process the other file and update sentences with the correct number
    updated_b_lines = []
    with open(b_file_path, 'r', encoding='utf-8') as b_file:
        for line in b_file:
            sentence = line.strip()
            if sentence in sentence_count:
                next_number = max(sentence_count[sentence]) + 1
                sentence_count[sentence].append(next_number)
            else:
                next_number = 0
                sentence_count[sentence] = [next_number]
            
            updated_b_lines.append(f"{sentence} ({next_number})\n")
    
    # Step 3: Write the updated sentences back to the file
    with open(b_file_path, 'w', encoding='utf-8') as b_file:
        b_file.writelines(updated_b_lines)

def select_file(title, default_file=None):
    root = tk.Tk()
    root.withdraw() # Hide the root window

    file_path = filedialog.askopenfilename(title=title, initialfile=default_file)
    return file_path

if __name__ == "__main__":
    # Define the folder path where the files are located
    folder_path = os.path.dirname(os.path.abspath(__file__))  # Same folder as the script
    
    # Find the main database file starting with "Clip Collections"
    clip_files = [file for file in os.listdir(folder_path) if file.startswith("Clip Collections") and file.endswith(".txt")]
    
    if clip_files:
        # Automatically select the main database file (the one starting with "Clip Collections")
        a_file_path = os.path.join(folder_path, clip_files[0])
    else:
        # Ask user to select the main database file if not found
        print("No 'Clip Collections' file found. Please select the main database file (with numbers).")
        a_file_path = select_file("Select the main database file (with numbers)")

    # Find all other .txt files in the folder
    txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt") and not file.startswith("Clip Collections")]
    
    if len(txt_files) == 1:
        # Automatically select the only other .txt file
        b_file_path = os.path.join(folder_path, txt_files[0])
    elif len(txt_files) > 1:
        # Ask user to select the .txt file to update
        print("Multiple text files found for updating. Please select the file to be updated.")
        b_file_path = select_file("Select the file to be updated", default_file=os.path.join(folder_path, txt_files[0]))
    else:
        print("Error: No file found to update.")
        b_file_path = None

    # Validate file paths and process
    if not a_file_path:
        print("Error: No file selected for the main database.")
    elif not os.path.isfile(a_file_path):
        print(f"Error: The file '{a_file_path}' does not exist.")
    elif not b_file_path:
        print("Error: No file selected for updating.")
    elif not os.path.isfile(b_file_path):
        print(f"Error: The file '{b_file_path}' does not exist.")
    else:
        process_files(a_file_path, b_file_path)
        print(f"Updated '{b_file_path}' successfully.")
