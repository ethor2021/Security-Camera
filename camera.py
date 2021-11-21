import cv2
import time
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
#from ffpyplayer.player import MediaPlayer
SECONDS_TO_RECORD_AFTER_DETECTION = 5

class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0) #main camera
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        self.detection = False
        self.detection_stopped_time = None
        self.timer_started = False
        self.frame_size = (int(self.capture.get(3)), int(self.capture.get(4)))
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.imageTaken = False

    def record(self):
        while True:
            _, frame  = self.capture.read()

            #all classifiers require grey scale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            bodies = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) + len(bodies) > 0:
                if self.detection:
                    self.timer_started = False
                else:
                    self.detection = True
                    out = cv2.VideoWriter("video" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".mp4", self.fourcc, 20, self.frame_size)
                    print("Recording")
                    image_name = "image" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
                    cv2.imwrite(image_name, frame)
                    self.send_email(image_name)
            elif self.detection:
                if self.timer_started:
                    if time.time() - self.detection_stopped_time > SECONDS_TO_RECORD_AFTER_DETECTION:
                        self.detection = False
                        self.timer_started = False
                        out.release()
                        print("NOT RECORDING")
                else:
                    self.timer_started = True
                    self.detection_stopped_time = time.time()

            if self.detection:
                out.write(frame)

            #for (x, y, width, height) in faces:
            #    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

            cv2.imshow("Camera: press 'q' to quit", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        out.release()
        self.capture.release()
        cv2.destroyAllWindows

    def send_email(self, image_name):
        with open(image_name, 'rb') as f:
            img_data = f.read()
        file = open('email-info.txt', 'r')
        fromEmail = file.readline()
        toEmail = file.readline()
        gmail_password = file.readline()
        msg = MIMEMultipart()
        msg['Subject'] = 'Security Camera Recording Activated - Face Image Attached'
        msg['From'] = fromEmail
        msg['To'] = toEmail

        text = MIMEText("There has been a person spotted on your security camera. Attached is an image of their face.")
        msg.attach(text)
        image = MIMEImage(img_data, name=os.path.basename(image_name))
        msg.attach(image)

        server = SMTP(host='smtp.gmail.com', port=587)
        server.ehlo()
        server.starttls()
        server.login(fromEmail, gmail_password)
        server.sendmail(fromEmail, toEmail, msg.as_string())
        server.close()

        print('Email Sent')

if __name__ == "__main__":
    cam = Camera()
    cam.record()