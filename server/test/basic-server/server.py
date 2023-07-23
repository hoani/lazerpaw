from flask import Flask, render_template, Response
import cv2 as cv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(capture):
    while True:
        isTrue, frame = capture.read()
        if not isTrue:
            break
        ok, frameJpeg = cv.imencode(".jpeg", frame)
        if ok:
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frameJpeg.tobytes() + 
                b'\r\n')

@app.route('/video_feed')
def video_feed():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(cap),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port =9090, debug=True, threaded=True)