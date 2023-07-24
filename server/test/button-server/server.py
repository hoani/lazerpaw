from flask import Flask, render_template, Response, request
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
    return Response(gen(videoQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/proc_feed')
def proc_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(procQueue),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/button')
def button():
    print("button pressed")
    return ""

@app.route('/videoclick', methods=["POST"])
def videoclick():
    print("video pressed", request.form)
    return ""


            
def gen(q):
    while True:
        frame = q.get(block=True, timeout=None)
        ok, frameJpeg = cv.imencode(".jpeg", frame)
        if ok:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frameJpeg.tobytes() + 
                b'\r\n')
                
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

        grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        try:
            procQueue.get_nowait()
        except:
            pass
        procQueue.put(grey)



