import time
import pygame
import neat
import sys
from constants import *
from flappy_bird import FlappyBird
from pipe_pair import PipePair
from ground import Ground

gen_num = 0


def draw_game(birds, dead_birds, ground, pipe_pairs, window, total_score, gen_num):
    """
    Draws the whole screen
    """
    window.blit(SCENE_IMG, (0, 0))

    for pipe_pair in pipe_pairs:
        pipe_pair.draw(window)

    score = SCORE_FONT.render(str(total_score), 1, (255, 255, 255))
    window.blit(score, (WINDOW_WIDTH//2 -
                        score.get_width()//2, 10))

    for bird in birds:
        bird.draw(window)

    for dead_bird in dead_birds:
        dead_bird.draw(window)

    ground.draw(window)

    if gen_num > 0:
        gen = STATS_FONT.render(
            "Gen: " + str(gen_num), 1, (255, 255, 255))
        window.blit(gen, (WINDOW_WIDTH//2 -
                          gen.get_width()//2, WINDOW_HEIGHT - 100))

    pygame.display.update()


def main(genomes, config, ai_enabled=True):
    """
    Main function that has the game loop and calls draw function
    """
    global gen_num

    if ai_enabled:
        gen_num += 1

    birds = [FlappyBird(
        WINDOW_WIDTH//3 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2, False)]
    dead_birds = []

    if ai_enabled:
        nets = []
        ge = []
        birds.clear()
        generated_tints = []

        for _, gen in genomes:
            net = neat.nn.FeedForwardNetwork.create(gen, config)
            nets.append(net)

            birds.append(FlappyBird(
                WINDOW_WIDTH//3 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2, ai_enabled, AI_TINT))
            gen.fitness = 0
            ge.append(gen)

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    ground = Ground(WINDOW_HEIGHT - GROUND_HEIGHT)
    ticker = pygame.time.Clock()
    total_score = 0
    pipe_pairs = [PipePair(WINDOW_WIDTH + PIPE_STARTING_DIST)]

    # main game loop
    while (len(birds) and ai_enabled) or (not ai_enabled):
        ticker.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and not ai_enabled:
                if event.key == pygame.K_SPACE and len(birds):
                    birds[0].jump()
                elif event.key == pygame.K_r:
                    birds = [FlappyBird(
                        WINDOW_WIDTH//3 - BIRD_IMGS[0].get_width()//2, WINDOW_HEIGHT//2 - BIRD_IMGS[0].get_height()//2, False)]
                    dead_birds = []
                    total_score = 0
                    pipe_pairs = [PipePair(WINDOW_WIDTH + PIPE_STARTING_DIST)]
                    continue

        for i, dead_bird in enumerate(dead_birds):
            if dead_bird.y < WINDOW_HEIGHT - GROUND_HEIGHT - BIRD_IMGS[0].get_height():
                dead_bird.move()
            elif dead_bird.x + BIRD_IMGS[0].get_width() < 0:
                dead_birds.pop(i)

        if len(birds):
            pipe_ind = 0
            if len(pipe_pairs) > 1 and birds[0].x > pipe_pairs[0].x + PIPE_IMG.get_width():
                pipe_ind = 1

            for i, bird in enumerate(birds):
                if bird.y < WINDOW_HEIGHT - GROUND_HEIGHT - BIRD_IMGS[0].get_height():
                    bird.move()

                    if ai_enabled:
                        ge[i].fitness += 0.1
                        out = nets[i].activate((bird.y, abs(
                            bird.y - pipe_pairs[pipe_ind].height), abs(bird.y - pipe_pairs[pipe_ind].bottom)))

                        if out[0] > 0.5:
                            bird.jump()
                elif bird.alive:
                    bird.die()
                    dead_birds.append(birds.pop(i))
                    if ai_enabled:
                        nets.pop(i)
                        ge.pop(i)

            new_pipe = False
            x = 0
            while x < len(pipe_pairs) and len(birds):
                pipe_pair = pipe_pairs[x]

                for i, bird in enumerate(birds):
                    if pipe_pair.collision(bird):
                        bird.die()
                        dead_birds.append(birds.pop(i))
                        if ai_enabled:
                            ge[i].fitness -= 1
                            nets.pop(i)
                            ge.pop(i)

                    if not pipe_pair.passed and pipe_pair.x < bird.x:
                        pipe_pair.passed = True
                        new_pipe = True

                if pipe_pair.x + PIPE_IMG.get_width() < 0:
                    pipe_pairs.pop(x)
                    continue

                pipe_pair.move()
                x += 1

            if new_pipe:
                total_score += 1
                pipe_pairs.append(PipePair(WINDOW_WIDTH + NEW_PIPE_DIST))

                if ai_enabled:
                    for gen in ge:
                        gen.fitness += 5

            if len(birds):
                ground.move()

                for dead_bird in dead_birds:
                    dead_bird.move_horizontally()

        draw_game(birds, dead_birds, ground,
                  pipe_pairs, window, total_score, gen_num)


def setup_config(conf_path):
    conf = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                              conf_path)

    p = neat.Population(conf)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, AI_MAX_RUNS)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-ai":
        curr_dir = os.path.dirname(__file__)
        conf_path = os.path.join(curr_dir, "neat-config.txt")
        setup_config(conf_path)
    else:
        main(None, None, False)
