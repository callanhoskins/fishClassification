# Author: Callan Hoskins
# Modified: 12 Mar 2021
# This script scrapes FishBase for pictures.
# If you allow it to run fully, it will collect more than 60k pictures.
# Modify MAX_PAGE, MIN_FAM, MAX_FAM to decrease the number of pictures it collects.

import requests
from bs4 import BeautifulSoup
import os
import errno
import cv2


url_index = 'https://www.fishbase.us/photos/FamilyThumbnailsSummary.php?famcode='
url_photo = 'http://d1iraxgbwuhpbw.cloudfront.net/images/species/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
MAX_PAGE = 595

# Make output directory
output_dir = 'fish_pics'
try:
    os.makedirs(output_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Get names of image from FishBase URL
def get_image_names(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    images = soup.find_all('img')
    img_names = [img['src'].lower() for img in images]
    return [name[name.find('_')+1:] for name in img_names]

# Download and save image
def download_image(species_name, fam_code):
    r = requests.get(url_photo + species_name, headers=headers)
    with open(f'{output_dir}/' + fam_code.zfill(3) + '_' + species_name, 'wb') as f:
        f.write(r.content)


# This function crops the image to be square with its dimensions min(height, width) x min(height, width)
def crop_img(img):
    center = (img.shape[0]//2, img.shape[1]//2)
    half_len = min(center[0], center[1])
    img = img[center[0]-half_len:center[0]+half_len, center[1]-half_len:center[1]+half_len]
    return img

# This function zero-pads the image on the top and bottom so that it's a square
# can change the code to zero-pad it on the side
def zero_pad_img(img):
    height, width, channels = img.shape
    pad_amt = (width - height) // 2
    img = cv2.copyMakeBorder(img, pad_amt, pad_amt, 0, 0, cv2.BORDER_CONSTANT, value=0)
    return img


# Iterate over all families and download raw images to output_dir
for fam_code in range(0, MAX_PAGE):
    fam_code = str(fam_code)
    print('{}: '.format(fam_code), end='')
    img_names = get_image_names(url_index + fam_code)
    for name in img_names:
        download_image(name, fam_code)
        print('*', end='')


# Resize images so that they are square and of size 256x256
# Set MIN_FAM and MAX_FAM to lower runtime of this script and only run it on certain families of fish
MAX_FAM = '370'
MIN_FAM = '349'
OUTPUT_SHAPE = (256, 256)
resized_output_dir = 'resized_fish_pics'
try:
    os.makedirs(resized_output_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

files_paths = os.listdir(output_dir)

for file in files_paths:
    if file <= MAX_FAM and file >= MIN_FAM:
        print(file)
        try:
            image = cv2.imread(f'{output_dir}/{file}')
            image = zero_pad_img(image)
            image = cv2.resize(image, OUTPUT_SHAPE)
            cv2.imwrite(f'{resized_output_dir}/{file}', image)
        except AttributeError as e:
            print(e)

