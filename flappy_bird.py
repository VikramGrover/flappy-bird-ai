import random
import time
import pygame
import neat
import os


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


# images-related global variables
IMG_FOLDER_NAME = "imgs"
IMG_SIZE_MULTIPLIER = 1.3
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


class Ground:
    VELOCITY = GROUND_AND_PIPE_VELOCITY
    WIDTH = GROUND_IMG.get_width()
    IMG = GROUND_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Moves the ground and handles stitching of images
        """
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        """
        Draws the ground
        """
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


def draw_game(bird, ground, pipe_pairs, window, total_score):
    """
    Draws the whole screen
    """
    window.blit(SCENE_IMG, (0, 0))
    for pipe_pair in pipe_pairs:
        pipe_pair.draw(window)

    score = SCORE_FONT.render(str(total_score), 1, (255, 255, 255))
    window.blit(score, (WINDOW_WIDTH//2 -
                        score.get_width()//2, 10))
    bird.draw(window)
    ground.draw(window)
    pygame.display.update()


def main():
    """
    Main function that has the game loop and calls draw function
    """

    flappy_bird = FlappyBird(
        WINDOW_WIDTH//3 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2)
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    ground = Ground(WINDOW_HEIGHT - GROUND_HEIGHT)
    ticker = pygame.time.Clock()
    total_score = 0
    pipe_pairs = [PipePair(WINDOW_WIDTH + PIPE_STARTING_DIST)]
    game_over = False

    # main game loop
    while True:
        ticker.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and flappy_bird.alive:
                    flappy_bird.jump()
                elif event.key == pygame.K_r:
                    flappy_bird = FlappyBird(
                        WINDOW_WIDTH//3 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2)
                    total_score = 0
                    pipe_pairs = [PipePair(WINDOW_WIDTH + PIPE_STARTING_DIST)]
                    game_over = False
                    continue

        if not game_over:
            if flappy_bird.y < WINDOW_HEIGHT - GROUND_HEIGHT - BIRD_IMGS[0].get_height():
                flappy_bird.move()
            elif flappy_bird.alive:
                flappy_bird.die()
            else:
                game_over = True

            new_pipe = False
            i = 0
            while i < len(pipe_pairs) and flappy_bird.alive:
                pipe_pair = pipe_pairs[i]

                if pipe_pair.collision(flappy_bird):
                    flappy_bird.die()

                if pipe_pair.x + pipe_pair.TOP_PIPE_IMG.get_width() < 0:
                    pipe_pairs.pop(i)
                    continue

                if not pipe_pair.passed and pipe_pair.x < flappy_bird.x:
                    pipe_pair.passed = True
                    new_pipe = True

                pipe_pair.move()
                i += 1

            if new_pipe:
                total_score += 1
                pipe_pairs.append(PipePair(WINDOW_WIDTH + NEW_PIPE_DIST))

            if flappy_bird.alive:
                ground.move()

            draw_game(flappy_bird, ground, pipe_pairs, window, total_score)


# calling main function
main()
