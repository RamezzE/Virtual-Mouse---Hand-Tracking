from presenters import CameraPresenter as Camera
from db.db import Database
import numpy as np
import yaml 

with open('paths.yaml', 'r') as f:
    paths = yaml.safe_load(f)
class SettingsModel:
    def __init__(self):
        self.db = Database(paths['db']['actions'], paths['db']['schema'])

    def get_actions(self):
        return (np.array(self.db.get('Actions', columns_to_select='name'))).reshape(-1)

    def get_mappings(self):
        return np.array((self.db.get('Mappings', columns_to_select='action_id'))).reshape(-1)

    def get_last_used_camera(self):
        return self.db.get('CameraSettings', columns_to_select=['value'], name='Camera')[0]

    def get_detection_confidence(self):
        return float(self.db.get('DetectionSettings', columns_to_select=['value'], name='Detection Confidence')[0])

    def get_tracking_confidence(self):
        return float(self.db.get('DetectionSettings', columns_to_select=['value'], name='Tracking Confidence')[0])

    def get_detection_responsiveness(self):
        return int(self.db.get('DetectionSettings', columns_to_select=['value'], name='Detection Responsiveness')[0])
    
    def get_relative_mouse_sensitivity(self):
        return float(self.db.get('MouseSettings', columns_to_select=['value'], name='Relative Mouse Sensitivity')[0])
    
    def get_relative_mouse(self):
        return int(self.db.get('MouseSettings', columns_to_select=['value'], name='Relative Mouse')[0])
    
    def get_scroll_sensitivity(self):
        return float(self.db.get('MouseSettings', columns_to_select=['value'], name='Scroll Sensitivity')[0])
    
    def update_detection_confidence(self, value):
        self.db.update('DetectionSettings', {'value': value}, name='Detection Confidence')

    def update_tracking_confidence(self, value):
        self.db.update('DetectionSettings', {'value': value}, name='Tracking Confidence')

    def update_gesture_mappings(self, gesture_id, action_id):
        self.db.update('Mappings', {'action_id': action_id}, gesture_id=gesture_id)
        
    def update_detection_responsiveness(self, value):
        self.db.update('DetectionSettings', {'value': value}, name='Detection Responsiveness')
        
    def update_relative_mouse_sensitivity(self, value):
        self.db.update('MouseSettings', {'value': value}, name='Relative Mouse Sensitivity')
        
    def update_relative_mouse(self, value):
        self.db.update('MouseSettings', {'value': value}, name='Relative Mouse')
        
    def update_scroll_sensitivity(self, value):
        self.db.update('MouseSettings', {'value': value}, name='Scroll Sensitivity')
        
    def get_available_cameras(self, max_cameras = 5):
        return np.array(Camera.get_available_cameras(max_cameras))