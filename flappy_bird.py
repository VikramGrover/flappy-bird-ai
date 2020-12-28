import random
import time
import pygame
import neat
import os

IMG_FOLDER_NAME = "imgs"
IMG_MULTIPLIER = 1.3


def load_images():
    """
    Loads all the images from the "imgs" folder in the directory into a python dict
    """
    output = {}
    file_names = [file for file in os.listdir(os.path.join(
        IMG_FOLDER_NAME)) if os.path.isfile(os.path.join(IMG_FOLDER_NAME, file))]

    for name in file_names:
        output[os.path.splitext(name)[0]] = pygame.transform.rotozoom(
            pygame.image.load(os.path.join(IMG_FOLDER_NAME, name)), 0, IMG_MULTIPLIER)

    return output


IMG_DICT = load_images()
BIRD_IMGS = [IMG_DICT['fb1'], IMG_DICT['fb2'], IMG_DICT['fb3']]
GROUND_IMG = IMG_DICT['ground']
PIP_IMG = IMG_DICT['pipe']
SCENE_IMG = IMG_DICT['scene']
WINDOW_WIDTH = SCENE_IMG.get_width()
WINDOW_HEIGHT = SCENE_IMG.get_height()
FRAMERATE = 60


class FlappyBird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VEL = 20
    ANIMATION_TIME = 5
    JUMP_VEL = -9.8
    MAX_VEL = 9.8

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_height = self.y
        self.curr_rotation = 0
        self.jump_tick = 0.0
        self.curr_vel = 0.0
        self.img_tick = 0
        self.img_index = 0
        self.flapping_dir = 1
        self.curr_img = self.IMGS[0]
        print(self.IMGS)

    def jump(self):
        """
        Performs a jump on the bird
        """
        self.curr_vel = self.JUMP_VEL
        self.jump_tick = 0.0
        self.start_height = self.y

    def move(self):
        """
        Moves the bird from the main game loop
        """
        self.jump_tick += 0.1

        displacement = self.curr_vel * self.jump_tick
        self.curr_vel += (0.5 * self.jump_tick)
        self.curr_vel = min(self.curr_vel, self.MAX_VEL)

        self.y += displacement

        if displacement < 0 or self.y < self.start_height + 50:
            # moving up or still above the starting height
            self.curr_rotation = max(self.curr_rotation, self.MAX_ROTATION)
        elif self.curr_rotation > -90:
            # moving down
            self.curr_rotation -= self.ROTATION_VEL

    def draw(self, window):
        """
        Draws the bird onto the window, handles rotation and flapping of wings
        """
        self.img_tick += 1

        if self.curr_rotation <= -80:
            # the bird is falling and the bird should not be flapping
            self.img_index = 1
            self.curr_img = self.IMGS[1]
            self.img_tick = 0
        elif (self.img_tick % self.ANIMATION_TIME) == 0:
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
        return pygame.mask.from_surface(self.curr_img)


def draw_game(bird, window):
    """
    Draws the whole screen
    """
    window.blit(SCENE_IMG, (0, 0))
    bird.draw(window)
    pygame.display.update()


def main():
    """
    Main function that has the game loop and calls draw function
    """

    flappy_bird = FlappyBird(
        WINDOW_WIDTH//2 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2)
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    ticker = pygame.time.Clock()

    running = True
    # main game loop
    while running:
        ticker.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flappy_bird.jump()

        flappy_bird.move()
        draw_game(flappy_bird, window)

    pygame.quit()
    quit()


# calling main function
main()
