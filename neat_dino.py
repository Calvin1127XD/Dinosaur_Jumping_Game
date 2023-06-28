import os
import neat
import pickle
import random
from game import game_loop
from game import Player, WINDOW_HEIGHT, PLAYER_SIZE


def eval_genomes(genomes, config):
    nets = []
    agents = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        agents.append(Player(50, WINDOW_HEIGHT - PLAYER_SIZE, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))

    scores = game_loop(False, agents, neural_networks=nets)
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = scores[i]

def run_neat(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(eval_genomes, 50)  # You can adjust the number of generations if needed

    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run_neat(config_path)