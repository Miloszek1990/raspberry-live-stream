from src.Configs import Configs
from src.Analysis import Analysis

import threading

import cv2
import flask
import picamera
import picamera.array

class Streamer(Configs):

    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.videoResolution
        self.camera.framerate = self.frameRate
        self.analysis = Analysis()

    def captureFrames(self):

        rawCapture = picamera.array.PiRGBArray(self.camera, size=self.videoResolution)
        frames = self.camera.capture_continuous(rawCapture, format=self.videoFormat, use_video_port=True)
        
        for i, frame in enumerate(frames):
            print(i)
            image = frame.array
            image = self.analysis.main_analysis(image)
            
            with threading.Lock():
                return_key, encoded_image = cv2.imencode(self.videoEncoding, image)
                yield(b"--frame\r\n' b'Content-Type: image/jpg\r\n\r\n" + bytearray(encoded_image) + b"\r\n")
            
            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)

    def runStream(self):

        app = flask.Flask(__name__)

        @app.route("/")
        def streamFrames():
            return flask.Response(self.captureFrames(), mimetype="multipart/x-mixed-replace; boundary=frame")

        process_thread = threading.Thread(target=self.captureFrames)
        process_thread.daemon = True
        process_thread.start()

        # the host machine's localhost and is discoverable by other machines on the same network
        # app.run("192.168.0.85", port="8091", ssl_context=('cert.pem', 'key.pem'))
        app.run(self.RaspberryIP, port=self.port, threaded=True)