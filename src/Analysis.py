from src.Configs import Configs

import cv2
import numpy as np

class Analysis(Configs):

    def __init__(self):
        pass
    
    def main_analysis(self, image):
        # make some frame analysis...
        image = cv2.blur(image, (5, 5))
        
        # returning goes by reference anyway
        return image