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
        .p-content { flex-grow: 1; min-width: 0; }
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

        /* ── Mode toggle ── */
        .mode-toggle { display: flex; margin-bottom: 20px; border-radius: 4px; overflow: hidden; border: 1px solid #4e5058; }
        .mode-toggle button { flex: 1; background: transparent; border: none; color: var(--muted); padding: 9px; cursor: pointer; font-weight: 600; font-size: 13px; transition: background 0.15s, color 0.15s; }
        .mode-toggle button.active { background: var(--blurple); color: white; }

        /* ── Two-column layout ── */
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media (max-width: 520px) {
            .two-col { grid-template-columns: 1fr; }
            .btn-row { grid-template-columns: 1fr; }
            .field-inputs { grid-template-columns: 1fr; }
        }

        /* ── Embed accent color picker ── */
        .color-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .color-row input[type="color"] { width: 44px; height: 36px; padding: 2px 3px; border-radius: 4px; cursor: pointer; border: none; background: var(--input); flex-shrink: 0; }
        .hex-label { font-size: 13px; color: var(--text); font-family: monospace; min-width: 60px; }
        .preset-swatches { display: flex; gap: 6px; flex-wrap: wrap; }
        .color-swatch { width: 22px; height: 22px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: border-color 0.1s, transform 0.1s; flex-shrink: 0; }
        .color-swatch:hover { border-color: white; transform: scale(1.18); }

        /* ── ANSI text-color toolbar ── */
        .ansi-toolbar { display: flex; gap: 5px; flex-wrap: wrap; align-items: center; background: #1a1b1e; padding: 8px 10px; border-radius: 4px 4px 0 0; border-bottom: 1px solid #3b3d44; }
        .ansi-toolbar .tb-label { font-size: 10px; color: var(--muted); text-transform: uppercase; font-weight: bold; margin-right: 2px; white-space: nowrap; }
        .ansi-swatch { width: 20px; height: 20px; border-radius: 3px; cursor: pointer; border: 2px solid transparent; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; transition: border-color 0.1s, transform 0.1s; flex-shrink: 0; user-select: none; }
        .ansi-swatch:hover { border-color: white; transform: scale(1.2); }
        .tb-meta { background: #4e5058; color: white; }
        .ansi-textarea { border-radius: 0 0 4px 4px !important; }

        /* ── Embed live preview card ── */
        .embed-card { background: #2b2d31; border-radius: 4px; overflow: hidden; display: flex; max-width: 520px; margin-top: 8px; border-left: 4px solid #5865f2; }
        .embed-inner { padding: 12px 16px 12px 12px; flex-grow: 1; min-width: 0; }
        .embed-thumb-img { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; margin: 12px 12px 12px 0; flex-shrink: 0; align-self: flex-start; }
        .embed-author-row { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
        .embed-author-icon { width: 22px; height: 22px; border-radius: 50%; object-fit: cover; }
        .embed-author-name { font-size: 13px; font-weight: 600; color: var(--text); }
        .embed-title { font-size: 15px; font-weight: 700; color: #00b0f4; margin-bottom: 6px; word-break: break-word; }
        .embed-title a { color: #00b0f4; text-decoration: none; }
        .embed-title a:hover { text-decoration: underline; }
        .embed-desc { font-size: 13px; color: var(--text); white-space: pre-wrap; word-break: break-word; margin-bottom: 8px; line-height: 1.45; }
        .embed-fields { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
        .embed-field-name { font-size: 12px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
        .embed-field-value { font-size: 13px; color: var(--text); white-space: pre-wrap; }
        .embed-big-img { width: 100%; border-radius: 4px; margin-top: 8px; display: block; max-height: 300px; object-fit: contain; }
        .embed-footer-row { display: flex; align-items: center; gap: 6px; margin-top: 8px; }
        .embed-footer-icon { width: 18px; height: 18px; border-radius: 50%; object-fit: cover; }
        .embed-footer-text { font-size: 11px; color: var(--muted); }

        /* ── Field builder rows ── */
        .field-item { background: var(--input); border-radius: 4px; padding: 10px; margin-bottom: 8px; }
        .field-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .field-item-header span { font-size: 11px; color: var(--muted); font-weight: bold; text-transform: uppercase; }
        .field-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .field-inputs input { font-size: 13px; }
        .inline-row { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: var(--muted); cursor: pointer; }
        .inline-row input[type="checkbox"] { width: auto; cursor: pointer; }

        .sec-divider { border: none; border-top: 1px solid #3b3d44; margin: 18px 0 15px; }
        .sub-label { font-size: 11px; font-weight: normal; text-transform: none; color: var(--blurple); margin-left: 6px; }
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

            <!-- Presets -->
            <label>Saved Presets (Auto-fills Webhook, Name &amp; PFP)</label>
            <div class="flex-row">
                <select id="preset_select" onchange="loadPreset()">
                    <option value="">-- Select a Preset --</option>
                </select>
                <button class="secondary" onclick="savePreset()">Save as Preset</button>
                <button class="danger" onclick="deletePreset()" title="Delete selected preset">&#x1F5D1;</button>
            </div>

            <!-- Webhook URL -->
            <div class="form-group">
                <label>Webhook URL</label>
                <input type="text" id="w_url" placeholder="https://discord.com/api/webhooks/..." oninput="inspectWebhook()">
                <div id="w_info" class="inspector"></div>
            </div>

            <!-- Name / Avatar -->
            <div class="two-col" style="margin-top:10px;">
                <div class="form-group">
                    <label>Override Name (Used for Preset Name)</label>
                    <input type="text" id="w_name" placeholder="Optional" oninput="updatePreview()">
                </div>
                <div class="form-group">
                    <label>Override Avatar URL</label>
                    <input type="text" id="w_avatar" placeholder="Optional" oninput="updatePreview()">
                </div>
            </div>

            <!-- Mode toggle -->
            <div class="mode-toggle">
                <button id="btn-mode-msg" class="active" onclick="setMode('message')">Message</button>
                <button id="btn-mode-embed" onclick="setMode('embed')">Embed Builder</button>
            </div>

            <!-- ══ MESSAGE MODE ══ -->
            <div id="section-message">
                <div class="form-group">
                    <label>Message Content</label>
                    <textarea id="w_content" placeholder="Type a message... Use <@USER_ID> to mention someone." oninput="updatePreview()" rows="4"></textarea>
                    <div id="w_counter" class="counter">0 / 2000</div>
                </div>
            </div>

            <!-- ══ EMBED BUILDER MODE ══ -->
            <div id="section-embed" style="display:none;">

                <!-- Accent Color -->
                <div class="form-group">
                    <label>Embed Accent Color</label>
                    <div class="color-row">
                        <input type="color" id="embed_color" value="#5865f2" oninput="onAccentChange()">
                        <span class="hex-label" id="embed_color_hex">#5865f2</span>
                        <div class="preset-swatches" id="preset-swatches"></div>
                    </div>
                </div>

                <hr class="sec-divider">

                <!-- Author -->
                <div class="two-col">
                    <div class="form-group">
                        <label>Author Name</label>
                        <input type="text" id="embed_author" placeholder="Author name..." oninput="updateEmbedPreview()">
                    </div>
                    <div class="form-group">
                        <label>Author Icon URL</label>
                        <input type="text" id="embed_author_icon" placeholder="https://..." oninput="updateEmbedPreview()">
                    </div>
                </div>

                <!-- Title + URL -->
                <div class="two-col">
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="embed_title" placeholder="Embed title..." oninput="updateEmbedPreview()">
                    </div>
                    <div class="form-group">
                        <label>Title URL</label>
                        <input type="text" id="embed_url" placeholder="https://..." oninput="updateEmbedPreview()">
                    </div>
                </div>

                <!-- Description + ANSI color toolbar -->
                <div class="form-group">
                    <label>Description <span class="sub-label">Select text then tap a color to highlight it</span></label>
                    <div class="ansi-toolbar" id="ansi-toolbar">
                        <span class="tb-label">Colors:</span>
                    </div>
                    <textarea id="embed_desc" class="ansi-textarea" placeholder="Description... Select any text above, then click a color swatch to colorize it." oninput="updateEmbedPreview()" rows="5"></textarea>
                </div>

                <!-- Thumbnail + Image -->
                <div class="two-col">
                    <div class="form-group">
                        <label>Thumbnail URL <span class="sub-label">small, top-right</span></label>
                        <input type="text" id="embed_thumb" placeholder="https://..." oninput="updateEmbedPreview()">
                    </div>
                    <div class="form-group">
                        <label>Image URL <span class="sub-label">large, bottom</span></label>
                        <input type="text" id="embed_image" placeholder="https://..." oninput="updateEmbedPreview()">
                    </div>
                </div>

                <!-- Footer -->
                <div class="two-col">
                    <div class="form-group">
                        <label>Footer Text</label>
                        <input type="text" id="embed_footer" placeholder="Footer text..." oninput="updateEmbedPreview()">
                    </div>
                    <div class="form-group">
                        <label>Footer Icon URL</label>
                        <input type="text" id="embed_footer_icon" placeholder="https://..." oninput="updateEmbedPreview()">
                    </div>
                </div>

                <!-- Fields -->
                <div class="form-group">
                    <label>Fields</label>
                    <div id="embed_fields_list"></div>
                    <button class="secondary" style="width:100%;margin-top:4px;" onclick="addField()">+ Add Field</button>
                </div>

                <hr class="sec-divider">

                <!-- Optional plain content above embed -->
                <div class="form-group">
                    <label>Message Content <span class="sub-label">optional, appears above the embed</span></label>
                    <textarea id="embed_extra_content" placeholder="Optional plain text above the embed..." oninput="updatePreview()" rows="2"></textarea>
                </div>
            </div>

            <!-- Live preview -->
            <label style="margin-top:10px;">Live Discord Preview</label>
            <div class="preview-box">
                <div class="p-avatar"><img id="pre_img" src="https://discord.com/assets/f78426a064bc9dd24847.png"></div>
                <div class="p-content">
                    <div class="p-name"><span id="pre_name">Webhook</span> <span class="p-tag">APP</span></div>
                    <div id="pre_text" class="p-text">Message preview...</div>
                    <div id="pre_embed"></div>
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
// ─────────────────────────────────────────────
//  Constants
// ─────────────────────────────────────────────
const ESC = String.fromCharCode(27);   // ANSI escape character (decimal 27)

const ANSI_PALETTE = [
    { code: '30', bg: '#4f545c', label: 'Dark Gray' },
    { code: '31', bg: '#dc322f', label: 'Red' },
    { code: '32', bg: '#859900', label: 'Green' },
    { code: '33', bg: '#b58900', label: 'Yellow' },
    { code: '34', bg: '#268bd2', label: 'Blue' },
    { code: '35', bg: '#d33682', label: 'Pink' },
    { code: '36', bg: '#2aa198', label: 'Cyan' },
    { code: '37', bg: '#dcddde', label: 'White' },
    { code: '90', bg: '#586e75', label: 'Bright Gray' },
    { code: '91', bg: '#cb4b16', label: 'Orange' },
    { code: '92', bg: '#6bb33b', label: 'Bright Green' },
    { code: '93', bg: '#e8b429', label: 'Bright Yellow' },
    { code: '94', bg: '#5b9bd5', label: 'Bright Blue' },
    { code: '95', bg: '#9b59b6', label: 'Purple' },
    { code: '96', bg: '#5bc0de', label: 'Bright Cyan' },
    { code: '97', bg: '#f8f8f8', label: 'Bright White' },
];

const ANSI_COLOR_MAP = {
    30: '#4f545c', 31: '#dc322f', 32: '#859900', 33: '#b58900',
    34: '#268bd2', 35: '#d33682', 36: '#2aa198', 37: '#dcddde',
    90: '#586e75', 91: '#cb4b16', 92: '#6bb33b', 93: '#e8b429',
    94: '#5b9bd5', 95: '#9b59b6', 96: '#5bc0de', 97: '#f8f8f8',
};

const ACCENT_PRESETS = [
    '#5865f2','#57f287','#fee75c','#ed4245','#eb459e',
    '#1abc9c','#e67e22','#9b59b6','#3498db','#ff6b6b',
    '#ffd700','#00b0f4','#ff4500','#2ecc71','#ffffff',
];

// ─────────────────────────────────────────────
//  Init
// ─────────────────────────────────────────────
let currentMode = 'message';
let savedSel = { start: 0, end: 0 };   // saved textarea selection for mobile
let fieldCount = 0;

window.onload = () => {
    buildAnsiToolbar();
    buildAccentPresets();
    refreshPresets();
    const savedUrl = localStorage.getItem('last_webhook');
    if (savedUrl) {
        document.getElementById('w_url').value = savedUrl;
        inspectWebhook();
    }
};

// ─────────────────────────────────────────────
//  Build ANSI toolbar
// ─────────────────────────────────────────────
function buildAnsiToolbar() {
    const toolbar = document.getElementById('ansi-toolbar');

    ANSI_PALETTE.forEach(c => {
        const sw = document.createElement('div');
        sw.className = 'ansi-swatch';
        sw.style.background = c.bg;
        if (c.bg === '#dcddde' || c.bg === '#f8f8f8') sw.style.border = '2px solid #4e5058';
        sw.title = c.label;
        sw.addEventListener('mousedown', e => e.preventDefault());
        sw.addEventListener('touchstart', saveSelectionFromTA, { passive: true });
        sw.addEventListener('click', () => applyAnsiCode(c.code));
        toolbar.appendChild(sw);
    });

    // Bold
    const bBtn = makeTbBtn('B', 'Bold', 'font-weight:900');
    bBtn.addEventListener('click', () => applyAnsiCode('1'));
    toolbar.appendChild(bBtn);

    // Underline
    const uBtn = makeTbBtn('U', 'Underline', 'text-decoration:underline');
    uBtn.addEventListener('click', () => applyAnsiCode('4'));
    toolbar.appendChild(uBtn);

    // Clear
    const xBtn = makeTbBtn('x', 'Remove color from selection', '');
    xBtn.style.fontSize = '11px';
    xBtn.addEventListener('click', clearAnsiFromSelection);
    toolbar.appendChild(xBtn);
}

function makeTbBtn(text, title, extraStyle) {
    const el = document.createElement('div');
    el.className = 'ansi-swatch tb-meta';
    el.title = title;
    el.textContent = text;
    if (extraStyle) el.style.cssText += extraStyle;
    el.addEventListener('mousedown', e => e.preventDefault());
    el.addEventListener('touchstart', saveSelectionFromTA, { passive: true });
    return el;
}

function saveSelectionFromTA() {
    const ta = document.getElementById('embed_desc');
    savedSel.start = ta.selectionStart;
    savedSel.end   = ta.selectionEnd;
}

// ─────────────────────────────────────────────
//  Build accent color presets
// ─────────────────────────────────────────────
function buildAccentPresets() {
    const container = document.getElementById('preset-swatches');
    ACCENT_PRESETS.forEach(hex => {
        const sw = document.createElement('div');
        sw.className = 'color-swatch';
        sw.style.background = hex;
        if (hex === '#ffffff') sw.style.border = '2px solid #4e5058';
        sw.title = hex;
        sw.onclick = () => {
            document.getElementById('embed_color').value = hex;
            onAccentChange();
        };
        container.appendChild(sw);
    });
}

// ─────────────────────────────────────────────
//  Mode toggle
// ─────────────────────────────────────────────
function setMode(mode) {
    currentMode = mode;
    document.getElementById('btn-mode-msg').classList.toggle('active', mode === 'message');
    document.getElementById('btn-mode-embed').classList.toggle('active', mode === 'embed');
    document.getElementById('section-message').style.display = mode === 'message' ? '' : 'none';
    document.getElementById('section-embed').style.display   = mode === 'embed'   ? '' : 'none';
    updatePreview();
}

// ─────────────────────────────────────────────
//  Nav
// ─────────────────────────────────────────────
function setView(v) {
    document.querySelectorAll('.view, nav button').forEach(el => el.classList.remove('active'));
    document.getElementById('view-' + v).classList.add('active');
    document.getElementById('nav-' + v).classList.add('active');
}

// ─────────────────────────────────────────────
//  Presets
// ─────────────────────────────────────────────
function savePreset() {
    const status = document.getElementById('status');
    let name = document.getElementById('w_name').value.trim();
    if (!name) name = "Unnamed Preset " + Math.floor(Math.random() * 100);

    const presetData = {
        url:      document.getElementById('w_url').value,
        username: document.getElementById('w_name').value,
        avatar:   document.getElementById('w_avatar').value
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
    if (!select.value) return;
    const presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
    const p = presets[select.value];
    if (p) {
        document.getElementById('w_url').value    = p.url      || "";
        document.getElementById('w_name').value   = p.username || "";
        document.getElementById('w_avatar').value = p.avatar   || "";
        inspectWebhook();
        updatePreview();
    }
}

function refreshPresets() {
    const select = document.getElementById('preset_select');
    select.innerHTML = '<option value="">-- Select a Preset --</option>';
    const presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
    for (const name of Object.keys(presets)) {
        select.innerHTML += `<option value="${name}">${name}</option>`;
    }
}

function deletePreset() {
    const select = document.getElementById('preset_select');
    const status = document.getElementById('status');
    const name   = select.value;
    if (!name) {
        status.innerText   = "Select a preset to delete first.";
        status.style.color = "var(--muted)";
        return;
    }
    let presets = JSON.parse(localStorage.getItem('app_presets') || '{}');
    delete presets[name];
    localStorage.setItem('app_presets', JSON.stringify(presets));
    refreshPresets();
    status.innerText   = `Deleted preset "${name}".`;
    status.style.color = "var(--red)";
}

// ─────────────────────────────────────────────
//  Accent color picker
// ─────────────────────────────────────────────
function onAccentChange() {
    const hex = document.getElementById('embed_color').value;
    document.getElementById('embed_color_hex').textContent = hex;
    updateEmbedPreview();
}

// ─────────────────────────────────────────────
//  ANSI text coloring
// ─────────────────────────────────────────────
function getSelection(ta) {
    if (document.activeElement === ta) {
        return { start: ta.selectionStart, end: ta.selectionEnd };
    }
    return { start: savedSel.start, end: savedSel.end };
}

function applyAnsiCode(code) {
    const ta    = document.getElementById('embed_desc');
    const sel   = getSelection(ta);
    const text  = ta.value;
    const open  = ESC + '[' + code + 'm';
    const close = ESC + '[0m';

    if (sel.start === sel.end) {
        // No selection: insert placeholder markers so user can see it worked
        const ins = open + close;
        ta.value = text.substring(0, sel.start) + ins + text.substring(sel.end);
    } else {
        const selected = text.substring(sel.start, sel.end);
        const wrapped  = open + selected + close;
        ta.value = text.substring(0, sel.start) + wrapped + text.substring(sel.end);
    }
    ensureAnsiBlock(ta);
    ta.focus();
    updateEmbedPreview();
}

function clearAnsiFromSelection() {
    const ta   = document.getElementById('embed_desc');
    const sel  = getSelection(ta);
    if (sel.start === sel.end) return;

    const chunk   = ta.value.substring(sel.start, sel.end);
    let cleaned   = '';
    let i = 0;
    while (i < chunk.length) {
        if (chunk.charCodeAt(i) === 27 && chunk[i + 1] === '[') {
            let j = i + 2;
            while (j < chunk.length && chunk[j] !== 'm') j++;
            i = j + 1;
        } else {
            cleaned += chunk[i];
            i++;
        }
    }
    ta.value = ta.value.substring(0, sel.start) + cleaned + ta.value.substring(sel.end);
    updateEmbedPreview();
}

function ensureAnsiBlock(ta) {
    const hasAnsi = ta.value.indexOf(ESC) !== -1;
    if (!hasAnsi) return;
    const prefix = '```ansi\\n';
    const suffix = '\\n```';
    let val = ta.value;
    if (val.startsWith(prefix)) val = val.substring(prefix.length);
    if (val.endsWith(suffix))   val = val.substring(0, val.length - suffix.length);
    ta.value = prefix + val + suffix;
}

// Convert raw ANSI-escaped string to coloured HTML (for preview only)
function ansiToHtml(raw) {
    let text = raw;
    const prefix = '```ansi\\n';
    const suffix = '\\n```';
    if (text.startsWith(prefix)) text = text.substring(prefix.length);
    if (text.endsWith(suffix))   text = text.substring(0, text.length - suffix.length);

    let html = '';
    let openSpans = 0;
    let i = 0;
    while (i < text.length) {
        const code = text.charCodeAt(i);
        if (code === 27 && text[i + 1] === '[') {
            let j = i + 2;
            while (j < text.length && text[j] !== 'm') j++;
            const n = parseInt(text.substring(i + 2, j), 10);
            i = j + 1;
            if (n === 0) {
                html += '</span>'.repeat(openSpans);
                openSpans = 0;
            } else if (n === 1) {
                html += '<span style="font-weight:bold">';
                openSpans++;
            } else if (n === 4) {
                html += '<span style="text-decoration:underline">';
                openSpans++;
            } else if (ANSI_COLOR_MAP[n]) {
                html += '<span style="color:' + ANSI_COLOR_MAP[n] + '">';
                openSpans++;
            }
        } else {
            const c = text[i];
            if      (c === '&') html += '&amp;';
            else if (c === '<') html += '&lt;';
            else if (c === '>') html += '&gt;';
            else                html += c;
            i++;
        }
    }
    html += '</span>'.repeat(openSpans);
    return html;
}

// ─────────────────────────────────────────────
//  Embed fields
// ─────────────────────────────────────────────
function addField() {
    const id   = fieldCount++;
    const list = document.getElementById('embed_fields_list');
    const div  = document.createElement('div');
    div.className = 'field-item';
    div.id = 'field-' + id;
    div.innerHTML =
        '<div class="field-item-header">' +
            '<span>Field ' + (id + 1) + '</span>' +
            '<button class="danger" style="padding:3px 8px;font-size:12px;" onmousedown="event.preventDefault()" onclick="removeField(' + id + ')">&#x2715; Remove</button>' +
        '</div>' +
        '<div class="field-inputs">' +
            '<input type="text" placeholder="Field name..." id="fn-' + id + '" oninput="updateEmbedPreview()">' +
            '<input type="text" placeholder="Field value..." id="fv-' + id + '" oninput="updateEmbedPreview()">' +
        '</div>' +
        '<label class="inline-row">' +
            '<input type="checkbox" id="fi-' + id + '" onchange="updateEmbedPreview()"> Inline' +
        '</label>';
    list.appendChild(div);
    updateEmbedPreview();
}

function removeField(id) {
    const el = document.getElementById('field-' + id);
    if (el) el.remove();
    updateEmbedPreview();
}

function getFields() {
    const fields = [];
    document.querySelectorAll('.field-item').forEach(item => {
        const id     = item.id.replace('field-', '');
        const name   = (document.getElementById('fn-' + id)  || {}).value || '';
        const value  = (document.getElementById('fv-' + id)  || {}).value || '';
        const inline = (document.getElementById('fi-' + id)  || {}).checked || false;
        if (name || value) fields.push({ name, value, inline });
    });
    return fields;
}

// ─────────────────────────────────────────────
//  Preview
// ─────────────────────────────────────────────
function escH(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function updatePreview() {
    const name   = document.getElementById('w_name').value   || "Webhook";
    const avatar = document.getElementById('w_avatar').value || "https://discord.com/assets/f78426a064bc9dd24847.png";
    document.getElementById('pre_name').innerText = name;
    document.getElementById('pre_img').src = avatar;

    if (currentMode === 'message') {
        const content = document.getElementById('w_content').value;
        let parsed = content
            .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
            .replace(/\\*(.*?)\\*/g, '<i>$1</i>')
            .replace(/`(.*?)`/g, '<code style="background:#2b2d31;padding:2px;">$1</code>');
        document.getElementById('pre_text').innerHTML = parsed || "Message preview...";
        document.getElementById('pre_text').style.display = '';
        document.getElementById('pre_embed').innerHTML = '';

        const count = content.length;
        const cEl = document.getElementById('w_counter');
        cEl.innerText = count + ' / 2000';
        cEl.className = count > 2000 ? "counter limit" : "counter";
    } else {
        const extra = document.getElementById('embed_extra_content').value;
        const preText = document.getElementById('pre_text');
        preText.innerText = extra || '';
        preText.style.display = extra ? '' : 'none';
        updateEmbedPreview();
    }
}

function updateEmbedPreview() {
    if (currentMode !== 'embed') return;

    const color      = document.getElementById('embed_color').value;
    const title      = document.getElementById('embed_title').value;
    const titleUrl   = document.getElementById('embed_url').value;
    const desc       = document.getElementById('embed_desc').value;
    const authorName = document.getElementById('embed_author').value;
    const authorIcon = document.getElementById('embed_author_icon').value;
    const footerTxt  = document.getElementById('embed_footer').value;
    const footerIcon = document.getElementById('embed_footer_icon').value;
    const thumbUrl   = document.getElementById('embed_thumb').value;
    const imageUrl   = document.getElementById('embed_image').value;
    const fields     = getFields();

    // Nothing to show?
    if (!title && !desc && !authorName && !footerTxt && !imageUrl && !thumbUrl && fields.length === 0) {
        document.getElementById('pre_embed').innerHTML = '';
        return;
    }

    let h = '<div class="embed-card" style="border-left-color:' + color + ';">';
    h += '<div class="embed-inner">';

    if (authorName) {
        h += '<div class="embed-author-row">';
        if (authorIcon) h += '<img class="embed-author-icon" src="' + escH(authorIcon) + '" onerror="this.style.display=\'none\'">';
        h += '<span class="embed-author-name">' + escH(authorName) + '</span></div>';
    }

    if (title) {
        h += '<div class="embed-title">';
        h += titleUrl ? '<a href="' + escH(titleUrl) + '" target="_blank">' + escH(title) + '</a>' : escH(title);
        h += '</div>';
    }

    if (desc) {
        h += '<div class="embed-desc">' + ansiToHtml(desc) + '</div>';
    }

    if (fields.length > 0) {
        h += '<div class="embed-fields">';
        fields.forEach(f => {
            const w = f.inline ? 'calc(33% - 6px)' : '100%';
            h += '<div class="embed-field" style="min-width:' + w + ';max-width:' + w + ';">';
            h += '<div class="embed-field-name">'  + escH(f.name)  + '</div>';
            h += '<div class="embed-field-value">' + escH(f.value) + '</div>';
            h += '</div>';
        });
        h += '</div>';
    }

    if (imageUrl) {
        h += '<img class="embed-big-img" src="' + escH(imageUrl) + '" onerror="this.style.display=\'none\'">';
    }

    if (footerTxt) {
        h += '<div class="embed-footer-row">';
        if (footerIcon) h += '<img class="embed-footer-icon" src="' + escH(footerIcon) + '" onerror="this.style.display=\'none\'">';
        h += '<span class="embed-footer-text">' + escH(footerTxt) + '</span></div>';
    }

    h += '</div>'; // embed-inner

    if (thumbUrl) {
        h += '<img class="embed-thumb-img" src="' + escH(thumbUrl) + '" onerror="this.style.display=\'none\'">';
    }

    h += '</div>'; // embed-card

    document.getElementById('pre_embed').innerHTML = h;
}

// ─────────────────────────────────────────────
//  Webhook inspector
// ─────────────────────────────────────────────
async function inspectWebhook() {
    const url  = document.getElementById('w_url').value;
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

// ─────────────────────────────────────────────
//  JSON backup
// ─────────────────────────────────────────────
function exportJSON() {
    const data = {
        app_presets:  JSON.parse(localStorage.getItem('app_presets') || '{}'),
        last_webhook: localStorage.getItem('last_webhook') || ""
    };
    const ioBox  = document.getElementById('backup_io');
    const status = document.getElementById('status');
    ioBox.style.display = 'block';
    ioBox.value = JSON.stringify(data);
    ioBox.select();
    try {
        document.execCommand('copy');
        status.innerText = "Backup string copied to your clipboard!";
        status.style.color = "var(--green)";
    } catch(err) {
        status.innerText = "Backup generated. Please copy the text from the box below.";
        status.style.color = "var(--blurple)";
    }
}

function importJSON() {
    const ioBox  = document.getElementById('backup_io');
    const status = document.getElementById('status');
    if (ioBox.style.display === 'none' || ioBox.value.trim() === '') {
        ioBox.style.display = 'block';
        ioBox.value = '';
        status.innerText = "Paste your backup string into the box, then click Import again.";
        status.style.color = "var(--blurple)";
        return;
    }
    try {
        const data = JSON.parse(ioBox.value);
        if (data.app_presets)  localStorage.setItem('app_presets',  JSON.stringify(data.app_presets));
        if (data.last_webhook) localStorage.setItem('last_webhook', data.last_webhook);
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

// ─────────────────────────────────────────────
//  API calls
// ─────────────────────────────────────────────
async function apiCall(type) {
    const status = document.getElementById('status');
    const url    = document.getElementById('w_url').value;
    const msgId  = document.getElementById('w_msg_id').value;

    status.innerText    = "Processing...";
    status.style.color  = "white";

    const payload = {
        url,
        msg_id:     msgId,
        content:    currentMode === 'embed'
                        ? document.getElementById('embed_extra_content').value
                        : document.getElementById('w_content').value,
        username:   document.getElementById('w_name').value,
        avatar_url: document.getElementById('w_avatar').value,
    };

    if (currentMode === 'embed') {
        const hex      = document.getElementById('embed_color').value;
        const colorInt = parseInt(hex.replace('#', ''), 16);
        const emb = { color: colorInt };

        const title = document.getElementById('embed_title').value;
        const eurl  = document.getElementById('embed_url').value;
        const desc  = document.getElementById('embed_desc').value;
        if (title) emb.title       = title;
        if (eurl)  emb.url         = eurl;
        if (desc)  emb.description = desc;

        const authorName = document.getElementById('embed_author').value;
        if (authorName) {
            emb.author = { name: authorName };
            const aIcon = document.getElementById('embed_author_icon').value;
            if (aIcon) emb.author.icon_url = aIcon;
        }

        const footerTxt = document.getElementById('embed_footer').value;
        if (footerTxt) {
            emb.footer = { text: footerTxt };
            const fIcon = document.getElementById('embed_footer_icon').value;
            if (fIcon) emb.footer.icon_url = fIcon;
        }

        const thumb = document.getElementById('embed_thumb').value;
        const image = document.getElementById('embed_image').value;
        if (thumb) emb.thumbnail = { url: thumb };
        if (image) emb.image     = { url: image };

        const fields = getFields();
        if (fields.length > 0) emb.fields = fields;

        payload.embed = emb;
    }

    try {
        const r   = await fetch('/' + type, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });
        const res = await r.json();

        if (res.success) {
            status.innerText   = "Success!";
            status.style.color = "var(--green)";
            if (type === 'send' && res.id) {
                const label = currentMode === 'embed'
                    ? (document.getElementById('embed_title').value || 'Embed')
                    : payload.content;
                addToHistory(res.id, label);
                if (currentMode === 'message') {
                    document.getElementById('w_content').value = "";
                    updatePreview();
                }
            }
        } else {
            status.innerText   = res.error || "Failed";
            status.style.color = "var(--red)";
        }
    } catch(e) {
        status.innerText   = "Error connecting to server";
        status.style.color = "var(--red)";
    }
}

function addToHistory(id, text) {
    const list = document.getElementById('history_list');
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML =
        '<span>ID: ' + id.substring(0,8) + '... "' + String(text||'').substring(0,20) + '..."</span>' +
        '<button onclick="copyToId(\'' + id + '\')" style="background:var(--blurple);border:none;color:white;padding:4px 8px;border-radius:3px;cursor:pointer;">Use ID</button>';
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
    url  = data.get('url') + "?wait=true"

    payload = {
        "content":          data.get('content'),
        "username":         data.get('username'),
        "avatar_url":       data.get('avatar_url'),
        "allowed_mentions": {"parse": ["users", "roles", "everyone"]}
    }

    if data.get('embed'):
        payload['embeds'] = [data['embed']]

    try:
        r = requests.post(url, json={k: v for k, v in payload.items() if v is not None}, timeout=10)
        if r.status_code == 429:
            return jsonify({"error": "Rate limited! Wait a few seconds."}), 429
        r.raise_for_status()
        return jsonify({"success": True, "id": r.json().get('id')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    url  = f"{data.get('url')}/messages/{data.get('msg_id')}"

    payload = {
        "content":          data.get('content'),
        "username":         data.get('username'),
        "avatar_url":       data.get('avatar_url'),
        "allowed_mentions": {"parse": ["users", "roles", "everyone"]}
    }

    if data.get('embed'):
        payload['embeds'] = [data['embed']]

    try:
        r = requests.patch(url, json={k: v for k, v in payload.items() if v is not None}, timeout=10)
        r.raise_for_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": "Edit failed. Check Message ID."}), 400

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    url  = f"{data.get('url')}/messages/{data.get('msg_id')}"
    try:
        r = requests.delete(url, timeout=10)
        r.raise_for_status()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": "Delete failed. Check Message ID."}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
