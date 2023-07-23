from flask import Flask, render_template, Response
import cv2 as cv
import queue
from threading import Thread


app = Flask(__name__)
videoQueue = queue.Queue(maxsize=1)
procQueue = queue.Queue(maxsize=1)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(get_video(videoQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/proc_feed')
def proc_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(procQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def get_video(q):
    while True:
        frame = q.get(block=True, timeout=None)
        cv.circle(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), int(frame.shape[1]/128), (0,255,255), thickness=1)
        ok, frameJpeg = cv.imencode(".jpeg", frame)
        if ok:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frameJpeg.tobytes() + 
                b'\r\n')
            
def gen(q):
    while True:
        frame = q.get(block=True, timeout=None)
        ok, frameJpeg = cv.imencode(".jpeg", frame)
        if ok:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frameJpeg.tobytes() + 
                b'\r\n')
                

def start():
    def run():
        app.run(host='0.0.0.0', port =9090, debug=False, threaded=True)
    flaskThread = Thread(target=run, daemon=True)
    flaskThread.start()
    return flaskThread

def updateVideo(frame):
    updateQueue(videoQueue, frame.copy())

def updateProc(frame):
    updateQueue(procQueue, frame.copy())

def updateQueue(queue, item):
    try:
        queue.get_nowait()
    except:
        pass
    queue.put(item)


if __name__ == '__main__':

    flaskThread = start()
    

    cap = cv.VideoCapture(0)
    try:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

        while True:
            isTrue, frame = cap.read()
            if not isTrue:
                break
            updateVideo(frame)

            grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            updateProc(grey)
    except KeyboardInterrupt:
        cap.release()
        pass



