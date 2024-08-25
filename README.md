# Video Processing Automation

This repository contains a set of Python scripts to automate the process of managing video files and subtitles, and to streamline the workflow in Adobe Premiere Pro. The scripts handle tasks from creating text files with video names to automating the nesting of clips based on subtitles.

## Overview of Scripts

1. **`collection.intxt.py`** - Creates a text file listing all video names in a specified folder.
2. **`srt2txt.py`** - Converts subtitle files in SRT format to a processed text format.
3. **`updatetxt.py`** - Updates a text file with numbers based on a reference file.
4. **`start.nesting.py`** - Automates the process of nesting clips in Adobe Premiere Pro based on a text file.

## Requirements

Before using the scripts, ensure you have the following Python packages installed:
- `pyautogui`
- `pyperclip`
- `keyboard`
- `natsort`

You can install the required packages using pip:

```bash
pip install pyautogui pyperclip keyboard natsort
```

## Usage Instructions

### 1. `collection.intxt.py`

This script generates a text file listing all video files (with `.mp4` extension) from a specified folder.

**How to use:**

1. Update the `folder_path` variable in the script to point to the folder containing your video files.
2. Run the script:

    ```bash
    python collection.intxt.py
    ```

3. The script will create a text file named `Clip Collections[number].txt` in the current directory, where `[number]` indicates the count of files.

### 2. `srt2txt.py`

This script processes SRT subtitle files and converts them to a cleaned-up text format.

**How to use:**

1. Place your `.srt` files in the same directory as the script.
2. Run the script:

    ```bash
    python srt2txt.py
    ```

3. Follow the prompts to select an SRT file. The script will create a new `.txt` file with the processed subtitles.

### 3. `updatetxt.py`

This script updates a text file with sentence numbers based on a reference file created by `collection.intxt.py`.

**How to use:**

1. Ensure the reference file (created by `collection.intxt.py`) and the text file you want to update are in the same directory as the script.
2. Run the script:

    ```bash
    python updatetxt.py
    ```

3. Follow the prompts to select the reference file and the file to update. The script will update the selected text file with numbers.

### 4. `start.nesting.py`

This script automates the nesting of clips in Adobe Premiere Pro using the processed text file.

**How to use:**

1. Ensure Adobe Premiere Pro is open and the clips are ready for nesting.
2. Place the `.txt` file (created by `updatetxt.py`) in the same directory as the script.
3. Run the script:

    ```bash
    python start.nesting.py
    ```

4. Follow the prompts to select the text file. The script will start automating the nesting process. Switch focus to Adobe Premiere Pro within 5 seconds as instructed by the script.

## Notes

- Make sure that Adobe Premiere Pro is configured to use the same shortcuts as those used in the `start.nesting.py` script.
- Adjust the wait times in `start.nesting.py` if needed based on your system performance.

## Troubleshooting

- **File Not Found Error**: Ensure that the file paths are correct and the files exist in the specified directories.
- **Permissions Error**: Ensure you have read and write permissions for the files and directories you're working with.
- **Adobe Premiere Pro Issues**: Verify that the application is in focus when the script prompts you to switch.

Feel free to modify the scripts as needed to better fit your workflow or to adapt to changes in your software environment.

---

Let me know if you need any more details or adjustments!