from proprocess import preprocess_image
from io import BytesIO
import base64
import requests

API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-large-patch14"
headers = {"Authorization": "Bearer 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"}
imageurl = 'https://scontent-lhr8-1.cdninstagram.com/v/t51.2885-15/416678021_1081158129901003_1462508426101931245_n.jpg?stp=dst-jpg_e15&efg=e30&_nc_ht=scontent-lhr8-1.cdninstagram.com&_nc_cat=107&_nc_ohc=TiYnuno7MCsAX_YUoV7&edm=AGenrX8BAAAA&ccb=7-5&oh=00_AfAhWHHVe87N_ksm5qFy_YJiCdzX3e3dwJMMb0n_9uvuZg&oe=65BDBC0A&_nc_sid=ed990e'



def query(imageurl, givenarray):
    image = preprocess_image(imageurl)#Image.open(requests.get(imageurl, stream=True).raw)
    img_buffer = BytesIO()
    image.save(img_buffer, format="JPEG")  # Save the image to the buffer
    img_buffer.seek(0)
    img_data = img_buffer.read()
    payload = {
        "parameters": {"candidate_labels": givenarray},
        "inputs": base64.b64encode(img_data).decode("utf-8")
    }
    print(API_URL)
    response = requests.post(API_URL, headers=headers, json=payload)
    highest = 0
    curcat = ''
    for x in response.json():
      print(x)
      if highest < x['score']:
        highest = x['score']
        curcat = x['label']
    return curcat