"""Gene functions for the genetic algorithm."""
import random
import numpy as np

from colors import *
from settings import *
from fighter import Fighter


def get_random_action_weights():
    """Get random weights for each action.

    e.g. [0.23, 0.57, 0.19, 0.92]"""
    return np.random.random((1, NUM_ACTIONS))


def get_probable_action(action_weights):
    """Get action based on weighted probabilities.

    e.g. for [0.23, 0.57, 0.19, 0.92], action 0 has a 23% chance to execute.
    Returns a discrete action array like [1, 1, 0, 1]"""
    return np.rint(np.greater(action_weights, np.random.random((1, NUM_ACTIONS))))


def get_random_action():
    """Get a random action."""
    return np.less_equal(get_random_action_weights())


def get_random_fighter_pos():
    return random.randint(0, WIDTH-36), random.randint(0, HEIGHT - 36)


def create_random_fighter(id):
    """Create a random fighter with a given id."""
    x, y = get_random_fighter_pos()
    return Fighter(id=id, color=BLUE, radius=FIGHTER_RADIUS,
                   x=x, y=y, angle=random.randint(0, 359))


def fitness(fighter):
    """Fitness of a fighter."""

    # minimum is 1 because of the way 'get_probable_fit_fighter' is implemented
    return max(fighter.hits - fighter.damage, 1)


def get_probable_fit_fighter(population, total_fitness):
    """Select a fighter with probability based on fitness."""
    sorted_pop = sorted(population, key=lambda f: fitness(f))

    count = 0
    rand_index = random.randint(0, total_fitness)
    for p in sorted_pop:
        count += fitness(p)
        if rand_index <= count:
            return p


def get_parents(population):
    """Parents are more likely selected if they have better fitness."""

    total_fitness = sum([fitness(p) for p in population])

    population_copy = list(population)

    # select parent 1
    parent1 = get_probable_fit_fighter(population_copy, total_fitness)

    population_copy.remove(parent1)
    total_fitness -= fitness(parent1)

    # select parent 2
    parent2 = get_probable_fit_fighter(population_copy, total_fitness)

    return parent1, parent2


def breed_parents(child_id, parent1, parent2):
    """Create a new child with the given child id."""

    child = create_random_fighter(child_id)
    crossover_point = random.randint(1, NUM_STATES-1)  # must at least crossover 1 gene

    for i in range(NUM_STATES):
        mutations = np.random.choice([-ACTION_MUTATION_AMOUNT, 0, ACTION_MUTATION_AMOUNT],
                                     size=NUM_ACTIONS,
                                     p=[ACTION_MUTATION_RATE/2, 1 - ACTION_MUTATION_RATE, ACTION_MUTATION_RATE/2])
        if i < crossover_point:
            child.Q[i] = np.clip(parent1.Q[i] + mutations, 0, 1)
        else:
            child.Q[i] = np.clip(parent2.Q[i] + mutations, 0, 1)

    return child


def get_random_population(size=POPULATION_SIZE):
    """Get a new population, optionally start with previous elite fighters."""

    fighters = {}

    # fill in the remaining spaces with new random fighters
    for i in range(size):
        fighters[i] = create_random_fighter(i)

    return fighters


def breed_population(population):
    """Breed the entire population."""

    best_fighters = sorted(population.values(), key=lambda f: fitness(f), reverse=True)

    new_population = {}
    for i in range(NUM_ELITE):
        new_population[i] = best_fighters[i]  # keep some of the most elite
        new_population[i].id = i              # reset fighter id
        new_population[i].reset_state()       # reset fighter state
        x, y = get_random_fighter_pos()
        new_population[i].set_position(x, y)  # reset fighter to random position
        new_population[i].set_random_angle()  # reset fighter to random angle
        new_population[i].set_color(RED)      # make the elite red for easy visualization

    for i in range(NUM_ELITE, POPULATION_SIZE):
        parent1, parent2 = get_parents(new_population.values())
        new_population[i] = breed_parents(i, parent1, parent2)

    return new_population
