import os
from io import BytesIO
from PIL import Image
from rembg import remove

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "murugan-service.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
INPUT_FOLDER_NAME = "ImageInput"
OUTPUT_FOLDER_NAME = "ImageOutput"
MAX_IMAGES = 10

# === AUTH ===
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

def get_folder_id(folder_name):
    results = drive_service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed = false",
        fields="files(id, name)"
    ).execute()
    folders = results.get("files", [])
    return folders[0]["id"] if folders else None

def list_input_images(folder_id, max_files):
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
        pageSize=max_files,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def download_image(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def upload_image(image_bytes, filename, folder_id):
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(image_bytes, mimetype="image/png")
    drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

def process_and_upload(image_bytes, filename, output_folder_id):
    no_bg = remove(image_bytes.read())
    image = Image.open(BytesIO(no_bg)).convert("RGBA")
    new_size = (image.width * 2, image.height * 2)
    image = image.resize(new_size, Image.LANCZOS)
    output_io = BytesIO()
    image.save(output_io, format="PNG", dpi=(300, 300))
    output_io.seek(0)
    output_filename = f"{os.path.splitext(filename)[0]}_processed.png"
    upload_image(output_io, output_filename, output_folder_id)

def main():
    input_folder_id = get_folder_id(INPUT_FOLDER_NAME)
    output_folder_id = get_folder_id(OUTPUT_FOLDER_NAME)

    if not input_folder_id or not output_folder_id:
        print("❌ Folder(s) not found.")
        return

    images = list_input_images(input_folder_id, MAX_IMAGES)
    print(f"🔍 Found {len(images)} images to process.")

    for img in images:
        print(f"⚙️ Processing: {img['name']}")
        try:
            img_data = download_image(img["id"])
            process_and_upload(img_data, img["name"], output_folder_id)
        except Exception as e:
            print(f"❌ Error with {img['name']}: {e}")

if __name__ == "__main__":
    main()
