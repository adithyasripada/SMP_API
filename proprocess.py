import requests
from PIL import Image
def preprocess_image(image_url):
    if image_url == "storyboard_horizontal.png":
      image = Image.open(image_url)
    else: image = Image.open(requests.get(image_url, stream=True).raw)
    input_tensor = image
    return input_tensor