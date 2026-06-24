import pygame

pygame.init()


# SCREEN
WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Dash - Level 2")

clock = pygame.time.Clock()

# IMAGES

background = pygame.image.load("Levels/Level-2/deer_background.png").convert()

deer = pygame.image.load("Levels/Level-2/deer_assets_deer.png").convert_alpha()
deer_platform = pygame.image.load("Levels/Level-2/deer_assets_platform.png").convert_alpha()
deer_platform2 = pygame.image.load("Levels/Level-2/deer_assets_platform2.png").convert_alpha()
obstacle = pygame.image.load("Levels/Level-2/deer_assets_obstcales.png").convert_alpha()
berry = pygame.image.load("Levels/Level-2/deer_assets-food.png").convert_alpha()
you_lose = pygame.image.load("Levels/Level-2/you lose..png").convert_alpha()
you_win = pygame.image.load("Levels/Level-2/level 2 completed.png").convert_alpha()

# SCALE IMAGES
deer = pygame.transform.scale(deer, (140, 140))
deer_platform = pygame.transform.scale(deer_platform, (220, 90))
deer_platform2 = pygame.transform.scale(deer_platform2, (450, 90))
obstacle = pygame.transform.scale(obstacle, (80, 80))
berry = pygame.transform.scale(berry, (200, 200))
you_lose = pygame.transform.scale(you_lose, (500, 250))
you_win = pygame.transform.scale(you_win, (500, 250))

# PLAYER

deer_x = 200
deer_y = 400

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
    ("small", pygame.Rect(500, 450, 220, 90)),
    ("long", pygame.Rect(900, 620, 450, 90)),
    ("small", pygame.Rect(1340, 450, 220, 90)),
    ("long", pygame.Rect(1700, 620, 450, 90)),
    ("small", pygame.Rect(2200, 450, 220, 90)),
    ("long", pygame.Rect(2500, 620, 450, 90)),
    ("small", pygame.Rect(3000, 450, 220, 90)),
    ("long", pygame.Rect(3400, 620, 450, 90)),
    ("small", pygame.Rect(4100, 450, 220, 90)),
    ("long", pygame.Rect(4400, 620, 450, 90)),
    ("small", pygame.Rect(4600, 450, 220, 90)),
    ("long", pygame.Rect(5000, 620, 450, 90)),
    ("small", pygame.Rect(6000, 450, 220, 90)),
    ("long", pygame.Rect(6300, 620, 450, 90)),
    ("small", pygame.Rect(6900, 450, 220, 90)),
    ("long", pygame.Rect(7300, 620, 450, 90)),
    ("small", pygame.Rect(7800, 450, 220, 90)),
    ("long", pygame.Rect(8100, 620, 450, 90)),
    ("small", pygame.Rect(8600, 450, 220, 90)),
    ("long", pygame.Rect(8900, 620, 450, 90)),
    ("small", pygame.Rect(9400, 450, 220, 90)),
    ("long", pygame.Rect(9700, 620, 450, 90)),
    ("small", pygame.Rect(10200, 450, 220, 90)),
    ("long", pygame.Rect(10500, 620, 450, 90)),
    ("small", pygame.Rect(11000, 450, 220, 90)),
    ("long", pygame.Rect(11300, 620, 450, 90)),
]

# BERRIES
berries = [
    pygame.Rect(570, 360, 70, 70),
    pygame.Rect(1300, 360, 70, 70),
    pygame.Rect(1600, 360, 70, 70),
    pygame.Rect(2050, 530, 70, 70),
    pygame.Rect(2600, 360, 70, 70),
    pygame.Rect(3050, 530, 70, 70),
    pygame.Rect(3600, 360, 70, 70),
    pygame.Rect(4050, 530, 70, 70),
    pygame.Rect(4600, 360, 70, 70),
    pygame.Rect(5050, 530, 70, 70),
    pygame.Rect(5500, 360, 70, 70),
    pygame.Rect(5950, 530, 70, 70),
    pygame.Rect(6400, 360, 70, 70),
    pygame.Rect(6850, 530, 70, 70),
    pygame.Rect(7300, 360, 70, 70),
    pygame.Rect(7750, 530, 70, 70),
    pygame.Rect(8200, 360, 70, 70),
    pygame.Rect(8650, 530, 70, 70),
]


# OBSTACLES
obstacles = [
    pygame.Rect(1100, 540, 80, 80),
    pygame.Rect(1550, 370, 80, 80),
    pygame.Rect(2300, 540, 80, 80),
    pygame.Rect(2850, 370, 80, 80),
    pygame.Rect(3600, 540, 80, 80),
    pygame.Rect(4500, 540, 80, 80),
    pygame.Rect(5050, 540, 80, 80),
    pygame.Rect(5600, 540, 80, 80),
    pygame.Rect(6150, 540, 80, 80),
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
    deer_x += velocity_x

    velocity_y += gravity
    deer_y += velocity_y
    # CAMERA
    camera_x = deer_x - 300
    if camera_x < 0:
        camera_x = 0

    # HITBOX
    
    deer_rect = pygame.Rect(
        deer_x + 35,
        deer_y + 30,
        70,
        80
    )
    on_ground = False
    # PLATFORM COLLISION (FIXED)
    for platform_type, platform_rect in platforms:

        if deer_rect.colliderect(platform_rect):

            if velocity_y > 0:
                deer_rect.bottom = platform_rect.top
                deer_y = deer_rect.y
                velocity_y = 0
                on_ground = True

    # FALL RESET
    # FALL OFF MAP
   # FALL OFF MAP
    if deer_y > HEIGHT:

        lives -= 1

        deer_x = 200
        deer_y = 400

        velocity_x = 0
        velocity_y = 0

        pygame.time.delay(500)
    # BERRIES
    for berry_rect in berries[:]:
        if deer_rect.colliderect(berry_rect):
            berries.remove(berry_rect)
            score += 1

    # OBSTACLES
    for obstacle_rect in obstacles:

        obstacle_hitbox = pygame.Rect(
            obstacle_rect.x + 10,
            obstacle_rect.y + 10,
            60,
            60
        )

        if deer_rect.colliderect(obstacle_hitbox):

            lives -= 1

            # Respawn nearby instead of restarting the whole level
            deer_x = obstacle_rect.x - 250
            deer_y = 400

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
    if score >= 10:

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
            screen.blit(deer_platform2, (draw_x, platform_rect.y))
        else:
            screen.blit(deer_platform, (draw_x, platform_rect.y))

    # obstacles
    for obstacle_rect in obstacles:
        screen.blit(obstacle, (obstacle_rect.x - camera_x, obstacle_rect.y))

    # berries
    for berry_rect in berries:
        screen.blit(berry, (berry_rect.x - camera_x, berry_rect.y))

    # deer (fixed position on screen)
    screen.blit(deer, (deer_x - camera_x, deer_y))

    # UI
    screen.blit(font.render(f"Lives: {lives}", True, (255,255,255)), (20,20))
    screen.blit(font.render(f"Berries: {score}/10", True, (255,255,255)), (20,70))

    pygame.display.update()

pygame.quit()