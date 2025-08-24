import os
import json
import re
import sys

def get_all_files(dir_path):
    """Recursively get all file paths from a directory."""
    files_list = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

def generate_gallery():
    """Main function to generate the gallery."""

    # 1. Get folder path from user
    folder_path = input("Please enter the full path to your media folder: ").strip()

    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a valid directory.")
        sys.exit(1)

    print(f"Scanning folder: {folder_path}...")

    # 2. Scan for supported files
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.ogg']
    all_files = get_all_files(folder_path)

    media_files = sorted([
        os.path.relpath(f, folder_path).replace('\\', '/')
        for f in all_files
        if os.path.splitext(f)[1].lower() in supported_extensions
    ])

    if not media_files:
        print("No supported media files found in the specified directory.")
        sys.exit(0)

    print(f"Found {len(media_files)} media files.")

    # 3. Read the template file
    template_path = 'gallery.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file '{template_path}' not found.")
        sys.exit(1)

    # 4. Generate JavaScript data arrays
    media_files_js = json.dumps(media_files, indent=4)

    # Create the MEDIA_DATA object, mapping the relative path to the full path for local file access
    media_data = {
        rel_path: os.path.join(folder_path, rel_path).replace('\\', '/')
        for rel_path in media_files
    }
    media_data_js = json.dumps(media_data, indent=4)

    # 5. Inject data into the template
    # This regex looks for 'const MEDIA_FILES = [...]' and replaces the array content
    content_with_files = re.sub(
        r'(const MEDIA_FILES = )\[.*?\]',
        f'\\1{media_files_js}',
        template_content,
        flags=re.DOTALL
    )

    # This regex looks for 'const MEDIA_DATA = {...}' and replaces the object content
    final_content = re.sub(
        r'(const MEDIA_DATA = )\{.*?\}',
        f'\\1{media_data_js}',
        content_with_files,
        flags=re.DOTALL
    )

    # 6. Write the new content to gallery.html
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Successfully generated '{template_path}'!")
        print("You can now open the gallery.html file in your browser.")
    except IOError as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    generate_gallery()
