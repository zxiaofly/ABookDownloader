import time
import requests

def file_downloader(file_path, url):
    headers = {'Proxy-Connection': 'keep-alive'}
    r = requests.get(url, stream=True, headers=headers)
    content_length = float(r.headers['content-length'])
    with open(file_path, 'wb') as file:
        downloaded_length = 0
        last_downloaded_length = 0
        time_start = time.time()
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                file.write(chunk)
                downloaded_length += len(chunk)
                if time.time() - time_start > 1:
                    percentage = downloaded_length / content_length * 100
                    speed = (downloaded_length -
                             last_downloaded_length) / 2097152
                    last_downloaded_length = downloaded_length
                    print("\r Downloading: " + file_path + ': ' + '{:.2f}'.format(
                        percentage) + '% Speed: ' + '{:.2f}'.format(speed) + 'MB/S', end="")
                    time_start = time.time()
    print("\nDownload {} successfully!".format(file_path))
