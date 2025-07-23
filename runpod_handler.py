import base64
import runpod
from handler import clean_up_background

def handler(job):
    job_input = job["input"]
    image_b64 = job_input["image_base64"]
    image_bytes = base64.b64decode(image_b64)

    result = clean_up_background(image_bytes)
    encoded = base64.b64encode(result.read()).decode('utf-8')
    return {"output_image_base64": encoded}

runpod.serverless.start({"handler": handler})