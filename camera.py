import cv2
import time
import datetime
SECONDS_TO_RECORD_AFTER_DETECTION = 5
capture = cv2.VideoCapture(0) #main camera

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
detection = False
detection_stopped_time = None
timer_started = False
frame_size = (int(capture.get(3)), int(capture.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

while True:
    _, frame  = capture.read()

    #all classifiers require grey scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            out = cv2.VideoWriter("video" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".mp4", fourcc, 20, frame_size)
            print("Recording")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time > SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print("NOT RECORDING")
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    #for (x, y, width, height) in faces:
    #    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord('q'):
        break
out.release()
capture.release()
cv2.destroyAllWindows