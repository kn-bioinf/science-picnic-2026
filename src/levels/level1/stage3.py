# Transport na mikrotubuli: kinezyna niesie ładunek z etapu 2 i omija przeszkody
# (MAP-y), luki w torze i dyneinę.
# Sterowanie: ↑ / SPACE = skok, ↓ = szybki opad.
#
# Cała scena rysowana jest na stałej kanwie 1280x720 (config.W x H) i dopiero
# skalowana do okna — dzięki temu fizyka, rozmiary i odstępy są spójne na
# każdym ekranie (gra jest tak samo grywalna niezależnie od rozdzielczości).

import os
import random
import pygame
import src.config as config
from src.effects import CellBackground, draw_walking_complete, draw_cargo

_KIN_IMG = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'assets', 'images',
                        'heteroKinesin2Complete.png')
_DYN_IMG = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'assets', 'images',
                        'puzzle-pieces', 'DyneinMotor.png')


class Stage3:
    """
    Etap 3: transport na mikrotubuli (kinezyna niesie ładunek z etapu 2 i
    omija przeszkody – skok).
    """

    # Białka wiążące mikrotubule (MAP) jako przeszkody – do przeskoczenia
    MAPS = [('Tau',  (138,  96, 178)), ('MAP2', ( 90, 140, 200)),
            ('MAP4', (200, 150,  80)), ('DCX',  ( 90, 180, 130))]
    _DYN_EXTRA = 40.0     # dyneina nadjeżdża nieco szybciej niż przewija się tor

    #Ustawienia przy inicjowaniu
    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state = state
        self.next = next_fn
        self._btn = pygame.Rect(0, 0, 180, 48)

        # ładunek niesiony przez kinezynę = ostatni zadokowany w etapie 2
        # (a gdy etap 3 gramy solo i nic nie ma – domyślny pęcherzyk)
        self._cargo = getattr(state, "last_cargo", None) or ("Pęcherzyk", (134, 190, 240))

        self._distance = 0.0
        self._score = 0
        self._game_over = False
        self._obstacles = []
        self._next_spawn_distance = 0.0

        self._vy = 0.0
        self._jump_speed = -900.0
        self._gravity = 2000.0
        self._speed = 280.0

        self._kin_raw = pygame.image.load(_KIN_IMG).convert_alpha()
        self._dyn_raw = pygame.image.load(_DYN_IMG).convert_alpha()
        self._kin_img = None
        self._dyn_img = None
        self._t = 0.0
        self._walk_phase = 0.0
        self._runner_w = self._runner_h = 0
        self._runner_x = self._runner_y = 0
        self._rest_y = self._overlap = 0
        self._ground_y = 0

        self._canvas = pygame.Surface((config.W, config.H))
        self._bg = CellBackground(config.W, config.H)
        self._setup_layout()

    #Ustawienia pozycji kinezyny i przeszkód (w przestrzeni 1280x720)
    def _setup_layout(self):
        w, h = config.W, config.H
        self._ground_y = h - 140
        kin_h = int(h * 0.26)
        scale = kin_h / self._kin_raw.get_height()
        self._kin_img = pygame.transform.smoothscale(
            self._kin_raw,
            (max(1, int(self._kin_raw.get_width() * scale)), kin_h))
        self._runner_w = self._kin_img.get_width()
        self._runner_h = kin_h
        self._overlap = max(6, int(h * 0.02))      # stópki wchodzą w mikrotubulę
        self._runner_x = int(w * 0.18)
        self._rest_y = self._ground_y - self._runner_h + self._overlap
        self._runner_y = self._rest_y
        # dyneina-wróg (DyneinMotor), przeskalowana, odwrócona „na wprost"
        dyn_h = int(h * 0.11)
        ds = dyn_h / self._dyn_raw.get_height()
        dyn = pygame.transform.smoothscale(
            self._dyn_raw,
            (max(1, int(self._dyn_raw.get_width() * ds)), dyn_h))
        self._dyn_img = pygame.transform.flip(dyn, True, False)
        self._next_spawn_distance = 0.0

    # ----- skalowanie kanwy do okna (letterbox), jak w etapie 1 -----
    def _view(self):
        w, h = config.get_size()
        s = min(w / config.W, h / config.H)
        return s, (w - config.W * s) / 2, (h - config.H * s) / 2

    def _to_canvas(self, pos):
        s, ox, oy = self._view()
        if s <= 0:
            return pos
        return ((pos[0] - ox) / s, (pos[1] - oy) / s)

    #Obsługa zdarzeń: ↑/SPACE skok, ↓ szybki opad, klik „Dalej" po końcu
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_SPACE, pygame.K_UP):
                if not self._game_over and self._runner_y >= self._rest_y:
                    self._vy = self._jump_speed
            elif e.key == pygame.K_DOWN:
                if not self._game_over and self._runner_y < self._rest_y:
                    self._vy = max(self._vy, 1600.0)
            elif e.key == pygame.K_RETURN and self._game_over:
                self.next(self._score)          # Enter = Dalej po końcu biegu
        if (e.type == pygame.MOUSEBUTTONDOWN and self._game_over
                and self._btn.collidepoint(self._to_canvas(e.pos))):
            self.next(self._score)

    #Generowanie przeszkód: MAP (przeskok), luka w torze (przeskok), dyneina
    def _spawn_obstacle(self, w, h):
        kinds = ['map', 'map']
        if self._distance > 1200:
            kinds.append('gap')
        if self._distance > 2600:
            kinds.append('dynein')
        kind = random.choice(kinds)

        x0 = w + 30
        if kind == 'gap':
            gw = random.randint(70, 110)
            rect = pygame.Rect(x0, self._ground_y, gw, 44)
            self._obstacles.append({'kind': 'gap', 'rect': rect, 'fx': float(x0),
                                    'passed': False})
        elif kind == 'dynein':
            dw, dh = self._dyn_img.get_size()
            rect = pygame.Rect(x0, self._ground_y - dh + self._overlap, dw, dh)
            self._obstacles.append({'kind': 'dynein', 'rect': rect, 'fx': float(x0),
                                    'passed': False})
        else:
            name, col = random.choice(self.MAPS)
            oh = random.randint(48, 78)
            rect = pygame.Rect(x0, self._ground_y - oh, 50, oh)
            self._obstacles.append({'kind': 'map', 'name': name, 'color': col,
                                    'rect': rect, 'fx': float(x0), 'passed': False})

    #Aktualizacja: tempo, generowanie, fizyka skoku, kolizje
    def update(self, dt):
        if self._game_over:
            return
        w, h = config.W, config.H
        self._distance += self._speed * dt
        self._speed = 280.0 + min(260.0, self._distance * 0.008)   # spokojne tempo
        self._t += dt
        self._walk_phase += self._speed * dt * 0.02   # główki kroczą ∝ prędkości

        if self._distance >= self._next_spawn_distance:
            self._spawn_obstacle(w, h)
            # odstęp STAŁY w ODLEGŁOŚCI (nie skaluje się z prędkością) — dzięki
            # temu liczba przeszkód na dystans NIE maleje, gdy tor przyspiesza.
            # Przy rosnącej prędkości te same odstępy = coraz krótsze okno reakcji
            # (start ~1.9 s między przeszkodami → ~0.9 s przy maks. prędkości).
            self._next_spawn_distance = self._distance + random.uniform(490, 660)

        self._runner_y += self._vy * dt
        self._vy += self._gravity * dt
        if self._runner_y >= self._rest_y:
            self._runner_y = self._rest_y
            self._vy = 0.0

        feet = self._feet_rect()
        grounded = self._runner_y >= self._rest_y - 2
        remaining = []
        for item in self._obstacles:
            r = item["rect"]
            spd = self._speed + (self._DYN_EXTRA if item['kind'] == 'dynein' else 0)
            item['fx'] -= spd * dt                 # float → płynnie i w synchronie
            r.x = int(round(item['fx']))
            if r.right < 0:
                continue                           # zniknęła z lewej – usuwamy
            remaining.append(item)

            if not item["passed"] and r.right < self._runner_x:
                item["passed"] = True              # ominięta → punkt
                self._score += 1

            if item['kind'] == 'gap':
                # giniesz tylko gdy na ziemi i >70% podstawy wisi nad dziurą
                over = min(feet.right, r.right) - max(feet.left, r.left)
                if grounded and over > 0.70 * feet.width:
                    self._game_over = True
            else:
                box = r
                if item['kind'] == 'dynein':  # mniejszy hitbox – łatwiej przeskoczyć
                    box = pygame.Rect(r.x + int(r.w * 0.16), r.y + int(r.h * 0.34),
                                      int(r.w * 0.68), int(r.h * 0.66))
                if feet.colliderect(box):
                    self._game_over = True
        self._obstacles = remaining

    #Prostokąt kolizji = dolna część (stópki) kinezyny
    def _feet_rect(self):
        # ciasne pudełko wokół DOLNYCH główek motorycznych (nie całej sylwetki)
        fh = int(self._runner_h * 0.20)
        fw = int(self._runner_w * 0.56)
        x = self._runner_x + (self._runner_w - fw) // 2
        y = int(self._runner_y) + self._runner_h - fh
        return pygame.Rect(x, y, fw, fh)

    #Lite odcinki toru [x0,x1] z wyciętymi lukami
    @staticmethod
    def _segments(x0, x1, gaps):
        cuts = sorted((max(x0, gl), min(x1, gr)) for gl, gr in gaps
                      if gr > x0 and gl < x1)
        segs, cur = [], x0
        for gl, gr in cuts:
            if gl > cur:
                segs.append((cur, gl))
            cur = max(cur, gr)
        if cur < x1:
            segs.append((cur, x1))
        return segs

    #Mikrotubula: dwa rzędy koralików (dimery tubuliny). Kolor zależy od pozycji
    #w ŚWIECIE (nie od pętli), więc każdy koralik trzyma kolor i tor płynnie
    #jedzie zamiast migotać. `gaps` to uszkodzenia – czysto przerwany tor.
    def _draw_microtubule(self, w, y, scroll, gaps=()):
        # spokojny tor: lity, matowy podkład (rurka) + duże koraliki o niskim
        # kontraście (bez ostrego obrysu). Mniej męczy wzrok niż gęste, drobne,
        # mocno kontrastowe kropki. Podkład daje też proste krawędzie luk.
        r, step, th = 16, 28, 44
        base = (124, 174, 138)
        light, dark = (160, 197, 166), (138, 182, 150)
        for sx0, sx1 in self._segments(0, w, gaps):
            pygame.draw.rect(self._canvas, base, (int(sx0), y, int(sx1 - sx0), th))
        # koraliki świata – każdy ma stały kolor i realnie jedzie w lewo
        first = int((scroll - 2 * step) // step)
        last = int((scroll + w + 2 * step) // step)
        for row, ry in enumerate((y + 13, y + 31)):
            for wi in range(first, last + 1):
                sx = wi * step + row * (step // 2) - scroll
                if any(gl - r <= sx <= gr + r for gl, gr in gaps):
                    continue                       # przerwa w torze (luka)
                col = light if (wi + row) % 2 == 0 else dark
                pygame.draw.circle(self._canvas, col, (int(sx), ry), r)

    #Czytelny podpis przeszkody – biały tekst na ciemnej „pigułce"
    def _label(self, text, cx, cy):
        surf = config.font(16, bold=True).render(text, True, config.WHITE)
        rect = surf.get_rect(center=(cx, cy))
        bg = rect.inflate(14, 8)
        pill = pygame.Surface(bg.size, pygame.SRCALPHA)
        pygame.draw.rect(pill, (28, 32, 52, 205), pill.get_rect(), border_radius=9)
        self._canvas.blit(pill, bg.topleft)
        self._canvas.blit(surf, rect)

    #Przeszkoda MAP (Tau / MAP2 / MAP4 / DCX) – kłębek białka na mikrotubuli
    def _draw_map(self, rect, name, color):
        bump = tuple(max(0, c - 22) for c in color)
        pygame.draw.rect(self._canvas, color, rect, border_radius=12)
        cx = rect.centerx
        for dx, dy, rr in [(-9, -4, 12), (9, -6, 10), (1, 7, 12),
                           (-12, 9, 8), (12, 10, 8)]:
            pygame.draw.circle(self._canvas, bump, (cx + dx, rect.centery + dy), rr)
        self._label(name, cx, rect.top - 16)

    #Rysowanie sceny (na kanwie) i skalowanie do okna
    def draw(self):
        w, h = config.W, config.H
        cv = self._canvas

        # animowane tło „wnętrza komórki"
        self._bg.draw(cv, self._t)

        # mikrotubula (przewija się w lewo); luki = przerwy w torze
        gaps = [(it['rect'].left, it['rect'].right)
                for it in self._obstacles if it['kind'] == 'gap']
        self._draw_microtubule(w, self._ground_y, self._distance, gaps)

        # przeszkody wg typu
        for it in self._obstacles:
            if it['kind'] == 'map':
                self._draw_map(it['rect'], it['name'], it['color'])
            elif it['kind'] == 'dynein':
                cv.blit(self._dyn_img, it['rect'].topleft)
                self._label('Dyneina', it['rect'].centerx, it['rect'].top - 16)

        # kinezyna – kroczy z prędkością zależną od tempa biegu
        if self._game_over:
            cv.blit(self._kin_img, (self._runner_x, int(self._runner_y)))
        else:
            draw_walking_complete(cv, self._kin_img,
                                  (self._runner_x, int(self._runner_y)),
                                  self._walk_phase, speed=1.0, amp=4.0)

        # niesiony ładunek – siedzi na ogonie (górze) kinezyny i jedzie razem z nią
        ctype, ccolor = self._cargo
        draw_cargo(cv, ctype, ccolor,
                   self._runner_x + self._runner_w // 2,
                   int(self._runner_y) + int(self._runner_h * 0.10),
                   scale=0.55)

        # HUD – spójny label lewy-górny: tytuł etapu + Wynik
        cv.blit(config.font(26, bold=True).render(
            "Etap 3", True, config.TEXT), (30, 12))
        cv.blit(config.font(18, bold=True).render(
            "Transport", True, config.MUTED), (30, 44))
        cv.blit(config.font(24, bold=True).render(
            f"Wynik: {self._score}", True, config.ACCENT), (30, 70))
        cv.blit(config.font(20).render("↑ / SPACE: skok    ↓: szybki opad",
                                       True, config.MUTED), (30, 104))
        cv.blit(config.font(20).render(
            f"Przebyta odległość: {int(self._distance // 10)}", True, config.MUTED),
            (30, 130))

        if self._game_over:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 35, 160))
            cv.blit(overlay, (0, 0))
            msg = config.font(48, bold=True).render("Koniec transportu!", True, config.WHITE)
            cv.blit(msg, msg.get_rect(center=(w // 2, h // 2 - 60)))
            detail = config.font(24).render(f"Twój wynik: {self._score}", True, config.WHITE)
            cv.blit(detail, detail.get_rect(center=(w // 2, h // 2)))
            self._btn.center = (w // 2, h // 2 + 96)
            pygame.draw.rect(cv, config.ACCENT, self._btn, border_radius=8)
            btn_lbl = config.font(22, bold=True).render("Dalej", True, config.WHITE)
            cv.blit(btn_lbl, btn_lbl.get_rect(center=self._btn.center))

        # skaluj kanwę do okna (proporcjonalnie, wyśrodkowaną)
        s, ox, oy = self._view()
        scaled = pygame.transform.smoothscale(
            cv, (max(1, int(config.W * s)), max(1, int(config.H * s))))
        self.screen.fill(config.BG)
        self.screen.blit(scaled, (int(ox), int(oy)))
