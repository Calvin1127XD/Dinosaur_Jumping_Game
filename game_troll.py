# game.py
import pygame
import sys
import random

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 300
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PLAYER_SIZE = 60
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 50
JUMP_COUNT = 7
GRAVITY=0.45

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur Game")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image_on_ground = pygame.image.load("on_ground.png").convert_alpha()
        self.image_hopping = pygame.image.load("hopping.png").convert_alpha()
        self.image_on_ground = pygame.transform.scale(self.image_on_ground, (PLAYER_SIZE, PLAYER_SIZE))
        self.image_hopping = pygame.transform.scale(self.image_hopping, (PLAYER_SIZE, PLAYER_SIZE))
        self.image = self.image_on_ground
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y = y
        self.jumping = False
        self.jump_count = 0
        self.vel_y = 0

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_count = JUMP_COUNT
            self.image = self.image_hopping

    def update(self):
        if self.jumping:
            self.vel_y = -self.jump_count * 4
            self.jump_count -= GRAVITY
            if self.jump_count < -JUMP_COUNT:
                self.jumping = False

        self.vel_y += GRAVITY  # Gravity should always be applied, regardless of whether the player is jumping or not.

        self.y += self.vel_y
        if self.y > WINDOW_HEIGHT - PLAYER_SIZE:
            self.y = WINDOW_HEIGHT - PLAYER_SIZE
            self.vel_y = 0

        self.rect.y = self.y

        if self.rect.y == WINDOW_HEIGHT - PLAYER_SIZE:
            self.image = self.image_on_ground



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

def generate_obstacle(prev_x, min_separation):
    x = prev_x + min_separation + random.randint(0, 100)
    width = random.randint(15, 42)  # Change these values to set the range of obstacle widths
    height = random.randint(20, 85)  # Change these values to set the range of obstacle heights
    obstacle = Obstacle(x, WINDOW_HEIGHT - height, width, height)
    return obstacle

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def game_loop(human_playing, neural_network=None, current_best_score=0):
    best_score = current_best_score
    player = Player(50, WINDOW_HEIGHT - PLAYER_SIZE)
    min_separation = 200
    obstacles = [generate_obstacle(i * (min_separation + OBSTACLE_WIDTH), min_separation) for i in range(3)] 
    all_sprites = pygame.sprite.Group()
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

        clock.tick(FPS)
        screen.fill(WHITE)

        if not start_game:
            draw_text("Press SPACE to start", 36, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50)
        elif game_over:
            draw_text("GAME OVER", 48, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100)
            draw_text(f"Score: {score}", 36, WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - 40)
            draw_text(f"Best Score: {best_score}", 24, WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2)
            draw_text("Press SPACE to play again, ESC to exit", 24, WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 40)

        else:
            score += 1
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
                        return game_loop(human_playing, neural_network, best_score)
                    elif human_playing:
                        player.jump()
                if event.key == pygame.K_ESCAPE and game_over:
                    running = False
                    break

        if start_game and not game_over:
            all_sprites.update()

        for obstacle in obstacles:
            if player.rect.colliderect(obstacle.rect):
                game_over = True
                break

            for i, obstacle in enumerate(obstacles):
                if obstacle.rect.x <= -OBSTACLE_WIDTH:
                    all_sprites.remove(obstacle)
                    new_obstacle = generate_obstacle(obstacles[i - 1].rect.x, min_separation)
                    obstacles[i] = new_obstacle
                    all_sprites.add(new_obstacle)

            if not human_playing and neural_network is not None:
                inputs = (player.rect.y, obstacle.rect.x)
                output = neural_network.activate(inputs)
                if output[0] > 0.5:
                    player.jump()

            all_sprites.draw(screen)

        pygame.display.flip()

    return score


if __name__ == "__main__":
    game_loop(True, None)  # Set to False for computer play, and pass the neural network object when using NEAT

