import requests
def is_image_link(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            if content_type.startswith('image'):
                return True
    except Exception as e:
        print(f"Error checking image link: {e}")
    return False
