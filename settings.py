"""Global application settings."""
import pygame


####################################
#         General Settings         #
####################################

WIDTH = 640   # 1280
HEIGHT = 320  # 720
FPS = 30  # not always achievable, but no harm trying

####################################
#         Fighter Settings         #
####################################

TIME_TO_RELOAD = 1000  # milliseconds
SIGHT_RANGE = max(WIDTH, HEIGHT) * 0.2  # pixels
SIGHT_ANGLE = 30  # total view angle of 2*SIGHT_ANGLE (i.e. 60 degrees)

BULLET_SPEED = 10  # pixels per frame
BULLET_RADIUS = 8  # pixels

FIGHTER_SPEED = 2    # pixels per frame
FIGHTER_RADIUS = 18  # pixels

TURNING_RATE = 4  # degrees turned per "turn" action

NUM_OBSERVATIONS = 6  # bullet detected, fighter detected, on target, reloading, prev_state
NUM_STATES = (2**NUM_OBSERVATIONS)**2  # squared because prev state is stored
NUM_ACTIONS = 4  # turn left, turn right, move forward, shoot

SHOOT_EVENT = pygame.USEREVENT + 1  # used for posting shoot events


##############################################
#         Genetic Algorithm Settings         #
##############################################

RESET_MODEL_EACH_SESSION = False  # reset model from application session to session

NUM_GENERATIONS = 500
POPULATION_SIZE = 6

EPISODE_LENGTH = 12  # episode/trial length in seconds

NUM_ELITE = 2  # number of most elite fighters to keep in next generation

ACTION_MUTATION_RATE = .1  # independent probability of mutation per action
ACTION_MUTATION_AMOUNT = .03  # amount to mutate weight in the positive or negative direction

MODEL_FILE = "models/best_weights.csv"
