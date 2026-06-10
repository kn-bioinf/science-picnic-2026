# Bieg na mikrotubuli: omijaj przeszkody Tau, SPACE = skok.

import random
import pygame
import src.config as config


class Stage3:
    """
    Etap 3: bieg na mikrotubuli (runner – omijaj przeszkody, SPACE = skok).

    Interfejs:
        __init__(screen, state, next_fn)
        self.next(score: int)  – wywolaj gdy etap skonczony
    """

    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state = state
        self.next = next_fn
        self._btn = pygame.Rect(0, 0, 180, 48)

        self._distance = 0.0
        self._score = 0
        self._game_over = False
        self._obstacles = []
        self._next_spawn_distance = 0.0

        self._runner_w = 72
        self._runner_h = 54
        self._runner_x = 0
        self._runner_y = 0
        self._ground_y = 0
        self._vy = 0.0
        self._jump_speed = -850.0
        self._gravity = 2200.0

        self._speed = 400.0
        self._speed_growth = 12.0

        self._setup_layout()

    def _setup_layout(self):
        w, h = config.get_size()
        self._runner_x = int(w * 0.20)
        self._ground_y = h - 140
        self._runner_y = self._ground_y - self._runner_h
        self._next_spawn_distance = 0.0

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            if not self._game_over and self._runner_y >= self._ground_y - self._runner_h:
                self._vy = self._jump_speed
        if e.type == pygame.MOUSEBUTTONDOWN and self._game_over and self._btn.collidepoint(e.pos):
            self.next(self._score)

    def _spawn_obstacle(self, w, h):
        obstacle_w = 50
        obstacle_h = random.randint(50, 80)
        obstacle_y = self._ground_y - obstacle_h
        rect = pygame.Rect(w + 20, obstacle_y, obstacle_w, obstacle_h)
        self._obstacles.append({"rect": rect, "passed": False})

    def update(self, dt):
        if self._game_over:
            return

        w, h = config.get_size()
        self._distance += self._speed * dt
        self._speed = 400.0 + min(450.0, self._distance * 0.01)

        if self._distance >= self._next_spawn_distance:
            self._spawn_obstacle(w, h)
            spawn_distance = self._speed * random.uniform(0.85, 1.7) * (1.0 - self._distance * 0.00001)
            self._next_spawn_distance = self._distance + spawn_distance
            print(spawn_distance, self._speed)

        self._runner_y += self._vy * dt
        self._vy += self._gravity * dt
        if self._runner_y >= self._ground_y - self._runner_h:
            self._runner_y = self._ground_y - self._runner_h
            self._vy = 0.0

        runner_rect = pygame.Rect(self._runner_x, int(self._runner_y), self._runner_w, self._runner_h)
        remaining = []
        for item in self._obstacles:
            rect = item["rect"]
            rect.x -= int(self._speed * dt)
            if rect.right >= 0:
                if rect.right < self._runner_x and not item["passed"]:
                    item["passed"] = True
                    self._score += 1
                remaining.append(item)
        self._obstacles = remaining

        for item in self._obstacles:
            if runner_rect.colliderect(item["rect"]):
                self._game_over = True
                break

    def draw(self):
        w, h = config.get_size()
        if not self._runner_x:
            self._setup_layout()

        self.screen.fill(config.BG)

        # microtubule track
        track_y = self._ground_y + 24
        pygame.draw.rect(self.screen, config.MUTED, (0, self._ground_y, w, 6))
        for offset in range(0, w, 80):
            pygame.draw.rect(self.screen, config.ACCENT, (offset, track_y, 48, 14), border_radius=4)

        # kinesin runner
        runner_rect = pygame.Rect(self._runner_x, int(self._runner_y), self._runner_w, self._runner_h)
        pygame.draw.ellipse(self.screen, config.ACCENT, runner_rect)
        head = pygame.Rect(self._runner_x + 10, int(self._runner_y) + 8, 18, 18)
        pygame.draw.circle(self.screen, config.WHITE, head.center, 10)
        pygame.draw.line(self.screen, config.WHITE, (self._runner_x + 18, int(self._runner_y) + 24), (self._runner_x + 32, int(self._runner_y) + 38), 4)

        # Tau obstacles
        for item in self._obstacles:
            rect = item["rect"]
            pygame.draw.rect(self.screen, (128, 90, 170), rect, border_radius=10)
            label = config.font(18, bold=True).render("Tau", True, config.WHITE)
            self.screen.blit(label, label.get_rect(center=rect.center))

        # HUD
        title = config.font(36, bold=True).render("Kinezyna na mikrotubuli", True, config.TEXT)
        self.screen.blit(title, (30, 28))
        score_text = config.font(28).render(f"Punkty: {self._score}", True, config.ACCENT)
        self.screen.blit(score_text, (30, 76))
        dist_text = config.font(22).render("SPACE: skok", True, config.MUTED)
        self.screen.blit(dist_text, (30, 116))
        speed_text = config.font(22).render(f"Przebyta odległość: {int(self._distance // 10)}", True, config.MUTED)
        self.screen.blit(speed_text, (30, 146))

        if self._game_over:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 35, 160))
            self.screen.blit(overlay, (0, 0))

            msg = config.font(48, bold=True).render("Kolizja z Tau!", True, config.WHITE)
            self.screen.blit(msg, msg.get_rect(center=(w // 2, h // 2 - 60)))

            detail = config.font(24).render(f"Twój wynik: {self._score}", True, config.WHITE)
            self.screen.blit(detail, detail.get_rect(center=(w // 2, h // 2)))

            self._btn.center = (w // 2, h // 2 + 96)
            pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
            button_label = config.font(22, bold=True).render("Dalej", True, config.WHITE)
            self.screen.blit(button_label, button_label.get_rect(center=self._btn.center))
