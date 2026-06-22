
import pygame
import random
from os.path import join

#  SETUP 
pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Animal Dash")

clock = pygame.time.Clock()
running = True

#  BACKGROUND 
background = pygame.image.load(
    join("Levels/Level-3/images/whale_background.png")
).convert()

background = pygame.transform.scale(
    background,
    WINDOW_SIZE
)

bg_width = background.get_width()

#  PLAYER 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load(
            join("Levels/Level-3/images/whale.png")
        ).convert_alpha()

        self.rect = self.image.get_rect(center=(200, 350))

        self.pos = pygame.Vector2(self.rect.center)

        self.direction = pygame.Vector2()
        self.speed = 300

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

        self.rect.center = self.pos
        
        

        #self.image = pygame.image.load(
           # join("images", "bottle_whale.png")
        #).convert_alpha()


class Bottle(pygame.sprite.Sprite):
         def __init__(self):
            super().__init__()

    
            self.image = pygame.image.load(
            join("images", "bottle_whale.png")
        ).convert_alpha()

    



        #  BUBBLES 

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

        self.world_x = random.randint(0, 5000)
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

            # SPRITES 
player = Player()

all_sprites = pygame.sprite.Group()
bubble_group = pygame.sprite.Group()

all_sprites.add(player)

#  BUBBLE TIMER 
bubble_timer = 0

#  GAME LOOP 
while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn bubbles
    bubble_timer += dt

    if bubble_timer > 0.15:
        bubble = Bubble()

        bubble.world_x = player.pos.x + random.randint(-800, 800)

        bubble_group.add(bubble)

        bubble_timer = 0
         
         
    # Update
    player.update(dt)
    bubble_group.update(dt)

    # Camera follows whale
    camera_x = player.rect.centerx - WINDOW_WIDTH // 3

    # Draw repeating background
    start_x = -(camera_x % bg_width)

    screen.blit(background, (start_x, 0))
    screen.blit(background, (start_x + bg_width, 0))

    # Draw bubbles
    for bubble in bubble_group:
        screen.blit(
            bubble.image,
            (
                bubble.rect.x - camera_x,
                bubble.rect.y
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

   
    pygame.display.flip()

pygame.quit()