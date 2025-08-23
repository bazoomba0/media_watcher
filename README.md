# Local Media Gallery (Desktop Application)

This is a simple desktop application to view and manage media files from a local folder on your computer.

## Setup & Installation

1.  **Prerequisites:** You must have [Node.js](https://nodejs.org/) installed on your system.
2.  **Install Dependencies:** Open a terminal in the project directory and run the following command:
    ```bash
    npm install
    ```

## How to Use

1.  **Start the Application:** In your terminal, run:
    ```bash
    npm start
    ```
2.  **Select Your Media Folder:**
    *   Click the "Select Media Folder" button.
    *   In the native folder dialog that appears, choose the folder on your computer that contains your images and videos. All media from sub-folders will also be loaded.

## Features

### Marking Files for Deletion

-   To mark a file for deletion, hover over its thumbnail and click the trash can icon (&#128465;).
-   This does **not** immediately delete the file. It moves it to a temporary trash area within the application.
-   You can also check the "Auto-trash viewed files" box to automatically move any file to the trash after you view it in fullscreen.

### Trash View & Permanent Deletion

1.  **View Trashed Files:** Click the "View Trash" button at the top to see all the files you have marked for deletion.
2.  **Restore Files:** In the trash view, you can restore a file by clicking the restore icon (&#128472;) on its thumbnail. This will move it back to the main gallery view.
3.  **Permanently Delete Files:**
    *   In the trash view, click the "Permanently Delete Trashed Files" button.
    *   A native confirmation dialog will appear.
    *   If you confirm, all files currently in the trash will be **permanently deleted** from your computer. **This action cannot be undone.**