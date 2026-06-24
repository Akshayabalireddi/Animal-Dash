import pygame
import random

# Initialize pygame
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collectibles Example")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
BLUE = (0, 100, 255)

# Font
font = pygame.font.Font(None, 36)

# Player
player_size = 50
player = pygame.Rect(100, 100, player_size, player_size)
player_speed = 5

# Create collectibles
coins = []
for _ in range(10):
    coin = pygame.Rect(
        random.randint(0, WIDTH - 20),
        random.randint(0, HEIGHT - 20),
        20,
        20
    )
    coins.append(coin)

score = 0
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player.y -= player_speed
    if keys[pygame.K_s]:
        player.y += player_speed
    if keys[pygame.K_a]:
        player.x -= player_speed
    if keys[pygame.K_d]:
        player.x += player_speed

    # Keep player on screen
    player.x = max(0, min(player.x, WIDTH - player.width))
    player.y = max(0, min(player.y, HEIGHT - player.height))

    # Collect coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Draw
    screen.fill((30, 30, 30))

    pygame.draw.rect(screen, BLUE, player)

    for coin in coins:
        pygame.draw.circle(
            screen,
            YELLOW,
            coin.center,
            coin.width // 2
        )

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()