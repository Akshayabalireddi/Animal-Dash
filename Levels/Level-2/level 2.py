import pygame

pygame.init()

# ------------------------
# SCREEN
# ------------------------
WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Dash - Level 2")

clock = pygame.time.Clock()

# ------------------------
# IMAGES
# ------------------------
background = pygame.image.load("deer_background.png").convert()

deer = pygame.image.load("deer_assets_deer.png").convert_alpha()

deer_platform = pygame.image.load(
    "deer_assets_platform.png"
).convert_alpha()

deer_platform2 = pygame.image.load(
    "deer_assets_platform2.png"
).convert_alpha()

obstacle = pygame.image.load(
    "deer_assets_obstcales.png"
).convert_alpha()

berry = pygame.image.load(
    "deer_assets-food.png"
).convert_alpha()

# ------------------------
# SCALE IMAGES
# ------------------------
deer = pygame.transform.scale(deer, (140, 140))

deer_platform = pygame.transform.scale(
    deer_platform,
    (220, 90)
)

deer_platform2 = pygame.transform.scale(
    deer_platform2,
    (450, 90)
)

obstacle = pygame.transform.scale(
    obstacle,
    (80, 80)
)

berry = pygame.transform.scale(
    berry,
    (70, 70)
)

# ------------------------
# PLAYER
# ------------------------
deer_x = 100
deer_y = 450

player_width = 140
player_height = 140

velocity_y = 0
gravity = 1
jump_power = -18
on_ground = False

# ------------------------
# SCORE & LIVES
# ------------------------
lives = 3
score = 0

font = pygame.font.Font(None, 50)

# ------------------------
# PLATFORMS
# ------------------------
platforms = [
    ("long", pygame.Rect(0, 620, 450, 90)),
    ("small", pygame.Rect(500, 450, 220, 90)),
    ("long", pygame.Rect(780, 620, 450, 90)),
    ("small", pygame.Rect(1040, 450, 220, 90)),

    ("long", pygame.Rect(1400, 620, 450, 90)),
    ("small", pygame.Rect(1900, 450, 220, 90)),
    ("long", pygame.Rect(2300, 620, 450, 90))
]

# ------------------------
# BERRIES
# ------------------------
berries = [
    pygame.Rect(570, 370, 70, 70),
    pygame.Rect(860, 540, 70, 70),
    pygame.Rect(1110, 370, 70, 70)
]

# ------------------------
# OBSTACLES
# ------------------------
obstacles = [
    pygame.Rect(870, 540, 80, 80)
]
camera_x = 0
# ------------------------
# GAME LOOP
# ------------------------
running = True

while running:

    clock.tick(60)

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_w and on_ground:
                velocity_y = jump_power
                on_ground = False

    # ------------------------
    # MOVEMENT
    # ------------------------
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        deer_x -= 5

    if keys[pygame.K_d]:
        deer_x += 5
        camera_x = deer_x - 300

    if camera_x < 0:
        camera_x = 0

    # GRAVITY
    velocity_y += gravity
    deer_y += velocity_y

    deer_rect = pygame.Rect(
        deer_x,
        deer_y,
        player_width,
        player_height
    )

    on_ground = False

    # PLATFORM COLLISION
    for platform_type, platform_rect in platforms:

        if deer_rect.colliderect(platform_rect):

            if velocity_y > 0:
                deer_y = platform_rect.top - player_height
                velocity_y = 0
                on_ground = True

    # FALL OFF MAP
    if deer_y > HEIGHT:
        deer_x = 100
        deer_y = 450

    deer_rect = pygame.Rect(
        deer_x,
        deer_y,
        player_width,
        player_height
    )

    # ------------------------
    # BERRY COLLECTION
    # ------------------------
    for berry_rect in berries[:]:

        if deer_rect.colliderect(berry_rect):
            berries.remove(berry_rect)
            score += 1

    # ------------------------
    # OBSTACLE COLLISION
    # ------------------------
    for obstacle_rect in obstacles:

        if deer_rect.colliderect(obstacle_rect):

            lives -= 1

            deer_x = 100
            deer_y = 450

            pygame.time.delay(300)

    # GAME OVER
    if lives <= 0:
        print("GAME OVER")
        running = False

    # WIN
    if score == 3:
        print("YOU WIN!")
        running = False

    # ------------------------
    # DRAW
    # ------------------------
    screen.blit(background, (-camera_x * 0.2, 0))

    for platform_type, platform_rect in platforms:

        draw_x = platform_rect.x - camera_x

        if platform_type == "long":
            screen.blit(deer_platform2, (draw_x, platform_rect.y))
        else:
            screen.blit(deer_platform, (draw_x, platform_rect.y))

    for obstacle_rect in obstacles:
        screen.blit(
            obstacle,
            (obstacle_rect.x - camera_x,
             obstacle_rect.y)
    )

    for berry_rect in berries:
        screen.blit(
            berry,
            (berry_rect.x - camera_x,
            berry_rect.y)
    )

    screen.blit(deer, (300, deer_y))

    lives_text = font.render(
        f"Lives: {lives}",
        True,
        (255, 255, 255)
    )

    score_text = font.render(
        f"Berries Collected: {score}/3",
        True,
        (255, 255, 255)
    )

    screen.blit(lives_text, (20, 20))
    screen.blit(score_text, (20, 70))

    pygame.display.update()

pygame.quit()
