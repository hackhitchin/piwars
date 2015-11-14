# import the necessary packages
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading

class LedTrack(object):


    def __init__(self, resolution=(640,480), fps=30, h_flip=True, v_flip=True, thresh_min=240, thresh_max=255):
        # Default class constructor
        self.resolution = resolution # Tuple of X and Y video resolution (320,240) default
        self.fps = fps # Frames per second request in video feed
        self.h_flip = h_flip # Flag set when we want the video feed flipped horizontally
        self.v_flip = v_flip # Flag set when we want the video feed flipped vertically
        self.thresh_min = thresh_min # Min value for pixel thresholding
        self.thresh_max = thresh_max # Max value for pixel thresholding
        self.max_tracked_gap = 10 # Number of images/frames to ignore before we say not tracked anymore
        self.tracked = False # Flag set when the led has been found in the frame
        self.blob_pixel_pos = 0 # Horizontal pixel of tracked led
        self.blob_pixel_size = 0 # Pixel size of tracked led
        self.camera_h_fov = 53.0 # Horizontal field of view of the Pi camera module
        self.lock = threading.Lock() # Thread locking member variable
        self.thread = None # Handle to camera looping thread
        self.exit = False # Flag set when we want the process to exit
        self.debug = True # Flag set when we want the visual output (note, must be run in X)


    def get_current_led_pos(self):
        # Return tracking status and horizontal position
        # Angle returned is the angle in degrees where middle 
        # of view is 0.0, left is -ve and right is +ve
        tracked = False # Flag denoting whether the blob was found
        angle_in_degs = 0.0 # Angle in degrees, 0.0 is middle of view.
        size = 0 # Blob size in pixels

        # Grab the thread lock
        self.lock.acquire()
        try:
            tracked = self.tracked
            if tracked:
                # Linearly interpolate angle from X pixel position
                ratio = self.blob_pixel_pos / self.resolution[0]
                angle_in_degs = (self.camera_h_fov * ratio) - (self.camera_h_fov/2.0)
                # Estimate distance to LED using blob pixel size
                size = self.blob_pixel_size
        finally:
            self.lock.release()

        # Return tracked state and position
        return tracked, angle_in_degs, size


    def search_image(self, detector, image_original, thresh_min, thresh_max, no_images_since_tracked):
        # Method looks in individual image for the IR LED
        return_value = True # Return False if user has indicated they wish to quit

        # load the image and convert it to grayscale
        image_gray = cv2.cvtColor(image_original, cv2.COLOR_BGR2GRAY)

        # Invert image black to white
        ret,image_gray = cv2.threshold(image_gray, thresh_min, thresh_max, cv2.THRESH_BINARY_INV)

        # Detect blobs on grayscale image
        key_points = detector.detect(image_gray)

        # Grab the thread lock
        self.lock.acquire()
        try:
            # Test whether we found any blobs
            max_key_point_size = 0 # Max blob size in THIS frame.
            tracked = False
            for key_point in key_points:
                tracked = True # Flag set when the led has been found in the frame
                no_images_since_tracked = 0 # Tracked, reset counter
                if max_key_point_size < key_point.size:
                    self.blob_pixel_pos = key_point.pt[0] # Horizontal pixel of tracked led
                    self.blob_pixel_size = key_point.size # Pixel size of tracked led
                    max_key_point_size = key_point.size # Remember largest blob size

            # If not tracked, count number of frames since last found
            if not tracked:
                no_images_since_tracked = no_images_since_tracked+1
                # If not tracked in a set number of images, reset tracked to False
                if no_images_since_tracked >= self.max_tracked_gap:
                    self.tracked = False # effectively lost tracking
            else:
                # We found it, so flag it as tracked
                self.tracked = True

            if self.debug:
                # Draw detected blobs as red circles.
                # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
                key_point_colour = (0,0,255)
                image_key_points = cv2.drawKeypoints(image_gray, key_points, np.array([]), key_point_colour, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

                # Show keypoints
                cv2.imshow("Keypoints", image_key_points)
                cv2.imshow("Original", image_original)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q") or key == ord("Q"):
                    self.exit = True

            if self.exit == True:
                return_value = False
        finally:
            # Release the thread lock
            self.lock.release()
        return return_value,no_images_since_tracked


    def tracking_loop(self):
        # Main tracking loop. Each frame is searched for a particular IR LED.
        # If found, we store its position in member variables ready for another 
        # module to ask this module for the current LED position.

        # Initialize the camera
        camera = PiCamera()

        # Initialise the default thresholding values
        thresh_min = 240
        thresh_max = 255
        # Grab the thread lock
        self.lock.acquire()
        try:
            # Set the camera parameters/properties
            camera.hflip = self.h_flip
            camera.vflip = self.v_flip
            camera.resolution = self.resolution
            camera.framerate = self.fps
            # Grab a reference to the raw camera capture
            raw_capture = PiRGBArray(camera, size=self.resolution)
            # Grab the thresholding values ready for repeated use
            thresh_min = self.thresh_min
            thresh_max = self.thresh_max
        finally:
            # Release the thread lock
            self.lock.release()

        # allow the camera to warmup
        time.sleep(0.1)

        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 10;
        params.maxThreshold = 200;

        # Filter by Area.
        params.filterByArea = True
        params.minArea = 10
        params.maxArea = 150

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.1

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.87

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.2

        # Create simple Blob Detector with parameter list
        detector = cv2.SimpleBlobDetector_create(params)

        # Remember number of frames since last successful track
        no_images_since_tracked = 0

        # capture frames from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image
            image_original = frame.array

            # Pass original image into searching method
            return_value,no_images_since_tracked = self.search_image(detector, image_original, thresh_min, thresh_max, no_images_since_tracked)

            # clear the stream in preparation for the next frame
            raw_capture.truncate(0)

            # Test whether user wants to quit
            if return_value == False:
                break


    def start_tracker(self):
        # Kick off new thread listening for doorbell events
        self.thread = threading.Thread(target=self.tracking_loop)
        self.thread.start()


    def stop_tracker(self):
        # Stop tracking thread gracefully

        # Grab the thread lock
        self.lock.acquire()
        try:
            # Set member variable True so tracking loop quits
            self.exit = True
        finally:
            self.lock.release()


if __name__ == '__main__':
    # If this module is run independantly, simply instantiate 
    # the tracker class and kick off its tracking loop.
    tracker = LedTrack()
    tracker.start_tracker()

    # Loop set number of times
    for n in range(0,10):
        # Sleep for a second
        time.sleep(1.0)
        tracked,angle_in_degs,size = tracker.get_current_led_pos()
        if tracked:
            print("size = " + str(size) + "Angle = " + str(angle_in_degs))
        else:
            print("Not found")

    tracker.stop_tracker()

