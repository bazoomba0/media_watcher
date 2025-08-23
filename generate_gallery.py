import os
import json
import re

# Directory containing the media files
MEDIA_DIR = 'media'
# Path to the gallery HTML file
GALLERY_HTML = 'gallery.html'
# Supported file extensions
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.ogg']

def get_media_files():
    """Scans the media directory for supported files."""
    if not os.path.isdir(MEDIA_DIR):
        print(f"Error: Media directory '{MEDIA_DIR}' not found.")
        print("Please create it and add your media files.")
        return []

    files = os.listdir(MEDIA_DIR)
    media_files = sorted([f for f in files if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS])
    return media_files

def update_gallery_html(media_files):
    """Reads gallery.html, replaces the media file arrays, and writes it back."""
    try:
        with open(GALLERY_HTML, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {GALLERY_HTML} not found.")
        return

    # 1. Generate the MEDIA_FILES array
    # The json.dumps function is a safe way to create a JSON-formatted string,
    # which is exactly what's needed for a JavaScript array.
    media_files_js = json.dumps(media_files, indent=4)

    # 2. Generate the MEDIA_DATA object
    # This creates a dictionary mapping the filename to its path in the media folder.
    media_data = {f: os.path.join(MEDIA_DIR, f).replace('\\', '/') for f in media_files}
    media_data_js = json.dumps(media_data, indent=4)

    # Use regular expressions to replace the old arrays.
    # re.DOTALL allows '.' to match newlines, which is important for multi-line arrays.
    content = re.sub(r'const MEDIA_FILES = .*?;', f'const MEDIA_FILES = {media_files_js};', content, flags=re.DOTALL)
    content = re.sub(r'const MEDIA_DATA = .*?;', f'const MEDIA_DATA = {media_data_js};', content, flags=re.DOTALL)

    try:
        with open(GALLERY_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {GALLERY_HTML} with {len(media_files)} media files.")
    except IOError as e:
        print(f"Error writing to {GALLERY_HTML}: {e}")

if __name__ == '__main__':
    print("Starting gallery generation...")
    media_files = get_media_files()
    if media_files:
        update_gallery_html(media_files)
    else:
        print("No media files found. The gallery will be empty.")
        # If no files are found, we still update the gallery to be empty
        update_gallery_html([])
    print("Done.")
