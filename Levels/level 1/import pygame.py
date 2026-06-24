import pygame
from os.path import join, dirname, abspath
BASE_DIR = dirname(abspath(__file__))

pygame.init()


# SCREEN
WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Dash - Level 2")

clock = pygame.time.Clock()

# IMAGES

background = pygame.image.load(join(BASE_DIR,'duck', 'duckbackground.png')).convert_alpha()

duck = pygame.image.load(join(BASE_DIR,'duck', 'duck_duck1.png')).convert_alpha()
duck_platform = pygame.image.load(join(BASE_DIR,'duck', 'duck_assets_platform1.png')).convert_alpha()
duck_platform2 = pygame.image.load(join(BASE_DIR,'duck', 'duck_assets_platform2.png')).convert_alpha()
obstacle = pygame.image.load(join(BASE_DIR,'duck', 'duck_enviroment_reeds.png')).convert_alpha()
bread = pygame.image.load(join(BASE_DIR,'duck', 'duck_duck_food.png')).convert_alpha()
you_lose = pygame.image.load(join(BASE_DIR,'duck', 'you lose..png')).convert_alpha()
you_win = pygame.image.load(join(BASE_DIR,'duck', 'level 1 completed.png')).convert_alpha()

# SCALE IMAGES
duck = pygame.transform.scale(duck, (140, 140))
duck_platform = pygame.transform.scale(duck_platform, (220, 90))
duck_platform2 = pygame.transform.scale(duck_platform2, (450, 90))
obstacle = pygame.transform.scale(obstacle, (80, 80))
bread = pygame.transform.scale(bread, (80, 80))
you_lose = pygame.transform.scale(you_lose, (500, 250))
you_win = pygame.transform.scale(you_win, (500, 250))

# PLAYER

duck_x = 200
duck_y = 400

player_width = 140
player_height = 140

velocity_x = 1
velocity_y = 0

gravity = 1
jump_power = -20

friction = 0.80
move_speed = 1.2

on_ground = False

# GAME DATA
lives = 5
score = 0

font = pygame.font.Font(None, 50)
# CAMERA
camera_x = 0

# PLATFORMS

platforms = [
    ("long", pygame.Rect(0, 620, 450, 90)),
    ("small", pygame.Rect(450, 470, 220, 90)),

    ("long", pygame.Rect(750, 620, 450, 90)),
    ("small", pygame.Rect(1200, 470, 220, 90)),

    ("long", pygame.Rect(1500, 620, 450, 90)),
    ("small", pygame.Rect(1950, 470, 220, 90)),

    ("long", pygame.Rect(2250, 620, 450, 90)),
    ("small", pygame.Rect(2700, 470, 220, 90)),

    ("long", pygame.Rect(3000, 620, 450, 90)),
    ("small", pygame.Rect(3450, 470, 220, 90)),

    ("long", pygame.Rect(3750, 620, 450, 90)),
    ("small", pygame.Rect(4200, 470, 220, 90)),

    ("long", pygame.Rect(4500, 620, 450, 90)),
    ("small", pygame.Rect(4950, 470, 220, 90)),

    ("long", pygame.Rect(5250, 620, 450, 90)),
    ("small", pygame.Rect(5700, 470, 220, 90)),

    ("long", pygame.Rect(6000, 620, 450, 90)),
    ("small", pygame.Rect(6450, 470, 220, 90)),

    ("long", pygame.Rect(6750, 620, 450, 90)),
    ("small", pygame.Rect(7200, 470, 220, 90)),

    ("long", pygame.Rect(7500, 620, 450, 90)),
]

# BERRIES
breads = [
    pygame.Rect(520, 410, 70, 70),
    pygame.Rect(1350, 410, 70, 70),
    pygame.Rect(2020, 410, 70, 70),
    pygame.Rect(2770, 410, 70, 70),
    pygame.Rect(3520, 410, 70, 70),
    pygame.Rect(4270, 410, 70, 70),
    pygame.Rect(5020, 410, 70, 70),
    pygame.Rect(5770, 410, 70, 70),
    pygame.Rect(6520, 410, 70, 70),
    pygame.Rect(7270, 410, 70, 70),
]


# OBSTACLES
obstacles = [
    pygame.Rect(1700, 540, 80, 80),
    pygame.Rect(3200, 540, 80, 80),
    pygame.Rect(4700, 540, 80, 80),
    pygame.Rect(6200, 540, 80, 80),
]

max_platform_x = 3000

# GAME LOOP
running = True

while running:

    clock.tick(60)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # LONG HORIZONTAL JUMP
            if event.key == pygame.K_UP and on_ground:
                velocity_y = -26
                velocity_x = 8
                on_ground = False

# AUTO-SPAWN PLATFORMS
    last_platform_x = platforms[-1][1].x

    if last_platform_x - camera_x < WIDTH:
        new_x = last_platform_x + 400

        import random

        platform_type = random.choice(["small", "long"])

        if platform_type == "small":
            new_rect = pygame.Rect(new_x, random.choice([450, 500]), 220, 90)
        else:
            new_rect = pygame.Rect(new_x, 620, 450, 90)

        platforms.append((platform_type, new_rect))
    # INPUT
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        velocity_x -= move_speed

    if keys[pygame.K_RIGHT]:
        velocity_x += move_speed

   
    # APPLY PHYSICS
    velocity_x *= friction
    duck_x += velocity_x

    velocity_y += gravity
    duck_y += velocity_y
    # CAMERA
    camera_x = duck_x - 300
    if camera_x < 0:
        camera_x = 0

    # HITBOX
    duck_rect = pygame.Rect(
        duck_x + 35,
        duck_y + 30,
        70,
        80
    )
    on_ground = False
    # PLATFORM COLLISION (FIXED)
    for platform_type, platform_rect in platforms:

        if duck_rect.colliderect(platform_rect):

            if velocity_y > 0:
                duck_rect.bottom = platform_rect.top
                duck_y = duck_rect.y
                velocity_y = 0
                on_ground = True

    # FALL RESET
    # FALL OFF MAP
   # FALL OFF MAP
    if duck_y > HEIGHT:

        lives -= 1

        duck_x = 200
        duck_y = 400

        velocity_x = 0
        velocity_y = 0

        pygame.time.delay(500)
    # BREADS
    for bread_rect in breads[:]:
        if duck_rect.colliderect(bread_rect):
            breads.remove(bread_rect)
            score += 1

    # OBSTACLES
    for obstacle_rect in obstacles:

        obstacle_hitbox = pygame.Rect(
            obstacle_rect.x + 10,
            obstacle_rect.y + 10,
            60,
            60
        )

        if duck_rect.colliderect(obstacle_hitbox):

            lives -= 1

            # Respawn nearby instead of restarting the whole level
            duck_x = obstacle_rect.x - 250
            duck_y = 400

            velocity_x = 0
            velocity_y = 0

            pygame.time.delay(500)

            break

    # WIN / LOSE
    if lives <= 0:

        screen.blit(background, (-camera_x * 0.5, 0))

        screen.blit(
            you_lose,
            (
                WIDTH // 2 - you_lose.get_width() // 2,
                HEIGHT // 2 - you_lose.get_height() // 2
            )
        )

        pygame.display.update()
        pygame.time.delay(3000)
        running = False
    if score >= 5:

        screen.blit(background, (-camera_x * 0.5, 0))

        screen.blit(
            you_win,
            (
                WIDTH // 2 - you_win.get_width() // 2,
                HEIGHT // 2 - you_win.get_height() // 2
            )
        )

        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    # DRAW
    screen.blit(background, (0, 0))

    # platforms
    for platform_type, platform_rect in platforms:

        draw_x = platform_rect.x - camera_x

        if platform_type == "long":
            screen.blit(duck_platform2, (draw_x, platform_rect.y))
        else:
            screen.blit(duck_platform, (draw_x, platform_rect.y))

    # obstacles
    for obstacle_rect in obstacles:
        screen.blit(obstacle, (obstacle_rect.x - camera_x, obstacle_rect.y))

    # breads
    for bread_rect in breads:
        screen.blit(bread, (bread_rect.x - camera_x, bread_rect.y))

    # duck (fixed position on screen)
    screen.blit(duck, (duck_x - camera_x, duck_y))

    # UI
    screen.blit(font.render(f"Lives: {lives}", True, (255,255,255)), (20,20))
    screen.blit(font.render(f"Breads: {score}/5", True, (255,255,255)), (20,70))

    pygame.display.update()

pygame.quit()