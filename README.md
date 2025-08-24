# Local Media Gallery Generator

This project contains a static HTML gallery and a Python script to generate its content from a local folder.

## How to Use

1.  **Prerequisites:** You need Python 3 installed on your system.
2.  **Run the Generator Script:** Open a terminal in the project directory and run the following command:
    ```bash
    python generate_gallery.py
    ```
3.  **Enter Folder Path:** When prompted, paste the full path to the folder containing your media files and press Enter.
4.  **View Your Gallery:** The script will overwrite `gallery.html` with your media. You can now open this file in your web browser to view the gallery.

## Notes

-   The generated `gallery.html` is a self-contained file that can be opened from anywhere on your computer.
-   The paths to the media are absolute, so the `gallery.html` file will work as long as the media files are not moved.
-   If you add or remove files from your media folder, simply run the script again to regenerate the gallery.