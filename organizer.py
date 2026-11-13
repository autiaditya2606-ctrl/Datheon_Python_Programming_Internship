
import os
import json
import shutil
import logging
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("organizer.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

HISTORY_FILENAME = ".organizer_history.json"
LOG_FILENAME = "organizer.log"

# File extension to category mapping
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".csv": "Documents",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",

    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    ".webm": "Videos",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",

    # Code
    ".py": "Code",
    ".js": "Code",
    ".html": "Code",
    ".css": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".sql": "Code",
}

DEFAULT_CATEGORY = "Others"


def save_history(history_path, history):
    """Save undo history safely using a temporary file."""
    temp_path = history_path.with_name(
        history_path.name + ".tmp"
    )

    try:
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        os.replace(temp_path, history_path)

    finally:
        if temp_path.exists():
            temp_path.unlink()


def get_unique_path(destination):
    """Generate a filename that does not already exist."""
    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


def organize_directory(directory):
    """Organize files and record their original locations."""
    root = Path(directory).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: Invalid directory: {root}")
        return

    history_path = root / HISTORY_FILENAME

    # Protect the history of an earlier operation
    if history_path.exists():
        print(
            "\nUndo history already exists for this directory."
        )
        print("Undo the previous operation before organizing again.")
        return

    history = []
    moved_count = 0
    skipped_count = 0
    error_count = 0
    category_counts = defaultdict(int)

    logging.info("Starting organization: %s", root)

    try:
        with os.scandir(root) as entries:
            for entry in entries:

                # Process only regular files in the selected directory
                if not entry.is_file(follow_symlinks=False):
                    continue

                source = Path(entry.path)

                # Never organize the utility's own files
                if source.name in {
                    HISTORY_FILENAME,
                    HISTORY_FILENAME + ".tmp",
                    LOG_FILENAME,
                    "organizer.py",
                }:
                    skipped_count += 1
                    continue

                extension = source.suffix.lower()
                category = EXTENSION_MAP.get(
                    extension, DEFAULT_CATEGORY
                )

                target_folder = root / category

                try:
                    target_folder.mkdir(exist_ok=True)

                    destination = get_unique_path(
                        target_folder / source.name
                    )

                    # Move the file
                    shutil.move(str(source), str(destination))

                    # Record the move immediately
                    history.append({
                        "original": str(source),
                        "organized": str(destination),
                    })

                    # Save after every successful move
                    save_history(history_path, history)

                    moved_count += 1
                    category_counts[category] += 1

                    logging.info(
                        "Moved: %s -> %s",
                        source.name,
                        destination,
                    )

                except PermissionError as exc:
                    error_count += 1
                    logging.error(
                        "Permission denied for %s: %s",
                        source.name,
                        exc,
                    )

                except OSError as exc:
                    error_count += 1
                    logging.error(
                        "Could not move %s: %s",
                        source.name,
                        exc,
                    )

    except PermissionError as exc:
        logging.error("Cannot access directory: %s", exc)
        return

    except OSError as exc:
        logging.error("Could not scan directory: %s", exc)
        return

    print("\n" + "=" * 42)
    print("       FILE ORGANIZER SUMMARY")
    print("=" * 42)
    print(f"Directory       : {root}")
    print(f"Files relocated : {moved_count}")
    print(f"Files skipped   : {skipped_count}")
    print(f"Errors          : {error_count}")

    if category_counts:
        print("\nFiles organized by category:")

        for category, count in sorted(category_counts.items()):
            print(f"  {category:<12}: {count}")

    print("=" * 42)

    if history:
        print(f"Undo history saved in: {history_path}")
    else:
        print("No files were moved.")

    logging.info(
        "Organization completed. Files relocated: %d",
        moved_count,
    )


def undo_organization(directory):
    """Restore files to their original locations."""
    root = Path(directory).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: Invalid directory: {root}")
        return

    history_path = root / HISTORY_FILENAME

    if not history_path.exists():
        print("No undo history found for this directory.")
        return

    try:
        with history_path.open("r", encoding="utf-8") as file:
            history = json.load(file)

    except (OSError, json.JSONDecodeError) as exc:
        logging.error("Could not read undo history: %s", exc)
        print("Could not read the history file. It has been preserved.")
        return

    if not isinstance(history, list):
        print("Invalid history format. The history file was preserved.")
        return

    restored_count = 0
    remaining = []

    print("\nStarting undo operation...")

    # Reverse the moves in the opposite order
    for item in reversed(history):
        try:
            original = Path(item["original"])
            organized = Path(item["organized"])

            if not organized.is_file():
                if original.exists():
                    # Already restored
                    continue

                logging.warning(
                    "File is missing from both locations: %s",
                    organized,
                )
                remaining.append(item)
                continue

            if original.exists():
                logging.warning(
                    "Original path already exists; skipping: %s",
                    original,
                )
                remaining.append(item)
                continue

            original.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(organized), str(original))

            restored_count += 1
            logging.info("Restored: %s", original)

        except (KeyError, TypeError, PermissionError, OSError) as exc:
            logging.error("Could not restore file: %s", exc)
            remaining.append(item)

    # Preserve only entries that still need attention
    try:
        if remaining:
            save_history(history_path, list(reversed(remaining)))
            print("Some files could not be restored.")
            print("Their history has been kept for another attempt.")
        else:
            history_path.unlink(missing_ok=True)
            print("All recorded files have been restored.")
            print("Undo history cleared.")

    except OSError as exc:
        logging.error("Could not update undo history: %s", exc)
        print("Warning: Could not update the history file.")

    print("\n" + "=" * 42)
    print("          UNDO SUMMARY")
    print("=" * 42)
    print(f"Directory       : {root}")
    print(f"Files restored  : {restored_count}")
    print(f"Files remaining : {len(remaining)}")
    print("=" * 42)


def main():
    print("\n" + "=" * 42)
    print("     AUTOMATED FILE ORGANIZER")
    print("=" * 42)
    print("1. Organize files")
    print("2. Undo last organization")
    print("3. Exit")

    choice = input("\nChoose an option (1-3): ").strip()

    if choice == "1":
        folder = input(
            "Enter the directory path to organize: "
        ).strip()

        organize_directory(folder)

    elif choice == "2":
        folder = input(
            "Enter the directory path to undo: "
        ).strip()

        undo_organization(folder)

    elif choice == "3":
        print("Exiting File Organizer.")

    else:
        print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
