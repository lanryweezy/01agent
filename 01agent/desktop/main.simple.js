import { app, BrowserWindow, Menu, ipcMain, screen } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';
import Store from 'electron-store';
import url from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const store = new Store();
let mainWindow;

// Simple constants
const constants = {
  ACCESS_TOKEN_STORE_KEY: '_NA_ACCESS_TOK',
  REFRESH_TOKEN_STORE_KEY: '_NA_REFRESH_TOK',
  DEVICE_ID_STORE_KEY: '_NA_DEVICE_ID',
  DARK_MODE_STORE_KEY: '_NA_IS_DARK_MODE',
};

// Basic IPC handlers
ipcMain.handle('get-token', () => store.get(constants.ACCESS_TOKEN_STORE_KEY));
ipcMain.on('set-token', (_, token) => store.set(constants.ACCESS_TOKEN_STORE_KEY, token));
ipcMain.on('delete-token', () => store.delete(constants.ACCESS_TOKEN_STORE_KEY));

function createWindow() {
  if (mainWindow) return;
  
  // Get screen dimensions for side panel positioning
  const { screen } = await import('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workArea;
  
  // Side panel dimensions (like Cursor/Kiro)
  const panelWidth = 400;
  const panelHeight = screenHeight - 100;
  const panelX = screenWidth - panelWidth - 20;
  const panelY = 50;
  
  mainWindow = new BrowserWindow({
    width: panelWidth,
    height: panelHeight,
    x: panelX,
    y: panelY,
    minWidth: 350,
    minHeight: 500,
    maxWidth: 600,
    title: '01Agent - AI Desktop Assistant',
    icon: path.join(__dirname, 'assets', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    frame: true,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    alwaysOnTop: false,
    skipTaskbar: false,
    resizable: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
      webSecurity: true
    },
  });

  const startURL = isDev
    ? 'http://localhost:6763'
    : url.format({
        pathname: path.join(__dirname, '01agent-app', 'build', 'index.html'),
        protocol: 'file:',
        slashes: true,
      });

  mainWindow.loadURL(startURL);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

const createAppMenu = () => {
  const template = [
    {
      label: 'App',
      submenu: [
        {
          label: 'Logout',
          click: () => {
            mainWindow?.webContents.send('trigger-logout');
          },
        },
        { role: 'quit' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'togglefullscreen' },
        { role: 'toggledevtools' },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
};

// Single instance lock
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

app.whenReady().then(() => {
  createWindow();
  createAppMenu();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});