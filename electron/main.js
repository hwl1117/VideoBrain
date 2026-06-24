const { app, BrowserWindow, dialog, shell, ipcMain } = require('electron');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');
const BACKEND_DIR = path.join(ROOT_DIR, 'backend');
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000/health';

let mainWindow;
const children = [];

function npmCommand() {
  return process.platform === 'win32' ? 'npm.cmd' : 'npm';
}

function nodeCommand() {
  return process.platform === 'win32' ? 'node.exe' : 'node';
}

function spawnService(name, command, args, cwd) {
  const child = spawn(command, args, {
    cwd,
    env: {
      ...process.env,
      FORCE_COLOR: '1',
      BROWSER: 'none',
      API_URL: 'http://localhost:8000',
    },
    stdio: 'pipe',
    shell: true,
    windowsHide: true,
  });

  children.push(child);

  child.stdout.on('data', (data) => {
    console.log(`[${name}] ${data.toString().trim()}`);
  });

  child.stderr.on('data', (data) => {
    console.error(`[${name}] ${data.toString().trim()}`);
  });

  child.on('exit', (code) => {
    console.log(`[${name}] exited with code ${code}`);
  });

  child.on('error', (error) => {
    console.error(`[${name}] failed:`, error);
  });

  return child;
}

function waitForUrl(url, timeoutMs = 90000) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    const attempt = () => {
      const request = http.get(url, (response) => {
        response.resume();
        if (response.statusCode >= 200 && response.statusCode < 500) {
          resolve();
          return;
        }
        retry();
      });

      request.on('error', retry);
      request.setTimeout(3000, () => {
        request.destroy();
        retry();
      });
    };

    const retry = () => {
      if (Date.now() - startedAt > timeoutMs) {
        reject(new Error(`Timed out waiting for ${url}`));
        return;
      }
      setTimeout(attempt, 1000);
    };

    attempt();
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    frame: false,
    width: 1280,
    height: 860,
    minWidth: 1100,
    minHeight: 720,
    title: 'AgencySuperpowersProduct',
    backgroundColor: '#09090b',
    icon: path.join(ROOT_DIR, 'videobrain.ico'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  await mainWindow.loadURL(FRONTEND_URL);

  // Inject a thin overlay title bar after page loads (once)
  mainWindow.webContents.once('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      (function() {
        if (document.getElementById('electron-titlebar')) return;

        var style = document.createElement('style');
        style.textContent = '#electron-titlebar{position:fixed;top:0;left:0;right:0;height:30px;z-index:99999;display:flex;align-items:center;justify-content:flex-end;background:rgba(9,9,11,0.85);-webkit-app-region:drag;user-select:none;pointer-events:auto}#electron-titlebar button{width:44px;height:30px;border:none;background:transparent;color:#a1a1aa;font-size:14px;cursor:pointer;-webkit-app-region:no-drag;display:flex;align-items:center;justify-content:center;transition:background 0.15s}#electron-titlebar button:hover{background:rgba(255,255,255,0.1);color:#fff}#electron-titlebar button#eb-close:hover{background:#e11d48;color:#fff}';
        document.head.appendChild(style);

        var bar = document.createElement('div');
        bar.id = 'electron-titlebar';
        bar.innerHTML = '<button id="eb-min" title="最小化"><svg width="12" height="12" viewBox="0 0 12 12"><rect y="5" width="12" height="2" fill="currentColor"/></svg></button><button id="eb-max" title="最大化"><svg width="12" height="12" viewBox="0 0 12 12"><rect x="1" y="1" width="10" height="10" stroke="currentColor" stroke-width="1.5" fill="none"/></svg></button><button id="eb-close" title="关闭"><svg width="12" height="12" viewBox="0 0 12 12"><line x1="1" y1="1" x2="11" y2="11" stroke="currentColor" stroke-width="1.5"/><line x1="11" y1="1" x2="1" y2="11" stroke="currentColor" stroke-width="1.5"/></svg></button>';
        document.body.appendChild(bar);

        document.getElementById('eb-min').onclick = function() { window.electronAPI.minimize(); };
        document.getElementById('eb-max').onclick = function() { window.electronAPI.maximize(); };
        document.getElementById('eb-close').onclick = function() { window.electronAPI.close(); };

        // Push page content down so title bar doesn't overlap
        document.body.style.paddingTop = '30px';
      })();
    `);
  });
}

// IPC for window controls
ipcMain.handle('win:minimize', () => { if (mainWindow) mainWindow.minimize(); });
ipcMain.handle('win:maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
  }
});
ipcMain.handle('win:close', () => { if (mainWindow) mainWindow.close(); });

async function boot() {
  // 启动 Python 后端
  spawnService('backend', 'python', ['-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000'], BACKEND_DIR);
  // 启动前端
  spawnService('frontend', npmCommand(), ['run', 'dev', '--', '-p', '3000'], FRONTEND_DIR);

  try {
    await Promise.all([
      waitForUrl(FRONTEND_URL),
      waitForUrl(BACKEND_URL).catch(() => undefined),
    ]);
    await createWindow();
  } catch (error) {
    dialog.showErrorBox(
      'AgencySuperpowersProduct start failed',
      `Local services failed to start.\n\nPlease ensure Node.js and dependencies are installed.\n\n${error.message}`,
    );
    app.quit();
  }
}

function stopChildren() {
  for (const child of children) {
    if (!child.killed) {
      child.kill();
    }
  }
}

app.whenReady().then(boot);

app.on('window-all-closed', () => {
  stopChildren();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', stopChildren);

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await createWindow();
  }
});