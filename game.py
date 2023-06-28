# game.py
import pygame
import sys
import random
import os
import pickle
import itertools
import neat

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 300
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PLAYER_SIZE = 30
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 50
MAX_SCORE_THRESHOLD = 12000  # Adjust this value as needed

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur Game")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.score = 0
        self.alive = True
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_velocity = 0

    def update(self):
        self.y_velocity += 1
        self.rect.y += self.y_velocity
        if self.rect.y > WINDOW_HEIGHT - PLAYER_SIZE:
            self.rect.y = WINDOW_HEIGHT - PLAYER_SIZE
            self.y_velocity = 0

    def jump(self):
        if self.rect.y == WINDOW_HEIGHT - PLAYER_SIZE:
            self.y_velocity = -18

def draw_nodes(inputs, output, x, y, node_radius=10):
    num_inputs = len(inputs)
    input_spacing = 30
    output_spacing = 30

    # Draw input nodes
    for i, input_value in enumerate(inputs):
        input_y = y + i * input_spacing
        pygame.draw.circle(screen, BLACK, (x, input_y), node_radius)
        draw_text(f"{input_value:.2f}", 16, x + 2 * node_radius, input_y - node_radius // 2)

    # Draw output node
    output_y = y + (num_inputs - 1) * input_spacing // 2
    pygame.draw.circle(screen, BLACK, (x + 100, output_y), node_radius)
    draw_text(f"{output[0]:.2f}", 16, x + 100 + 2 * node_radius, output_y - node_radius // 2)

    # Draw connections
    for i in range(num_inputs):
        input_y = y + i * input_spacing
        pygame.draw.line(screen, BLACK, (x + node_radius, input_y), (x + 100 - node_radius, output_y), 2)


def load_winner(config_path):
    with open('winner.pkl', 'rb') as f:
        genome = pickle.load(f)

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    winner_net = neat.nn.FeedForwardNetwork.create(genome, config)

    return winner_net

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= 5

def get_obstacle_info(player, obstacles):
    obstacle_info = []

    for obstacle in obstacles:
        distance = obstacle.rect.x - player.rect.x - PLAYER_SIZE
        width = obstacle.rect.width
        height = obstacle.rect.height
        obstacle_info.append((distance, width, height))

    obstacle_info.sort(key=lambda x: x[0])

    on_ground = player.rect.y == WINDOW_HEIGHT - PLAYER_SIZE

    return obstacle_info[:3], on_ground

def generate_obstacle(prev_x, min_separation):
    x = prev_x + min_separation + random.randint(0, 100)
    width = random.randint(20, 50)
    height = random.randint(20, 100)
    obstacle = Obstacle(x, WINDOW_HEIGHT - height, width, height)
    return obstacle

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def game_loop(human_playing, agents, neural_networks=None, current_best_score=0, auto_start=False, generation=0):
    best_score = current_best_score
    min_separation = 160
    obstacles = [generate_obstacle(i * (min_separation + OBSTACLE_WIDTH), min_separation) for i in range(3)]
    all_sprites = pygame.sprite.Group()

    players = agents if not human_playing else [Player(50, WINDOW_HEIGHT - PLAYER_SIZE, BLACK)]
    alive_agents = len(players)

    for player in players:
        all_sprites.add(player)

    for obstacle in obstacles:
        all_sprites.add(obstacle)

    start_game = False
    game_over = False
    score = 0

    running = True
    while running:
        if game_over:
            best_score = max(best_score, score)
            if not human_playing:
                return [player.score for player in (players if not human_playing else [players[0]])]

        clock.tick(FPS)
        screen.fill(WHITE)

        if auto_start or not start_game:
            start_game = True

        if not start_game:
            draw_text("Press SPACE to start", 36, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50)
        elif game_over:
            draw_text("GAME OVER", 48, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100)
            draw_text(f"Score: {score}", 36, WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - 40)
            draw_text(f"Best Score: {best_score}", 24, WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2)
            draw_text("Press SPACE to play again, ESC to exit", 24, WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 40)

        else:
            score += 1
            for player in players:
                player.score = score
                if not human_playing and player.score > MAX_SCORE_THRESHOLD:
                    player.alive = False
            draw_text(f"Score: {score}", 24, 10, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not start_game:
                        start_game = True
                    elif game_over:
                        return game_loop(human_playing, agents, neural_networks, best_score)
                    elif human_playing:
                        player.jump()
                if event.key == pygame.K_ESCAPE and game_over:
                    running = False
                    break

        if start_game and not game_over:
            all_sprites.update()

            # Handle agent collisions and remove dead agents
            for obstacle in obstacles:
                if human_playing:
                    if player.rect.colliderect(obstacle.rect):
                        game_over = True
                        break
                else:
                    for i, player in enumerate(players):
                        if player.rect.colliderect(obstacle.rect) and player.alive:
                            player.alive = False
                            alive_agents -= 1

                if not human_playing and (alive_agents <= 0 or all(player.score > MAX_SCORE_THRESHOLD for player in players)):
                    game_over = True

            # Replace obstacles that have left the screen
            for i, obstacle in enumerate(obstacles):
                if obstacle.rect.x <= -OBSTACLE_WIDTH:
                    all_sprites.remove(obstacle)
                    new_obstacle = generate_obstacle(obstacles[i - 1].rect.x, min_separation)
                    obstacles[i] = new_obstacle
                    all_sprites.add(new_obstacle)

            if not human_playing and neural_networks is not None:
                for i, player in enumerate(players):
                    if not player.alive:
                        continue

                    # Get inputs for the neural network
                    closest_obstacles, on_ground = get_obstacle_info(player, obstacles)
                    inputs = [info[0] for info in closest_obstacles] + \
                             [info[2] for info in closest_obstacles] + \
                             [int(on_ground)]

                    output = neural_networks[i].activate(inputs)
                    if output[0] > 0.5:
                        player.jump()
                    if i == 0:  # Show the nodes for the first agent
                        draw_nodes(inputs, output, WINDOW_WIDTH - 150, 10)


            all_sprites.draw(screen)

        pygame.display.flip()

    return score

if __name__ == "__main__":
    human_playing = False  # Set this to True if you want to play the game yourself

    if human_playing:
        game_loop(human_playing, None)
    else:
        # Load your NEAT configuration and neural networks here, then call the game_loop function with the appropriate arguments.
        config_path = "config-feedforward.txt"
        winner_net = load_winner(config_path)
        player = Player(50, WINDOW_HEIGHT - PLAYER_SIZE, BLACK)
        game_loop(human_playing, [player], neural_networks=[winner_net])
