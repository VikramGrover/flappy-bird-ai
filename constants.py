import os
import pygame
from preprocess import load_images

# images-related global variables
IMG_DICT = load_images()
BIRD_IMGS = [IMG_DICT['fb1'], IMG_DICT['fb2'], IMG_DICT['fb3']]
GROUND_IMG = IMG_DICT['ground']
PIP_IMG = IMG_DICT['pipe']
SCENE_IMG = IMG_DICT['scene']

# environment-related global variables - tweak these to change the environment
GROUND_AND_PIPE_VELOCITY = 2
GROUND_HEIGHT = 50
PIPE_STARTING_DIST = 700
NEW_PIPE_DIST = 10
FRAMERATE = 130
PIPE_GAP = 140
GRAVITATIONAL_VEL = 1.8
MAX_GRAVITATIONAL_VEL = 5.2

# bird-related global variables - tweak these to change bird gameplay
BIRD_ROT_VEL = 1
BIRD_MAX_ROT = 25
BIRD_WING_FLAP_RATE = 5
BIRD_JUMP_VEL = -3.8
BIRD_JUMP_BOOST = -2.7

# window-realted global variables
WINDOW_WIDTH = SCENE_IMG.get_width()
WINDOW_HEIGHT = SCENE_IMG.get_height()
pygame.font.init()
SCORE_FONT = pygame.font.SysFont("arial", 50)
