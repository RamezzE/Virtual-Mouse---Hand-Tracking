from kivy.clock import Clock
import cv2
from model.GestureDetectionModel import GestureDetetctionModel as Model

class GestureDetectionPresenter:
    def __init__(self, view):
        self.model = Model(self.on_dependencies_loaded)
        self.view = view
        
        self.dependencies_loaded = False
        self.saving_settings = False
        
        Clock.schedule_interval(self.update, 0)
        
    def on_dependencies_loaded(self):
        self.dependencies_loaded = True
        Clock.schedule_once(self.update_status, 0)

    def update_status(self, dt = 0):
        if not self.dependencies_loaded:
            self.view.show_loading("Loading dependencies...")
        elif self.saving_settings:
            self.view.show_loading("Saving settings...")
        else:
            self.view.hide_loading("Press the toggle button\n to start/stop camera feed")

    def update(self, dt):
        self.update_status()
        self.view.update_fps(int(Clock.get_rfps()))

        if not self.view.camera.running or not self.dependencies_loaded:
            return  

        frame = self.view.camera.get_latest_frame()
        
        if frame is not None:
            frame = cv2.flip(frame, 1)
            frame = self.model.HD.findHands(img=frame, drawConnections=True)
            landmarks = self.model.HD.getLandmarks()
            
            if landmarks:
                prediction = self.model.GP.predict(landmarks)
                frame = self.model.handle_input(prediction, frame)

            self.view.show_frame(frame)
            
    def update_settings(self):
        self.model.update_settings()