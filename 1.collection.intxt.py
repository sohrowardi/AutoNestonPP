import os
from natsort import natsorted

def create_txt_file():
    # Define the folder path
    folder_path = r"F:\VIDEO (Clip Collection)\Movies and Shows\Movies and shows"
    
    # Check if the folder or drive exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder or drive '{folder_path}' was not found.")
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
            # Remove the .mp4 extension but keep the rest of the filename intact
            file_name_without_ext = os.path.splitext(file)[0]
            txt_file.write(file_name_without_ext + "\n")
    
    print(f"Successfully written {len(mp4_files)} files (without extension) to {txt_file_name}")

if __name__ == "__main__":
    create_txt_file()

input()