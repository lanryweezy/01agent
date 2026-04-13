import { BrowserWindow, screen } from 'electron';
import path from 'path';
import url from 'url';
import isDev from 'electron-is-dev';

let backgroundAuthWindow;
let bgAgentWindow;

function createWindow(readyToClose, ipcMain) {
  // Get screen dimensions for side panel positioning
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workArea;
  
  // Side panel dimensions (like Cursor/Kiro)
  const panelWidth = 400;
  const panelHeight = screenHeight - 100;
  const panelX = screenWidth - panelWidth - 20;
  const panelY = 50;
  
  const mainWindow = new BrowserWindow({
    width: panelWidth,
    height: panelHeight,
    x: panelX,
    y: panelY,
    minWidth: 350,
    minHeight: 500,
    maxWidth: 600,
    title: '01Agent - AI Desktop Assistant',
    frame: true,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    alwaysOnTop: false,
    skipTaskbar: false,
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'electron', 'preload.js'),
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

  mainWindow.on('close', async (e) => {
    if (readyToClose) return;

    e.preventDefault();
    if (mainWindow?.webContents) {
      mainWindow?.webContents.send('trigger-cancel-all-tasks');
    }

    ipcMain.once('cancel-all-tasks-done', () => {
      readyToClose = true;
      mainWindow.close();
    });
  });

  return mainWindow;
}

function createOverlayWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workArea;

  const overlayWindow = new BrowserWindow({
    width: screenWidth,
    height: screenHeight,
    x: 0,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    focusable: false,
    skipTaskbar: true,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, 'electron', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Allow clicking through the overlay to reach underlying windows
  overlayWindow.setIgnoreMouseEvents(true, { forward: true });

  const overlayURL = isDev
    ? 'http://localhost:6763/#/overlay'
    : `file://${path.join(__dirname, '01agent-app', 'build', 'index.html')}#/overlay`;

  overlayWindow.loadURL(overlayURL);

  return overlayWindow;
}

function expandMinimizeOverlay(overlayWindow, expanded, hasSuggestions = false) {
  if (!overlayWindow || overlayWindow.isDestroyed()) return;

  const W = expanded ? 350 : 60;
  const H = expanded ? (hasSuggestions ? 380 : 60) : 60;
  const M = 25;
  const { width: SW, height: SH } = screen.getPrimaryDisplay().workArea;
  const X = SW - W - M;
  const Y = SH - H - M;

  overlayWindow.setBounds({ x: X, y: Y, width: W, height: H }, true);
}

function launchBackgroundAuthWindow(cleanupBackgroundAuthServices, waitForNoVNCPortReady, startBackgroundAuthServices) {
    if (backgroundAuthWindow) return;

    startBackgroundAuthServices();

    waitForNoVNCPortReady(39742, 20000)
        .then(() => {
        backgroundAuthWindow = new BrowserWindow({
            width: 1350,
            height: 780,
            title: '01Agent Background Auth',
            webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            preload: path.join(__dirname, 'electron', 'preload.js'),
            },
        });

        const reactURL = isDev
            ? 'http://localhost:6763/#/background-auth'
            : `file://${path.join(__dirname, '01agent-app', 'build', 'index.html')}#/background-auth`;

        backgroundAuthWindow.loadURL(reactURL);

        backgroundAuthWindow.on('closed', () => {
            cleanupBackgroundAuthServices();
            backgroundAuthWindow = null;
        });
        })
        .catch((err) => {
        console.error('❌ noVNC failed to start:', err);
        cleanupBackgroundAuthServices();
        });
}

function launchBackgroundAgentWindow(waitForNoVNCPortReady) {
    if (bgAgentWindow) return;

    waitForNoVNCPortReady(39742, 20000)
        .then(() => {
        bgAgentWindow = new BrowserWindow({
            width: 1350,
            height: 780,
            title: '01Agent Background Task',
            webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            preload: path.join(__dirname, 'electron', 'preload.js'),
            },
        });

        const reactURL = isDev
            ? 'http://localhost:6763/#/background-task'
            : `file://${path.join(__dirname, '01agent-app', 'build', 'index.html')}#/background-task`;

        bgAgentWindow.loadURL(reactURL);

        bgAgentWindow.on('closed', () => {
            bgAgentWindow = null;
        });
        })
        .catch((err) => {
        console.error('noVNC failed to start:', err);
        });
}
export {
    createWindow,
    createOverlayWindow,
    expandMinimizeOverlay,
    launchBackgroundAuthWindow,
    launchBackgroundAgentWindow,
    backgroundAuthWindow,
    bgAgentWindow,
};
