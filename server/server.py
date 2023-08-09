from flask import Flask, render_template, Response, request
import cv2 as cv
import queue
from threading import Thread
from typing import Callable
import json
import time


app = Flask(__name__)
videoQueue = queue.Queue(maxsize=1)
procQueue = queue.Queue(maxsize=1)
dataQueue = queue.Queue(maxsize=1)

startCb = lambda _: _
stopCb = lambda _: _
lazerTesterCb = lambda _: _
shutdownCb = lambda _: _
thresholdCb = lambda _: _
manualEnCb = lambda _: _
manualCmdCb = lambda _a, _b, _c, _d: None

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    if "once" in request.args.keys():
        return Response(generate_video_frame_once(videoQueue),mimetype='image/jpeg; boundary=frame')
    return Response(generate_video_frame(videoQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/proc_feed')
def proc_feed():
    return Response(generate_video_frame(procQueue),
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
    w = request.form.get("w", type=int)
    h = request.form.get("h", type=int)
    print("video pressed: x =", x, " y =", y)
    manualCmdCb(x, y, w, h)
    return ""

@app.route('/manual', methods=["POST"])
def manual_click():
    if request.form.get("manual") == 'true':
        manualEnCb(True)
        print("manual mode")
    else:
        manualEnCb(False)
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

@app.route('/data_feed')
def data_feed():
    return Response(generate_data_feed(dataQueue),
                    mimetype='text/plain')

            
def generate_data_feed(q):
    while True:
        data = q.get(block=True, timeout=None)
        yield(data)
            
def generate_video_frame(q):
    while True:
        jpegBytes = generate_video_frame_single(q)
        if jpegBytes is not None:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                jpegBytes + 
                b'\r\n')
            
def generate_video_frame_once(q):
    frame = q.get(block=True, timeout=None)
    frame = cv.flip(frame, -1)
    ok, frameJpeg = cv.imencode(".jpeg", frame)
    if ok:
        return frameJpeg.tobytes()
    return None
            
def generate_video_frame_single(q):
    frame = q.get(block=True, timeout=None)
    ok, frameJpeg = cv.imencode(".jpeg", frame)
    if ok:
        return frameJpeg.tobytes()
    return None
            
def start():
    def run():
        app.run(host='0.0.0.0', port =8000, debug=False, threaded=True)
    flaskThread = Thread(target=run, daemon=True)
    flaskThread.start()
    return flaskThread

def update_video(frame):
    update_queue(videoQueue, frame.copy())

def update_proc(frame):
    update_queue(procQueue, frame.copy())

def update_data(data):
    update_queue(dataQueue, json.dumps(data)+"\n")

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

def set_manual_enabled_cb(fn: Callable[[bool],None]):
    global manualEnCb
    manualEnCb = fn

def set_manual_command_cb(fn: Callable[[int, int, int, int],None]):
    global manualCmdCb
    manualCmdCb = fn


if __name__ == '__main__':

    flaskThread = start()
    

    cap = cv.VideoCapture(0)
    try:
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            isTrue, frame = cap.read()
            if not isTrue:
                break
            update_video(frame)

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            start = time.time()
            gray = cv.resize(gray, (80,60), cv.INTER_LINEAR)
            _, masked = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)
            print("deltaT: ", (time.time() - start)*1000)
            update_proc(masked)

            current_time = time.strftime("%H:%M:%S")
            state = "IDLE"
            data = {"time": current_time, "state": state}
            update_data(data)
    except KeyboardInterrupt:
        cap.release()
        pass
