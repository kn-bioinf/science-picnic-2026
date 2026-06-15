# Etap 2: dokowanie ładunku (refleksówka - SPACE upuszcza ładunek na ogon kinezyny).
# Cała scena rysowana na stałej kanwie 1280x720 i skalowana do okna (spójnie z 1 i 3).

import os
import random
import pygame
import src.config as config
from src.effects import draw_walking_complete, draw_cargo, CellBackground

_KIN_IMG = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'assets', 'images',
                        'heteroKinesin2Complete.png')


class Stage2:
    """Etap 2: dokowanie ładunku. self.next(score) gdy etap skończony."""

    # Ładunki kinezyny - wyłącznie z komórek ZWIERZĘCYCH
    OBJECTS = [
        {"name": "Pęcherzyk", "color": (134, 190, 240)},
        {"name": "Mitochondrium", "color": (220, 140, 70)},
        {"name": "Lizosom", "color": (175, 95, 200)},
    ]

    # Komunikaty po nietrafieniu - losowane, żeby porażka nie była monotonna
    FAIL_MESSAGES = [
        "Ładunek poleciał w cytozol!",
        "Pudło! Ogon kinezyny pozostał pusty.",
        "Spóźniony zrzut - ładunek minął kinezynę.",
        "Za wcześnie! Ładunek nie trafił w ogon.",
        "Ładunek rozpłynął się w cytoplazmie...",
    ]

    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state = state
        self.next = next_fn
        self._btn = pygame.Rect(0, 0, 180, 48)

        self._line_y = self._min_x = self._max_x = 0
        self._anchor_x = self._anchor_y = 0
        self._pos = [0.0, 0.0]
        self._vel = [0.0, 0.0]
        self._direction = 1
        self._line_speed = 210.0
        self._gravity = 1400.0

        self._released = False
        self._hit = False
        self._failed = False
        self._fail_msg = ""
        self._score = 0

        self._target = None
        self._object_type = None
        self._object_color = None

        self._kin_raw = pygame.image.load(_KIN_IMG).convert_alpha()
        self._kin_img = None
        self._kin_pos = (0, 0)
        self._mt_y = 0
        self._t = 0.0
        self._canvas = pygame.Surface((config.W, config.H))
        self._bg = CellBackground(config.W, config.H)
        self._setup_board()

    #Ustawienia planszy (w przestrzeni 1280x720)
    def _setup_board(self):
        w, h = config.W, config.H
        # szyna ligandu poniżej dwuwierszowego HUD-u (tytuł + Wynik + podpowiedzi),
        # żeby przesuwający się ładunek i jego podpis nie nachodziły na etykiety
        self._line_y = int(h * 0.27)
        self._min_x = int(w * 0.14)
        self._max_x = int(w * 0.86)
        self._direction = random.choice([-1, 1])
        self._released = self._hit = self._failed = False
        self._mt_y = int(h * 0.86)
        kin_h = int(h * 0.40)     
        scale = kin_h / self._kin_raw.get_height()
        self._kin_img = pygame.transform.smoothscale(
            self._kin_raw,
            (max(1, int(self._kin_raw.get_width() * scale)), kin_h))
        self._kin_overlap = max(6, int(h * 0.02))
        self._kin_speed = 90.0
        self._kin_dir = random.choice([-1, 1])
        self._kin_x = float(w * random.uniform(0.30, 0.70))
        self._refresh_kin()

        self._choose_object()
        self._anchor_x = int(w * random.uniform(0.35, 0.65))
        self._anchor_y = self._line_y
        self._pos = [float(self._anchor_x), float(self._anchor_y)]
        self._vel = [0.0, 0.0]

    def _choose_object(self):
        choice = random.choice(self.OBJECTS)
        self._object_type = choice["name"]
        self._object_color = choice["color"]

    def _refresh_kin(self):
        kw, kh = self._kin_img.get_size()
        top = self._mt_y - kh + self._kin_overlap
        self._kin_pos = (int(self._kin_x - kw / 2), top)
        self._target = pygame.Rect(0, 0, max(70, int(kw * 0.7)), 54)
        self._target.center = (int(self._kin_x), top + int(kh * 0.12))

    # ----- skalowanie kanwy do okna (letterbox), jak w etapach 1 i 3 -----
    def _view(self):
        w, h = config.get_size()
        s = min(w / config.W, h / config.H)
        return s, (w - config.W * s) / 2, (h - config.H * s) / 2

    def _to_canvas(self, pos):
        s, ox, oy = self._view()
        if s <= 0:
            return pos
        return ((pos[0] - ox) / s, (pos[1] - oy) / s)

    #Obsługa zdarzeń: SPACE lub lewy klik upuszcza, Enter/klik = Dalej po pudle
    def handle_event(self, e):
        # zrzut ładunku: spacja ALBO lewy przycisk myszy (oba działają tak samo)
        drop = ((e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE)
                or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1
                    and not self._failed))
        if drop and not self._released and not self._hit and not self._failed:
            self._released = True
            self._vel = [0.0, 0.0]
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and self._failed:
            self.next(self._score)
        elif (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self._failed
              and self._btn.collidepoint(self._to_canvas(e.pos))):
            self.next(self._score)

    def update(self, dt):
        self._t += dt
        if self._hit or self._failed:
            return
        w, h = config.W, config.H
        if self._score >= 10:                 # od poziomu 10 kinezyna chodzi
            lo, hi = w * 0.16, w * 0.84
            self._kin_x += self._kin_dir * self._kin_speed * dt
            if self._kin_x < lo:
                self._kin_x, self._kin_dir = lo, 1
            elif self._kin_x > hi:
                self._kin_x, self._kin_dir = hi, -1
            self._refresh_kin()

        if not self._released:
            new_x = self._anchor_x + self._direction * (self._line_speed + self._score * 30.0) * dt
            if new_x < self._min_x:
                new_x, self._direction = self._min_x, 1
            elif new_x > self._max_x:
                new_x, self._direction = self._max_x, -1
            self._anchor_x = new_x
            self._pos = [self._anchor_x, self._anchor_y]
        else:
            self._vel[1] += self._gravity * dt
            self._pos[0] += self._vel[0] * dt
            self._pos[1] += self._vel[1] * dt
            # większa tolerancja: liczy się już sam brzeg ładunku nad kieszenią
            # (zarys niebieski rysujemy bez zmian, poszerzamy tylko strefę łapania)
            pocket = self._target.inflate(40, 30)
            if pocket.collidepoint(int(self._pos[0]), int(self._pos[1])):
                self._hit = True
                self._score += 1
                # zapamiętaj zadokowany ładunek - etap 3 (transport) go poniesie
                self.state.last_cargo = (self._object_type, self._object_color)
                self._setup_board()
            elif self._pos[1] > h + 20:
                self._failed = True
                self._fail_msg = random.choice(self.FAIL_MESSAGES)

    def _draw_object(self, x, y):
        cv = self._canvas
        draw_cargo(cv, self._object_type, self._object_color, x, y)
        lbl = config.font(16, bold=True).render(self._object_type, True, config.TEXT)
        cv.blit(lbl, lbl.get_rect(midtop=(x, y + 22)))

    def _draw_microtubule(self, x0, x1, y):
        r, step = 13, 22
        light, dark = (150, 205, 140), (70, 150, 85)
        for row, ry in enumerate((y + r, y + r + step - 3)):
            x = x0 + r + (row * (step // 2))
            i = 0
            while x < x1 - r:
                col = light if (i + row) % 2 == 0 else dark
                pygame.draw.circle(self._canvas, col, (int(x), ry), r)
                pygame.draw.circle(self._canvas, dark, (int(x), ry), r, 1)
                x += step
                i += 1

    def draw(self):
        w, h = config.W, config.H
        cv = self._canvas
        self._bg.draw(cv, self._t)

        # szyna ligandu
        pygame.draw.line(cv, config.MUTED, (self._min_x, self._line_y),
                         (self._max_x, self._line_y), 4)
        pygame.draw.circle(cv, config.ACCENT, (self._min_x, self._line_y), 6)
        pygame.draw.circle(cv, config.ACCENT, (self._max_x, self._line_y), 6)

        # mikrotubula + kinezyna (statyczna; od poziomu 10 kroczy)
        self._draw_microtubule(0, w, self._mt_y)
        if self._score >= 10:
            draw_walking_complete(cv, self._kin_img, self._kin_pos, self._t)
        else:
            cv.blit(self._kin_img, self._kin_pos)
        pygame.draw.ellipse(cv, config.ACCENT, self._target, 2)

        self._draw_object(int(self._pos[0]), int(self._pos[1]))

        # tytuł w DWÓCH liniach ("Etap 2" / nazwa) - spójnie z etapem 1
        cv.blit(config.font(26, bold=True).render(
            "Etap 2", True, config.TEXT), (30, 12))
        cv.blit(config.font(18, bold=True).render(
            "Dokowanie ładunku", True, config.MUTED), (30, 44))
        cv.blit(config.font(24, bold=True).render(
            f"Wynik: {self._score}", True, config.ACCENT), (30, 70))

        if self._failed:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 45, 170))
            cv.blit(overlay, (0, 0))
            res = config.font(40, bold=True).render(self._fail_msg,
                                                    True, config.WHITE)
            cv.blit(res, res.get_rect(center=(w // 2, h // 2 - 50)))
            det = config.font(24).render(f"Wynik: {self._score}", True, config.WHITE)
            cv.blit(det, det.get_rect(center=(w // 2, h // 2 + 2)))
            self._btn.center = (w // 2, h // 2 + 70)
            pygame.draw.rect(cv, config.ACCENT, self._btn, border_radius=8)
            bl = config.font(22, bold=True).render("Dalej", True, config.WHITE)
            cv.blit(bl, bl.get_rect(center=self._btn.center))
            hint = config.font(15).render("Enter - dalej", True, (210, 215, 230))
            cv.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 116)))

        # skaluj kanwę do okna
        s, ox, oy = self._view()
        scaled = pygame.transform.smoothscale(
            cv, (max(1, int(config.W * s)), max(1, int(config.H * s))))
        self.screen.fill(config.BG)
        self.screen.blit(scaled, (int(ox), int(oy)))
