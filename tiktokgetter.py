import requests
from PIL import Image
import urllib.request
from moviepy.editor import VideoFileClip
import imghdr

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