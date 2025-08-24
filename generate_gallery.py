from __future__ import annotations
import os
import json
import argparse
from datetime import datetime

HTML_TEMPLATE = r"""<!doctype html>
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
      <div class="path" id="mediaPath">Media: /</div>
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
    // FILE_LIST and MEDIA_ROOT will be injected by generator
    const FILE_LIST = __FILE_LIST__;
    const MEDIA_ROOT = '__MEDIA_ROOT__';
  </script>
  <script src="js/gallery.js"></script>
</body>
</html>
"""

def gather_files(media_dir: str):
    """Recursively gather files in media_dir and return list of relative paths."""
    files = []
    for root, dirs, filenames in os.walk(media_dir):
        # skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')] 
        for fn in filenames:
            if fn.startswith('.'): 
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, start=media_dir)
            # use forward slashes for URLs
            rel = rel.replace(os.path.sep, '/')
            files.append(rel)
    files.sort()
    return files


def render_html(media_root: str, files: list[str], out_path: str):
    js_file_list = json.dumps(files)
    html = HTML_TEMPLATE.replace('__FILE_LIST__', js_file_list).replace('__MEDIA_ROOT__', media_root.replace('\', '/'))
    with open(out_path, 'w', encoding='utf8') as f:
        f.write(html)
    print(f"Wrote {out_path} with {len(files)} files. Media root: {media_root}")


def main():
    parser = argparse.ArgumentParser(description='Generate gallery.html from a media folder (recursive).')
    parser.add_argument('--media-folder', '-m', default='media', help='Path to media folder to index (default: media)')
    parser.add_argument('--out', '-o', default='gallery.html', help='Output HTML file (default: gallery.html)')
    args = parser.parse_args()

    media = args.media_folder
    if not os.path.isdir(media):
        print(f"Error: media folder '{media}' does not exist or is not a directory.")
        return

    files = gather_files(media)
    render_html(media, files, args.out)


if __name__ == '__main__':
    main()