const { app, BrowserWindow, ipcMain, dialog } = require('electron');
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

  mainWindow.loadFile('gallery.html');

  // Open the DevTools for debugging.
  mainWindow.webContents.openDevTools();
}

// --- IPC Handlers for File System Access ---

// Recursively get all file paths from a directory
function getAllFiles(dirPath, arrayOfFiles) {
  const files = fs.readdirSync(dirPath);

  arrayOfFiles = arrayOfFiles || [];

  files.forEach(function (file) {
    if (fs.statSync(path.join(dirPath, file)).isDirectory()) {
      arrayOfFiles = getAllFiles(path.join(dirPath, file), arrayOfFiles);
    } else {
      arrayOfFiles.push(path.join(dirPath, file));
    }
  });

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
  const files = getAllFiles(folderPath);
  return files;
});

ipcMain.handle('delete-files', async (event, filePaths) => {
    const { response } = await dialog.showMessageBox({
        type: 'warning',
        buttons: ['Cancel', 'Delete'],
        defaultId: 0,
        title: 'Confirm Deletion',
        message: `Are you sure you want to permanently delete ${filePaths.length} file(s)?`,
        detail: 'This action cannot be undone.',
    });

    if (response === 1) { // User clicked "Delete"
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
