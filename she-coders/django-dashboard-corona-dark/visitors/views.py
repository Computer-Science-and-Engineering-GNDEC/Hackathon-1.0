import argparse
import datetime
import imutils
import math
import cv2
import numpy as np
import ipdb
from django.shortcuts import render, redirect


def visitor(request):
    
    width = 800

    textIn = 0
    textOut = 0
    camera = cv2.VideoCapture("/home/don/Hackathon-1.0/she-coders/django-dashboard-corona-dark/visitors/test2.mp4")

    firstFrame = None

    # loop over the frames of the video
    while True:
        # grab the current frame and initialize the occupied/unoccupied
        # text
        (grabbed, frame) = camera.read()
        text = "Unoccupied"

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if not grabbed:
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=width)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            continue

        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        # loop over the contours
        for c in cnts:
            #print(c)
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 12000:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.line(frame, (width // 2, 0), (width, 450), (250, 0, 1), 2)  # blue line
            cv2.line(frame, (width // 2 - 50, 0), (width - 50, 450), (0, 0, 255), 2)  # red line

            rectagleCenterPont = ((x + x + w) // 2, (y + y + h) // 2)
            cv2.circle(frame, rectagleCenterPont, 1, (0, 0, 255), 5)

            x=(x+x+w) //2;
            y = (y+y+h) //2;
            res = -450 * x + 400 * y + 157500
            if ((res >= -550) and (res < 550)):
                    
                textIn += 1
            else:
                pass

            
            resOut = -450 * x + 400 * y + 180000
            if ((resOut >= -550) and (resOut <= 550)):
                textOut += 1
            else:
                pass
                    

            # draw the text and timestamp on the frame

            # show the frame and record if the user presses a key
            # cv2.imshow("Thresh", thresh)
            # cv2.imshow("Frame Delta", frameDelta)
            print('Entered'+str(textIn))
            print('Exit' + str(textOut))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.putText(frame, "In: {}".format(str(textIn)), (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Out: {}".format(str(textOut)), (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.imshow("Security Feed", frame)

    # cleanup the camera and close any open windows
   # camera.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #cv2.waitKey(1)
    context = {
        'textin' : textIn,
        'textout' :textOut
    }
    
    return render(request, 'basic-table.html', context=context)
