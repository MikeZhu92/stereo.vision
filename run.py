"""
Task Specification – Road Surface Region Detection

    You are required develop to road surface detection system that correctly detects the 3D planar orientation and bounds (i.e. edges) of any free (unoccupied) road surface region immediately in- front of the vehicle in which the autonomous vehicle needs to operate (e.g. for staying in the correct lane / staying on the road itself / avoiding obstacles / automatic braking).

    In constructing your solution you may wish to consider the following aspects of your design:
    • exploring the optimization of the provided stereo vision algorithm in use and its operation and hows its performance under varying illumination conditions could perhaps be improved using the HSV or other colour spaces covered in CS SM L2 - Image Processing (these paper also presents an interesting research approach [1,2], others solutions exist also for illumination invariant colour spaces; use these as a starting point for your search).

    • selection of a region of interest, possibly adaptively, within the image (including possibly areas of road, pavement, other or not) that represents the region directly in-front of the vehicle and how to deal with the problem of missing disparity (depth) values in that region.

    • Calculating the equation of a plane from 3 points in 3D: http://mathworld.wolfram.com/Plane.html

    [Further hint: for this assignment this can be done in full projected floating-point 3D space (X,Y, Z)or in integer image space (x,y,disparity) – see provided hints python file]

    Your solution must use a RANdom SAmple and Consensus (RANSAC) approach to perform the detection of the 3D plane in front of the vehicle (when and where possible). For the avoidance of doubt, no credit will be given for a 2D solution based on the built-in Hough Transform or Douglas- Pecker contour detection in OpenCV or that does not recover the 3D parameters of the plane.

    Additionally, some example images may not have significant noise-free disparity (depth) available in front of the vehicle or the road region may be partially occluded by other objects (people, vehicles etc.). The road surface itself will change in terrain type, illumination conditions and road markings – ideally your solution should be able to cope with all of these. Road edges may or may not be marked by line markings in the colour image. All examples will contain a clear front facing view of the road in front of the vehicle only – your system should report all appropriate road surface plane instances it can detect recognising this may not be possible for all cases within the data set provided.
"""

# imports, don't touch them lol
import cv2
import os
import random
import numpy as np
import extra as ex
import csv
import functions as f

# ---------------------------------------------------------------------------

# obvious variable name for the dataset directory
dataset_path = "dataset";

# optional edits (if needed)
directory_to_cycle_left = "left-images";
directory_to_cycle_right = "right-images";

# set to timestamp to skip forward to, optional (empty for start)
# e.g. set to 1506943191.487683 for the end of the Bailey, just as the vehicle turns
skip_forward_file_pattern = "";

# display full or cropped disparity image
crop_disparity = False;
# pause until key press after each image
pause_playback = False;


#####################################################################

# resolve full directory location of data set for left / right images

full_path_directory_left =  os.path.join(dataset_path, directory_to_cycle_left);
full_path_directory_right =  os.path.join(dataset_path, directory_to_cycle_right);

# get a list of the left image files and sort them (by timestamp in filename)

left_file_list = sorted(os.listdir(full_path_directory_left));

# setup the disparity stereo processor to find a maximum of 128 disparity values
# (adjust parameters if needed - this will effect speed to processing)
max_disparity = 32;
stereoProcessor = cv2.StereoSGBM_create(0, max_disparity, 21);

# Start the loop
try:
    for filename_left in left_file_list:
        """
        Here we'll cycle through the files, and finding each stereo pair.
        We'll then process them to detect the road surface planes, and compute 
        the stereo disparity.
        """

        # skip forward to start a file we specify by timestamp (if this is set)
        if ((len(skip_forward_file_pattern) > 0) and not(skip_forward_file_pattern in filename_left)):
            continue;
        elif ((len(skip_forward_file_pattern) > 0) and (skip_forward_file_pattern in filename_left)):
            skip_forward_file_pattern = "";

        # from the left image filename get the correspondoning right image

        filename_right = filename_left.replace("_L", "_R");
        full_path_filename_left = os.path.join(full_path_directory_left, filename_left);
        full_path_filename_right = os.path.join(full_path_directory_right, filename_right);

        # check the file is a PNG file (left) and check a correspondoning right image actually exists

        if ('.png' in filename_left) and (os.path.isfile(full_path_filename_right)) :

            # read left and right images and display in windows
            # N.B. despite one being grayscale both are in fact stored as 3-channel
            # RGB images so load both as such

            imgL = cv2.imread(full_path_filename_left, cv2.IMREAD_COLOR)
            imgR = cv2.imread(full_path_filename_right, cv2.IMREAD_COLOR)

            # for sanity print out these filenames
            print(full_path_filename_left);
            print(full_path_filename_right);
            print();

            # ● Furthermore, for each image file it encounters in the directory listing it must display the following to standard output:
                # filename_L.png
                # filename_R.png : road surface normal (a, b, c)


            # where “filename” is the current image filename and (a, b, c) are the normalized surface normal coefficients of the road plane that has been detected. When no road plane region can be detected output a zero vector. Your final program must run through all the files as a “batch” without requiring a user key press or similar.

            print("-- files loaded successfully");
            print();

            # remember to convert to grayscale (as the disparity matching works on grayscale)
            # N.B. need to do for both as both are 3-channel images

            grayL = cv2.cvtColor(imgL,cv2.COLOR_BGR2GRAY);
            grayR = cv2.cvtColor(imgR,cv2.COLOR_BGR2GRAY);

            # compute disparity image from undistorted and rectified stereo images that we have loaded
            # (which for reasons best known to the OpenCV developers is returned scaled by 16)

            disparity = stereoProcessor.compute(grayL,grayR);

            # filter out noise and speckles (adjust parameters as needed)

            dispNoiseFilter = 5; # increase for more agressive filtering
            cv2.filterSpeckles(disparity, 0, 4000, max_disparity - dispNoiseFilter);

            # scale the disparity to 8-bit for viewing
            # divide by 16 and convert to 8-bit image (then range of values should
            # be 0 -> max_disparity) but in fact is (-1 -> max_disparity - 1)
            # so we fix this also using a initial threshold between 0 and max_disparity
            # as disparity=-1 means no disparity available

            _, disparity = cv2.threshold(disparity,0, max_disparity * 16, cv2.THRESH_TOZERO);
            disparity_scaled = (disparity / 16.).astype(np.uint8);

            # crop disparity to chop out left part where there are with no disparity
            # as this area is not seen by both cameras and also
            # chop out the bottom area (where we see the front of car bonnet)

            if (crop_disparity):
                width = np.size(disparity_scaled, 1);
                disparity_scaled = disparity_scaled[0:390,135:width];

            # display image (scaling it to the full 0->255 range based on the number
            # of disparities in use for the stereo part)

            cv2.imshow("disparity", (disparity_scaled * (256. / max_disparity)).astype(np.uint8));


            # project to a 3D colour point cloud (with or without colour)

            # ● When the road surface plane are detected within a stereo image it must display a red polygon on the left (colour) image highlighting where the road plane has been detected as shown in Figure 1 (see the drawing examples in the OpenCV Python Lab exercises).

            points = f.project_disparity_to_3d(disparity_scaled, max_disparity, imgL);

            # write to file in an X simple ASCII X Y Z format that can be viewed in 3D
            # using the on-line viewer at http://lidarview.com/
            # (by uploading, selecting X Y Z format, press render , rotating the view)

            point_cloud_file = open('3d_points.txt', 'w');
            csv_writer = csv.writer(point_cloud_file, delimiter=' ');
            csv_writer.writerows(points);
            point_cloud_file.close();

            # select a random subset of the 3D points (4 in total)
            # and them project back to the 2D image (as an example)

            pts = f.project_3D_points_to_2D_image_points(random.sample(points, 4));
            pts = np.array(pts, np.int32);
            pts = pts.reshape((-1,1,2));

            cv2.polylines(imgL,[pts],True,(0,255,255), 3);

            cv2.imshow('left image',imgL)
            cv2.imshow('right image',imgR)

            # ● For the purposes of this assignment when a road has either curved road edges or other complexities due to the road configuration (e.g. junctions, roundabouts, road type, occlusions) report and display the road boundaries as far as possible using a polygon or an alternative pixel-wise boundary.

            # You may use any heuristics you wish to aid/filter/adjust your approach but RANSAC must be central to the detection you perform.

            # ● Your program must compile and work with OpenCV 3.3 on the lab PCs.
            ex.handleKey(cv2, pause_playback, disparity_scaled, imgL, imgR, crop_disparity)
        else:
            print("-- files skipped (perhaps one is missing or not PNG)");

except Exception as error:
    print("Exception:", error)
# close all windows

cv2.destroyAllWindows()