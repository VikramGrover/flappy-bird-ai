import os
import pygame

IMG_FOLDER_NAME = "imgs"
IMG_SIZE_MULTIPLIER = 1.3


def load_images():
    """
    Loads all the images from the "imgs" folder in the directory into a python dict
    """
    output = {}
    file_names = [file for file in os.listdir(os.path.join(
        IMG_FOLDER_NAME)) if os.path.isfile(os.path.join(IMG_FOLDER_NAME, file))]

    for name in file_names:
        output[os.path.splitext(name)[0]] = pygame.transform.rotozoom(
            pygame.image.load(os.path.join(IMG_FOLDER_NAME, name)), 0, IMG_SIZE_MULTIPLIER)

    return output
