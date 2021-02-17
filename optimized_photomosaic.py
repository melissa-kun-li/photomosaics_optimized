from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
from skimage.util import img_as_ubyte
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description = 'Takes in an input photo (.jpg) and a folder of source images (.jpg), creates a photomosaic where each "pixel" is one source image!')
    parser.add_argument('square_pixel', type = int, help = 'A larger value indicates the photomosaic will be made of larger pixels/fewer source images, a smaller value means the sections of the image will be more subdivided and smaller pixels/more source images used.')
    parser.add_argument('input_image', type = str, help = 'The file name of the input image e.g. input.jpg, to turn into a photomosaic.')
    parser.add_argument('output_image', type = str, help = 'The file name of the outputted pixel art/photomosaic e.g. photomosaic.jpg. This will be saved in the program directory.')
    args = parser.parse_args()

    photomosaic(args)

def photomosaic(args):

    start_time = time.time()
    # change this value to affect the size of the photomosaic section! NOTE: smaller size will take longer to render
    square_pixel = args.square_pixel

    my_image = io.imread(args.input_image)

    # NOTE: this is the directory of the source images folder. Future, will let person decide which dir
    photo_dir= './small_photoset/*jpg'

    # dictionary where the keys are the filepaths of the source images, and the values are the loaded source_image
    source_images = {}

    # dictionary where the keys are the filepaths of the source images, and the values are the average rgb values
    source_image_avg_rgb_dict = {}
   
    print('Loading images...')

    # load all the source images (photos you'd like to become the "pixels")
    image_collection = io.imread_collection(photo_dir)

    # iterate through all the source images
    for filepath in image_collection.files:
        source_image = io.imread(filepath)
        # store the square cropped source image into the dictionary source_images with filepath as the key
        source_images[filepath] = square_source_images(source_image)
        img = square_source_images(source_image)
        # store the source image's average rgb value into the dictionary with filepath as key
        source_image_avg_rgb_dict[filepath] = calculate_average_colour(img)

    # this will allow for all the "pixel" squares to fit equally in the frame
    trim_rows = my_image.shape[0] % square_pixel
    trim_columns = my_image.shape[1] % square_pixel
    my_image = my_image[0:my_image.shape[0]-trim_rows, 0:my_image.shape[1]-trim_columns]
    print('Your photo height and width are: ', my_image.shape) # this prints the height and width of your input image, NOTE: if it's >1000 it will be quite slow. Future: I will optimize
    print('Creating your photomosaic! Please wait, this can take up to 5 minutes. If it is not finished after 5 minutes, please resize your photo and/or increase the pixel square size.')
    row = []
    temporary_img = []

    total_iterations = int((my_image.shape[0] / square_pixel) * (my_image.shape[1] / square_pixel))
    iteration = 0

    # this will iterate through each pixel_region and move to the next region by value in square_pixel
    # the photomosaic will be created row by row
    for i in range(0, my_image.shape[0], square_pixel):
        for j in range(0, my_image.shape[1], square_pixel):

            iteration += 1
            print('Iteration', iteration, 'of', total_iterations)

            pixel_region = my_image[i:i+square_pixel, j:j+square_pixel]

            # calculate the average colour of the region in the input image
            pixel_colour = calculate_average_colour(pixel_region)

            # calculate the closest average colour match between input
            best_match = match_colour(pixel_colour, source_image_avg_rgb_dict)

            img = source_images[best_match]

            # resize the best match source image to the size of the square_pixel
            img = resize(img, (square_pixel,square_pixel), anti_aliasing=True)

            # the commented line below can give you a picture where the pixels are the average colour!
            # my_image[i:i+square_pixel, j:j+square_pixel] = pixel_colour
            
            row.append(img)

        temporary_img.append(np.hstack(row))
        row = []
    photomosaic = np.vstack(temporary_img)  

    # converts image to uint8 to suppress the warning that there's lossy conversion
    photomosaic = img_as_ubyte(photomosaic)

    io.imsave(args.output_image, photomosaic)

    total_time = time.time() - start_time
    print(f'Photomosaic created in {total_time}s! Please check this project directory for your image :)')

# calculates the average rgb colour for the source images and input image section
def calculate_average_colour(pixel_region):
    # list turns [1 2 3] to [1, 2, 3] so that I can match avg rgb colours easier
    return(list(np.mean(pixel_region, axis =(0,1))))

# finds the smallest distance between the average colours of the source image and the pixel_region, indicating the best match
def match_colour(pixel_colour, source_image_avg_rgb_dict):
    smallest_distance = None
    best_match = None
    for filepath in source_image_avg_rgb_dict:
        distance = (pixel_colour[0] - source_image_avg_rgb_dict[filepath][0])**2 + (pixel_colour[1] - source_image_avg_rgb_dict[filepath][1])**2 + (pixel_colour[2] - source_image_avg_rgb_dict[filepath][2])**2
        if smallest_distance == None or distance < smallest_distance:
            smallest_distance = distance
            best_match = filepath
    return best_match
        
# this will make the source images into squares
def square_source_images(source_img):
    # crop on the smaller, e.g. if 1280 * 800 pixels, crop to 800 * 800
    # if more rows than columns
    if source_img.shape[0] > source_img.shape[1]:
        crop = source_img.shape[0] - source_img.shape[1]
        new_height = source_img.shape[0] - crop
        source_img = source_img[0:new_height,:]
        return source_img 
    else: # if more columns than rows
        crop = source_img.shape[1] - source_img.shape[0]
        new_width = source_img.shape[1] - crop
        source_img = source_img[:, 0:new_width]
        return source_img

if __name__ == '__main__':
    main()