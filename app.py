import json
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Styling Constants
DARK_BG = "#1e1f22"
DARK_FG = "#e6e6e6"
ENTRY_BG = "#2b2d31"
BUTTON_BG = "#5865F2"
NAV_BG = "#111214"
BORDER = "#3f4147"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Discord Toolset</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: {{ DARK_BG }};
            color: {{ DARK_FG }};
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }
        /* Navbar Styling */
        nav {
            width: 100%;
            background-color: {{ NAV_BG }};
            padding: 10px 0;
            display: flex;
            justify-content: center;
            gap: 15px;
            border-bottom: 1px solid {{ BORDER }};
        }
        nav button {
            background: none;
            border: 1px solid {{ BORDER }};
            color: {{ DARK_FG }};
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.2s;
        }
        nav button.active {
            background-color: {{ BUTTON_BG }};
            border-color: {{ BUTTON_BG }};
        }

        .container {
            width: 100%;
            max-width: 800px;
            padding: 20px;
            box-sizing: border-box;
            flex-grow: 1;
        }

        /* Tool Views */
        .view { display: none; width: 100%; height: 100%; }
        .view.active { display: block; }

        h1 { font-size: 24px; margin-bottom: 20px; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            background-color: {{ ENTRY_BG }};
            color: {{ DARK_FG }};
            border: 1px solid {{ BORDER }};
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 16px;
        }
        textarea { height: 120px; resize: vertical; }
        .action-btn {
            width: 100%;
            padding: 15px;
            background-color: {{ BUTTON_BG }};
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        #status { margin-top: 15px; text-align: center; font-weight: bold; }
        .success { color: #43b581; }
        .error { color: #f04747; }

        iframe {
            width: 100%;
            height: 600px;
            border: 1px solid {{ BORDER }};
            border-radius: 8px;
            background: white;
        }
    </style>
</head>
<body>

    <nav>
        <button id="btn-webhook" class="active" onclick="switchView('webhook')">Webhook Sender</button>
        <button id="btn-pfp" onclick="switchView('pfp')">PFP Grabber</button>
    </nav>

    <div class="container">
        <div id="view-webhook" class="view active">
            <h1>Discord Webhook Sender</h1>
            <div class="form-group">
                <label>Webhook URL</label>
                <input type="text" id="webhook_url" placeholder="https://discord.com/api/webhooks/...">
            </div>
            <div class="form-group">
                <label>Username Override</label>
                <input type="text" id="username" placeholder="Optional">
            </div>
            <div class="form-group">
                <label>Avatar URL Override</label>
                <input type="text" id="avatar_url" placeholder="Optional">
            </div>
            <div class="form-group">
                <label>Message Content</label>
                <textarea id="content" placeholder="Type your message here..."></textarea>
            </div>
            <button class="action-btn" onclick="sendWebhook()">Send to Discord</button>
            <div id="status"></div>
        </div>

        <div id="view-pfp" class="view">
            <h1>PFP Grabber</h1>
            <iframe src="https://discordlabs.org/tools/pfp-grabber"></iframe>
        </div>
    </div>

    <script>
        function switchView(viewName) {
            // Update buttons
            document.getElementById('btn-webhook').classList.remove('active');
            document.getElementById('btn-pfp').classList.remove('active');
            document.getElementById('btn-' + viewName).classList.add('active');

            // Update views
            document.getElementById('view-webhook').classList.remove('active');
            document.getElementById('view-pfp').classList.remove('active');
            document.getElementById('view-' + viewName).classList.add('active');
        }

        async function sendWebhook() {
            const statusDiv = document.getElementById('status');
            statusDiv.className = '';
            statusDiv.innerText = 'Sending...';

            const data = {
                webhook_url: document.getElementById('webhook_url').value,
                username: document.getElementById('username').value,
                avatar_url: document.getElementById('avatar_url').value,
                content: document.getElementById('content').value
            };

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (response.ok) {
                    statusDiv.className = 'success';
                    statusDiv.innerText = 'Message sent successfully!';
                    document.getElementById('content').value = '';
                } else {
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Error: ' + result.error;
                }
            } catch (e) {
                statusDiv.className = 'error';
                statusDiv.innerText = 'Error: ' + e.message;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                DARK_BG=DARK_BG, 
                                DARK_FG=DARK_FG, 
                                ENTRY_BG=ENTRY_BG, 
                                BUTTON_BG=BUTTON_BG, 
                                NAV_BG=NAV_BG,
                                BORDER=BORDER)

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    webhook_url = data.get('webhook_url')
    if not webhook_url:
        return jsonify({"error": "Webhook URL is required"}), 400

    payload = {
        "content": data.get('content'),
        "username": data.get('username'),
        "avatar_url": data.get('avatar_url')
    }
    payload = {k: v for k, v in payload.items() if v}

    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        r.raise_for_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
