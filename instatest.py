import re 
import requests



def truncate_url(url):
    # Find the index of the 5th forward slash
    index = 0
    for _ in range(5):
        index = url.find('/', index + 1)
        if index == -1:
            break
    
    # If there are at least 5 forward slashes, truncate the URL
    if index != -1:
        truncated_url = url[:index + 1]
        return truncated_url
    else:
        return None


def worker(url):
    url = url.replace('reels', 'p')
    url = url.replace('reel', 'p')
    parts = url.split('/')
    url = truncate_url(url)
    print(url)
    if not url.endswith('/'):
        url += '/'
    print(url + "media/?size=l")

    try:
        # Send a GET request without a proxy
        print(f"GETTING REQUEST FOR URL: {url} WITH NO PROXY")
        r = requests.get(url + "media/?size=l")
    except Exception as e:
        # Send a GET request with a proxy if the previous attempt fails
        print(f"GETTING REQUEST FOR URL: {url} WITH PROXY")
        print(f"Error: {e}")
        r = requests.get(
            url + "media/?size=l",
            proxies={
                "https": 'http://7KrAOumff6uMdSrF:3UPw4vDCeBOstj7l_streaming-1@geo.iproyal.com:12321'
            },
        )
    if r.ok:
        print(r.url)
        return r.url
    else:
        print("Failed to retrieve image.")
        return None

# Test the worker function with the provided Instagram URL
worker('https://www.instagram.com/p/C3HviLVug_R/?hl=en&img_index=1')


