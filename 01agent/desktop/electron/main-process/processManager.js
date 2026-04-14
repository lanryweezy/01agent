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

    let buffer = '';
    aiagentProcess.stdout.on('data', (data) => {
        buffer += data.toString();
        let lines = buffer.split('\n');
        buffer = lines.pop(); // Keep partial line in buffer

        for (let line of lines) {
            line = line.trim();
            if (!line) continue;
            console.log(`[Agent]: ${line}`);

            if (line.startsWith('{') && line.endsWith('}')) {
                try {
                    const json = JSON.parse(line);
                    if (json.event === 'action') {
                        mainWindow?.webContents.send('agent-action', json.data);
                        overlayWindow?.webContents.send('agent-action', json.data);
                    } else if (json.event === 'status') {
                        mainWindow?.webContents.send('agent-status', json.data);
                    }
                } catch (e) {
                    console.error('Failed to parse agent JSON line:', line, e);
                }
            }
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
