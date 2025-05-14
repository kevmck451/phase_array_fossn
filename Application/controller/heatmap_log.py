from datetime import datetime
import os
from PIL import Image


class Heatmap_Log:
    def __init__(self, save_directory):
        self.save_directory = save_directory
        self.image_counter = 0

    def save_heatmap_image(self, image: Image.Image, reason: str):
        filename = f'heatmap_{self.image_counter}_{reason}.png'
        filepath = os.path.join(self.save_directory, filename)
        image.save(filepath)
        self.image_counter += 1
        return filepath
