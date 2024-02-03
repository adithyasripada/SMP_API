#from flask import Flask, request, render_template
import csv
import io
import re
import pandas as pd
import requests
import threading
import requests
import base64
from PIL import Image
from io import BytesIO
import imghdr
import requests
from moviepy.editor import VideoFileClip
from PIL import Image
import urllib.request
import streamlit as st
import os

st.title("""Social Media Post Image Classifier""")

file = st.file_uploader("Pick a file")
classarray = ["Baseball","Basketball","Football","Tennis","Unspecified"]



#app = Flask(__name__)

# Function for concurrent GET link calls
def concurrent_get_links(urls):
    results = []

    # Define a worker function for each thread
    def worker(url):
        try:
            print(f"GETTING REQUEST FOR URL: {url} WITH NO PROXY")
            r = requests.get(url + "media/?size=l")
        except:
            # With proxy
            print(f"GETTING REQUEST FOR URL: {url} WITH PROXY")
            r = requests.get(
                url + "media/?size=l",
                proxies={
                    "https": 'http://7KrAOumff6uMdSrF:3UPw4vDCeBOstj7l_streaming-1@geo.iproyal.com:12321'
                },
            )
        results.append(r.url)

    threads = [threading.Thread(target=worker, args=(url,)) for url in urls]

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results


# Function to preprocess image
def preprocess_image(image_url):
    if image_url == "storyboard_horizontal.png":
      image = Image.open(image_url)
    else: image = Image.open(requests.get(image_url, stream=True).raw)
    input_tensor = image
    return input_tensor



def get_link_tik(givenurl):
    url = 'https://www.tikwm.com/api/'
    form_data = {'url': givenurl, 'hd': '1'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(url, data=form_data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        json_response = response.json()
        if 'data' in json_response and 'wmplay' in json_response['data']:
            res = json_response['data']['wmplay']
        else:
            print("Unexpected JSON structure or missing data")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except KeyError as e:
        print(f"Key error: {e}")
        return None

    tikurl = 'tiktokimagetoprocess.mp4'
    urllib.request.urlretrieve(res, tikurl)

    try:
        clip = VideoFileClip(tikurl)
        dur = clip.duration
        durinc = dur / 4
        tracker = 0
        framearr = []
        for x in range(4):
            b = str(x) + "hello.png"
            clip.save_frame(b, t=tracker)
            frame = Image.open(b)
            framearr.append(frame)
            tracker += durinc

        width = sum(frame.width for frame in framearr)
        height = framearr[0].height
        storyboard = Image.new('RGB', (width, height))
        offset = 0
        for frame in framearr:
            storyboard.paste(frame, (offset, 0))
            offset += frame.width

        tiktokpath = 'storyboard_horizontal.png'
        storyboard.save(tiktokpath)
        return tiktokpath

    except Exception as e:
        print(f"Error processing video: {e}")
        return None

#@app.route('/')
# def index():
#     # Load the model outside the function
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return 'No file part'

#     file = request.files['file']

#     if file.filename == '':
#         return 'No selected file'

#     js_array_data = request.form['dataArray']
#     classarray = js_array_data.split(',')


def classify(file,classarray):
    if file:
        print(file)
        content = parse_csv(file)
        final = ""
        for x in content:
            print("Adi")
            print(x)
            tik_path = get_link_tik(x)
            print(tik_path)
            #response = requests.get(x)
            #image_data = response.content #
            img = preprocess_image(tik_path)
            img_buffer = BytesIO()
            img.save(img_buffer, format="JPEG")  # Save the image to the buffer
            img_buffer.seek(0)
            image_data = img_buffer.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            div1 = '<div style="display:flex font-size:20px">'
            div2 = '</div>'
            img = f'<img src="data:image/jpeg;base64,{base64_image}" width="200" height="200">'
            
            finalclass=query(tik_path, classarray)
            line = div1 + img + finalclass + div2 + '<br><br>' 
            final = final + line
        return final

def parse_csv(file):
    # Load data from CSV
    data = pd.read_csv(file)
    # Extract URLs from the 'Image_URL' column
    urls = [row['Image_URL'] for index, row in data.iterrows()]
    result_urls = urls#concurrent_get_links(urls)
    return result_urls

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
    response = requests.post(API_URL, headers=headers, json=payload)
    print(response)
    highest = 0
    curcat = ''
    for x in response.json():
      if highest < (x['score']):
        highest = (x['score'])
        curcat = x['label']
    return curcat

if st.button("Classify"):
    html_string = classify(file,classarray)
    st.markdown(html_string, unsafe_allow_html=True)
