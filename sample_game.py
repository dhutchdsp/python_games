# Import the pygame module
import pygame
# Import random for random numbers
import random
import time

import math
wave_counter = 0.0

clock = pygame.time.Clock()

FPS = 60
RESPAWN_TIME_SEC = 2
RESPAWN_COUNTER_TICKS = FPS * RESPAWN_TIME_SEC

LEVEL_FONT_SIZE = 96

LEVEL_TIME_MS = 10000

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000

# Difficulty
difficulty_level = 0
wait_between_levels_counter = 0
waiting_between_levels = False

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
TEAL = (0, 255, 255)
BLUE  = (0, 0, 255)
PURPLE = (255, 0, 255)
RED = (255, 100, 100)
GREY = (150, 150, 150)
RED_GREEN = (255, 255, 0)

# ENEMY DIFFICULTY COLOR ARRAY
e_level_color = [
    GREEN,
    TEAL,
    BLUE,
    PURPLE,
    GREY,
    RED_GREEN,
    RED,
    RED,
    RED,
    RED,
    RED
]

# Initialize pygame
pygame.init()

# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.dead = False

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if not self.dead:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -5)
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, 5)
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

            # Keep player on the screen
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
            

    def respawn(self):
        self.surf.fill((255, 255, 255))
        self.rect.left = 0
        self.rect.top = 0
        self.dead = False

    def die(self):
        self.surf.fill((255, 0, 0))
        self.dead = True


# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill(e_level_color[difficulty_level])
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(2, 5) * (difficulty_level + 1)
        self.rand_id = random.randint(0,100)
        self.osc_rand_min = (difficulty_level) * 2
        self.rand_osc_amp = random.randint(self.osc_rand_min, self.osc_rand_min + difficulty_level)
        self.rand_osc_speed = random.randint(0,20)/20 * difficulty_level

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, math.sin(self.rand_id + wave_counter * self.rand_osc_speed) * self.rand_osc_amp)
        if self.rect.right < 0:
            self.kill()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

spawn_enemies = False

############### Events ################
# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 500)

# Create event for raising difficulty
LEVELUP = pygame.USEREVENT + 2
pygame.time.set_timer(LEVELUP, LEVEL_TIME_MS)

# Create event for respawning
RESPAWN = pygame.USEREVENT + 3

# Event for turning on enemies
ENEMIES_WILL_TURN_ON = pygame.USEREVENT + 4
pygame.time.set_timer(ENEMIES_WILL_TURN_ON, LEVEL_TIME_MS // 3)

ENEMIES_WILL_TURN_OFF = pygame.USEREVENT + 5

# Instantiate player. Right now, this is just a rectangle.
player = Player()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Difficulty Text
t0 = time.time()
font = pygame.font.SysFont(None, LEVEL_FONT_SIZE)
img = font.render("Level: " + str(difficulty_level), True, e_level_color[difficulty_level])

# Variable to keep the main loop running
running = True

# START GAME
player.respawn()

# Main loop
while running:
    clock.tick(FPS)
    # Math counter update
    wave_counter += .1
    wave = math.sin(wave_counter)


    pressed_keys = pygame.key.get_pressed()

    # Player Actions
    
    # Get the set of keys pressed and check for user input
    player.update(pressed_keys)

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies) and not player.dead:
        # If so, then remove the player and stop the loop
        player.die()
        pygame.time.set_timer(RESPAWN, 3000)
        spawn_enemies = False
        pygame.time.set_timer(ENEMIES_WILL_TURN_OFF, 0)
        

    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False

        # Add a new enemy?
        elif event.type == ADDENEMY:
            if spawn_enemies:
                # Create the new enemy and add it to sprite groups
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        elif event.type == LEVELUP:
            if not player.dead:
                difficulty_level += 1
                img = font.render("Level: " + str(difficulty_level), True, e_level_color[difficulty_level])
                pygame.time.set_timer(ADDENEMY, 500 // difficulty_level + 1)
                spawn_enemies = False
                pygame.time.set_timer(ENEMIES_WILL_TURN_ON, LEVEL_TIME_MS // 3)

        elif event.type == RESPAWN:
            player.respawn()
            pygame.time.set_timer(RESPAWN, 0)
            pygame.time.set_timer(LEVELUP, 0)
            pygame.time.set_timer(LEVELUP, LEVEL_TIME_MS)
            pygame.time.set_timer(ENEMIES_WILL_TURN_ON, LEVEL_TIME_MS // 3)
            pygame.time.set_timer(ADDENEMY, 500)
            difficulty_level = 0
            img = font.render("Level: " + str(difficulty_level), True, e_level_color[difficulty_level])

        elif event.type == ENEMIES_WILL_TURN_ON:
            spawn_enemies = True
            pygame.time.set_timer(ENEMIES_WILL_TURN_ON, 0)
            pygame.time.set_timer(ENEMIES_WILL_TURN_OFF, LEVEL_TIME_MS // 3)

        elif event.type == ENEMIES_WILL_TURN_OFF:
            spawn_enemies = False
            pygame.time.set_timer(ENEMIES_WILL_TURN_OFF, 0)
    
    # Update enemy position
    enemies.update()

    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    screen.blit(img, (SCREEN_WIDTH - (3 * LEVEL_FONT_SIZE), 20))

    # Update the display
    pygame.display.flip()

