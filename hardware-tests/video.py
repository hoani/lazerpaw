import cv2 as cv
import time


cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 120)

while True:
    isTrue, frame = cap.read()
    # if cv.waitKey(20) & 0xFF==ord('d'):
    # This is the preferred way - if `isTrue` is false (the frame could 
    # not be read, or we're at the end of the video), we immediately
    # break from the loop. 
    if isTrue:
        start = time.time()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, thres = cv.threshold(gray, 95, 255, cv.THRESH_BINARY)
        cv.imwrite('thres.jpg', thres)
        cv.imwrite('image.jpg', frame)
        end = time.time()
        print(end - start)
        if cv.waitKey(5) & 0xFF==ord('d'):
            break
    else:
        break

cap.release()
cv.destroyAllWindows()
