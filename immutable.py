import os
import subprocess

def get_immutable_files():
    """
    Finds all files with the immutable bit set.
    Returns a set of file paths.
    """
    immutable_files = set()
    try:
        # Use the lsattr command to list files with the immutable attribute
        result = subprocess.run(["lsattr", "-R", "/"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=1)  # Split into attributes and file path
            if len(parts) == 2:  # Ensure line has both attributes and a file path
                attributes, file_path = parts
                if 'i' in attributes:  # Check if the immutable bit is set
                    # Ensure the file_path looks valid
                    if os.path.exists(file_path) or os.path.islink(file_path):
                        immutable_files.add(file_path)
    except subprocess.CalledProcessError as e:
        print(f"Error while running lsattr: {e}")
    except Exception as e:
        print(f"Unexpected error while finding immutable files: {e}")
    return immutable_files

def get_process_files(pid):
    """
    Get all files used by a specific process.
    Returns a list of file paths.
    """
    files = []
    fd_path = f"/proc/{pid}/fd"
    try:
        for fd in os.listdir(fd_path):
            file_path = os.readlink(os.path.join(fd_path, fd))
            files.append(file_path)
    except Exception:
        pass
    return files

def find_processes_with_immutable_files():
    """
    Finds running processes that are using files with the immutable bit set.
    """
    immutable_files = get_immutable_files()
    if not immutable_files:
        print("No files with the immutable bit set found.")
        return

    print("Immutable files found:")
    for f in immutable_files:
        print(f"  {f}")
    print("\nSearching for processes using these files...\n")

    processes_using_immutable = []

    for pid in os.listdir("/proc"):
        if pid.isdigit():  # Only process directories named with digits (process IDs)
            try:
                cmdline_path = f"/proc/{pid}/cmdline"
                with open(cmdline_path, "r") as f:
                    cmdline = f.read().replace("\x00", " ").strip()
                files = get_process_files(pid)
                for file in files:
                    if file in immutable_files:
                        processes_using_immutable.append((pid, cmdline, file))
            except Exception:
                pass

    if processes_using_immutable:
        print("Processes using immutable files:")
        for pid, cmdline, file in processes_using_immutable:
            print(f"PID: {pid}, Command: {cmdline}, File: {file}")
    else:
        print("No processes found using immutable files.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run as root.")
    else:
        find_processes_with_immutable_files()
