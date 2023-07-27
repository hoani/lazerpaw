from flask import Flask, render_template, Response
import cv2 as cv
import queue
from threading import Thread
import time
import json


app = Flask(__name__)
videoQueue = queue.Queue(maxsize=1)
dataQueue = queue.Queue(maxsize=1)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(videoQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

            
def gen(q):
    while True:
        frame = q.get(block=True, timeout=None)
        ok, frameJpeg = cv.imencode(".jpeg", frame)
        if ok:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frameJpeg.tobytes() + 
                b'\r\n')
            
@app.route('/data_feed')
def data_feed():
    return Response(datagen(dataQueue),
                    mimetype='text/plain')

            
def datagen(q):
    while True:
        data = q.get(block=True, timeout=None)
        yield(data)
                
def run():
    app.run(host='0.0.0.0', port =9090, debug=False, threaded=True)


if __name__ == '__main__':

    flaskThread = Thread(target=run)
    flaskThread.start()

    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        isTrue, frame = cap.read()
        if not isTrue:
            break
        try:
            videoQueue.get_nowait()
        except:
            pass
        videoQueue.put(frame)

        current_time = time.strftime("%H:%M:%S")
        state = "IDLE"
        data = {"time": current_time, "state": state}
        try:
            dataQueue.get_nowait()
        except:
            pass
        dataQueue.put(json.dumps(data)+"\n")



