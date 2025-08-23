# Local Media Gallery

This is a simple, browser-based gallery to view media files from a local folder on your computer.

## How to use

1.  **Open the Gallery:** Open the `gallery.html` file in a modern web browser (like Chrome, Firefox, or Edge).
2.  **Select Your Media Folder:**
    *   Click the "Select Media Folder" button.
    *   In the dialog that appears, choose the folder on your computer that contains your images and videos.
3.  **Load the Media:** Click the "Load Media" button to display all the supported media from your selected folder and its subfolders.

## Features

### Marking Files for Deletion

-   To mark a file for deletion, hover over its thumbnail and click the trash can icon (&#128465;).
-   This does **not** delete the file from your computer. It only moves it to a temporary trash area within the gallery.

### Trash View & Deleting Files

1.  **View Trashed Files:** Click the "View Trash" button at the top to see all the files you have marked for deletion.
2.  **Restore Files:** In the trash view, you can restore a file by clicking the restore icon (&#128472;) on its thumbnail.
3.  **Generate a Delete Script:**
    *   To permanently delete the files from your computer, click the "Generate Delete Script" button.
    *   This will create a list of commands in a text box.
    *   Copy these commands and paste them into the appropriate terminal for your operating system (e.g., Command Prompt or PowerShell on Windows, or Terminal on macOS/Linux).
    *   Running this script will permanently delete the files. **This action cannot be undone.**