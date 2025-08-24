# Local Media Gallery Generator

This project provides a Python script to generate a sophisticated, self-contained HTML gallery from a local folder of media files. The generated gallery includes an interactive trash system, layout controls, and other features.

## How to Use

1.  **Prerequisites:** You need Python 3 installed on your system. The script uses the `tkinter` library, which is included with most Python installations.

2.  **Run the Generator Script:** Open a terminal or command prompt in the project directory and run the following command:
    ```bash
    python generate_gallery.py
    ```

3.  **Select Your Folder:** A folder picker window will appear. Navigate to and select the folder containing your media files.

4.  **Open Your Gallery:** The script will create a new HTML file in the current directory, named like `gallery-YourFolderName.html`. Open this new file in your web browser to view and manage your gallery.

## Features of the Generated Gallery

-   **Interactive Trash:** Click the trash icon (&#128465;) on any item to move it to the trash. This is a "soft" delete; it only marks the file for deletion.
-   **Trash View:** Click the "View Trash" button to see all marked files. From there, you can restore them or generate a delete script.
-   **Generate Delete Script:** In the trash view, you can generate a batch script (`.bat` for Windows, `.sh` for others) to permanently delete the marked files from your computer.
-   **Undo:** When you trash a file, an "Undo" button appears for 5 seconds.
-   **Auto-Trash:** Check the "Auto-trash viewed files" box to automatically move any file to the trash after you view it in fullscreen.
-   **Layout Controls:** Use the "Thumbnail Width" slider to adjust the size of the thumbnails.

## Notes

-   The `gallery_template.html` file is the base template. Do not delete it.
-   Each time you run the script on a folder, it will create a new, separate HTML file for that gallery.
-   The paths to the media in the generated file are absolute, so the gallery file will work as long as the media files are not moved.