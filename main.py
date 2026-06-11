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


def circle_rect_collision(circle_pos, radius, rect):
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    dx = circle_pos.x - closest_x
    dy = circle_pos.y - closest_y
    return dx * dx + dy * dy <= radius * radius


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
        if self.life <= 0:
            return
        alpha = max(0, int(255 * self.life))
        temp = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(temp, (*self.color, alpha), (4, 4), 4)
        surf.blit(temp, (int(self.pos.x - 4), int(self.pos.y - 4)))


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
        self.rect.size = (self.radius * 2, self.radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def offscreen(self, height):
        return self.pos.y > height + 100


class Basket:
    def __init__(self, width, height):
        self.base_size = pygame.Vector2(120, 22)
        self.pos = pygame.Vector2(width // 2, height - 80)

        self.speed = 900
        self.rect = pygame.Rect(0, 0, self.base_size.x, self.base_size.y)
        self.scale = pygame.Vector2(1, 1)

        self.red_flash_time = 0
        self.red_flash_duration = 0.15

        self.shake_offset = pygame.Vector2(0, 0)

        # ✅ CONTROL STATE
        self.mode = "mouse"
        self.last_mouse_x = pygame.mouse.get_pos()[0]

    def hit_juice(self):
        self.scale = pygame.Vector2(1.6, 0.6)

    def red_hit(self):
        self.red_flash_time = self.red_flash_duration

    def update(self, dt, width, height):
        keys = pygame.key.get_pressed()
        mouse_x = pygame.mouse.get_pos()[0]

        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]

        keyboard_used = left or right

        # detect real mouse movement
        mouse_moved = abs(mouse_x - self.last_mouse_x) > 5
        self.last_mouse_x = mouse_x

        # -----------------------------
        # MODE SWITCH (STRICT)
        # -----------------------------

        if keyboard_used:
            self.mode = "keyboard"
        elif mouse_moved:
            self.mode = "mouse"

        # -----------------------------
        # MOVEMENT (NO MIXING)
        # -----------------------------

        if self.mode == "keyboard":
            direction = right - left
            self.pos.x += direction * self.speed * dt
        else:
            self.pos.x = mouse_x

        # -----------------------------
        # clamp
        # -----------------------------

        half_w = (self.base_size.x * self.scale.x) / 2
        self.pos.x = max(half_w, min(width - half_w, self.pos.x))
        self.pos.y = height - 80

        # -----------------------------
        # effects
        # -----------------------------

        self.scale += (pygame.Vector2(1, 1) - self.scale) * 10 * dt
        self.red_flash_time = max(0, self.red_flash_time - dt)

        w = self.base_size.x * self.scale.x
        h = self.base_size.y * self.scale.y
        self.rect.size = (int(w), int(h))
        self.rect.center = self.pos


class Game:
    def __init__(self):
        self.reset()
        self.shake_time = 0
        self.shake_strength = 0

        self.stars = self.generate_stars(WIDTH, HEIGHT)

    def generate_stars(self, w, h):
        return [
            (random.randint(0, w), random.randint(0, h),
             random.randint(1, 3), random.randint(150, 255))
            for _ in range(150)
        ]

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

    def apply_shake(self, dt):
        if self.shake_time > 0:
            self.shake_time -= dt
            return pygame.Vector2(
                random.uniform(-self.shake_strength, self.shake_strength),
                random.uniform(-self.shake_strength, self.shake_strength)
            )
        return pygame.Vector2()

    def spawn(self):
        self.objects.append(FallingObject(WIDTH))

    def update(self, dt):
        if self.game_over:
            return

        self.basket.update(dt, WIDTH, HEIGHT)

        self.spawn_timer += dt
        spawn_delay = max(0.08, 0.5 * math.exp(-self.score * 0.01))

        while self.spawn_timer >= spawn_delay:
            self.spawn()
            self.spawn_timer -= spawn_delay

        new_objects = []

        for obj in self.objects:
            obj.update(dt)

            if circle_rect_collision(obj.pos, obj.radius, self.basket.rect):
                if obj.type in ("good", "gold"):
                    self.basket.hit_juice()
                else:
                    self.basket.red_hit()
                    self.add_shake(16)
                    self.lives -= 1

                self.particles.extend([Particle(obj.pos, obj.color) for _ in range(20)])

                if obj.type == "good":
                    self.score += 1
                elif obj.type == "gold":
                    self.score += 10

            elif not obj.offscreen(HEIGHT):
                new_objects.append(obj)

        self.objects = new_objects

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        if self.lives <= 0:
            self.game_over = True

    def draw(self, surf, dt):
        shake = self.apply_shake(dt)
        surf.fill(BLACK)

        t = pygame.time.get_ticks() * 0.002
        for i, (x, y, r, b) in enumerate(self.stars):
            twinkle = int(b * (0.5 + 0.5 * math.sin(t + i)))
            pygame.draw.circle(
                surf,
                (twinkle, twinkle, twinkle),
                (int(x + shake.x), int(y + shake.y)),
                r
            )

        for obj in self.objects:
            obj.draw(surf)

        for p in self.particles:
            p.draw(surf)

        self.basket.shake_offset = shake
        self.basket.draw = lambda s: pygame.draw.rect(
            s,
            RED if self.basket.red_flash_time > 0 else CYAN,
            self.basket.rect.move(self.basket.shake_offset),
            border_radius=12
        )
        self.basket.draw(surf)

        surf.blit(FONT.render(f"Score: {self.score}", True, WHITE), (20, 20))
        surf.blit(FONT.render(f"Lives: {self.lives}", True, RED), (20, 60))

        if self.game_over:
            over = BIG_FONT.render("GAME OVER", True, RED)
            restart = FONT.render("Press R to Restart", True, WHITE)

            surf.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 80))
            surf.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 20))

    def handle_events(self):
        global WIDTH, HEIGHT, screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

                self.stars = self.generate_stars(WIDTH, HEIGHT)

                self.basket.pos.y = HEIGHT - 80

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()

        return True


game = Game()
running = True

while running:
    dt = min(clock.tick(FPS) / 1000, 1 / 30)
    running = game.handle_events()
    game.update(dt)
    game.draw(screen, dt)
    pygame.display.flip()

pygame.quit()