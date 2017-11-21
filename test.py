# imports, don't touch them lol
import cv2
import os
import numpy as np
import functions as f
import stereovision as sv

# ---------------------------------------------------------------------------

# obvious variable name for the dataset directory
dataset_path = "dataset";

# optional edits (if needed)
directory_to_cycle_left = "left-images";
directory_to_cycle_right = "right-images";

# set to timestamp to skip forward to, optional (empty for start)
# e.g. set to 1506943191.487683 for the end of the Bailey, just as the vehicle turns
skip_forward_file_pattern = "";

# ---------------------------------------------------------------------------

# resolve full directory location of data set for left / right images
path_dir_l =  os.path.join(dataset_path, directory_to_cycle_left);
path_dir_r =  os.path.join(dataset_path, directory_to_cycle_right);

# get a list of the left image files and sort them (by timestamp in filename)
filelist_l = sorted(os.listdir(path_dir_l));


# Start the loop
filename_l = "1506942475.481834_L.png"
# filename_l = "1506943132.486155_L.png"

options = {
    'crop_disparity' : False, # display full or cropped disparity image
    'pause_playback' : False, # pause until key press after each image
    'max_disparity' : 256,
    'ransac_trials' : 500,
    'loop' : False,
    'point_threshold' : 0.04
}
# setup the disparity stereo processor to find a maximum of 128 disparity values
# (adjust parameters if needed - this will effect speed to processing)



# # from the left image filename get the correspondoning right image
imageStores = f.loadImages(filename_l, path_dir_l, path_dir_r)
if imageStores != False:
    imgL, imgR = imageStores
    imgL = sv.performStereoVision(imgL, imgR, options)
    
    cv2.imshow('left image',imgL)

    # print the following.
    # filename_L.png
    # filename_R.png : road surface normal (a, b, c)

    cv2.waitKey(0);
else:
    print("-- files skipped (perhaps one is missing or not PNG)");


# close all windows
cv2.destroyAllWindows()