import numpy as np
import mouse
import pyautogui
pyautogui.FAILSAFE = False
import time

class MouseController:
    
    def __init__(self, screen_size, relative_mouse_sensitivity = 0.75, relative_mouse = False, scroll_sensitivity = 0.5):
        self.screen_width, self.screen_height = screen_size
        self.mouse_held = False
        self.just_clicked_left = self.just_clicked_right = self.ctrl_pressed = False
        self.prev_pos, self.prev_pos_time = None, None
        self.hand_speed = 0
        self.relative_mouse = relative_mouse
        self.relative_mouse_sensitivity = relative_mouse_sensitivity
        self.range_x, self.range_y = None, None
        self.scroll_sensitivity = scroll_sensitivity
        self.prev_z = None
        
    def toggle_relative_mouse(self):
        if self.relative_mouse:
            self.relative_mouse = False
        else:
            self.relative_mouse = True
            
    def set_relative_mouse_sensitivity(self, sensitivity):
        self.relative_mouse_sensitivity = sensitivity
        
    def set_scroll_sensitivity(self, sensitivity):
        self.scroll_sensitivity = sensitivity
        
    def move_mouse(self, pos, img_shape):
        if not pos:
            return
        
        if self.prev_pos is None:
            self.prev_pos = pos
            return
        
        if self.range_x is None or self.range_y is None:
            self.range_x = [img_shape[0]*0.35, img_shape[0]*1.1]   
            self.range_y = [img_shape[1]*0.2, img_shape[1]*0.575]
        
        if self.relative_mouse:
            self.__move_mouse_relative(pos)
            return
        else:
            self.__move_mouse_absolute(pos)
        
    def __move_mouse_absolute(self, pos):
        
        x = np.interp(pos[0], (self.range_x[0], self.range_x[1]), (0, self.screen_width))
        y = np.interp(pos[1], (self.range_y[0], self.range_y[1]), (0, self.screen_height))
            
        mouse.move(x, y)
        
    def __move_mouse_relative(self, pos):
        
        x = np.interp(pos[0], (self.range_x[0], self.range_x[1]), (0, self.screen_width))
        y = np.interp(pos[1], (self.range_y[0], self.range_y[1]), (0, self.screen_height))
        
        prev_x = np.interp(self.prev_pos[0], (self.range_x[0], self.range_x[1]), (0, self.screen_width))
        prev_y = np.interp(self.prev_pos[1], (self.range_y[0], self.range_y[1]), (0, self.screen_height))
        
        self.prev_pos = pos
        
        new_x = (x - prev_x) * self.relative_mouse_sensitivity  
        new_y = (y - prev_y) * self.relative_mouse_sensitivity
                
        mouse.move(new_x, new_y, absolute = False)
        
    def reset_mouse_pos(self):
        self.prev_pos = None
        
    def click_mouse(self, button = 'left'):
        just_clicked = False
        if button == 'left':
            just_clicked = self.just_clicked_left
            
        elif button == 'right':
            just_clicked = self.just_clicked_right
            
        else: return
        
        if just_clicked:
            return
        
        mouse.click(button)
        
        if button == 'left':
            self.just_clicked_left = True
        else: self.just_clicked_right = True 
        
    def double_click(self, button = 'left'):
        if button == 'left':
            if not self.just_clicked_left:
                mouse.double_click(button)
                self.just_clicked_left = True
                
        elif button == 'right':
            if not self.just_clicked_right:
                mouse.double_click(button)
                self.just_clicked_right = True
        
    def __press_mouse(self, button = 'left'):
        if not self.mouse_held:
            mouse.press(button)
            self.mouse_held = True
        
    def __release_mouse(self, button = 'left'):
        if self.mouse_held:
            mouse.release(button)
            self.mouse_held = False
            
    def __calculate_speed(self, pos):
        
        prev_x, prev_y = self.prev_pos
        x, y = pos
        
        current_time = time.time()
        
        if self.prev_pos_time is None:
            self.prev_pos_time = current_time
            return 0
        
        elapsed_time = current_time - self.prev_pos_time
                  
        distance_x = abs(x - prev_x)
        distance_y = abs(y - prev_y)
        
        distance = np.sqrt(distance_x ** 2 + distance_y ** 2) 
        
        if elapsed_time <= 0:
            return 0
        
        self.prev_pos_time = current_time
        self.prev_pos = pos
                
        self.hand_speed = distance[0] / elapsed_time
        
        return self.hand_speed
    
    def handle_mouse_press(self, condition, button = 'left'):
        if condition:
            self.__press_mouse(button)
            return True
        else:
            self.__release_mouse(button)
            return False            
        
    def reset_click(self, button = 'both'):
        if button == 'left':
            self.just_clicked_left = False
        elif button == 'right': self.just_clicked_right = False
        else:
            self.just_clicked_left = self.just_clicked_right = False
            
    def reset_zoom(self):
        if self.ctrl_pressed:
            pyautogui.keyUp('ctrl')
            self.ctrl_pressed = False
            self.prev_z = None
            
    def handle_scroll(self, scroll_up = True):
        if scroll_up:
            mouse.wheel(self.scroll_sensitivity)
        else: mouse.wheel(-self.scroll_sensitivity)
        
    def __handle_zoom(self, zoom_in = True):
        if not self.ctrl_pressed:
            pyautogui.keyDown('ctrl')
            self.ctrl_pressed = True
        mouse.wheel(1 if zoom_in else -1)
            
    def handle_zoom(self, current_z):
        if self.prev_z is None:
            self.prev_z = current_z
            return
        
        z_percent_diff = (current_z - self.prev_z)/self.prev_z

        change_threshold = 0.05
        if z_percent_diff > change_threshold:
            self.__handle_zoom(zoom_in=False)
            self.prev_z = current_z
        elif z_percent_diff < -change_threshold:
            self.__handle_zoom(zoom_in=True) 
            self.prev_z = current_z
          