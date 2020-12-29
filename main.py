import time
import pygame
import neat
from constants import *
from flappy_bird import FlappyBird
from pipe_pair import PipePair
from ground import Ground


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


if __name__ == "__main__":
    main()
