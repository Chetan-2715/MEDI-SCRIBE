from google.cloud import vision
import io
import os

def detect_text(content: bytes) -> str:
    """Detects text in the file located in Google Cloud Storage or a local file."""
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    if texts:
        return texts[0].description
    return ""

def detect_text_from_path(path: str) -> str:
    """Detects text from a local file path."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    return detect_text(content)
