const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      // preload: path.join(__dirname, 'preload.js'), // We'll use nodeIntegration directly for simplicity
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false, // Required to load local file URLs
    },
  });

  mainWindow.loadFile('index.html');

  // Open the DevTools for debugging.
  mainWindow.webContents.openDevTools();
}

// --- IPC Handlers for File System Access ---

// Asynchronously and recursively get all file paths from a directory
async function getAllFiles(dirPath, arrayOfFiles = []) {
    try {
        const files = await fs.promises.readdir(dirPath);

        for (const file of files) {
            const fullPath = path.join(dirPath, file);
            try {
                const stats = await fs.promises.stat(fullPath);
                if (stats.isDirectory()) {
                    await getAllFiles(fullPath, arrayOfFiles);
                } else {
                    arrayOfFiles.push(fullPath);
                }
            } catch (err) {
                console.error(`Could not stat file ${fullPath}: ${err}`);
            }
        }
    } catch (err) {
        console.error(`Could not read directory ${dirPath}: ${err}`);
    }
    return arrayOfFiles;
}


ipcMain.handle('open-folder-dialog', async (event) => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openDirectory'],
  });

  if (canceled || filePaths.length === 0) {
    return []; // User cancelled or selected no folder
  }

  const folderPath = filePaths[0];
  const files = await getAllFiles(folderPath);
  return files;
});

ipcMain.handle('delete-files', async (event, { filePaths, confirm }) => {
    let doDelete = true;
    if (confirm) {
        const { response } = await dialog.showMessageBox({
            type: 'warning',
            buttons: ['Cancel', 'Delete'],
            defaultId: 0,
            title: 'Confirm Deletion',
            message: `Are you sure you want to permanently delete ${filePaths.length} file(s)?`,
            detail: 'This action cannot be undone.',
        });
        doDelete = (response === 1); // User clicked "Delete"
    }

    if (doDelete) {
        let deletedCount = 0;
        try {
            filePaths.forEach(filePath => {
                fs.unlinkSync(filePath);
                deletedCount++;
            });
            return { success: true, deletedCount };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    return { success: false, error: 'Deletion cancelled by user.' };
});

ipcMain.on('show-in-explorer', (event, filePath) => {
    shell.showItemInFolder(filePath);
});


// --- App Lifecycle ---

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
