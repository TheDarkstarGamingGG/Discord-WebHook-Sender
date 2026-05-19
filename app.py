import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Discord UI Constants
DARK_BG = "#313338"  
NAV_BG = "#1e1f22"
ENTRY_BG = "#1e1f22"
BUTTON_BG = "#5865f2"
BORDER = "#1e1f22"
TEXT_PRIMARY = "#dbdee1"
TEXT_MUTED = "#b5bac1"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Discord Toolkit Pro</title>
    <style>
        :root {
            --bg: #313338; --nav: #1e1f22; --input: #1e1f22;
            --blurple: #5865f2; --green: #23a55a; --red: #f23f43;
            --text: #dbdee1; --muted: #b5bac1;
        }
        body {
            font-family: 'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: var(--bg); color: var(--text);
            margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh;
        }
        nav {
            background: var(--nav); padding: 10px; display: flex; justify-content: center; gap: 10px;
            border-bottom: 1px solid #1e1f22;
        }
        nav button {
            background: transparent; border: 1px solid #4e5058; color: white;
            padding: 6px 15px; border-radius: 3px; cursor: pointer; font-weight: 500;
        }
        nav button.active { background: var(--blurple); border-color: var(--blurple); }
        
        .container { max-width: 900px; width: 100%; margin: 0 auto; padding: 20px; box-sizing: border-box; flex-grow: 1; overflow-y: auto; }
        .view { display: none; } .view.active { display: block; }
        
        .card { background: #2b2d31; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 12px; font-weight: bold; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }
        
        input, textarea, select {
            width: 100%; padding: 10px; background: var(--input); border: none; color: white;
            border-radius: 4px; font-size: 15px; box-sizing: border-box; font-family: inherit;
        }
        select { cursor: pointer; }
        
        .inspector { font-size: 13px; margin-top: 5px; color: var(--green); min-height: 18px; }
        .counter { text-align: right; font-size: 12px; color: var(--muted); margin-top: 4px; }
        .counter.limit { color: var(--red); }

        .preview-box { background: var(--bg); border-left: 4px solid var(--blurple); padding: 10px; margin-top: 10px; display: flex; gap: 15px; }
        .p-avatar { width: 40px; height: 40px; border-radius: 50%; background: #5865f2; flex-shrink: 0; overflow: hidden; }
        .p-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .p-content { flex-grow: 1; }
        .p-name { font-weight: 600; font-size: 16px; margin-bottom: 2px; display: flex; align-items: center; gap: 5px; }
        .p-tag { background: var(--blurple); font-size: 10px; padding: 1px 4px; border-radius: 3px; }
        .p-text { font-size: 15px; line-height: 1.3; white-space: pre-wrap; word-break: break-word; }

        .btn-row { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; margin-top: 10px; }
        .flex-row { display: flex; gap: 10px; margin-bottom: 15px; }
        button.primary { background: var(--blurple); border: none; color: white; padding: 12px; border-radius: 3px; font-weight: bold; cursor: pointer; }
        button.secondary { background: #4e5058; border: none; color: white; padding: 10px; cursor: pointer; border-radius: 3px; white-space: nowrap; font-weight: bold; }
        button.danger { background: var(--red); border: none; color: white; padding: 10px; cursor: pointer; border-radius: 3px; }
        
        .utility-bar { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; padding-top: 15px; border-top: 1px solid #4e5058; }

        .history-item { 
            background: var(--input); padding: 10px; border-radius: 4px; margin-top: 5px;
            display: flex; justify-content: space-between; align-items: center; font-size: 13px;
        }
        iframe { width: 100%; height: 80vh; border: none; border-radius: 8px; background: white; }
    </style>
</head>
<body>

<nav>
    <button id="nav-send" class="active" onclick="setView('send')">Webhook Dashboard</button>
    <button id="nav-grab" onclick="setView('grab')">PFP Grabber</button>
</nav>

<div class="container">
    <div id="view-send" class="view active">
        <div class="card">
            <label>Saved Presets (Auto-fills Webhook, Name & PFP)</label>
            <div class="flex-row">
                <select id="preset_select" onchange="loadPreset()">
                    <option value="">-- Select a Preset --</option>
                </select>
                <button class="secondary" onclick="savePreset()">Save as Preset</button>
            </div>

            <div class="form-group">
                <label>Webhook URL</label>
                <input type="text" id="w_url" placeholder="https://discord.com/api/webhooks/..." oninput="inspectWebhook()">
                <div id="w_info" class="inspector"></div>
            </div>

            <div style="display: flex; gap: 15px; margin-top: 10px;">
                <div class="form-group" style="flex: 1;">
                    <label>Override Name (Used for Preset Name)</label>
                    <input type="text" id="w_name" placeholder="Optional" oninput="updatePreview()">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>Override Avatar URL</label>
                    <input type="text" id="w_avatar" placeholder="Optional" oninput="updatePreview()">
                </div>
            </div>

            <div class="form-group">
                <label>Message Content</label>
                <textarea id="w_content" placeholder="Type a message... Use <@USER_ID> to mention someone." oninput="updatePreview()" rows="4"></textarea>
                <div id="w_counter" class="counter">0 / 2000</div>
            </div>

            <label style="margin-top: 20px;">Live Discord Preview</label>
            <div class="preview-box">
                <div class="p-avatar"><img id="pre_img" src="https://discord.com/assets/f78426a064bc9dd24847.png"></div>
                <div class="p-content">
                    <div class="p-name"><span id="pre_name">Webhook</span> <span class="p-tag">APP</span></div>
                    <div id="pre_text" class="p-text">Message preview...</div>
                </div>
            </div>

            <div class="form-group" style="margin-top: 20px;">
                <label>Message ID (For Edit/Delete)</label>
                <input type="text" id="w_msg_id" placeholder="Paste ID to edit or delete">
            </div>

            <div class="btn-row">
                <button class="primary" id="btn_send" onclick="apiCall('send')">Send Message</button>
                <button class="secondary" id="btn_edit" onclick="apiCall('edit')">Edit</button>
                <button class="danger" id="btn_delete" onclick="apiCall('delete')">Delete</button>
            </div>
            
            <div id="status" style="text-align: center; margin-top: 10px; font-weight: bold; font-size: 14px;"></div>
            
            <div class="utility-bar">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12px; color: var(--muted);">Data Backup (Bypasses Browser Pop-up Blockers)</span>
                    <div style="display: flex; gap: 10px;">
                        <button class="secondary" style="padding: 5px 10px; font-size: 12px;" onclick="exportJSON()">Export JSON String</button>
                        <button class="secondary" style="padding: 5px 10px; font-size: 12px;" onclick="importJSON()">Import JSON String</button>
                    </div>
                </div>
                <textarea id="backup_io" placeholder="Backup string will appear here. Or, paste your string here and click Import." rows="3" style="display: none; font-family: monospace; font-size: 11px;"></textarea>
            </div>
        </div>

        <label>Session History</label>
        <div id="history_list"></div>
    </div>

    <div id="view-grab" class="view">
        <iframe src="https://discordlabs.org/tools/pfp-grabber"></iframe>
    </div>
</div>

<script>
    window.onload = () => {
        refreshPresets();
        const savedUrl = localStorage.getItem('last_webhook');
        if(savedUrl) {
            document.getElementById('w_url').value = savedUrl;
            inspectWebhook();
        }
    };

    function setView(v) {
        document.querySelectorAll('.view, nav button').forEach(el => el.classList.remove('active'));
        document.getElementById('view-' + v).classList.add('active');
        document.getElementById('nav-' + v).classList.add('active');
    }

    // --- PRESETS LOGIC (No Prompts) ---
    function savePreset() {
        const status = document.getElementById('status');
        let name = document.getElementById('w_name').value.trim();
        
        // Use a fallback name if the Override Name is blank
        if (!name) {
            name = "Unnamed Preset " + Math.floor(Math.random() * 100);
        }

        const presetData = {
            url: document.getElementById('w_url').value,
            username: document.getElementById('w_name').value,
            avatar: document.getElementById('w_avatar').value
        };

        let presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
        presets[name] = presetData;
        localStorage.setItem('app_presets', JSON.stringify(presets));
        refreshPresets();
        
        status.innerText = `Saved as "${name}"!`;
        status.style.color = "var(--green)";
    }

    function loadPreset() {
        const select = document.getElementById('preset_select');
        if(!select.value) return;
        
        const presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
        const p = presets[select.value];
        if(p) {
            document.getElementById('w_url').value = p.url || "";
            document.getElementById('w_name').value = p.username || "";
            document.getElementById('w_avatar').value = p.avatar || "";
            inspectWebhook();
            updatePreview();
        }
    }

    function refreshPresets() {
        const select = document.getElementById('preset_select');
        select.innerHTML = '<option value="">-- Select a Preset --</option>';
        
        const presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
        for(const name of Object.keys(presets)) {
            select.innerHTML += `<option value="${name}">${name}</option>`;
        }
    }

    // --- PREVIEW & INSPECTOR ---
    function updatePreview() {
        const name = document.getElementById('w_name').value || "Webhook";
        const avatar = document.getElementById('w_avatar').value || "https://discord.com/assets/f78426a064bc9dd24847.png";
        const content = document.getElementById('w_content').value;
        
        document.getElementById('pre_name').innerText = name;
        document.getElementById('pre_img').src = avatar;
        
        let parsed = content.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                            .replace(/\\*(.*?)\\*/g, '<i>$1</i>')
                            .replace(/`(.*?)`/g, '<code style="background:#2b2d31;padding:2px;">$1</code>');
        
        document.getElementById('pre_text').innerHTML = parsed || "Message preview...";
        
        const count = content.length;
        const counterEl = document.getElementById('w_counter');
        counterEl.innerText = `${count} / 2000`;
        counterEl.className = count > 2000 ? "counter limit" : "counter";
    }

    async function inspectWebhook() {
        const url = document.getElementById('w_url').value;
        const info = document.getElementById('w_info');
        if (!url.includes('webhooks/')) return info.innerText = "";
        
        try {
            const r = await fetch(url);
            if (r.ok) {
                const data = await r.json();
                info.style.color = "var(--green)";
                info.innerText = `Connected to: #${data.name || 'unknown'}`;
                localStorage.setItem('last_webhook', url);
            } else {
                info.style.color = "var(--red)";
                info.innerText = "Invalid Webhook URL";
            }
        } catch(e) { info.innerText = ""; }
    }

    // --- JSON EXPORT / IMPORT (No file downloads or prompts) ---
    function exportJSON() {
        const data = {
            app_presets: JSON.parse(localStorage.getItem('app_presets') || '{}'),
            last_webhook: localStorage.getItem('last_webhook') || ""
        };
        const backupString = JSON.stringify(data);
        
        const ioBox = document.getElementById('backup_io');
        const status = document.getElementById('status');
        
        ioBox.style.display = 'block';
        ioBox.value = backupString;
        
        // Try to auto-copy
        ioBox.select();
        try {
            document.execCommand('copy');
            status.innerText = "Backup string copied to your clipboard!";
            status.style.color = "var(--green)";
        } catch (err) {
            status.innerText = "Backup generated. Please copy the text from the box below.";
            status.style.color = "var(--blurple)";
        }
    }

    function importJSON() {
        const ioBox = document.getElementById('backup_io');
        const status = document.getElementById('status');
        
        // If the box is hidden or empty, open it and tell the user to paste
        if (ioBox.style.display === 'none' || ioBox.value.trim() === '') {
            ioBox.style.display = 'block';
            ioBox.value = '';
            status.innerText = "Paste your backup string into the box, then click Import again.";
            status.style.color = "var(--blurple)";
            return;
        }

        try {
            const data = JSON.parse(ioBox.value);
            if(data.app_presets) localStorage.setItem('app_presets', JSON.stringify(data.app_presets));
            if(data.last_webhook) localStorage.setItem('last_webhook', data.last_webhook);
            refreshPresets();
            
            ioBox.value = '';
            ioBox.style.display = 'none';
            status.innerText = "Backup imported successfully!";
            status.style.color = "var(--green)";
        } catch(e) {
            status.innerText = "Invalid JSON string. Please make sure you copied it correctly.";
            status.style.color = "var(--red)";
        }
    }

    // --- API CALLS ---
    async function apiCall(type) {
        const status = document.getElementById('status');
        const url = document.getElementById('w_url').value;
        const msgId = document.getElementById('w_msg_id').value;
        
        status.innerText = "Processing...";
        status.style.color = "white";

        const payload = {
            url: url,
            msg_id: msgId,
            content: document.getElementById('w_content').value,
            username: document.getElementById('w_name').value,
            avatar_url: document.getElementById('w_avatar').value
        };

        try {
            const r = await fetch('/' + type, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const res = await r.json();

            if (res.success) {
                status.innerText = "Success!";
                status.style.color = "var(--green)";
                if(type === 'send' && res.id) {
                    addToHistory(res.id, payload.content);
                    document.getElementById('w_content').value = "";
                    updatePreview();
                }
            } else {
                status.innerText = res.error || "Failed";
                status.style.color = "var(--red)";
            }
        } catch(e) {
            status.innerText = "Error connecting to server";
        }
    }

    function addToHistory(id, text) {
        const list = document.getElementById('history_list');
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <span>ID: ${id.substring(0,8)}... "${text.substring(0,20)}..."</span>
            <button onclick="copyToId('${id}')" style="background:var(--blurple);border:none;color:white;padding:4px 8px;border-radius:3px;cursor:pointer;">Use ID</button>
        `;
        list.prepend(item);
    }

    function copyToId(id) {
        document.getElementById('w_msg_id').value = id;
        document.getElementById('w_msg_id').style.border = "1px solid var(--blurple)";
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    url = data.get('url') + "?wait=true"
    
    payload = {
        "content": data.get('content'), 
        "username": data.get('username'), 
        "avatar_url": data.get('avatar_url'),
        "allowed_mentions": {"parse": ["users", "roles", "everyone"]}
    }
    
    try:
        r = requests.post(url, json={k:v for k,v in payload.items() if v}, timeout=10)
        if r.status_code == 429: return jsonify({"error": "Rate limited! Wait a few seconds."}), 429
        r.raise_for_status()
        return jsonify({"success": True, "id": r.json().get('id')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    url = f"{data.get('url')}/messages/{data.get('msg_id')}"
    
    payload = {
        "content": data.get('content'), 
        "username": data.get('username'), 
        "avatar_url": data.get('avatar_url'),
        "allowed_mentions": {"parse": ["users", "roles", "everyone"]}
    }
    
    try:
        r = requests.patch(url, json={k:v for k,v in payload.items() if v}, timeout=10)
        r.raise_for_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": "Edit failed. Check Message ID."}), 400

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    url = f"{data.get('url')}/messages/{data.get('msg_id')}"
    try:
        r = requests.delete(url, timeout=10)
        r.raise_for_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": "Delete failed. Check Message ID."}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
