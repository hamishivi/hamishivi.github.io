'''
Very basic script for uploading images/gifs to imgur. given filepath, uploads and returns link.
combines with notion script to automate my setup
'''
import pyimgur
from secrets import CLIENT_ID

im = pyimgur.Imgur(CLIENT_ID)

def upload_to_imgur(filepath: str, name: str) -> str:
    uploaded_image = im.upload_image(filepath, title=name)
    return uploaded_image.link