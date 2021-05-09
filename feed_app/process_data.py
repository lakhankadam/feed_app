import subprocess
from PIL import Image
from s3 import upload_to_s3
import subprocess
import requests

BASE_URL = 'http://lkadambucket.s3-ap-southeast-1.amazonaws.com'
UPLOAD_PREFIX = 'uploads'
VIDEO_FORMATS = ['webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'rrc', 'gifv', 'mng', 'mov', 'avi', 'qt', 'wmv', 'yuv', 'rm', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b']
IMAGE_FORMATS = ['jpg', 'jpeg', 'jpe', 'jif', 'jfif', 'jfi', 'png', 'gif', 'webp', 'tiff', 'tif', 'psd', 'raw', 'arw', 'cr2', 'nrw', 'k25', 'bmp', 'dib', 'svg', 'svgz']

def resize_and_upload_image(file_name,uuid):
    download_path = "/".join([BASE_URL,uuid,file_name])
    path = "/".join(['jobs', file_name])
    im = Image.open(requests.get(download_path, stream=True).raw)
    resized_im = im.resize((round(im.size[0]*0.4), round(im.size[1]*0.4)))
    resized_im.save(path)
    status = upload_to_s3(file_name, uuid, 'jobs')
    print(status)
    subprocess.run(['rm',path])
def resize_and_upload_video(file_name,url):
    return True
def resize_images_and_videos(url):
    file_name, uuid = url.split('/')[-1], url.split('/')[-2]
    extension = file_name.split('.')[1]
    if extension in IMAGE_FORMATS:
        resize_and_upload_image(file_name,uuid)
    
    elif extension in VIDEO_FORMATS:
        resize_and_upload_video(file_name,uuid)