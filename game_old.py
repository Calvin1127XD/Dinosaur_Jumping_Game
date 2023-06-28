import pygame
import sys
#import neat
import os
import random

pygame.init()

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 300
FPS = 60
PLAYER_SIZE = 20
OBSTACLE_WIDTH = 10
OBSTACLE_HEIGHT = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur Game")
clock = pygame.time.Clock()

# Player and obstacle classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.jump_speed = 0
        self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_speed = -18

    def update(self):
        self.rect.y += self.jump_speed
        if self.is_jumping:
            self.jump_speed += 1
        if self.rect.y >= WINDOW_HEIGHT - PLAYER_SIZE:
            self.rect.y = WINDOW_HEIGHT - PLAYER_SIZE
            self.is_jumping = False
            self.jump_speed = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x <= -OBSTACLE_WIDTH:
            self.rect.x = WINDOW_WIDTH

def generate_obstacle(min_separation):
    x = WINDOW_WIDTH + random.randint(min_separation, min_separation + 100)
    obstacle = Obstacle(x, WINDOW_HEIGHT - OBSTACLE_HEIGHT)
    return obstacle


def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def game_loop(human_playing):
    player = Player(50, WINDOW_HEIGHT - PLAYER_SIZE)
    

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(obstacles)

    start_game = False
    game_over = False

    obstacle = generate_obstacle(200)  # Change the 200 to adjust minimum separation between obstacles

    score = 0

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(WHITE)
        
        if not start_game:
            draw_text("Press SPACE to start", 36, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50)
        elif game_over:
            draw_text("GAME OVER", 48, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50)
            draw_text("Press SPACE to play again, ESC to exit", 24, WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2)
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
                        return game_loop(human_playing)
                    elif human_playing:
                        player.jump()
                elif event.key == pygame.K_ESCAPE and game_over:
                    running = False
                    pygame.quit()
                    sys.exit()

        if not human_playing:
            # Implement NEAT algorithm here
            pass

        if start_game and not game_over:
            all_sprites.update()
            for obstacle in obstacles:
                if player.rect.colliderect(obstacle.rect):
                    game_over = True


        all_sprites.draw(screen)
        pygame.display.flip()

game_loop(True)  # Set to False for computer play
