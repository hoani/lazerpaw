from flask import Flask, render_template, Response, request
import cv2 as cv
import queue
from threading import Thread
from typing import Callable


app = Flask(__name__)
videoQueue = queue.Queue(maxsize=1)
procQueue = queue.Queue(maxsize=1)

startCb = lambda _: _
stopCb = lambda _: _
lazerTesterCb = lambda _: _
shutdownCb = lambda _: _
thresholdCb = lambda _: _

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    if "once" in request.args.keys():
        return Response(gen_single(videoQueue),mimetype='image/jpeg; boundary=frame')
    return Response(gen(videoQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/proc_feed')
def proc_feed():
    return Response(gen(procQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/button')
def button():
    try:
        if "start" in request.args.keys():
            print("start triggered")
            startCb()
        if "stop" in request.args.keys():
            print("stop triggered")
            stopCb()
        if "lazer" in request.args.keys():
            if request.args.get("lazer") == "on":
                print("lazer on")
                lazerTesterCb(True)
            else:
                print("lazer off")
                lazerTesterCb(False)
        if "shutdown" in request.args.keys():
            print("shutdown triggered")
            shutdownCb()
    except:
        pass
    return ""

@app.route('/videoclick', methods=["POST"])
def video_click():
    print(request.form)
    x = request.form.get("x", type=int)
    y = request.form.get("y", type=int)
    print("video pressed: x =", x, " y =", y)
    return ""

@app.route('/manual', methods=["POST"])
def manual_click():
    if request.form.get("manual") == 'true':
        print("manual mode")
    else:
        print("manual disabled")
    return ""

@app.route('/threshold', methods=["POST"])
def threshold_click():
    try:
        value = request.form.get("value")
        print("threshold value", value)
        thresholdCb(int(value))
    except:
        pass
    return ""
            
def gen(q):
    while True:
        jpegBytes = gen_single(q)
        if jpegBytes is not None:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                jpegBytes + 
                b'\r\n')
            
def gen_single(q):
    frame = q.get(block=True, timeout=None)
    ok, frameJpeg = cv.imencode(".jpeg", frame)
    if ok:
        return frameJpeg.tobytes()
    return None
            
def start():
    def run():
        app.run(host='0.0.0.0', port =9090, debug=False, threaded=True)
    flaskThread = Thread(target=run, daemon=True)
    flaskThread.start()
    return flaskThread

def update_video(frame):
    update_queue(videoQueue, frame.copy())

def update_proc(frame):
    update_queue(procQueue, frame.copy())

def update_queue(queue, item):
    try:
        queue.get_nowait()
    except:
        pass
    queue.put(item)

def set_start_cb(fn: Callable[[None],None]):
    global startCb
    startCb = fn

def set_stop_cb(fn: Callable[[None],None]):
    global stopCb
    stopCb = fn

def set_lazer_tester_cb(fn: Callable[[bool],None]):
    global lazerTesterCb
    lazerTesterCb = fn

def set_shutdown_cb(fn: Callable[[None],None]):
    global shutdownCb
    shutdownCb = fn

def set_threshold_cb(fn: Callable[[int],None]):
    global thresholdCb
    thresholdCb = fn


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
            update_video(frame)

            grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            update_proc(grey)
    except KeyboardInterrupt:
        cap.release()
        pass
