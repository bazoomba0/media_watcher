#!/usr/bin/env python3
"""
generate_gallery.py

- Opens a folder picker (GUI) if no --root is provided.
- Lists the chosen folder plus its immediate subfolders and lets you pick which folders to generate galleries for.
- Writes one standalone gallery_<foldername>.html inside each selected folder.
- Each gallery includes:
  - Thumbnails (images), view buttons, delete icons, checkboxes
  - Auto-delete (if checked, viewing a file marks/removes it)
  - Undo for last deletion (5s)
  - Mark all, Trash modal with list and Unmark
  - Downloadable delete scripts (bash and .bat) referencing the files (relative paths)
"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk = None

GALLERY_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Gallery - __FOLDER_NAME__</title>
<style>
  body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:0;padding:0}
  header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:#222;color:#fff}
  .path{font-size:0.9rem;opacity:0.9}
  .controls{display:flex;gap:12px;align-items:center}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;padding:12px}
  .card{border:1px solid #ddd;padding:6px;background:#fff;display:flex;flex-direction:column;gap:6px}
  .thumb{height:120px;object-fit:cover;width:100%;background:#111;color:#ddd;display:flex;align-items:center;justify-content:center}
  .meta{display:flex;justify-content:space-between;align-items:center;font-size:0.85rem}
  .trash{cursor:pointer;position:relative}
  .badge{position:absolute;top:-6px;right:-6px;background:crimson;color:#fff;border-radius:999px;padding:2px 6px;font-size:12px}
  .modal{position:fixed;inset:0;background:rgba(0,0,0,0.5);display:none;align-items:center;justify-content:center}
  .modal .box{background:#fff;padding:16px;max-width:900px;width:95%;max-height:80%;overflow:auto}
  button{cursor:pointer}
  .undo{position:fixed;right:16px;bottom:16px;background:#222;color:#fff;padding:8px 12px;border-radius:6px;display:none}
  .controls button{background:#fff;border:0;padding:6px 10px;border-radius:4px}
  .controls label{color:#fff}
  a.small{font-size:0.85rem}
</style>
</head>
<body>
  <header>
    <div>
      <div style="font-weight:600">Media Watcher</div>
      <div class="path" id="mediaPath">Media: __FOLDER_NAME__</div>
    </div>
    <div class="controls">
      <label><input type="checkbox" id="autoDelete"> Auto-delete (delete on view)</label>
      <button id="markAll">Mark all</button>
      <div class="trash" id="trashBtn" title="Marked for deletion">
        🗑️<span class="badge" id="trashCount" style="display:none">0</span>
      </div>
    </div>
  </header>

  <div class="grid" id="grid"></div>

  <div class="modal" id="trashModal">
    <div class="box">
      <h3>Files marked for deletion (<span id="markedCount">0</span>)</h3>
      <div id="markedList"></div>
      <hr />
      <div>
        <button id="downloadBash">Download bash delete script</button>
        <button id="downloadWin">Download Windows delete script (.bat)</button>
        <button id="copyScript">Copy bash script to clipboard</button>
        <button id="closeTrash">Close</button>
      </div>
    </div>
  </div>

  <button class="undo" id="undoBtn">Undo last delete</button>

<script>
const FILE_LIST = __FILE_LIST__;
const MEDIA_ROOT = "__MEDIA_ROOT__";

(function(){
  const grid = document.getElementById('grid');
  const mediaPathEl = document.getElementById('mediaPath');
  const autoDeleteEl = document.getElementById('autoDelete');
  const trashBtn = document.getElementById('trashBtn');
  const trashCountEl = document.getElementById('trashCount');
  const trashModal = document.getElementById('trashModal');
  const markedListEl = document.getElementById('markedList');
  const markedCountEl = document.getElementById('markedCount');
  const undoBtn = document.getElementById('undoBtn');
  const markAllBtn = document.getElementById('markAll');
  const downloadBash = document.getElementById('downloadBash');
  const downloadWin = document.getElementById('downloadWin');
  const copyScript = document.getElementById('copyScript');
  const closeTrash = document.getElementById('closeTrash');

  mediaPathEl.textContent = 'Media: ' + MEDIA_ROOT;

  const state = {
    marked: new Set(),
    lastDeleted: null,
    undoTimer: null,
    removedDOM: new Map()
  };

  function updateTrashCount(){
    const n = state.marked.size;
    if(n>0){
      trashCountEl.style.display='inline-block';
      trashCountEl.textContent = n;
    } else {
      trashCountEl.style.display='none';
    }
  }

  function renderGrid(){
    grid.innerHTML = '';
    FILE_LIST.forEach(function(rel){
      const card = document.createElement('div');
      card.className = 'card';
      card.dataset.rel = rel;

      const thumb = document.createElement('div');
      thumb.className = 'thumb';
      const fullPath = (MEDIA_ROOT.replace(/\\/+$/,'') + '/' + rel).replace(/\\+/g,'/');

      if(/\\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(rel)){
        const img = document.createElement('img');
        img.src = fullPath;
        img.className = 'thumb';
        img.alt = rel;
        img.loading = 'lazy';
        thumb.appendChild(img);
      } else {
        thumb.textContent = rel.split('/').slice(-1)[0];
      }

      const meta = document.createElement('div');
      meta.className = 'meta';

      const label = document.createElement('div');
      label.textContent = rel;
      label.style.overflow='hidden';
      label.style.textOverflow='ellipsis';
      label.style.whiteSpace='nowrap';
      label.style.maxWidth='60%';

      const controls = document.createElement('div');

      const viewBtn = document.createElement('button');
      viewBtn.textContent = 'View';
      viewBtn.onclick = function(){
        window.open(fullPath, '_blank');
        if(autoDeleteEl.checked){
          performDelete(rel, card);
        }
      };

      const delBtn = document.createElement('button');
      delBtn.textContent = '🗑️';
      delBtn.title = 'Mark for deletion';
      delBtn.onclick = function(){
        markForDeletion(rel);
        renderGrid();
      };

      const chk = document.createElement('input');
      chk.type='checkbox';
      chk.checked = state.marked.has(rel);
      chk.onchange = function(){
        if(chk.checked) state.marked.add(rel); else state.marked.delete(rel);
        updateTrashCount();
      };

      controls.appendChild(viewBtn);
      controls.appendChild(delBtn);
      controls.appendChild(chk);

      meta.appendChild(label);
      meta.appendChild(controls);

      card.appendChild(thumb);
      card.appendChild(meta);

      grid.appendChild(card);
    });
    updateTrashCount();
  }

  function markForDeletion(rel){
    state.marked.add(rel);
    state.lastDeleted = rel;
    updateTrashCount();
    showUndo();
  }

  function performDelete(rel, cardEl){
    state.marked.add(rel);
    state.lastDeleted = rel;
    state.removedDOM.set(rel, cardEl.cloneNode(true));
    cardEl.remove();
    updateTrashCount();
    showUndo();
  }

  function showUndo(){
    undoBtn.style.display='block';
    if(state.undoTimer) clearTimeout(state.undoTimer);
    state.undoTimer = setTimeout(function(){
      state.lastDeleted = null;
      undoBtn.style.display='none';
      state.undoTimer = null;
    }, 5000);
  }

  undoBtn.onclick = function(){
    if(state.lastDeleted){
      const rel = state.lastDeleted;
      if(state.removedDOM.has(rel)){
        const node = state.removedDOM.get(rel);
        grid.appendChild(node);
        state.removedDOM.delete(rel);
      }
      if(state.marked.has(rel)) state.marked.delete(rel);
      state.lastDeleted = null;
      if(state.undoTimer) clearTimeout(state.undoTimer);
      undoBtn.style.display='none';
      updateTrashCount();
    }
  };

  trashBtn.onclick = function(){
    populateMarkedList();
    trashModal.style.display='flex';
  };

  closeTrash.onclick = function(){trashModal.style.display='none'};

  function populateMarkedList(){
    markedListEl.innerHTML='';
    const arr = Array.from(state.marked);
    markedCountEl.textContent = arr.length;
    if(arr.length===0){
      markedListEl.textContent='No files marked for deletion.';
      return;
    }
    arr.forEach(function(rel){
      const row = document.createElement('div');
      row.style.display='flex';
      row.style.justifyContent='space-between';
      row.style.padding='6px 0';
      const name = document.createElement('div');
      name.textContent = rel;
      const unmark = document.createElement('button');
      unmark.textContent='Unmark';
      unmark.onclick = function(){ state.marked.delete(rel); updateTrashCount(); populateMarkedList(); };
      row.appendChild(name);
      row.appendChild(unmark);
      markedListEl.appendChild(row);
    });
  }

  markAllBtn.onclick = function(){
    FILE_LIST.forEach(f=>state.marked.add(f));
    updateTrashCount();
    renderGrid();
  };

  function buildBashScript(){
    const lines = ['#!/bin/sh','# Delete script generated by media_watcher',''];
    Array.from(state.marked).forEach(rel=>{
      const p = (MEDIA_ROOT.replace(/\\/+$/,'') + '/' + rel).replace(/\\/g,'/');
      lines.push('rm -v -- "' + p.replace(/"/g,'\\"') + '"');
    });
    return lines.join('\n') + '\n';
  }

  function buildWinScript(){
    const lines = ['@echo off','rem Delete script generated by media_watcher',''];
    Array.from(state.marked).forEach(rel=>{
      const p = (MEDIA_ROOT.replace(/\\/+$/,'') + '\\' + rel).replace(/\\\\/g,'\\\\\\\\');
      lines.push('del /f /q "' + p + '"');
    });
    return lines.join('\r\n') + '\r\n';
  }

  function download(filename, content){
    const blob = new Blob([content],{type:'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  downloadBash.onclick = function(){ download('delete_marked.sh', buildBashScript()); };
  downloadWin.onclick = function(){ download('delete_marked.bat', buildWinScript()); };
  copyScript.onclick = function(){ navigator.clipboard.writeText(buildBashScript()); alert('Bash delete script copied to clipboard'); };

  renderGrid();
})();
</script>
</body>
</html>
"""

def choose_root_with_gui():
    if tk is None:
        print("Tkinter not available; please run with --root PATH")
        return None
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select a root folder (galleries will be created for selected subfolders)")
    root.destroy()
    return folder or None

def list_candidate_dirs(root_path: Path):
    # return [root, child dirs]
    dirs = [root_path]
    for entry in sorted(root_path.iterdir()):
        if entry.is_dir():
            dirs.append(entry)
    return dirs

def prompt_select_dirs(candidates):
    print("Choose which folders to generate galleries for:")
    for i, p in enumerate(candidates):
        print(f"  {i:2d}) {p}")
    print("Enter indices separated by commas, or 'all' to select all (default: all): ", end="")
    choice = input().strip()
    if choice == "" or choice.lower() == "all":
        return candidates
    indices = []
    for part in choice.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            idx = int(part)
            if 0 <= idx < len(candidates):
                indices.append(idx)
        except Exception:
            pass
    if not indices:
        print("No valid indices selected; defaulting to all.")
        return candidates
    return [candidates[i] for i in indices]

def gather_files(folder: Path):
    files = []
    for root, dirs, filenames in os.walk(folder):
        for fname in filenames:
            full = Path(root) / fname
            rel = full.relative_to(folder).as_posix()
            files.append(rel)
    files.sort()
    return files

def safe_filename(name: str):
    # simple safe name for gallery file using folder name
    cleaned = "".join(c if c.isalnum() or c in "-._" else "_" for c in name)
    if not cleaned:
        cleaned = "gallery"
    return cleaned

def generate_for_folder(folder: Path):
    files = gather_files(folder)
    if not files:
        print(f"Skipping {folder} (no files found).")
        return None
    file_list_json = json.dumps(files)
    media_root = "."  # gallery will live inside the folder
    html = GALLERY_TEMPLATE.replace("__FILE_LIST__", file_list_json).replace("__MEDIA_ROOT__", media_root).replace("__FOLDER_NAME__", folder.name)
    filename = folder / f"gallery_{safe_filename(folder.name)}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

def main():
    parser = argparse.ArgumentParser(description="Generate per-folder gallery HTML files (opens folder picker if no --root)")
    parser.add_argument("--root", "-r", help="Root folder (if omitted a GUI folder picker will open on supported systems)")
    args = parser.parse_args()

    root_path = None
    if args.root:
        root_path = Path(args.root).expanduser().resolve()
        if not root_path.exists() or not root_path.is_dir():
            print("Provided --root is not a valid directory:", args.root)
            sys.exit(1)
    else:
        picked = choose_root_with_gui()
        if not picked:
            print("No folder picked, exiting.")
            sys.exit(0)
        root_path = Path(picked).resolve()

    candidates = list_candidate_dirs(root_path)
    print(f"Detected {len(candidates)} folder(s).")
    selected = prompt_select_dirs(candidates)

    generated = []
    for p in selected:
        out = generate_for_folder(p)
        if out:
            generated.append(out)
            print("Wrote:", out)

    if generated:
        print("\nGenerated galleries:")
        for g in generated:
            print(" -", g)
        print("\nOpen each generated gallery (they are placed inside their respective folders).")
        print("Notes:")
        print(" - The generated delete scripts (downloadable from the gallery UI) reference files relative to the gallery file.")
        print(" - The browser cannot delete files. The delete scripts are what you run on your machine to remove marked files.")
    else:
        print("No galleries generated.")

if __name__ == "__main__":
    main()