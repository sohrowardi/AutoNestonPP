import os
import json
import tkinter as tk
from tkinter import filedialog
from natsort import natsorted

# Define a file to store the last used folder path
config_file = "last_folder.json"

def get_folder_path():
    """Retrieve the last used folder or ask the user to select a new one using a GUI."""
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            folder_path = data.get("folder_path", "")
            if os.path.exists(folder_path):
                return folder_path
    
    # Open a GUI dialog to select a folder
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select the folder containing your clips")
    
    if not folder_path:
        print("No folder selected. Exiting...")
        exit()
    
    # Save the folder path for future use
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({"folder_path": folder_path}, f)
    
    return folder_path

def create_txt_file():
    folder_path = get_folder_path()
    
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' was not found. Please reselect.")
        os.remove(config_file)  # Remove the stored path since it's invalid
        create_txt_file()  # Restart the function to ask again
        return
    
    # Get the list of .mp4 files
    mp4_files = [file for file in os.listdir(folder_path) if file.endswith(".mp4")]
    
    # Sort the files naturally
    mp4_files = natsorted(mp4_files)
    
    # Define the output .txt file name
    txt_file_name = f"Clip Collections[{len(mp4_files)}].txt"
    
    # Write the sorted file names (without extension) to the .txt file
    with open(txt_file_name, "w", encoding="utf-8") as txt_file:
        for file in mp4_files:
            file_name_without_ext = os.path.splitext(file)[0]
            txt_file.write(file_name_without_ext + "\n")
    
    print(f"Successfully written {len(mp4_files)} files (without extension) to {txt_file_name}")

if __name__ == "__main__":
    create_txt_file()

input()