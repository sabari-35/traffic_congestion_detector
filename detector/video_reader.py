import cv2

class VideoReader:
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
