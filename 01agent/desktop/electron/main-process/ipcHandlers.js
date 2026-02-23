import { ipcMain } from 'electron';
import { expandMinimizeOverlay } from './windowManager.js';
import { stopAiAgent, aiagentProcess } from './processManager.js';
import { loginWithGoogle } from './auth.js';
import { setupBackgroundMode, isBackgroundModeReady } from '../utils/wslSetup.js';
import { spawn } from 'child_process';
import path from 'path';

function registerIpcHandlers(store, mainWindow, overlayWindow, bgSetupWindow, bgAgentWindow) {
    ipcMain.on('set-token', (_, token) => {
        store.set(constants.ACCESS_TOKEN_STORE_KEY, token);
        if (!overlayWindow) {
            createOverlayWindow();
        }
    });

    ipcMain.handle('get-token', () => store.get(constants.ACCESS_TOKEN_STORE_KEY));

    ipcMain.on('delete-token', () => {
        store.delete(constants.ACCESS_TOKEN_STORE_KEY);
        if (overlayWindow) {
            overlayWindow.close();
        }
    });

    ipcMain.on('set-refresh-token', (_, token) => store.set(constants.REFRESH_TOKEN_STORE_KEY, token));

    ipcMain.handle('get-refresh-token', () => store.get(constants.REFRESH_TOKEN_STORE_KEY));

    ipcMain.on('delete-refresh-token', () => store.delete(constants.REFRESH_TOKEN_STORE_KEY));

    ipcMain.on('expand-overlay', (_, hasSuggestions) => {
        console.log("[Main Process] Received 'expand-overlay' IPC message.");
        expandMinimizeOverlay(overlayWindow, true, hasSuggestions);
    });

    ipcMain.on('set-dark-mode', (_, isDarkMode) => {
        store.set(constants.DARK_MODE_STORE_KEY, isDarkMode.toString());
        if (overlayWindow) {
            overlayWindow.reload();
        }
    });

    ipcMain.handle('is-dark-mode', () => store.get(constants.DARK_MODE_STORE_KEY));

    ipcMain.handle('get-last-background-mode-value', () => store.get(constants.LAST_BACKGROUND_MODE_VALUE));

    ipcMain.handle('get-last-thinking-mode-value', () => store.get(constants.LAST_THINKING_MODE_VALUE));

    ipcMain.on('set-last-thinking-mode-value', (_, lastThinkingModeValue) => store.set(constants.LAST_THINKING_MODE_VALUE, lastThinkingModeValue));

    ipcMain.on('minimize-overlay', () => {
        console.log("[Main Process] Received 'minimize-overlay' IPC message.");
        expandMinimizeOverlay(overlayWindow, false);
    });

    ipcMain.handle('check-background-ready', () => {
        return isBackgroundModeReady();
    });

    ipcMain.handle('start-background-setup', async () => {
        // Prevent duplicate windows
        if (bgSetupWindow && !bgSetupWindow.isDestroyed()) {
            bgSetupWindow.focus();
            return;
        }

        bgSetupWindow = new BrowserWindow({
            width: 600,
            height: 300,
            title: 'Setting up Background Mode',
            resizable: false,
            modal: true,
            webPreferences: {
            preload: path.join(__dirname, 'electron', 'preload.js'),
            contextIsolation: true,
            },
        });

        const bgSetupUrl = isDev
            ? 'http://localhost:6763/#/background-setup'
            : `file://${path.join(__dirname, '01agent-app', 'build', 'index.html')}#/background-setup`;

        bgSetupWindow.loadURL(bgSetupUrl);

        bgSetupWindow.on('closed', () => {
            bgSetupWindow = null;
        });

        const defaultErr = 'Setup Failed: Please ensure you have Windows 10 or higher and that virtualization is enabled in BIOS.';

        let result = { success: false, error: defaultErr };

        try {
            result = await setupBackgroundMode({
                onStatus: (msg) => {
                    if (!bgSetupWindow?.isDestroyed()) {
                    bgSetupWindow.webContents.send('setup-status', msg);
                    }
                },
                onProgress: (pct) => {
                    if (!bgSetupWindow?.isDestroyed()) {
                    bgSetupWindow.webContents.send('setup-progress', pct);
                    }
                },
            });
        } catch (err) {
            console.error('❌ Setup failed:', err);
            result = {
            success: false,
            error: err?.message || defaultErr,
            };
        }

        if (bgSetupWindow && !bgSetupWindow.isDestroyed()) {
            bgSetupWindow.webContents.send('setup-complete', result);
        }

        if (result.success) {
            launchBackgroundAuthWindow();
        }

        return result;
    });

    ipcMain.handle('get-suggestions', async (_, baseURL) => {
        return new Promise((resolve, reject) => {
            const suggestor = spawn(path.join(__dirname, 'aiagent', 'venv', 'Scripts', 'python'), [path.join(__dirname, 'aiagent', 'suggestor.py')], {
                env: {
                },
            });

            let output = '';
            let errorOutput = '';

            suggestor.stdout.on('data', (data) => {
                output += data.toString();
            });

            suggestor.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            suggestor.on('close', (code) => {
                if (code === 0) {
                    try {
                        const result = JSON.parse(output);
                        resolve(result);
                    } catch (err) {
                        console.error('❌ Failed to parse suggestor output:', output);
                        reject(err);
                    }
                } else {
                    console.error('❌ Suggestor exited with error:', errorOutput);
                    reject(new Error('Suggestor failed'));
                }
            });
        });
    });

    ipcMain.on('launch-ai-agent', async (_, baseURL, threadId, backgroundMode) => {
        const isWindows = process.platform === 'win32';
        const isMac = process.platform === 'darwin';

        store.set(constants.LAST_BACKGROUND_MODE_VALUE, backgroundMode.toString());

        if (!backgroundMode) {
            aiagentProcess = spawn(isWindows ? path.join(__dirname, 'aiagent', 'venv', 'Scripts', 'python') : path.join(__dirname, 'aiagent', 'venv', 'bin', 'python'), [path.join(__dirname, 'aiagent', 'main.py')], {
                env: {
                    01AGENT_API_URL: baseURL,
                    01AGENT_THREAD_ID: threadId,
                    01AGENT_USER_ACCESS_TOKEN: store.get(constants.ACCESS_TOKEN_STORE_KEY),
                    PYTHONUTF8: '1',
                },
            });

            mainWindow?.minimize();
        } else {
            const envVars = {
                SKIP_LLM_API_KEY_VERIFICATION: 'true',
                PYTHONUTF8: '1',
            };

            const shellCommand = Object.entries(envVars)
            .map(([k, v]) => `${k}="${v}"`).join(' ') + ' bash /agent/launch_bg_agent.sh';

            aiagentProcess = spawn('wsl', ['-d', 'NeuralOS', '--', 'bash', '-c', shellCommand]);

            launchBackgroundAgentWindow();
        }

        mainWindow?.webContents.send('ai-agent-launch', threadId);
        overlayWindow?.webContents.send('ai-agent-launch', threadId);
        expandMinimizeOverlay(overlayWindow, true, false);

        aiagentProcess.stdout.on('data', (data) => console.log(`[Agent stdout]: ${data}`));
        aiagentProcess.stderr.on('data', (data) => console.error(`[Agent stderr]: ${data}`));

        aiagentProcess.on('error', err => {
            console.error('❌  Agent process failed to start:', err);
            mainWindow?.webContents.send('trigger-cancel-all-tasks');
        });

        aiagentProcess.on('exit', (code, signal) => {
            console.log(`[Agent exited with code ${code}]`);
            if (bgAgentWindow) {
                bgAgentWindow.close();
            }
            cleanupBGAgent();
            if (mainWindow?.isMinimized()) {
                mainWindow.restore();
            }
            if (mainWindow) {
                mainWindow.focus();
            }
            mainWindow?.webContents.send('ai-agent-exit');
            overlayWindow?.webContents.send('ai-agent-exit');

            if (code !== 0 || signal) {
                mainWindow?.webContents.send('trigger-cancel-all-tasks');
            }
            aiagentProcess = null;
        });
    });

    ipcMain.on('stop-ai-agent', stopAiAgent);

    ipcMain.handle('login-with-google', loginWithGoogle);
}

export {
    registerIpcHandlers,
};
