import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 144

WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
CYAN = (0, 255, 255)
RED = (255, 70, 70)
GREEN = (80, 255, 120)
GOLD = (255, 215, 0)

BALL_TYPES = {"good": GREEN, "bad": RED, "gold": GOLD}

FONT = pygame.font.SysFont("arial", 28)
BIG_FONT = pygame.font.SysFont("arial", 72)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Color Catcher")
clock = pygame.time.Clock()

PARTICLE_SURFACE = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(PARTICLE_SURFACE, WHITE, (10, 10), 4)


class Particle:
    def __init__(self, pos, color):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(120, 420)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel.y += 600 * dt

    def draw(self, surf):
        alpha = max(0, int(255 * self.life))
        img = PARTICLE_SURFACE.copy()
        img.fill((*self.color, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, self.pos)


class FallingObject:
    def __init__(self, width):
        self.radius = random.randint(18, 24)
        self.type = random.choices(["good", "bad", "gold"], weights=[3, 1, 1])[0]
        self.color = BALL_TYPES[self.type]
        self.pos = pygame.Vector2(random.randint(self.radius, width - self.radius), -50)
        self.vel = pygame.Vector2(0, random.randint(250, 500))
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, self.pos, self.radius)

    def offscreen(self, height):
        return self.pos.y > height + 100


class Basket:
    def __init__(self, width, height):
        self.base_size = pygame.Vector2(120, 22)
        self.pos = pygame.Vector2(width // 2, height - 80)
        self.vel_x = 0
        self.acc = 3500
        self.max_speed = 900
        self.rect = pygame.Rect(0, 0, self.base_size.x, self.base_size.y)
        self.rect.center = self.pos
        self.scale = pygame.Vector2(1, 1)
        self.shake_offset = pygame.Vector2(0, 0)
        self.red_flash_time = 0       
        self.red_flash_duration = 0.15  

    def hit_juice(self):
        self.scale = pygame.Vector2(1.6, 0.6)
    
    def red_hit(self):
        self.red_flash_time = self.red_flash_duration

    def update(self, dt, width, height):
        keys = pygame.key.get_pressed()
        direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.vel_x += direction * self.acc * dt
        self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))
        self.vel_x -= self.vel_x * 8 * dt
        self.pos.x += self.vel_x * dt
        self.pos.x += (pygame.mouse.get_pos()[0] - self.pos.x) * (1 - math.exp(-12 * dt))
        self.pos.x = max(self.base_size.x / 2, min(width - self.base_size.x / 2, self.pos.x))
        self.pos.y = height - 80
        self.scale += (pygame.Vector2(1, 1) - self.scale) * 10 * dt
        self.rect.center = self.pos

    def draw(self, surf):
        w, h = self.base_size.x * self.scale.x, self.base_size.y * self.scale.y
        rect = pygame.Rect(0, 0, w, h)
        rect.center = self.pos + self.shake_offset
        color = CYAN
        if self.red_flash_time > 0:
            color = RED  # flash red
            self.red_flash_time -= 1 / FPS

        pygame.draw.rect(surf, color, rect, border_radius=12)


class Game:
    def __init__(self):
        self.reset()
        self.shake_time = 0
        self.shake_strength = 0
        self.stars = [(random.randint(0, WIDTH),
                    random.randint(0, HEIGHT),
                    random.randint(1, 3),
                    random.randint(150, 255)) for _ in range(150)]

    def reset(self):
        self.basket = Basket(WIDTH, HEIGHT)
        self.objects = []
        self.particles = []
        self.spawn_timer = 0
        self.score = 0
        self.lives = 5
        self.game_over = False

    def add_shake(self, strength=10, time=0.25):
        self.shake_strength = strength
        self.shake_time = time

    def apply_shake(self):
        if self.shake_time > 0:
            self.shake_time -= 1 / FPS
            return pygame.Vector2(random.uniform(-self.shake_strength, self.shake_strength),
                                  random.uniform(-self.shake_strength, self.shake_strength))
        return pygame.Vector2(0, 0)

    def spawn(self):
        self.objects.append(FallingObject(self.width))

    def update(self, dt):
        if self.game_over:
            return

        self.basket.update(dt, self.width, self.height)

        self.spawn_timer += dt
        if self.spawn_timer >= max(0.15, 0.5 - self.score * 0.005):
            self.spawn()
            self.spawn_timer = 0

        new_objects = []
        for obj in self.objects:
            obj.update(dt)
            if self.basket.rect.colliderect(obj.rect):
                if obj.type == "good" or obj.type == "gold":
                    self.basket.hit_juice()
                # Red: flash + shake + lose life
                elif obj.type == "bad":
                    self.basket.red_hit()
                    self.add_shake(16)
                    self.lives -= 1

                # Particle effects for all types
                self.particles.extend([Particle(obj.pos, obj.color) for _ in range(20)])

                # Score handling
                if obj.type == "good":
                    self.score += 1
                elif obj.type == "gold":
                    self.score += 5
            elif not obj.offscreen(self.height):
                new_objects.append(obj)
        self.objects = new_objects

        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update(dt)

        if self.lives <= 0:
            self.game_over = True

    def draw(self, surf):
        shake = self.apply_shake()
        surf.fill(BLACK)

        t = pygame.time.get_ticks() * 0.002  
        for i, (x, y, radius, brightness) in enumerate(self.stars):
            twinkle = int(brightness * (0.5 + 0.5 * math.sin(t + i)))
            pygame.draw.circle(surf, (twinkle, twinkle, twinkle), (int(x + shake.x), int(y + shake.y)), radius)

        for obj in self.objects:
            obj.draw(surf)

        for p in self.particles:
            p.draw(surf)

        self.basket.shake_offset = shake
        self.basket.draw(surf)

        surf.blit(FONT.render(f"Score: {self.score}", True, WHITE), (20, 20))
        surf.blit(FONT.render(f"Lives: {self.lives}", True, RED), (20, 60))

        if self.game_over:
            over = BIG_FONT.render("GAME OVER", True, RED)
            restart = FONT.render("Press R to Restart", True, WHITE)
            surf.blit(over, (self.width // 2 - over.get_width() // 2, self.height // 2 - 80))
            surf.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 20))

    def handle_events(self):
        global WIDTH, HEIGHT, screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
        return True

    @property
    def width(self):
        return WIDTH

    @property
    def height(self):
        return HEIGHT


game = Game()
running = True

while running:
    dt = clock.tick(FPS) / 1000
    running = game.handle_events()
    game.update(dt)
    game.draw(screen)
    pygame.display.flip()

pygame.quit()