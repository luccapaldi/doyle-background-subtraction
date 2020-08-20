# Luc Capaldi
# Reimplement Doyle background subtraction in Python 3.
# - Added multi-channel support.
# - Runs from CL; easily scripted for batches of images.

# if num output files !=  num input files, unspecified output files will be
# given a generated name

# To-Do:
# - add support for varied channel images (e.g. 1 or 4)

# Note: Final image will have width and height 4 pixels smaller than the
#       original due to the noise reduction algorithm.

import argparse
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import matplotlib.animation as animation
import matplotlib
from skimage import io

# Create parser
parser = argparse.ArgumentParser(description="Perform Doyle background subtraction.")
# Required arguments
parser.add_argument("-s", "--source", nargs="*", type=str, help="path to source file")
parser.add_argument("-o", "--output", nargs="*", type=str, help="path to output file")
# Optional arguments
parser.add_argument("-c", "--close", nargs="?", default=True, help="use 3x3 bound (default True)")
parser.add_argument("-f", "--far", nargs="?", default=True, help="use 5x5 bound (default True)")
parser.add_argument("-cs", "--cutoff", type=float, default = 3.00, help="multiple of SD used as cutoff for subtraction")
parser.add_argument("-st", "--stack", nargs="?", default=False, help="specify if source is a tiff image stack")
# Parse arguments
args = parser.parse_args()

# Extract user input
sources = args.source  # input paths
outputs = args.output  # output paths
close = args.close  # Usage of 3x3 bound
far = args.far  # Usage of 5x5 bound
cutoff = args.cutoff  # multiple of SD used as cutoff for the subtraction
is_stack = args.stack

def main(source,filename):
    # Generate output filename as needed
    if outputs == None:
        name = source.split('/')[-1].split('.')[-2]
        suffix = source.split('/')[-1].split('.')[-1]
        filename = name + "-subtracted." + suffix

    img_out = []
    try:
        is_tiff = False
        # Use tifffile to handle tiff image stacks
        if source.lower().endswith(('.tif', '.tiff')):
            is_tiff = True
            sourcefile = tiff.imread(source)
        # Use matplotlib for other file types 
        else:
            #sourcefile = plt.imread(source)
            sourcefile = io.imread(source)

        # Perform background subtraction
        if is_tiff and is_stack:
            # Note: the frames are the first dimension of a tiff image stack
            frames = [] 
            for frame in range(len(sourcefile)):
                #frames.append(process_subtraction(sourcefile[frame][:,:,0]))
                frames.append(process_subtraction(sourcefile[frame]))
                img_out = np.asarray(frames) 
            tiff.imsave(filename, img_out) 
        else:
            img_out = process_subtraction(sourcefile)
            io.imsave(filename, img_out)

    except FileNotFoundError:
        print("'" + source + "' skipped because it does not exist.") 

# Processes multi-channel images for background subtraction
def process_subtraction(img):
    # Display warning for unsupported images
    if img.ndim != 2 and img.ndim != 3:
        print("Error! Only 2- and 3-channel images are supported.")
    else:
        shape = img.shape
        # Iterate over each channel 
        if img.ndim == 3 and shape[2] == 3:  # rgb
            img_subtracted = np.empty([(shape[0] - 4),(shape[1] - 4),3])
            img_subtracted[:,:,0] = subtract_channel(img[:,:,0])
            img_subtracted[:,:,1] = subtract_channel(img[:,:,1])
            img_subtracted[:,:,2] = subtract_channel(img[:,:,2])

        elif img.ndim == 3 and shape[2] == 1: # 3 channel grayscale
            img_subtracted = np.empty([(shape[0] - 4),(shape[1] - 4),1])
            img_subtracted[:,:,0] = subtract_channel(img[:,:,0])

        else:  # 2D grayscale or general 2-channel image
            img_subtracted = np.empty([(shape[0] - 4),(shape[1] - 4)])
            img_subtracted = subtract_channel(img)
    return img_subtracted

# Perform Doyle background subtraction on provided image channel
# Credit for original algorithm implementation in Python 2: Xavier Capaldi
# https://github.com/xcapaldi/imagej_noise-subtract
# Note: assume image is y by x
def subtract_channel(channel):
    # 1. INITIAL SUBTRACTION:
    
    # Cut image into rows of pixels
    rows = [channel[i,:] for i in range(channel.shape[0])]
    height = len(rows)

    # Gather pixels along boundary
    boundary = np.concatenate((rows[0], rows[height - 1]), axis=0).flatten().tolist()
    for r in range(1, height - 1):
        boundary.append(rows[r][0])  # leftmost pixels
        boundary.append(rows[r][-1])  # rightmost pixels

    # Calculate mean and sample SD (sigma) of intensity for boundary pixels
    mean = sum(boundary) / len(boundary) 
    sd = (sum((p - mean) ** 2 for p in boundary) / (len(boundary) - 1)) ** 0.5

    # Subtract mean intensity from each pixel; round negative numbers up to 0
    img_sub = (channel - mean)
    img_sub[img_sub < 0] = 0
    
    # 2. INDIVIDUAL NOISE SPOT REMOVAL:
    # Check the 3x3 and 5x5 regions surrounding the pixel of interest

    #               3x3:                   5x5:
    #          O O O O O O O          O O O O O O O
    #          O O O O O O O          O X X X X X O
    #          O O X X X O O          O X O O O X O
    #          O O X P X O O          O X O P O X O
    #          O O X X X O O          O X O O O X O
    #          O O O O O O O          O X X X X X O
    #          O O O O O O O          O O O O O O O
    
    # Iterate over every pixel, excluding those too close to boundary,
    # and calculate mean intensity
    img_final = img_sub 

    for i, p in np.ndenumerate(img_sub):
        # Ignore boundary pixels
        # Check 3x3 region
        try:
            if close == True:
                mean_close = ((img_sub[i[0] - 1][i[1] - 1]
                             + img_sub[i[0] - 1][i[1]]
                             + img_sub[i[0] - 1][i[1] + 1]
                             + img_sub[i[0]][i[1] - 1]
                             + img_sub[i[0]][i[1] + 1]
                             + img_sub[i[0] + 1][i[1] - 1]
                             + img_sub[i[0] + 1][i[1]]
                             + img_sub[i[0] + 1][i[1] + 1])
                             / 8)

            # Check 5x5 region
            if far == True:
                mean_far = ((img_sub[i[0] - 2][i[1] - 2] 
                           + img_sub[i[0] - 2][i[1] - 1]
                           + img_sub[i[0] - 2][i[1]]
                           + img_sub[i[0] - 2][i[1] + 1]
                           + img_sub[i[0] - 2][i[1] + 2]
                           + img_sub[i[0] - 1][i[1] - 2]
                           + img_sub[i[0] - 1][i[1] + 2]
                           + img_sub[i[0]][i[1] - 2]
                           + img_sub[i[0]][i[1] + 2]
                           + img_sub[i[0] + 1][i[1] - 2]
                           + img_sub[i[0] + 1][i[1] + 2]
                           + img_sub[i[0] + 2][i[1] - 2]
                           + img_sub[i[0] + 2][i[1] - 1]
                           + img_sub[i[0] + 2][i[1]]
                           + img_sub[i[0] + 2][i[1] + 1]
                           + img_sub[i[0] + 2][i[1] + 2])
                            / 16)
        except:
            pass
 
        # If close or far are <(cutoff*sigma), set pixel value to zero
        if (close == True) and (far == True):
            if mean_close < (cutoff * sd) or mean_far < (cutoff * sd):
               img_final[i[0]][i[1]] = 0 

        elif (close == True) and (far == False):
            if mean_close < (cutoff * sd):
               img_final[i[0]][i[1]] = 0 
        
        elif (close == False) and (far == True):
            if mean_far < (cutoff * sd):
               img_final[i[0]][i[1]] = 0 

    # Remove excess pixels on boundary
    shape = img_final.shape
    img_final = np.delete(img_final, [0,1,(shape[0]-1),(shape[0]-2)], axis=0)
    img_final = np.delete(img_final, [0,1,(shape[1]-1),(shape[1]-2)], axis=1)
    img_final = img_final#.astype(int)
    return img_final

# Execute program
try:
    for i in range(len(sources)):
        if outputs == None:
            main(sources[i], None)
        elif i >= len(outputs):
            main(sources[i], None)
            print("More sources than outputs! Excess output files will be \
                   given auto generated names.") 
        else:
            main(sources[i], outputs[i])
except TypeError:
    print("Error! Must specify source file(s).")
