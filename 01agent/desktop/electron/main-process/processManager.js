import { spawn, exec } from 'child_process';
import path from 'path';
import kill from 'tree-kill';

let aiagentProcess;

function startAiAgent(apiUrl, threadId, accessToken, mainWindow, overlayWindow) {
    if (aiagentProcess && !aiagentProcess.killed) return;

    const env = {
        ...process.env,
        '01AGENT_API_URL': apiUrl,
        '01AGENT_THREAD_ID': threadId,
        '01AGENT_USER_ACCESS_TOKEN': accessToken,
        PYTHONUNBUFFERED: '1'
    };

    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const agentScript = path.join(process.cwd(), 'aiagent', 'main.py');

    aiagentProcess = spawn(pythonPath, [agentScript], { env });

    aiagentProcess.stdout.on('data', (data) => {
        const str = data.toString();
        console.log(`[Agent]: ${str}`);
        if (str.includes('"event": "action"')) {
            try {
                const json = JSON.parse(str.trim());
                mainWindow?.webContents.send('agent-action', json.data);
                overlayWindow?.webContents.send('agent-action', json.data);
            } catch (e) {}
        } else if (str.includes('"event": "status"')) {
            try {
                const json = JSON.parse(str.trim());
                mainWindow?.webContents.send('agent-status', json.data);
            } catch (e) {}
        }
    });

    aiagentProcess.stderr.on('data', (data) => {
        console.error(`[Agent Error]: ${data.toString()}`);
    });

    aiagentProcess.on('close', (code) => {
        console.log(`[Agent] process exited with code ${code}`);
        aiagentProcess = null;
    });
}

function stopAiAgent() {
    if (aiagentProcess && !aiagentProcess.killed) {
        kill(aiagentProcess.pid, 'SIGKILL', (err) => {
            if (err) console.error('❌ Failed to kill agent:', err);
            else console.log('[✅ Agent stopped]');
        });
    }
    aiagentProcess = null;
}

export {
    startAiAgent,
    stopAiAgent,
    aiagentProcess
};
