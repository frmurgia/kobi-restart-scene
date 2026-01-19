#!/usr/bin/env python3
"""
HoloLens HTTP Reset Server - Styled version
Dashboard con stile Kobi
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

devices = {}
commands = {}
lock = threading.Lock()

# HTML Dashboard in stile Kobi
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kobi - HoloLens Control</title>

    <!-- Google Fonts - Inter e Inconsolata -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Inconsolata:wght@400;600&display=swap" rel="stylesheet">

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inconsolata', monospace;
            background: #f5f5f5;
            min-height: 100vh;
        }

        /* Headlines usano Inter */
        h1, h2, h3, .device-name, .logo, .btn, .device-status {
            font-family: 'Inter', -apple-system, sans-serif;
        }

        .container {
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar Kobi style */
        .sidebar {
            width: 500px;
            background: linear-gradient(180deg, #0a3d4a 0%, #0d4f5e 100%);
            color: white;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
        }

        .logo {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 40px;
            letter-spacing: 4px;
        }

        .logo-dots {
            font-weight: bold;
            font-size: 24px;
            letter-spacing: 12px;
        }

        .title {
            font-weight: bold;
            font-size: 24px;
            letter-spacing: 12px;
        }

        .sidebar-text {
            font-size: 16px;
            line-height: 1.6;
            opacity: 0.9;
            margin-bottom: 60px;
        }

        .server-info {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            font-size: 14px;
            margin-top: auto;
        }

        .server-info strong {
            display: block;
            margin-bottom: 8px;
            color: #17d1c4;
            font-family: 'Inter', sans-serif;
        }

        /* Main content */
        .main-content {
            flex: 1;
            padding: 60px 80px;
            overflow-y: auto;
        }

        h1 {
            font-size: 42px;
            font-weight: 300;
            color: #0a3d4a;
            margin-bottom: 12px;
        }

        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 50px;
        }

        /* Device cards */
        .devices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }

        .device-card {
            background: white;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }

        .device-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transform: translateY(-0.02px);
        }

        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #eee;
        }

        .device-name {
            font-size: 24px;
            font-weight: 500;
            color: #0a3d4a;
        }

        .device-status {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .device-status.ready {
            background: #d4f4dd;
            color: #0d9488;
        }

        .device-status.resetting {
            background: #fef3c7;
            color: #d97706;
        }

        .device-status.offline {
            background: #fee2e2;
            color: #dc2626;
        }

        .device-info {
            margin: 16px 0;
            font-size: 14px;
            color: #666;
        }

        /* Buttons */
        .btn {
            width: 100%;
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .btn-reset {
            background: #00B0B9;
            color: white;
        }

        .btn-reset:hover {
            background: #14b8ad;
        }

        .btn-reset:active {
            transform: translateY(0);
        }

        /* Global controls */
        .global-controls {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
        }

        .global-controls h2 {
            font-size: 28px;
            font-weight: 500;
            color: #0a3d4a;
            margin-bottom: 24px;
        }

        .btn-danger {
            background: #00B0B9;
            color: white;
            max-width: 400px;
            margin: 0 auto;
        }

        .btn-danger:hover {
            background: #b91c1c;
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: #999;
        }

        .empty-state svg {
            width: 120px;
            height: 120px;
            margin-bottom: 24px;
            opacity: 0.3;
        }

        .empty-state h3 {
            font-size: 24px;
            margin-bottom: 12px;
            color: #666;
        }

        .empty-state p {
            font-size: 16px;
        }

        @media (max-width: 1200px) {
            .container {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                padding: 40px 20px;
            }

            .main-content {
                padding: 40px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar Kobi -->
        <div class="sidebar">
            <div class="logo">
                <span class="title">°’°</span>Kobi
            </div>
            <div class="sidebar-text">
                Kobi is about collective intelligence, where collaboration among
                teachers and among students gives rise to ideas, emotions, visions.
            </div>
            <div class="server-info">
                <strong>Server Status</strong>
                Server URL: http://{{ server_ip }}:5000<br>
                <small>Configure this URL in HoloLens Unity project</small>
            </div>
        </div>

        <!-- Main content -->
        <div class="main-content">
            <h1>HoloLens Remote Control</h1>
            <p class="subtitle">Manage and reset your HoloLens devices remotely</p>

            <div class="devices-grid" id="devices"></div>

            <div class="global-controls">
                <h2>Global Controls</h2>
                <button class="btn btn-danger" onclick="resetAll()">
                     Reset All Devices
                </button>
            </div>
        </div>
    </div>

    <script>
        function updateDevices() {
            fetch('/api/devices')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('devices');

                    if (Object.keys(data).length === 0) {
                        container.innerHTML = `
                            <div class="empty-state" style="grid-column: 1 / -1;">
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                                </svg>
                                <h3>No devices connected</h3>
                                <p>Start your HoloLens applications to see them here</p>
                            </div>
                        `;
                        return;
                    }

                    container.innerHTML = '';

                    Object.entries(data).forEach(([id, device]) => {
                        const card = document.createElement('div');
                        card.className = 'device-card';

                        const statusClass = device.status === 'ready' ? 'ready' :
                                           device.status === 'resetting' ? 'resetting' : 'offline';

                        const statusText = device.status === 'ready' ? 'Ready' :
                                          device.status === 'resetting' ? 'Resetting' :
                                          device.status === 'reset_complete' ? 'Complete' : 'Offline';

                        card.innerHTML = `
                            <div class="device-header">
                                <div class="device-name">${id}</div>
                                <div class="device-status ${statusClass}">${statusText}</div>
                            </div>
                            <div class="device-info">
                                Last update: ${new Date(device.last_seen * 1000).toLocaleTimeString()}
                            </div>
                            <button class="btn btn-reset" onclick="resetDevice('${id}')">
                                 Reset Device
                            </button>
                        `;

                        container.appendChild(card);
                    });
                });
        }

        function resetDevice(deviceId) {
            fetch(`/api/reset/${deviceId}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    console.log('Reset sent:', data);
                    setTimeout(updateDevices, 500);
                });
        }

        function resetAll() {
            if (confirm('Are you sure you want to reset ALL devices?')) {
                fetch('/api/reset/all', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        console.log('Global reset sent:', data);
                        setTimeout(updateDevices, 500);
                    });
            }
        }

        // Auto-refresh every 2 seconds
        setInterval(updateDevices, 2000);
        updateDevices();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    import socket
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    return render_template_string(DASHBOARD_HTML, server_ip=server_ip)

@app.route('/api/devices')
def get_devices():
    with lock:
        now = time.time()
        for device_id, device in devices.items():
            if now - device['last_seen'] > 30:
                device['status'] = 'offline'
        return jsonify(devices)

@app.route('/api/status', methods=['POST'])
def update_status():
    data = request.json
    device_id = data.get('device')
    status = data.get('status')

    with lock:
        if device_id not in devices:
            devices[device_id] = {}

        devices[device_id].update({
            'status': status,
            'last_seen': time.time(),
            'timestamp': data.get('timestamp', '')
        })

    print(f"📨 Status da {device_id}: {status}")
    return jsonify({'success': True})

@app.route('/api/command/<device_id>')
def get_command(device_id):
    with lock:
        command = commands.pop(device_id, 'none')

    if command != 'none':
        print(f"📤 Comando inviato a {device_id}: {command}")

    return command

@app.route('/api/reset/<device_id>', methods=['POST'])
def reset_device(device_id):
    with lock:
        if device_id == 'all':
            for dev_id in devices.keys():
                commands[dev_id] = 'reset'
            print(f"📤 Reset globale → {len(devices)} devices")
            return jsonify({'success': True, 'devices': len(devices)})
        else:
            commands[device_id] = 'reset'
            print(f"📤 Reset → {device_id}")
            return jsonify({'success': True, 'device': device_id})

@app.route('/api/clear')
def clear_devices():
    with lock:
        devices.clear()
        commands.clear()
    return jsonify({'success': True})

def cleanup_offline_devices():
    while True:
        time.sleep(60)
        with lock:
            now = time.time()
            offline = [dev_id for dev_id, dev in devices.items()
                      if now - dev['last_seen'] > 120]
            for dev_id in offline:
                print(f"🗑️ Device rimosso: {dev_id}")
                devices.pop(dev_id, None)
                commands.pop(dev_id, None)

if __name__ == '__main__':
    import socket

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    cleanup_thread = threading.Thread(target=cleanup_offline_devices, daemon=True)
    cleanup_thread.start()

    print("\n" + "="*60)
    print("°'°Kobi - HoloLens Remote Control Server")
    print("="*60)
    print(f"\n📡 Server: http://{local_ip}:5000")
    print(f"🌐 Dashboard: http://{local_ip}:5000")
    print(f"\n💡 Configure in Unity HttpSceneResetter:")
    print(f"   Server URL: http://{local_ip}:5000")
    print("\n" + "="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
