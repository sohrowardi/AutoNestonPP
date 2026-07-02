import argparse
import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from natsort import natsorted

# Define a file to store the last used folder path
config_file = Path("last_folder.json")


def get_folder_path(folder_arg=None, reset=False):
    """Retrieve a folder path from the command line, saved config, or GUI."""
    if folder_arg:
        return Path(folder_arg)

    if not reset and config_file.exists():
        with config_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            folder_path = data.get("folder_path", "")
            if folder_path:
                candidate = Path(folder_path)
                if candidate.exists():
                    print(f"Using saved folder path: {candidate}")
                    return candidate
                else:
                    print(f"Saved folder path does not exist: {candidate}")

    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select the folder containing your clips")

    if not folder_path:
        print("No folder selected. Exiting...")
        sys.exit(1)

    selected = Path(folder_path)
    with config_file.open("w", encoding="utf-8") as f:
        json.dump({"folder_path": str(selected)}, f)

    print(f"Selected folder path: {selected}")
    return selected


def create_txt_file(folder_path=None, reset=False):
    folder = get_folder_path(folder_arg=folder_path, reset=reset)

    if not folder.exists():
        print(f"Error: The folder '{folder}' was not found. Please reselect.")
        if config_file.exists():
            config_file.unlink()
        return create_txt_file(reset=True)

    mp4_files = [file.name for file in folder.iterdir() if file.is_file() and file.suffix.lower() == ".mp4"]
    mp4_files = natsorted(mp4_files)

    txt_file_name = f"Clip Collections[{len(mp4_files)}].txt"
    output_path = Path.cwd() / txt_file_name

    with output_path.open("w", encoding="utf-8") as txt_file:
        for file_name in mp4_files:
            txt_file.write(Path(file_name).stem + "\n")

    print(f"Folder: {folder}")
    print(f"Found {len(mp4_files)} .mp4 files")
    print(f"Successfully written {len(mp4_files)} lines to {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a folder of .mp4 clips to a text list.")
    parser.add_argument("--folder", help="Path to the folder containing clips")
    parser.add_argument("--reset", action="store_true", help="Ignore saved folder path and choose a new one")
    args = parser.parse_args()

    create_txt_file(folder_path=args.folder, reset=args.reset)

    input()
