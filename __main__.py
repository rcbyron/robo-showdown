"""Initialize and start pygame."""
import pygame
import pygame.gfxdraw
import random
import time
import signal
import numpy as np
import tensorflow as tf

from bullet import Bullet
from fighter import Fighter, Vision
from colors import *
from settings import *
from gene_functions import *


def init_pygame():
    """Initialize pygame."""
    global screen, clock, bullet_sprites, default_font
    # initialize pygame and create window
    pygame.init()
    pygame.mixer.init()  # for sound

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("Genetic Fighting")
    clock = pygame.time.Clock()  # for syncing the FPS

    # group all the sprites together for ease of update
    bullet_sprites = pygame.sprite.Group()

    default_font = pygame.font.SysFont("arial bold", 28)


def reset_environment(new_fighters):
    """Reset the environment after each trial."""
    global population, bullet_sprites

    population = new_fighters

    bullet_sprites.empty()


##################################################################
#                         START THE GAME                         #
##################################################################

default_font = None

population = {}
next_population = get_random_population()

init_pygame()


tf_best_score = tf.Variable(0)
tf.summary.scalar('best_score_per_generation', tf_best_score)
summary_op = tf.summary.merge_all()

sess = tf.Session()
sess.run(tf.global_variables_initializer())
writer = tf.summary.FileWriter('graphs/'+time.strftime("session-%Y%m%d-%H%M%S"), sess.graph)

for generation in range(NUM_GENERATIONS):
    reset_environment(next_population)

    label_str = "Generation: " + str(generation)
    generation_label = default_font.render(label_str, 1, BLACK)
    print(label_str, end="")

    start_time = time.clock()

    # start simulation of current generation
    running = True
    while running and time.clock() - start_time < EPISODE_LENGTH:

        clock.tick(FPS)  # ensure loop runs at constant speed
        clock_time = pygame.time.get_ticks()

        # get all the events which have occurred until now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SHOOT_EVENT:
                bullet = Bullet(event.shooter, event.x, event.y, event.angle, BULLET_SPEED)
                bullet_sprites.add(bullet)

        # detect states of each fighter

        for fighter in population.values():

            if fighter.reloading and (clock_time - fighter.last_shot_time) > TIME_TO_RELOAD:
                fighter.reloading = False

            fighter.on_target = False
            fighter.fighter_on_left = False
            fighter.fighter_on_right = False

            for other_fighter in population.values():
                if fighter != other_fighter:
                    fighter.on_target |= fighter.vision.on_target(other_fighter.torso)
                    result = fighter.vision.detects(other_fighter.torso)
                    if result == "left":
                        fighter.fighter_on_left = True
                    elif result == "right":
                        fighter.fighter_on_right = True

            fighter.bullet_on_left = False
            fighter.bullet_on_right = False

            for bullet in bullet_sprites:
                if bullet.shooter != fighter.id:
                    result = fighter.vision.detects(bullet)
                    if result == "left":
                        fighter.bullet_on_left = True
                    elif result == "right":
                        fighter.bullet_on_right = True

        # detect bullet collision
        for fighter_id, fighter in population.items():
            for bullet in bullet_sprites:
                if bullet.shooter is not fighter_id and \
                        pygame.sprite.collide_circle(bullet, fighter.torso):
                    population[bullet.shooter].hits += 1
                    fighter.damage += 1
                    bullet.kill()

        # keyboard events for user controlled input
        # pressed = pygame.key.get_pressed()
        # user_action = [0, 0, 0, 0]
        # if pressed[pygame.K_LEFT]:
        #     user_action[0] = 1
        # if pressed[pygame.K_RIGHT]:
        #     user_action[1] = 1
        # if pressed[pygame.K_UP]:
        #     user_action[2] = 1
        # if pressed[pygame.K_SPACE]:
        #     user_action[3] = 1

        # execute actions for each fighter
        for fighter in population.values():
            action_weights = fighter.Q[fighter.state, :]
            # if fighter.id != 0:  # uncomment to control fighter 0 with keyboard
            fighter.update(actions=get_probable_action(action_weights))
        # fighters[0].update(actions=user_action)  # uncomment to control fighter 0 with keyboard

        bullet_sprites.update()

        # draw to screen
        screen.fill(WHITE)
        screen.blit(generation_label, (10, 10))

        for fighter in population.values():
            for sprite in fighter:
                sprite.draw(screen)
        bullet_sprites.draw(screen)

        pygame.display.update()

    # generation trial complete, store weights of best fighter
    best_fighter = max(population.values(), key=lambda f: fitness(f))
    best_fitness = fitness(best_fighter)
    best_weights = best_fighter.Q
    np.savetxt(MODEL_FILE, best_weights, delimiter=",")
    print(", best fitness:", best_fitness)

    # create new population from previous population
    next_population = breed_population(population)

    # update tensorflow data for visualization
    sess.run(tf_best_score.assign(best_fitness))

    summary = sess.run(summary_op)
    writer.add_summary(summary, generation)

pygame.quit()
