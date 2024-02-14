import pandas as pd

def parse_csv(file):
    # Load data from CSV
    data = pd.read_csv(file)
    # Extract URLs from the 'Image_URL' column
    urls = [row['Image_URL'] for index, row in data.iterrows()]
    result_urls = urls#concurrent_get_links(urls)
    return result_urls