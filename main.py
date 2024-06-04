import pygame
import sys
import random

# Initialiseer Pygame
pygame.init()

# Scherminstellingen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platform Game")

# Kleuren
LIGHT_BLUE = (173, 216, 230)
GRASS_GREEN = (20, 125, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Speler instellingen
small_size = 50
large_size = 100
player_color = (0, 0, 255)
player_x = 50
player_y = SCREEN_HEIGHT - small_size - 50
player_speed = 5
player_velocity_y = 0
gravity = 0.5
jump_strength = -10
max_jumps = 2
jumps_left = max_jumps
is_large = False

# Vijand instellingen
enemy_size = 50
enemy_color = (255, 0, 0)
enemy_speed = 3

# Power-up instellingen
powerup_size = 30
powerup_color = (0, 255, 0)
fixed_powerup_x = SCREEN_WIDTH + 100
fixed_powerup_y = SCREEN_HEIGHT - powerup_size - 250

# Eindpunt instellingen
end_x = 1500
end_y = SCREEN_HEIGHT - small_size - 350
end_size = 50
end_height = 350
end_color = (255, 255, 0)

# Speler klasse
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = small_size
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(player_color)
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.velocity_y = 0
        self.jumps_left = max_jumps
        self.is_large = False

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += player_speed

        self.velocity_y += gravity
        self.rect.y += self.velocity_y

        if self.rect.y >= SCREEN_HEIGHT - self.size - 50:
            self.rect.y = SCREEN_HEIGHT - self.size - 50
            self.velocity_y = 0
            self.jumps_left = max_jumps

    def jump(self):
        if self.jumps_left > 0:
            self.velocity_y = jump_strength
            self.jumps_left -= 1

    def grow(self):
        self.is_large = True
        self.size = large_size
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(player_color)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shrink(self):
        self.is_large = False
        self.size = small_size
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(player_color)
        self.rect = self.image.get_rect(center=self.rect.center)

# Vijand klasse
class Enemy(pygame.sprite.Sprite):
    def __init__(self, camera_x):
        super().__init__()
        self.image = pygame.Surface((enemy_size, enemy_size))
        self.image.fill(enemy_color)
        self.rect = self.image.get_rect()
        self.spawn_outside_screen(camera_x)
        self.speed = enemy_speed

    def spawn_outside_screen(self, camera_x):
        self.rect.x = camera_x + SCREEN_WIDTH + random.randint(50, 100)
        self.rect.y = SCREEN_HEIGHT - enemy_size - 50

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Power-up klasse
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, camera_x):
        super().__init__()
        self.image = pygame.Surface((powerup_size, powerup_size))
        self.image.fill(powerup_color)
        self.rect = self.image.get_rect()
        self.spawn_outside_screen(camera_x)

    def spawn_outside_screen(self, camera_x):
        self.rect.x = camera_x + fixed_powerup_x
        self.rect.y = fixed_powerup_y

    def update(self):
        self.rect.x -= enemy_speed
        if self.rect.right < 0:
            self.kill()

# Spel loop
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

camera_x = 0

# Voeg een vaste power-up toe aan het begin
initial_powerup = PowerUp(camera_x)
all_sprites.add(initial_powerup)
powerups.add(initial_powerup)

# Timer voor vijanden
enemy_spawn_timer = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    keys = pygame.key.get_pressed()
    player.update(keys)

    # Update timer
    enemy_spawn_timer += 1

    # Spawn vijanden elke 2 seconden
    if enemy_spawn_timer >= 60:  # 30 FPS * 2 seconden
        enemy = Enemy(camera_x)
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_timer = 0

    enemies.update()
    powerups.update()

    # Camera scrollen
    if player.rect.x > SCREEN_WIDTH // 2:
        camera_x = player.rect.x - SCREEN_WIDTH // 2

    # Collision detection
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            if player.velocity_y > 0 and player.rect.bottom <= enemy.rect.top + 10:
                enemy.kill()
                player.velocity_y = jump_strength
            else:
                if player.is_large:
                    player.shrink()
                    enemy.kill()
                else:
                    print("Game Over")
                    running = False

    for powerup in powerups:
        if player.rect.colliderect(powerup.rect):
            player.grow()
            powerup.kill()

    # Scherm bijwerken
    screen.fill(LIGHT_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
    pygame.draw.rect(screen, end_color, (end_x - camera_x, end_y, end_size, end_height))

    if player.rect.right > end_x:
        print("Je hebt gewonnen!")
        running = False

    pygame.display.flip()
    pygame.time.Clock().tick(30)