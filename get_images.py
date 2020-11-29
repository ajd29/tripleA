import boto3
import io
from PIL import Image

s3 = boto3.resource('s3')

# open image given specific key
def image_from_s3(bucket, key):
    image = bucket.Object(key)
    img_data = image.get().get('Body').read()

    return Image.open(io.BytesIO(img_data))

bucket = s3.Bucket('goes-nc-files') # connect to s3 bucket

"""
about goes-nc-files bucket save_directory

goes-nc-files/{year - either 2017,2018,2019, or 2020}/{type - always color}/{mode - either m3,m4,m6}
2017 and 2018 have m3 and m4
2019 has m3,m4, and m6
2020 has m4 and m6

to get images for 2017
files = bucket.objects.filter(Prefix='2017/color/')
"""

files = bucket.objects.filter(Prefix='2017/color/m3') # specify 2017/color/m3 folder

image_data = []

# put all image strings in list, image_data
for file in files.all():
    image = file.key
    image_data.append(image)

# opens first image in image_data
# this will print out the image
image_from_s3(bucket,image_data[0])

# save first image in image_data to variable
img = image_from_s3(bucket,image_data[0])

# get size of image
img.size
