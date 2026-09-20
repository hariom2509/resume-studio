#!/usr/bin/env python3
"""
Resume Creator — Live Studio & UI Server
Author: Resume Creator
Description: Provides a zero-dependency local web studio for real-time resume
previewing, A4 print layout inspection, live hot-reloading, and instant PDF/LaTeX export.
"""

import os
import sys
import json
import time
import hashlib
import shutil
import urllib.parse
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "resume_data.json")
HTML_FILE = os.path.join(CURRENT_DIR, "resume.html")
TEX_FILE = os.path.join(CURRENT_DIR, "resume.tex")
BACKUP_FILE = os.path.join(CURRENT_DIR, "resume.backup.html")
DEFAULT_PORT = 5050


def get_file_hash(fpath):
    if os.path.exists(fpath):
        try:
            with open(fpath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            pass
    return ""


STUDIO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resume Studio — ATS Resume Template</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg-base: #090d16;
    --bg-surface: #111726;
    --bg-surface-elevated: #1a2236;
    --border-subtle: #242f47;
    --border-strong: #3b4d75;
    --primary: #3b82f6;
    --primary-glow: rgba(59, 130, 246, 0.25);
    --accent: #10b981;
    --accent-glow: rgba(16, 185, 129, 0.2);
    --warning: #f59e0b;
    --text-main: #f1f5f9;
    --text-muted: #94a3b8;
    --text-dim: #64748b;
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-base);
    color: var(--text-main);
    min-height: 100vh;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* Header Bar */
  header {
    height: 64px;
    background: rgba(17, 23, 38, 0.9);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    z-index: 100;
    flex-shrink: 0;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    box-shadow: 0 4px 14px var(--primary-glow);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    color: #fff;
  }

  .brand-text h1 {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .version-badge {
    font-size: 11px;
    font-weight: 600;
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid rgba(59, 130, 246, 0.3);
  }

  .brand-text p {
    font-size: 11px;
    color: var(--text-muted);
  }

  /* Toolbar Controls */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .control-group {
    display: flex;
    align-items: center;
    background: var(--bg-surface-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 3px;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 13px;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: all 0.18s ease;
    text-decoration: none;
    user-select: none;
    white-space: nowrap;
  }

  .btn-icon-only {
    padding: 7px 10px;
  }

  .btn-subtle {
    background: transparent;
    color: var(--text-muted);
  }
  .btn-subtle:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #fff;
  }
  .btn-subtle.active {
    background: var(--primary);
    color: #fff;
  }

  .btn-primary {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #fff;
    box-shadow: 0 2px 10px var(--primary-glow);
  }
  .btn-primary:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px var(--primary-glow);
  }

  .btn-accent {
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff;
    box-shadow: 0 2px 10px var(--accent-glow);
  }
  .btn-accent:hover {
    background: linear-gradient(135deg, #34d399, #10b981);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px var(--accent-glow);
  }

  .btn-outline {
    background: var(--bg-surface-elevated);
    border: 1px solid var(--border-subtle);
    color: var(--text-main);
  }
  .btn-outline:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: var(--border-strong);
    color: #fff;
  }

  /* Status Pill */
  .sync-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: #34d399;
  }

  .pulse-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
  }

  /* Workspace */
  .workspace {
    flex: 1;
    display: flex;
    overflow: hidden;
    position: relative;
  }

  /* Canvas Stage - Full Scrolling Enabled */
  .canvas-stage {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: radial-gradient(circle at 50% 15%, #151d30 0%, #090d16 100%);
    overflow-y: scroll !important;
    overflow-x: auto !important;
    scroll-behavior: smooth;
    padding: 24px 20px 100px;
    position: relative;
    height: calc(100vh - 64px);
  }

  /* Custom Scrollbars */
  .canvas-stage::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  .canvas-stage::-webkit-scrollbar-track {
    background: #0d121e;
  }
  .canvas-stage::-webkit-scrollbar-thumb {
    background: #242f47;
    border-radius: 5px;
  }
  .canvas-stage::-webkit-scrollbar-thumb:hover {
    background: #3b4d75;
  }

  /* A4 Paper Frame */
  .paper-wrapper {
    position: relative;
    transition: transform 0.15s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: top center;
    margin-bottom: 30px;
  }

  .a4-sheet {
    width: 210mm;
    min-height: 297mm;
    background: #ffffff;
    box-shadow: 
      0 12px 36px rgba(0, 0, 0, 0.55),
      0 28px 70px rgba(0, 0, 0, 0.65),
      0 0 0 1px rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    position: relative;
    overflow: visible;
  }

  #resume-frame {
    width: 100%;
    min-height: 297mm;
    border: none;
    display: block;
    background: #ffffff;
  }

  /* Page Fit Indicator Float */
  .page-fit-bar {
    position: sticky;
    bottom: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 18px;
    background: rgba(17, 23, 38, 0.95);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-strong);
    border-radius: 12px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
    z-index: 50;
    margin-top: 20px;
  }

  .fit-status {
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .fit-status.ok { color: #34d399; }
  .fit-status.warning { color: #fbbf24; }

  .badge-dim {
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    background: var(--bg-surface-elevated);
    padding: 3px 8px;
    border-radius: 4px;
    color: var(--text-muted);
  }

  /* Side Drawer for JSON & HTML Live Editing */
  .drawer {
    width: 520px;
    background: var(--bg-surface);
    border-left: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), margin-right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 90;
  }

  .drawer.collapsed {
    margin-right: -520px;
  }

  .drawer-header {
    height: 52px;
    padding: 0 16px;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  .drawer-tabs {
    display: flex;
    gap: 4px;
  }

  .drawer-tab {
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    background: transparent;
    color: var(--text-muted);
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .drawer-tab.active {
    background: var(--bg-surface-elevated);
    color: #fff;
  }

  .drawer-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .code-editor {
    width: 100%;
    flex: 1;
    min-height: 400px;
    background: #0d121f;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 14px;
    resize: none;
    outline: none;
  }

  .code-editor:focus {
    border-color: var(--primary);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 16px;
  }

  .stat-card {
    background: var(--bg-surface-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 12px;
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-dim);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 15px;
    font-weight: 700;
    color: #fff;
  }

  /* Toast notification */
  .toast {
    position: fixed;
    top: 76px;
    right: 24px;
    background: #1e293b;
    border: 1px solid var(--border-strong);
    color: #fff;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    gap: 10px;
    transform: translateY(-20px);
    opacity: 0;
    pointer-events: none;
    transition: all 0.25s ease;
    z-index: 200;
  }

  .toast.show {
    transform: translateY(0);
    opacity: 1;
  }
</style>
</head>
<body>

<!-- Header -->
<header>
  <div class="brand">
    <div class="logo-icon">CV</div>
    <div class="brand-text">
      <h1>Resume Studio <span class="version-badge">Live ATS v1.1</span></h1>
      <p>ATS-Optimized Single-Page Resume Template</p>
    </div>
  </div>

  <div class="toolbar">
    <!-- Live Sync Status -->
    <div class="sync-indicator" id="sync-status">
      <div class="pulse-dot"></div>
      <span id="sync-text">Live Sync Active</span>
    </div>

    <!-- Zoom Controls -->
    <div class="control-group">
      <button class="btn btn-subtle btn-icon-only" onclick="adjustZoom(-0.05)" title="Zoom Out">−</button>
      <span id="zoom-label" style="font-size: 12px; font-weight: 600; padding: 0 8px; min-width: 44px; text-align: center;">95%</span>
      <button class="btn btn-subtle btn-icon-only" onclick="adjustZoom(0.05)" title="Zoom In">+</button>
      <button class="btn btn-subtle" onclick="resetZoom()" style="font-size: 11px;">Fit</button>
    </div>

    <!-- Actions -->
    <a href="/resume.html" target="_blank" class="btn btn-outline" title="Open Full Standalone HTML with Native Browser Scrolling">
      <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
      Open Clean HTML ↗
    </a>

    <button class="btn btn-outline" onclick="toggleDrawer()" id="btn-toggle-drawer">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
      Edit &amp; Code
    </button>

    <a href="/resume.tex" download="resume.tex" class="btn btn-outline" title="Download Overleaf LaTeX Code">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
      LaTeX (.tex)
    </a>

    <button class="btn btn-primary" onclick="printResume()" id="btn-print">
      <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
      Print / Save PDF
    </button>
  </div>
</header>

<!-- Main Workspace -->
<div class="workspace">
  <!-- Canvas Stage -->
  <main class="canvas-stage" id="stage">
    <div class="paper-wrapper" id="paper">
      <div class="a4-sheet" id="sheet">
        <iframe id="resume-frame" src="/resume.html" onload="onFrameLoad()"></iframe>
      </div>
    </div>

    <!-- Floating 1-Page Fit Status Bar -->
    <div class="page-fit-bar">
      <div class="fit-status ok" id="fit-badge">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
        <span id="fit-text">1-Page Fit: Optimal (Single Page Target)</span>
      </div>
      <div class="badge-dim" id="dim-badge">A4 • 210mm × 297mm</div>
      <button class="btn btn-subtle" onclick="reloadFrame()" style="font-size: 11px; padding: 4px 8px;">
        <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
        Reload
      </button>
    </div>
  </main>

  <!-- Side Drawer (Live HTML & JSON Editors) -->
  <aside class="drawer collapsed" id="drawer">
    <div class="drawer-header">
      <div class="drawer-tabs">
        <button class="drawer-tab active" id="tab-html" onclick="switchTab('html')">resume.html</button>
        <button class="drawer-tab" id="tab-data" onclick="switchTab('data')">resume_data.json</button>
        <button class="drawer-tab" id="tab-info" onclick="switchTab('info')">ATS &amp; Specs</button>
      </div>
      <button class="btn btn-subtle btn-icon-only" onclick="toggleDrawer()">✕</button>
    </div>

    <!-- Tab 1: Live HTML Editor -->
    <div class="drawer-body" id="drawer-content-html" style="display: flex; flex-direction: column; height: 100%;">
      <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 10px;">
        Edit your <b>resume.html</b> directly. Changes save straight to disk and update the live preview instantly!
      </p>
      <textarea id="html-editor" class="code-editor" spellcheck="false"></textarea>
      <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px;">
        <button class="btn btn-outline" onclick="loadRawHtml()">Reset</button>
        <button class="btn btn-accent" onclick="saveHtmlData()">Save HTML &amp; Update UI</button>
      </div>
    </div>

    <!-- Tab 2: JSON Editor -->
    <div class="drawer-body" id="drawer-content-data" style="display: none; flex-direction: column; height: 100%;">
      <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 10px;">
        Structured JSON model. Click <b>"Save &amp; Recompile"</b> to regenerate HTML &amp; LaTeX from JSON.
      </p>
      <textarea id="json-editor" class="code-editor" spellcheck="false"></textarea>
      <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px;">
        <button class="btn btn-outline" onclick="loadRawJson()">Reset</button>
        <button class="btn btn-accent" onclick="saveJsonData()">Save &amp; Recompile</button>
      </div>
    </div>

    <!-- Tab 3: Specs -->
    <div class="drawer-body" id="drawer-content-info" style="display: none;">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Target Format</div>
          <div class="stat-value">A4 Single Page</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Font Family</div>
          <div class="stat-value">Lora (Serif ATS)</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">LaTeX Engine</div>
          <div class="stat-value">pdfLaTeX / Overleaf</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Live Sync Engine</div>
          <div class="stat-value">MD5 Hash Polling (500ms)</div>
        </div>
      </div>
      <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.6; background: var(--bg-surface-elevated); padding: 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
        <b style="color: #fff;">💡 Printing &amp; Saving PDF:</b><br>
        1. Click <b>Print / Save PDF</b> in the top bar.<br>
        2. Set destination to <b>Save as PDF</b>.<br>
        3. Under <i>More Settings</i>, ensure <b>Headers and footers</b> are <b>unchecked</b>.<br>
        4. Margins: <b>Default</b> (all margins are calibrated in CSS).
      </div>
    </div>
  </aside>
</div>

<!-- Toast -->
<div class="toast" id="toast">
  <span id="toast-icon">⚡</span>
  <span id="toast-msg">Live Sync: File updated on disk</span>
</div>

<script>
  let currentZoom = 0.95;
  let lastHash = '';

  function applyZoom() {
    const paper = document.getElementById('paper');
    paper.style.transform = `scale(${currentZoom})`;
    document.getElementById('zoom-label').innerText = `${Math.round(currentZoom * 100)}%`;
  }

  function adjustZoom(delta) {
    currentZoom = Math.min(1.4, Math.max(0.45, currentZoom + delta));
    applyZoom();
  }

  function resetZoom() {
    currentZoom = 0.95;
    applyZoom();
  }

  function printResume() {
    const iframe = document.getElementById('resume-frame');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    }
  }

  function reloadFrame() {
    const iframe = document.getElementById('resume-frame');
    iframe.src = '/resume.html?t=' + Date.now();
  }

  // Handle iframe load, scrolling interception, and dynamic auto-sizing
  function onFrameLoad() {
    const iframe = document.getElementById('resume-frame');
    const stage = document.getElementById('stage');
    const sheet = document.getElementById('sheet');

    try {
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      if (!doc || !doc.body) return;

      // 1. Calculate actual content height
      const bodyH = doc.body.scrollHeight;
      const docH = doc.documentElement.scrollHeight;
      const realHeight = Math.max(bodyH, docH);
      const minA4Height = 1123; // 297mm in standard px
      const finalHeight = Math.max(minA4Height, realHeight + 15);

      iframe.style.height = finalHeight + 'px';
      sheet.style.minHeight = finalHeight + 'px';

      // 2. FORWARD WHEEL SCROLL EVENTS from inside iframe to parent canvas stage
      doc.addEventListener('wheel', function(e) {
        stage.scrollTop += e.deltaY;
      }, { passive: true });

      // 3. Touch scroll forwarding
      let startY = 0;
      doc.addEventListener('touchstart', function(e) {
        if (e.touches.length > 0) startY = e.touches[0].clientY;
      }, { passive: true });
      doc.addEventListener('touchmove', function(e) {
        if (e.touches.length > 0) {
          const delta = startY - e.touches[0].clientY;
          stage.scrollTop += delta;
          startY = e.touches[0].clientY;
        }
      }, { passive: true });

      // 4. Update 1-Page Fit Status
      const fitBadge = document.getElementById('fit-badge');
      const fitText = document.getElementById('fit-text');
      if (realHeight <= 1125) {
        fitBadge.className = 'fit-status ok';
        fitText.innerText = `1-Page Fit: Optimal (${realHeight}px / 1125px)`;
      } else {
        fitBadge.className = 'fit-status warning';
        fitText.innerText = `1-Page Fit Warning: Height (${realHeight}px) exceeds 1 page (1125px)`;
      }
    } catch (e) {
      console.error('Frame setup error:', e);
    }
  }

  function toggleDrawer() {
    const drawer = document.getElementById('drawer');
    const btn = document.getElementById('btn-toggle-drawer');
    drawer.classList.toggle('collapsed');
    btn.classList.toggle('active');
    if (!drawer.classList.contains('collapsed')) {
      loadRawHtml();
      loadRawJson();
    }
  }

  function switchTab(tab) {
    document.getElementById('tab-html').classList.toggle('active', tab === 'html');
    document.getElementById('tab-data').classList.toggle('active', tab === 'data');
    document.getElementById('tab-info').classList.toggle('active', tab === 'info');
    document.getElementById('drawer-content-html').style.display = tab === 'html' ? 'flex' : 'none';
    document.getElementById('drawer-content-data').style.display = tab === 'data' ? 'flex' : 'none';
    document.getElementById('drawer-content-info').style.display = tab === 'info' ? 'block' : 'none';
    if (tab === 'html') loadRawHtml();
    if (tab === 'data') loadRawJson();
  }

  async function loadRawHtml() {
    try {
      const res = await fetch('/api/html?t=' + Date.now());
      const htmlText = await res.text();
      document.getElementById('html-editor').value = htmlText;
    } catch (e) {
      console.error(e);
    }
  }

  async function saveHtmlData() {
    try {
      const text = document.getElementById('html-editor').value;
      const res = await fetch('/api/save_html', {
        method: 'POST',
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
        body: text
      });
      const result = await res.json();
      if (result.success) {
        showToast('resume.html saved & live preview updated!', '✨');
        reloadFrame();
      } else {
        alert('Error saving HTML: ' + (result.error || 'Unknown error'));
      }
    } catch (e) {
      alert('Error saving HTML: ' + e.message);
    }
  }

  async function loadRawJson() {
    try {
      const res = await fetch('/api/data?t=' + Date.now());
      const data = await res.json();
      document.getElementById('json-editor').value = JSON.stringify(data, null, 2);
    } catch (e) {
      console.error(e);
    }
  }

  async function saveJsonData() {
    try {
      const text = document.getElementById('json-editor').value;
      const parsed = JSON.parse(text);
      const res = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed)
      });
      const result = await res.json();
      if (result.success) {
        showToast('resume_data.json saved & recompiled!', '✨');
        reloadFrame();
        loadRawHtml();
      } else {
        alert('Error saving: ' + (result.error || 'Unknown error'));
      }
    } catch (e) {
      alert('Invalid JSON syntax: ' + e.message);
    }
  }

  function showToast(msg, icon = '⚡') {
    const toast = document.getElementById('toast');
    document.getElementById('toast-msg').innerText = msg;
    document.getElementById('toast-icon').innerText = icon;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3200);
  }

  // Fast MD5 Live Sync Poller
  async function pollStatus() {
    try {
      const res = await fetch('/api/status?_t=' + Date.now());
      const status = await res.json();
      if (lastHash && status.hash !== lastHash) {
        reloadFrame();
        showToast('Live Sync: Disk changes updated in UI!', '⚡');
        if (!document.getElementById('drawer').classList.contains('collapsed')) {
          loadRawHtml();
          loadRawJson();
        }
      }
      lastHash = status.hash;
    } catch (e) {
    } finally {
      setTimeout(pollStatus, 500);
    }
  }

  // Init
  applyZoom();
  pollStatus();
</script>
</body>
</html>
"""


class StudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {format % args}\n")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(STUDIO_HTML.encode("utf-8"))
            return

        if path == "/resume.html":
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(content)
                return

        if path == "/resume.tex":
            if os.path.exists(TEX_FILE):
                with open(TEX_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="resume.tex"')
                self.end_headers()
                self.wfile.write(content)
                return

        if path == "/api/html":
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
                return

        if path == "/api/data":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
                return

        if path == "/api/status":
            h_html = get_file_hash(HTML_FILE)
            h_json = get_file_hash(DATA_FILE)
            h_tex = get_file_hash(TEX_FILE)
            combined_hash = f"{h_html}:{h_json}:{h_tex}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps({
                "hash": combined_hash,
                "html_hash": h_html,
                "json_hash": h_json,
                "tex_hash": h_tex
            }).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/save_html":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")

                # Backup existing before writing
                if os.path.exists(HTML_FILE):
                    shutil.copyfile(HTML_FILE, BACKUP_FILE)

                with open(HTML_FILE, "w", encoding="utf-8") as f:
                    f.write(body)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        if parsed.path == "/api/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                new_data = json.loads(body.decode("utf-8"))

                # Write to resume_data.json
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, indent=2)

                # Recompile HTML & LaTeX safely
                try:
                    import generate
                    d = generate.load_data()
                    if os.path.exists(HTML_FILE):
                        shutil.copyfile(HTML_FILE, BACKUP_FILE)
                    with open(HTML_FILE, "w", encoding="utf-8") as f:
                        f.write(generate.build_html(d))
                    with open(TEX_FILE, "w", encoding="utf-8") as f:
                        f.write(generate.build_tex(d))
                except Exception as ex:
                    print(f"[!] Compilation error: {ex}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()


def run_server(port=DEFAULT_PORT, open_browser=True):
    server = HTTPServer(("127.0.0.1", port), StudioHandler)
    url = f"http://localhost:{port}"
    print("=" * 60)
    print(f"[*] Resume Studio Live Server running at: {url}")
    print(f"    - Live UI & Print Studio: {url}")
    print(f"    - Clean Standalone HTML:  {url}/resume.html")
    print(f"    - Raw LaTeX:              {url}/resume.tex")
    print(f"    - Live Sync:              MD5 Watcher active on resume.html & resume_data.json")
    print("=" * 60)

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Resume Studio server.")
        server.server_close()


if __name__ == "__main__":
    port = DEFAULT_PORT
    open_browser = "--no-browser" not in sys.argv
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)
    run_server(port=port, open_browser=open_browser)
