import io
from PIL import Image
from rembg import remove

def clean_up_background(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    img.thumbnail((1024, 1024), Image.LANCZOS)

    result = remove(img)
    result = result.resize((2048, 2048), Image.LANCZOS)

    output = io.BytesIO()
    result.save(output, format="PNG", dpi=(300, 300))
    output.seek(0)
    return output