import os
import shutil


def remove_directories():
    """
    Remove all __pycache__ and .idea directories in the relative path ../Spectrogram_Fingerprinting.
    """
    # Set the base path relative to this script
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    # Directories to remove
    dir_names = ["__pycache__", ".idea"]

    # Check if the base path exists
    if not os.path.exists(base_path):
        # print(f"Error: The path '{base_path}' does not exist.")
        return

    # print(f"Scanning {base_path} for {dir_names}...")
    for root, dirs, files in os.walk(base_path):  # Walk through the base directory
        for dir_name in dirs:
            if dir_name in dir_names:
                target_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(target_path, ignore_errors=False)  # Remove directory
                    # print(f"Removed: {target_path}")
                except Exception as e:
                    print(f"Error removing {target_path}: {e}")

    print("Cleanup complete.")
