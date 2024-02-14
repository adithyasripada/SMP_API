import re
import facebook_scraper as fs

def get_link_fb(url):
    pattern = r'\d+'
    numbers = re.findall(pattern, url)
    if len(numbers) >= 2:
        POST_ID = f"{numbers[0]}_{numbers[1]}"
    gen = fs.get_posts(post_urls=[POST_ID], credentials={'garyenglandd@gmail.com','Password12345*'})
    post = next(gen)
    if post['image_lowquality'] is not None:
        return post['image_lowquality']
    else: return None
