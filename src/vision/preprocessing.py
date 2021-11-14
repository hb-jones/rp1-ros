import cv2
import numpy as np


def crop(frame, topleft, bottomright): #TODO
    #Takes pixel coords of area to crop?
    #Maybe should be set in ROI
    if topleft == (0,0) and bottomright == (0,0):
        return frame
    top = topleft[0]
    left = topleft[1]
    bottom = bottomright[0]
    right = bottomright[1]
    frame[0:,0:left] = 0
    frame[0:top,0:] = 0
    frame[:,right:] = 0
    frame[bottom:,:] = 0
    return frame

def distance_crop(frame, min_dist, max_dist = 0):
    """Keeps area between min and max, distances in mm"""
    if max_dist == 0: #Add max if 0
        max_dist = 60000

    cropped_frame = np.where((frame > max_dist) | (frame <= min_dist), 0, frame)

    return cropped_frame

def mask(frame, mask_lower, mask_upper):
    #Convert to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #  Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv_frame, mask_lower, mask_upper)
    # Bitwise-AND mask and original image
    masked_frame = cv2.bitwise_and(frame,frame, mask= mask)
    return masked_frame

def morph_open(frame, kernal_size = 9):
    kernel = np.ones((kernal_size,kernal_size),np.uint8)
    morphed_frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    return morphed_frame


def morph_close(frame, kernal_size = 40):
    kernel = np.ones((kernal_size,kernal_size),np.uint8)
    morphed_frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
    return morphed_frame


def threshold(frame, blur_kernal_size = 5): 
    gs_masked_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Must be in greyscale colourspace
    blurred_frame = cv2.GaussianBlur(gs_masked_frame, (blur_kernal_size,blur_kernal_size),0)
    ret3,thresh = cv2.threshold(blurred_frame,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return thresh

def stereo_threshold(frame, blur_kernal_size = 5):
    #gs_masked_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Must be in greyscale colourspace
    blurred_frame = cv2.GaussianBlur(frame, (blur_kernal_size,blur_kernal_size),0)
    ret3,thresh = cv2.threshold(blurred_frame,0,2**16-1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return thresh