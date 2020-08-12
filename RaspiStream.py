#!/usr/bin/python3
import cv2
import numpy as np
from imutils.video import FPS
import datetime
from flask import Response, Flask
import threading

from picamera.array import PiRGBArray
from picamera import PiCamera

def capture_frames():

    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    #thread_lock = threading.Lock()
    #with threading.Lock():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        #print(image.shape)
        with threading.Lock():
            return_key, encoded_image = cv2.imencode(".jpg", image)
            yield(b"--frame\r\n' b'Content-Type: image/jpg\r\n\r\n" + bytearray(encoded_image) + b"\r\n")

            # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

def run_stream():

    app = Flask(__name__)

    @app.route("/")
    def streamFrames():
        return Response(capture_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    # Create a thread and attach the method that captures the image frames, to it
    process_thread = threading.Thread(target=capture_frames)
    process_thread.daemon = True

    # Start the thread
    process_thread.start()

    # start the Flask Web Application
    # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
    # the host machine's localhost and is discoverable by other machines on the same network
    # app.run("192.168.0.85", port="8091", ssl_context=('cert.pem', 'key.pem'))
    app.run("192.168.0.3", port="8000", threaded=True)

if __name__ == "__main__":
    print("Streamer at: " + __name__)
    run_stream()
