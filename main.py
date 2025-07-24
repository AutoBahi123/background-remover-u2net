import os
from rembg import remove
from PIL import Image
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

def process_images():
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
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh

    def upload_image(image_bytes, filename, folder_id):
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaIoBaseUpload(image_bytes, mimetype="image/png")
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    input_folder_id = get_folder_id(INPUT_FOLDER_NAME)
    output_folder_id = get_folder_id(OUTPUT_FOLDER_NAME)
    images = list_input_images(input_folder_id, MAX_IMAGES)

    for image in images:
        image_data = download_image(image["id"])
        input_image = Image.open(image_data)
        output_image = remove(input_image)
        output_buffer = BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        output_filename = f"no-bg-{image['name']}"
        upload_image(output_buffer, output_filename, output_folder_id)

    return {"done": True}
