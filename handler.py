from main import process_images

def handler(event):
    try:
        result = process_images()
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
