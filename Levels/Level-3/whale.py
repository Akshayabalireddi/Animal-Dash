
import pygame
import random
from os.path import join

# SETUP
pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Animal Dash")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)

running = True

# BACKGROUND
background = pygame.image.load(
    join("Levels", "Level-3", "images", "whale_background.png")
).convert()

background = pygame.transform.scale(background, WINDOW_SIZE)
bg_width = background.get_width()

# PLAYER
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.lives = 3

        self.image = pygame.image.load(
            join("Levels", "Level-3", "images", "whale.png")
        ).convert_alpha()

        self.rect = self.image.get_rect(center=(200, 350))

        self.pos = pygame.Vector2(self.rect.center)

        self.direction = pygame.Vector2()
        self.speed = 300

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.direction.x = (
            int(keys[pygame.K_RIGHT])
            - int(keys[pygame.K_LEFT])
        )

        self.direction.y = (
            int(keys[pygame.K_DOWN])
            - int(keys[pygame.K_UP])
        )

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.pos += self.direction * self.speed * dt

        self.pos.y = max(50, min(WINDOW_HEIGHT - 50, self.pos.y))

        self.rect.center = self.pos


# BUBBLES
class Bubble(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)

        pygame.draw.circle(
            self.image,
            (200, 230, 255),
            (10, 10),
            10,
            2
        )

        self.world_x = 0
        self.world_y = WINDOW_HEIGHT + random.randint(0, 200)

        self.rect = self.image.get_rect(
            center=(self.world_x, self.world_y)
        )

        self.speed = random.randint(80, 180)

    def update(self, dt):
        self.world_y -= self.speed * dt
        self.rect.center = (self.world_x, self.world_y)

        if self.rect.bottom < -50:
            self.kill()


# OBSTACLES
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()

        self.image = pygame.image.load(
            join("Levels", "Level-3", "images", "bottle_whale.png")
        ).convert_alpha()

        self.rect = self.image.get_rect(
            center=(x, random.randint(100, 600))
        )

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        pass


# FISH COLLECTABLES
class FishCollectable(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()

        self.image = pygame.image.load(
            join("Levels", "Level-3", "images", "fish_collactable.png")
        ).convert_alpha()

        self.rect = self.image.get_rect(
            center=(x, random.randint(100, 600))
        )

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        pass


def check_collision(player, sprite):
    if not player.rect.colliderect(sprite.rect):
        return False

    offset = (
        sprite.rect.x - player.rect.x,
        sprite.rect.y - player.rect.y,
    )

    return player.mask.overlap(sprite.mask, offset) is not None


# CREATE OBJECTS
player = Player()

bubble_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
fish_group = pygame.sprite.Group()

bubble_timer = 0
obstacle_timer = 0
fish_timer = 0

fish_count = 0
FISH_GOAL = 15

level_complete = False
game_over = False

win_timer = 0
lose_timer = 0

# GAME LOOP
while running:

    dt = clock.tick(60) / 1000

    if level_complete:
        win_timer += dt

        if win_timer >= 3:
            # Load Level 4 here
            running = False

    if game_over:
        lose_timer += dt

        if lose_timer >= 3:
            running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn bubbles
    bubble_timer += dt

    if bubble_timer > 0.15:
        bubble = Bubble()

        bubble.world_x = (
            player.pos.x + random.randint(-800, 800)
        )

        bubble_group.add(bubble)

        bubble_timer = 0

    # Spawn obstacles
    obstacle_timer += dt

    if obstacle_timer > 2:
        obstacle = Obstacle(
            player.pos.x + random.randint(600, 1200)
        )

        obstacle_group.add(obstacle)

        obstacle_timer = 0

    # Spawn fish
    fish_timer += dt

    if fish_timer > 3:
        fish = FishCollectable(
            player.pos.x + random.randint(500, 1500)
        )

        fish_group.add(fish)

        fish_timer = 0

    # Update
    player.update(dt)
    bubble_group.update(dt)
    obstacle_group.update(dt)
    fish_group.update(dt)

    # Obstacle collision
    hits = []

    for obstacle in obstacle_group:
        if check_collision(player, obstacle):
            hits.append(obstacle)
            obstacle.kill()

    if hits and not game_over:
        player.lives -= 1
        print("Lives:", player.lives)

        if player.lives <= 0:
            game_over = True

    # Fish collision
    for fish in fish_group:
        if check_collision(player, fish):
            fish.kill()
            fish_count += 1

            print("Fish:", fish_count)

            if fish_count >= FISH_GOAL:
                level_complete = True

    # Camera
    camera_x = player.rect.centerx - WINDOW_WIDTH // 3

    # Draw background
    start_x = -(camera_x % bg_width)

    for i in range(-1, 3):
        screen.blit(background, (start_x + i * bg_width, 0))

    # Draw bubbles
    for bubble in bubble_group:
        screen.blit(
            bubble.image,
            (
                bubble.rect.x - camera_x,
                bubble.rect.y
            )
        )

    # Draw obstacles
    for obstacle in obstacle_group:
        screen.blit(
            obstacle.image,
            (
                obstacle.rect.x - camera_x,
                obstacle.rect.y
            )
        )

    # Draw fish
    for fish in fish_group:
        screen.blit(
            fish.image,
            (
                fish.rect.x - camera_x,
                fish.rect.y
            )
        )

    # Draw whale
    screen.blit(
        player.image,
        (
            player.rect.x - camera_x,
            player.rect.y
        )
    )

    # Draw lives
    lives_text = font.render(
        f"Lives: {player.lives}",
        True,
        (255, 255, 255)
    )

    screen.blit(lives_text, (20, 20))

    # Draw fish count
    fish_text = font.render(
        f"Fish: {fish_count}/{FISH_GOAL}",
        True,
        (255, 255, 255)
    )

    screen.blit(fish_text, (20, 70))

    # Level Complete Message
    if level_complete:
        complete_text = font.render(
            "LEVEL COMPLETE!",
            True,
            (255, 255, 0)
        )

        screen.blit(
            complete_text,
            (
                WINDOW_WIDTH // 2
                - complete_text.get_width() // 2,
                WINDOW_HEIGHT // 2
            )
        )

    pygame.display.flip()

pygame.quit()

