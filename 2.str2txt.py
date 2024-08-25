import re
import os
import subprocess
import sys
from tkinter import Tk, filedialog

def capitalize_first_letter(text):
    if text:
        return text[0].upper() + text[1:]
    return text

def process_dialogue(dialogue):
    # Remove leading "- " or "-" if present
    if dialogue.startswith("- "):
        dialogue = dialogue[2:]
    elif dialogue.startswith("-"):
        dialogue = dialogue[1:]

    # Replace '?' with '.' in the middle of the dialogue
    dialogue = re.sub(r'(?<!\?)\?(?!$)', '.', dialogue)
    
    # Remove all double quotation marks
    dialogue = dialogue.replace('"', '')
    
    # Remove any "</i>" and replace corresponding "<i>" tags with plain text
    dialogue = re.sub(r'</i>', '', dialogue)
    dialogue = re.sub(r'<i>', '', dialogue)
    
    # Capitalize the first letter of each sentence
    dialogue = capitalize_first_letter(dialogue)
    
    # Remove trailing '.' or '?' or ',' if it's at the end of the sentence
    if dialogue.endswith(".") or dialogue.endswith("?") or dialogue.endswith(","):
        dialogue = dialogue[:-1]
    
    return dialogue

def remove_timestamps(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.readlines()

    dialogue = []
    current_dialogue = []
    for line in content:
        line = line.strip()
        # Skip lines that are timestamps or dialogue numbers
        if re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
            continue
        # If the line is empty, it means the end of a dialogue block
        if line == "":
            if current_dialogue:
                # Join dialogue lines, process them, and add to the dialogue list
                dialogue_text = " ".join(current_dialogue)
                dialogue_text = process_dialogue(dialogue_text)
                dialogue.append(dialogue_text)
                current_dialogue = []
        else:
            # Add the line to the current dialogue
            current_dialogue.append(line)

    # Append any remaining dialogue
    if current_dialogue:
        dialogue_text = " ".join(current_dialogue)
        dialogue_text = process_dialogue(dialogue_text)
        dialogue.append(dialogue_text)

    return "\n".join(dialogue)

def select_srt_file():
    Tk().withdraw()  # Hide the root window
    srt_files = [f for f in os.listdir() if f.endswith('.srt')]

    if not srt_files:
        print("No .srt files found in the directory.")
        return None

    if len(srt_files) == 1:
        return srt_files[0]

    print("Multiple .srt files found. Please select one:")
    for i, file in enumerate(srt_files):
        print(f"{i + 1}: {file}")

    while True:
        try:
            choice = int(input("Enter the number of the file you want to select: ")) - 1
            if 0 <= choice < len(srt_files):
                return srt_files[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # Change the working directory to the script's directory

    # Select the .srt file
    srt_file = select_srt_file()

    if srt_file is None:
        return

    # Define input and output file paths
    input_file = srt_file
    output_file = f"{os.path.splitext(input_file)[0]}.txt"
    
    print(f"Processing file: {input_file}")

    # Process the file to remove timestamps
    processed_text = remove_timestamps(input_file)

    print(f"Saving the processed text to {output_file}...")

    # Save the processed text to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(processed_text)

    print(f"Processed file saved as {output_file}")

    # Open the output file with the default text editor
    if os.name == 'nt':  # For Windows
        os.startfile(output_file)
    elif os.name == 'posix':  # For macOS or Linux
        subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', output_file))

if __name__ == "__main__":
    main()

input()
