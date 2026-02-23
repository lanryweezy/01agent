import { spawn, exec } from 'child_process';
import kill from 'tree-kill';

let aiagentProcess;
let bgAuthProcess;

function startBackgroundAuthServices() {
  bgAuthProcess = spawn('wsl', ['-d', 'NeuralOS', '--', 'bash', '/agent/background_mode_authentication.sh']);

  bgAuthProcess.stdout.on('data', data => {
    console.log(`[BG Auth]: ${data.toString()}`);
  });

  bgAuthProcess.stderr.on('data', data => {
    console.error(`[BG Auth ERROR]: ${data.toString()}`);
  });
}

function cleanupBackgroundAuthServices() {
    exec('wsl -d NeuralOS -- bash /agent/background_mode_authentication_cleanup.sh', (err) => {
        if (err) {
        console.error('[BG Auth]: Cleanup failed:', err);
        } else {
        console.log('[BG Auth]: Cleanup script executed.');
        }
    });

    if (bgAuthProcess) {
        if (!bgAuthProcess.killed) {
        bgAuthProcess.kill('SIGKILL');
        }
    }
    bgAuthProcess = null;
}

function cleanupBGAgent() {
    exec('wsl -d NeuralOS -- bash /agent/stop_bg_agent.sh', (err) => {
        if (err) {
        console.error('[BG Agent]: Cleanup failed:', err);
        } else {
        console.log('[BG Agent]: Cleanup script executed.');
        }
    });

    if (aiagentProcess) {
        if (!aiagentProcess.killed) {
        aiagentProcess.kill('SIGKILL');
        }
    }
}

function stopAiAgent() {
    if (aiagentProcess && !aiagentProcess.killed) {
        kill(aiagentProcess.pid, 'SIGKILL', (err) => {
            if (err) console.error('❌ Failed to kill agent:', err);
            else console.log('[✅ Agent forcibly stopped]');
        });
    }
    aiagentProcess = null;
    cleanupBGAgent();
}

export {
    startBackgroundAuthServices,
    cleanupBackgroundAuthServices,
    cleanupBGAgent,
    stopAiAgent,
    aiagentProcess,
    bgAuthProcess,
};
