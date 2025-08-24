#!/usr/bin/env python3
"""
generate_gallery.py

Generates gallery HTML files that inject the FILE_LIST and MEDIA_ROOT into the repository template which references js/gallery.js so the original thumbnail rendering and gallery viewing logic is preserved.

- Opens a folder picker (GUI) if no --root is provided.
- Lists the chosen folder plus its immediate subfolders and lets you pick which folders to generate galleries for.
- Writes one standalone gallery_<foldername>.html inside each selected folder.
- Injects FILE_LIST and MEDIA_ROOT placeholders into the template so the existing js/gallery.js (thumbnail/rendering/viewing logic) is used unchanged.

"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None

# Keep the HTML minimal and point to the repo's js/gallery.js which contains the original thumbnail/viewing logic.
HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Media Watcher Gallery</title>
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
  </style>
</head>
<body>
  <header>
    <div>
      <div style="font-weight:600">Media Watcher</div>
      <div class="path" id="mediaPath">Media: __FOLDER_NAME__</div>
    </div>
    <div class="controls">
      <label><input type="checkbox" id="deleteOnView"> Delete on view (mark for deletion automatically)</label>
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
    // FILE_LIST and MEDIA_ROOT will be injected by the generator
    const FILE_LIST = __FILE_LIST__;
    const MEDIA_ROOT = '__MEDIA_ROOT__';
  </script>
  <script src="js/gallery.js"></script>
</body>
</html>
''' 
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
        # skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')] 
        for fname in filenames:
            if fname.startswith('.'): 
                continue
            full = Path(root) / fname
            rel = full.relative_to(folder).as_posix()
            files.append(rel)
    files.sort()
    return files

def safe_filename(name: str):
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
    media_root = folder.resolve().as_posix()
    html = HTML_TEMPLATE.replace("__FILE_LIST__", file_list_json).replace("__MEDIA_ROOT__", media_root).replace("__FOLDER_NAME__", folder.name)
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
        print(" - The generator injects FILE_LIST and MEDIA_ROOT so the repository's js/gallery.js provides thumbnail rendering and viewing logic unchanged.")
    else:
        print("No galleries generated.")

if __name__ == "__main__":
    main()
