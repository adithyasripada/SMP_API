import pandas as pd
from PIL import Image
import requests
import torch
from transformers import BitsAndBytesConfig, pipeline
from torchvision import transforms
from bs4 import BeautifulSoup
import re
import json
import imghdr
import requests
from moviepy.editor import VideoFileClip
from PIL import Image
import urllib.request
import re
import pandas as pd
#from google.colab import drive

# Function to preprocess image
def preprocess_image(image_url):
    if image_url == "storyboard_horizontal.png":
      image = Image.open(image_url)
    else: image = Image.open(requests.get(image_url, stream=True).raw)
    input_tensor = image
    return input_tensor

# Function to process image and generate text
def process_image_and_generate_text(image_url):
    image_tensor = preprocess_image(image_url)

    max_new_tokens = 100
    prompt = f"USER: <image>\n What is the sports shown in the picture. If there is no sports specified return unspecified, answer in one word\nASSISTANT:"

    try:
        outputs = pipe(image_tensor, prompt=prompt, generate_kwargs={"max_new_tokens": 100})
        return outputs[0]["generated_text"]
    except Exception as e:
        return f"Error processing URL {image_url}: {e}"

#Function to get the insta link    
def get_link_insta(url):
    url = url.replace('reels', 'p')
    pattern = r'/\?img_index=\d+$'
    url = re.sub(pattern, '', url)
    if not url.endswith('/'):
        url += '/'
    print(url+"media/?size=l")
    try:
        # Without proxy
        print("GETTING REQUEST WITH NO PROXY")
        r = requests.get(url+"media/?size=l")
    except:
        # With proxy
        print("GETTING REQUEST WITH PROXY")
        r = requests.get(url+"media/?size=l", proxies={"https": 'http://7KrAOumff6uMdSrF:3UPw4vDCeBOstj7l_streaming-1@geo.iproyal.com:12321'})
    return r.url

#Function to login to facebook
def login_to_facebook():
    #open the webpage
    driver.get("http://www.facebook.com")

    #target username
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

    #enter username and password
    username.clear()
    username.send_keys("leeroyjj86@gmail.com")
    password.clear()
    password.send_keys("PassCode123*")

    #target the login button and click it
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    #We are logged in!


#Function to get facebook link
def get_link_fb  (url):
  driver.get(url)
  driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
  time.sleep(5)
  # imgResults = driver.find_elements(By.XPATH,"//img[@class='x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3']")
  imgResults = driver.find_elements(By.XPATH,"//img[@class='x85a59c x193iq5w x4fas0m x19kjcj4']")
  imgurl = []
  for img in imgResults:
      imgurl.append(img.get_attribute('src'))
  print(imgurl[0])
  return imgurl[0]



#Function to get TikTok link
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
    

# Function to extract the text after "ASSISTANT:"
def extract_after_assistant(text):
    marker = "ASSISTANT: "
    start_index = text.find(marker)
    if start_index != -1:
        # Extract everything after "ASSISTANT: "
        return text[start_index + len(marker):].strip()
    else:
        return 'unspecified'
    
#THE MAIN api Function to perform labeling
def label_imgs(data):
    csv_file_path = '/content/drive/My Drive/Classified_Image2.csv'
    facebook_pattern = re.compile(r'^https?://(?:www\.)?facebook\.com/.*$')
    instagram_pattern = re.compile(r'^https?://(?:www\.)?instagram\.com/.*$')

    results = []

    for index, row in data.iterrows():
        page_url = row['Image_URL']
        image_url = None
        # Check if the URL matches Facebook or Instagram patterns
        try:
            if facebook_pattern.match(page_url):
                image_url = get_link_fb(page_url)
            elif instagram_pattern.match(page_url):
                image_url = get_link_insta(page_url)
            else:
                image_url = get_link_tik(page_url)
        except IndexError:
            print(f"No image found for URL: {page_url}")
        continue  # Skip this iteration if no image is found

        if image_url:
            generated_text = process_image_and_generate_text(image_url)
            # Uncomment the following line once the extract_after_assistant function is defined and ready to use
            # category = extract_after_assistant(generated_text)
            results.append({'Image_URL': page_url, 'GeneratedText': generated_text})
        else:
            print(f"No image URL retrieved for {page_url}")

        # Save (append) every 250 iterations or at the last row
        if (index + 1) % 250 == 0 or (index + 1) == len(data):
            interim_df = pd.DataFrame(results)
            # Append to the CSV, without header if the file already exists
            with open(csv_file_path, 'a') as f:
                interim_df.to_csv(f, header=f.tell()==0, index=False)
            results = []  # Clear results after saving

    # Check if there are any remaining results to save
    if results:
        final_df = pd.DataFrame(results)
        with open(csv_file_path, 'a') as f:
            final_df.to_csv(f, header=f.tell()==0, index=False)