import pygame
import random
from constants import *


class PipePair:
    GAP = PIPE_GAP
    VELOCITY = GROUND_AND_PIPE_VELOCITY
    TOP_PIPE_IMG = pygame.transform.flip(PIP_IMG, False, True)
    BOTTOM_PIPE_IMG = PIP_IMG

    def __init__(self, x):
        self.x = x
        self.height = random.randrange(50, 350)
        self.top = self.height - self.TOP_PIPE_IMG.get_height()
        self.bottom = self.height + self.GAP
        self.passed = False

    def move(self):
        """
        Moves the PipePair at a set velocity
        """
        self.x -= self.VELOCITY

    def draw(self, window):
        """
        Draws the PipePair
        """
        window.blit(self.TOP_PIPE_IMG, (self.x, self.top))
        window.blit(self.BOTTOM_PIPE_IMG, (self.x, self.bottom))

    def collision(self, bird):
        """
        Detects collisions between bird and a PipePair
        """
        bird_img_mask = bird.image_mask()
        top_pipe_mask = pygame.mask.from_surface(self.TOP_PIPE_IMG)
        bottom_pipe_mask = pygame.mask.from_surface(self.BOTTOM_PIPE_IMG)

        if ((bird.x + bird.IMGS[0].get_width()) - self.x) >= 0 and (bird.y + bird.IMGS[0].get_height()) < 0:
            # player is trying to bypass the pipes from the top
            return True

        bird_top_pipe_offset = (self.x - bird.x, self.top - round(bird.y))
        bird_bottom_pipe_offset = (
            self.x - bird.x, self.bottom - round(bird.y))

        top_overlap = bird_img_mask.overlap(
            top_pipe_mask, bird_top_pipe_offset)
        bottom_overlap = bird_img_mask.overlap(
            bottom_pipe_mask, bird_bottom_pipe_offset)

        return (top_overlap or bottom_overlap)
