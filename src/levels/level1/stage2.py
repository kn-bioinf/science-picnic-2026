#TODO: komentarze w kodzie, oprawa graficzna, zmienienie upuszczania żeby było bardziej smooth;

import math
import random
import pygame
import src.config as config


class Stage2:
    """
    Etap 2: docking ATP (refleksowka – kliknij w odpowiednim momencie).

    Interfejs:
        __init__(screen, state, next_fn)
        self.next(score: int)  – wywolaj gdy etap skonczony
    """
    #Definiujemy ligandy
    OBJECTS = [
        {"name": "Pęcherzyk", "color": (134, 190, 240)},
        {"name": "Mitochondrium", "color": (220, 140, 70)},
        {"name": "Lizosom", "color": (175, 95, 200)},
        {"name": "Chloroplast", "color": (80, 175, 95)},
    ]

    #Ustawienia przy inicjowaniu
    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state = state
        self.next = next_fn
        self._btn = pygame.Rect(0, 0, 180, 48)

        self._line_y = 0
        self._min_x = 0
        self._max_x = 0
        self._anchor_x = 0
        self._anchor_y = 0
        self._pos = [0.0, 0.0]
        self._vel = [0.0, 0.0]
        self._direction = 1
        self._line_speed = 280.0
        self._gravity = 1400.0

        self._released = False
        self._hit = False
        self._failed = False
        self._score = 0

        self._target = None
        self._object_type = None
        self._object_color = None
        self._setup_board()

    #Ustawienia planszy, pozycji i celu
    def _setup_board(self):
        w, h = config.get_size()
        self._line_y = int(h * 0.20)
        self._min_x = int(w * 0.14)
        self._max_x = int(w * 0.86)
        self._direction = random.choice([-1, 1])
        self._released = False
        self._hit = False
        self._failed = False
        self._target = pygame.Rect(int(w * random.uniform(0.25, 0.75)), int(h * 0.68), 140, 46)

        self._choose_object()
        self._anchor_x = int(w * random.uniform(0.35, 0.65))
        self._anchor_y = self._line_y
        self._pos = [float(self._anchor_x), float(self._anchor_y)]
        self._vel = [0.0, 0.0]

    #Wybór ligandu do upuszczenia
    def _choose_object(self):
        choice = random.choice(self.OBJECTS)
        self._object_type = choice["name"]
        self._object_color = choice["color"]

    #Obsługa zdarzeń - spacja do upuszczenia, kliknięcie w przycisk po pominięciu celu
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self._released and not self._hit and not self._failed:
            self._released = True
            self._vel = [0.0, 0.0]
        if e.type == pygame.MOUSEBUTTONDOWN and self._failed and self._btn.collidepoint(e.pos):
            self.next(self._score)

    #Aktualizacja pozycji ligandu, sprawdzanie kolizji z celem i obsługa końca gry
    def update(self, dt):
        if self._hit or self._failed:
            return

        w, h = config.get_size()
        if not self._released:
            new_x = self._anchor_x + self._direction * (self._line_speed + (self._score*14.0)) * dt
            if new_x < self._min_x:
                new_x = self._min_x
                self._direction = 1
            elif new_x > self._max_x:
                new_x = self._max_x
                self._direction = -1
            self._anchor_x = new_x
            self._pos[0] = self._anchor_x
            self._pos[1] = self._anchor_y
        else:
            self._vel[1] += self._gravity * dt
            self._pos[0] += self._vel[0] * dt
            self._pos[1] += self._vel[1] * dt

            if self._target.collidepoint(int(self._pos[0]), int(self._pos[1])):
                self._hit = True
                self._score += 1
                self._setup_board()
            elif self._pos[1] > h + 20:
                self._failed = True

    #Rysowanie ligandu
    def _draw_object(self, x, y):
        color = self._object_color
        if self._object_type == "Pęcherzyk":
            pygame.draw.circle(self.screen, color, (x, y), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (x - 6, y - 6), 6)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 8, y - 8), 4)
        elif self._object_type == "Mitochondrium":
            pygame.draw.ellipse(self.screen, color, (x - 24, y - 16, 48, 32))
            for offset in (-12, -6, 0, 6, 12):
                pygame.draw.line(self.screen, (160, 90, 50), (x + offset, y - 10), (x + offset, y + 10), 3)
        elif self._object_type == "Lizosom":
            pygame.draw.circle(self.screen, color, (x, y), 20)
            for angle in range(0, 360, 45):
                dx = int(12 * math.cos(math.radians(angle)))
                dy = int(12 * math.sin(math.radians(angle)))
                pygame.draw.circle(self.screen, (220, 170, 235), (x + dx, y + dy), 6)
        elif self._object_type == "Chloroplast":
            pygame.draw.ellipse(self.screen, color, (x - 26, y - 16, 52, 32))
            for pos in range(-18, 19, 9):
                pygame.draw.line(self.screen, (50, 120, 55), (x + pos, y - 12), (x + pos + 4, y + 12), 4)
        label = config.font(16, bold=True).render(self._object_type, True, config.TEXT)
        self.screen.blit(label, label.get_rect(midtop=(x, y + 22)))

    #Rysowanie planszy, celu i informacji o grze
    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)

        pygame.draw.line(self.screen, config.MUTED, (self._min_x, self._line_y), (self._max_x, self._line_y), 4)
        pygame.draw.circle(self.screen, config.ACCENT, (self._min_x, self._line_y), 6)
        pygame.draw.circle(self.screen, config.ACCENT, (self._max_x, self._line_y), 6)

        pygame.draw.rect(self.screen, config.ACCENT, self._target, border_radius=16)
        kin = config.font(20, bold=True).render("Kinezyna", True, config.WHITE)
        self.screen.blit(kin, kin.get_rect(center=self._target.center))

        self._draw_object(int(self._pos[0]), int(self._pos[1]))

        title = config.font(36, bold=True).render("Docking ATP", True, config.TEXT)
        self.screen.blit(title, (30, 30))
        inst = config.font(22).render("Naciśnij SPACE, aby zwolnić obiekt nad kinezyną.", True, config.MUTED)
        self.screen.blit(inst, (30, 74))
        object_text = config.font(24).render(f"Ligand: {self._object_type}", True, config.ACCENT)
        self.screen.blit(object_text, (30, 110))
        score_text = config.font(22).render(f"Wynik: {self._score}", True, config.ACCENT)
        self.screen.blit(score_text, (30, 144))

        if self._hit or self._failed:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 45, 170))
            self.screen.blit(overlay, (0, 0))

            text = "Cel trafiony!" if self._hit else f"Nie trafiłeś w kieszeń."
            color = config.ACCENT if self._hit else config.MUTED
            result = config.font(40, bold=True).render(text, True, color)
            self.screen.blit(result, result.get_rect(center=(w // 2, h // 2 - 40)))

            detail = config.font(24).render("Kliknij Dalej, aby kontynuować.", True, config.WHITE)
            self.screen.blit(detail, detail.get_rect(center=(w // 2, h // 2 + 10)))

            self._btn.center = (w // 2, h // 2 + 96)
            pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
            button_label = config.font(22, bold=True).render("Dalej", True, config.WHITE)
            self.screen.blit(button_label, button_label.get_rect(center=self._btn.center))
