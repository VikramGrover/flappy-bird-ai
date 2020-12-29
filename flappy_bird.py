import pygame
from constants import *


class FlappyBird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = BIRD_MAX_ROT
    ROTATION_VEL = BIRD_ROT_VEL
    JUMP_VEL = BIRD_JUMP_VEL
    JUMP_VEL_BOOST = BIRD_JUMP_BOOST

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_height = self.y
        self.curr_rotation = 0
        self.jump_tick = 0.0
        self.curr_vel = 0.0
        self.img_tick = 0
        self.img_index = 1
        self.flapping_dir = 0
        self.curr_img = self.IMGS[1]
        self.alive = True

    def jump(self):
        """
        Performs a jump on the bird
        """
        self.curr_vel = self.JUMP_VEL
        self.jump_tick = 0.0
        self.flapping_dir = 1
        self.img_index = 0
        self.img_tick = 0
        self.start_height = self.y

    def move(self):
        """
        Moves the bird horizontally, also takes care of the rotation
        """
        self.jump_tick += 0.01

        self.curr_vel += (GRAVITATIONAL_VEL * self.jump_tick)
        self.curr_vel = min(self.curr_vel, MAX_GRAVITATIONAL_VEL)
        displacement = self.curr_vel * self.jump_tick

        if displacement < 0:
            displacement += self.JUMP_VEL_BOOST

        self.y += displacement

        if displacement < 0:
            # moving up or still above the starting height
            self.curr_rotation = max(self.curr_rotation, self.MAX_ROTATION)
        elif self.curr_rotation > -90:
            # moving down
            self.curr_rotation -= self.ROTATION_VEL

    def draw(self, window):
        """
        Draws the bird onto the window, also handles flapping of wings
        """
        if self.alive:
            self.img_tick += 1

        if self.curr_rotation <= -80:
            # the bird is falling and the bird should not be flapping
            self.img_index = 1
            self.curr_img = self.IMGS[1]
            self.img_tick = 0
        elif (self.img_tick % BIRD_WING_FLAP_RATE) == 0 and self.alive:
            # need to switch image
            self.img_tick = 0
            self.img_index += self.flapping_dir
            self.curr_img = self.IMGS[self.img_index]

            if self.img_index <= 0 or self.img_index >= len(self.IMGS) - 1:
                # switch the direction of wing flapping
                self.flapping_dir *= -1

        rot_img = pygame.transform.rotate(self.curr_img, self.curr_rotation)
        centered_rect = rot_img.get_rect(
            center=self.curr_img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rot_img, centered_rect.topleft)

    def image_mask(self):
        """
        Returns the image mask of the FlappyBird
        """
        return pygame.mask.from_surface(self.curr_img)

    def die(self):
        """
        Makes the FlappyBird die
        """
        self.alive = False
        self.curr_vel = 0
        self.curr_img = self.IMGS[1]
