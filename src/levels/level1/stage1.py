import pygame
import os
import math
import json
import random
import src.config as config
from src.effects import CellBackground

"""
Etap 1 – Złóż heterokinezynę-2.

Gracz buduje białko OD DOŁU na mikrotubuli, dokładając kolejno trzy klasy
elementów: najpierw głowę motoryczną (Motor), potem trzon (Stalk), na końcu
ogon (Tail). Kolejność klas jest wymuszona – nie da się położyć trzonu zanim
nie ma głowy itd. W każdej klasie do wyboru jest kilka wariantów pochodzących
z różnych białek motorycznych (heteroKinesin2, homoKinesin2, Kinesin1, Dynein,
MyosinV); tylko trio heteroKinesin2 jest poprawne.

Poprawność (gatunek) sprawdzana jest dopiero po wciśnięciu „Zatwierdź".
Wynik zależy od liczby prób – im mniej błędnych zatwierdzeń, tym lepiej.

Elementy łapią się magnetycznie (anchor-snap) do następnego wolnego miejsca w
strukturze. Pliki .png mają bardzo różne rozmiary, więc układane są wzdłuż
wspólnej osi pionowej (wyrównanie do środka w poziomie), a w pionie kolejny
element siada na poprzednim z niewielką zakładką.
"""

# ------------------------------------------------------------------ assety

_PIECES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'assets', 'images', 'puzzle-pieces'
)
_REFERENCE = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'assets', 'images',
    'heteroKinesin2Complete.png'
)

CORRECT_SPECIES = 'heteroKinesin2'

# Klasy elementów w kolejności budowania OD DOŁU (na mikrotubuli) DO GÓRY.
# (klucz w nazwie pliku, etykieta PL)
_CLASS_ORDER = [
    ('Motor', 'Głowa'),
    ('Stalk', 'Trzon'),
    ('Tail',  'Ogon'),
]
_CLASS_KEYS = [k for k, _ in _CLASS_ORDER]
# formy biernika do podpowiedzi „Dołóż …" (po polsku)
_CLASS_ACC  = {'Motor': 'głowę', 'Stalk': 'trzon', 'Tail': 'ogon'}

# Kolejność gatunków-celów na prawym panelu (heteroKinesin2 = cel zadania,
# jako pierwszy). Buildowalne są tylko te z kompletem 3 części.
_TARGET_ORDER = ['heteroKinesin2', 'homoKinesin2', 'Kinesin1', 'MyosinV', 'Dynein']

# Pełne nazwy i rdzenie do sklejania nazw chimer (np. rdzenie 'miozyno' +
# 'kinezyno' + 'dyneino' -> "chimera miozyno-kinezyno-dyneinowa").
_SPECIES_NAME = {
    'heteroKinesin2': 'heterokinezyna-2',
    'homoKinesin2':   'homokinezyna-2',
    'Kinesin1':       'kinezyna-1',
    'MyosinV':        'miozyna-V',
    'Dynein':         'dyneina',
}
_SPECIES_STEM = {
    'heteroKinesin2': 'heterokinezyno',
    'homoKinesin2':   'homokinezyno',
    'Kinesin1':       'kinezyno',
    'MyosinV':        'miozyno',
    'Dynein':         'dyneino',
}

# Wymienne domeny motoryczne: motor Kinesin1 i homoKinesin2 są ~identyczne –
# pokazujemy jeden, ważny dla obu gatunków. heteroKinesin2 motor zostaje osobny.
_MOTOR_INTERCHANGE = {'Kinesin1', 'homoKinesin2'}

# ------------------------------------------------------------------ strojenie

BUILD_SCALE = 0.8      # skala elementów w strefie budowania (mniejsze, by się mieściły)
SNAP_RADIUS = 110      # px – upuszczenie w tym promieniu łapie element do struktury
LERP_SPEED  = 11.0     # szybkość dolatywania (ease-out)

# Dokładne punkty łączenia (anchory) dla POPRAWNEGO trio heteroKinesin2,
# wyliczone przez dopasowanie każdej części do heteroKinesin2Complete.png
# (dopasowanie pikselowe 1:1). Współrzędne w pikselach NATYWNYCH obrazka,
# względem jego lewego-górnego rogu. 'bottom' = punkt, którym element siada na
# elemencie poniżej / na mikrotubuli; 'top' = punkt, do którego doczepia się
# element powyżej. Dzięki nim poprawna kinezyna składa się 1:1 z referencją
# (m.in. motor jest celowo przesunięty ~9 px w prawo od osi trzonu).
_HETERO_ANCHORS = {
    'Motor': {'bottom': (55, 44), 'top': (47,  5)},
    'Stalk': {'bottom': (13, 168), 'top': (12,  2)},
    'Tail':  {'bottom': (69, 88),  'top': (69,  0)},
}

TRAY_W   = 336         # lewy panel z elementami do wyboru
REF_W    = 244         # prawy panel referencyjny

# kolory specyficzne dla etapu
TRAY_BG   = (224, 232, 248)
REF_BG    = (224, 232, 248)
MT_LIGHT  = (150, 205, 140)
MT_DARK   = ( 70, 150,  85)
OK_GREEN  = ( 55, 175,  85)
BAD_RED   = (210,  70,  70)


# ------------------------------------------------------------------ helpers

def _species_of(filename):
    """heteroKinesin2Motor.png -> ('heteroKinesin2', 'Motor') albo None."""
    stem = filename[:-4] if filename.lower().endswith('.png') else filename
    for key in _CLASS_KEYS:
        if stem.endswith(key):
            return stem[:-len(key)], key
    return None


def _scan_pieces():
    """Zbiera dostępne elementy z folderu, pogrupowane wg klasy.
    Zwraca dict {klasa: [(species, filename), ...]}."""
    by_class = {k: [] for k in _CLASS_KEYS}
    try:
        files = sorted(os.listdir(_PIECES_DIR))
    except FileNotFoundError:
        files = []
    for f in files:
        if not f.lower().endswith('.png'):
            continue
        parsed = _species_of(f)
        if parsed:
            species, key = parsed
            by_class[key].append((species, f))
    return by_class


def _scaled(img, scale):
    w, h = img.get_size()
    return pygame.transform.smoothscale(img, (max(1, int(w * scale)),
                                              max(1, int(h * scale))))


def _load_anchor_overrides():
    """Ręcznie ustawione anchory z anchors.json (px natywne) – mają priorytet
    nad wartościami domyślnymi. Tworzone przez anchor_tool.py."""
    path = os.path.join(_PIECES_DIR, 'anchors.json')
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


# ------------------------------------------------------------------ element

class _Piece:
    """Jeden klocek: ma reprezentację w tacce (thumb) i w strukturze (build)."""

    def __init__(self, species, klass, raw):
        self.species = species
        self.klass   = klass                  # 'Motor' / 'Stalk' / 'Tail'
        # gatunki, dla których ten element jest poprawny (zwykle własny;
        # wymienny motor pasuje do kilku) – ustawiane w _build_pieces
        self.match_species = {species}
        self.build   = _scaled(raw, BUILD_SCALE)
        self.rect    = self.build.get_rect()  # aktualna pozycja w strefie budowania

        # thumbnail do tacki – dopasowany do komórki, nigdy większy niż w budowie
        self.thumb       = None
        self.thumb_rect  = pygame.Rect(0, 0, 0, 0)
        self.home        = (0, 0)             # środek miejsca w tacce

        # Anchory w pikselach obrazka BUILD, względem lewego-górnego rogu.
        # Domyślnie liczone z centroidu nieprzezroczystych pikseli przy dolnej
        # i górnej krawędzi (sensowne dla dowolnego kształtu); dla poprawnego
        # trio nadpisywane dokładnymi wartościami z referencji.
        self.top_anchor, self.bottom_anchor = self._default_anchors()

        # 'tray' | 'dragging' | 'snapping' | 'placed'
        self.state   = 'tray'
        self.wrong   = False                  # podświetlenie po błędnym zatwierdzeniu
        self.lerp_from = (0, 0)
        self.lerp_to   = (0, 0)
        self.lerp_t    = 0.0

    @property
    def is_correct(self):
        return self.species == CORRECT_SPECIES

    def _default_anchors(self):
        """Centroid nieprzezroczystych pikseli przy górnej i dolnej krawędzi."""
        w, h = self.build.get_size()
        try:
            alpha = pygame.surfarray.array_alpha(self.build)   # [x][y]
        except Exception:
            return (w / 2, 0.0), (w / 2, float(h - 1))
        band = max(1, int(h * 0.12))

        def centroid_x(y0, y1):
            cols = (alpha[:, y0:y1] > 40).any(axis=1)
            xs = [x for x in range(w) if cols[x]]
            return sum(xs) / len(xs) if xs else w / 2

        top    = (centroid_x(0, band),     0.0)
        bottom = (centroid_x(h - band, h),  float(h - 1))
        return top, bottom

    def set_anchors_native(self, native):
        """Nadpisz anchory wartościami w px NATYWNYCH (przeskaluje do BUILD)."""
        if native.get('top'):
            self.top_anchor = (native['top'][0] * BUILD_SCALE,
                               native['top'][1] * BUILD_SCALE)
        if native.get('bottom'):
            self.bottom_anchor = (native['bottom'][0] * BUILD_SCALE,
                                  native['bottom'][1] * BUILD_SCALE)

    def make_thumb(self, cell_w, cell_h):
        w, h = self.build.get_size()
        # build to już SCALE; thumb fit do komórki, ale nie powiększamy ponad build
        s = min(cell_w / w, cell_h / h, 1.0)
        self.thumb = _scaled(self.build, s)
        self.thumb_rect = self.thumb.get_rect()


# ------------------------------------------------------------------ etap

class Stage1:
    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state  = state
        self.next   = next_fn

        self._pieces  = self._build_pieces()
        # struktura = 3 typowane sloty wg klasy: [Motor (dół), Stalk, Tail (góra)]
        self._slots   = [None, None, None]
        self._drag    = None
        self._drag_from = None      # indeks slotu, z którego podniesiono element
        self._fails    = 0          # liczba błędnych „Zatwierdź" (wynik = 20 - pomyłki)
        self._solved   = False
        self._msg      = None       # komunikat po błędnym zatwierdzeniu
        self._score    = 0

        self._btn_next   = pygame.Rect(0, 0, 170, 44)
        self._btn_submit = pygame.Rect(0, 0, 170, 44)
        self._btn_reset  = pygame.Rect(0, 0, 200, 44)
        self._arrow_l    = pygame.Rect(0, 0, 34, 34)
        self._arrow_r    = pygame.Rect(0, 0, 34, 34)

        # cele do wyboru strzałkami (gatunki z kompletem części); hetero = cel
        # zadania i wartość domyślna
        self._targets   = [s for s in _TARGET_ORDER
                           if all(self._correct_piece(s, k) for k in _CLASS_KEYS)]
        self._target_idx = (self._targets.index(CORRECT_SPECIES)
                            if CORRECT_SPECIES in self._targets else 0)
        self._preview_cache = {}

        self._reference = self._load_reference()
        # Cała scena rysowana jest na stałej kanwie 1280x720 (config.W x H),
        # a następnie skalowana do aktualnego okna z zachowaniem proporcji.
        # Dzięki temu starannie dobrany układ "mieści się" niezależnie od
        # rozmiaru okna (skalowanie żyje poza stage1, w wymiarach z config.py).
        self._canvas = pygame.Surface((config.W, config.H))
        self._t   = 0.0             # czas (do animacji tła)
        self._bg  = CellBackground(config.W, config.H,
                                   TRAY_W + 16, config.W - REF_W - 16)
        self._relayout()

    # -------------------------------------------------------------- setup

    def _build_pieces(self):
        by_class = _scan_pieces()
        overrides = _load_anchor_overrides()

        # Wymienne motory: jeśli są oba (Kinesin1 + homoKinesin2), pokaż tylko
        # jeden (zostaje homoKinesin2), ale ważny dla obu gatunków.
        motors = by_class.get('Motor', [])
        present = {sp for sp, _ in motors}
        merged_motor_sp = None
        if _MOTOR_INTERCHANGE <= present:
            keep = 'homoKinesin2'
            by_class['Motor'] = [(sp, fn) for sp, fn in motors
                                 if sp == keep or sp not in _MOTOR_INTERCHANGE]
            merged_motor_sp = keep

        pieces = []
        cell_w = (TRAY_W - 24) // 3 - 6
        cell_h = 92

        col_x = [12 + i * ((TRAY_W - 24) // 3) + ((TRAY_W - 24) // 3) // 2
                 for i in range(3)]

        for ci, key in enumerate(_CLASS_KEYS):
            variants = by_class.get(key, [])
            random.shuffle(variants)
            y = 96
            for species, filename in variants:
                raw = pygame.image.load(
                    os.path.join(_PIECES_DIR, filename)).convert_alpha()
                p = _Piece(species, key, raw)
                if key == 'Motor' and species == merged_motor_sp:
                    p.match_species = set(_MOTOR_INTERCHANGE)   # ważny dla obu
                ov = overrides.get(filename)
                if ov and 'top' in ov and 'bottom' in ov:
                    p.set_anchors_native(ov)                       # ręczne z json
                elif species == CORRECT_SPECIES and key in _HETERO_ANCHORS:
                    p.set_anchors_native(_HETERO_ANCHORS[key])     # dokładne z referencji
                p.make_thumb(cell_w, cell_h)
                p.thumb_rect.center = (col_x[ci], int(y + p.thumb.get_height() / 2))
                p.home = p.thumb_rect.center
                p.rect = p.build.get_rect(center=p.home)
                pieces.append(p)
                y += p.thumb.get_height() + 14
        return pieces

    def _load_reference(self):
        try:
            img = pygame.image.load(_REFERENCE).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None
        w, h = img.get_size()
        target_w = REF_W - 60
        s = min(target_w / w, 360 / h)
        return _scaled(img, s)

    # -------------------------------------------------------------- cele

    def _correct_piece(self, species, klass):
        """Element właściwy dla (gatunek, klasa); uwzględnia wymienne motory."""
        for p in self._pieces:
            if p.klass == klass and species in p.match_species:
                return p
        return None

    def _target(self):
        return self._targets[self._target_idx]

    def _set_target(self, delta):
        if not self._targets:
            return
        self._target_idx = (self._target_idx + delta) % len(self._targets)
        self._solved = False        # nowy cel = świeże wyzwanie
        self._msg = None
        # pomyłki (self._fails) liczą się globalnie – nie zerujemy przy zmianie celu
        for p in self._slots:
            if p is not None:
                p.wrong = False

    def _assemble_surface(self, species):
        """Złóż poprawne trio gatunku w jeden Surface (lokalne współrzędne)."""
        placed = []
        conn = (0.0, 0.0)
        for key in _CLASS_KEYS:
            p = self._correct_piece(species, key)
            if p is None:
                return None
            tl = (conn[0] - p.bottom_anchor[0], conn[1] - p.bottom_anchor[1])
            placed.append((p, tl))
            conn = (tl[0] + p.top_anchor[0], tl[1] + p.top_anchor[1])
        minx = min(tl[0] for _, tl in placed)
        miny = min(tl[1] for _, tl in placed)
        maxx = max(tl[0] + p.build.get_width() for p, tl in placed)
        maxy = max(tl[1] + p.build.get_height() for p, tl in placed)
        surf = pygame.Surface((max(1, int(maxx - minx)),
                               max(1, int(maxy - miny))), pygame.SRCALPHA)
        for p, tl in placed:
            surf.blit(p.build, (int(tl[0] - minx), int(tl[1] - miny)))
        return surf

    def _target_preview(self, species):
        """Surface celu dopasowany do panelu (hetero z ładnej referencji)."""
        if species in self._preview_cache:
            return self._preview_cache[species]
        if species == CORRECT_SPECIES and self._reference is not None:
            surf = self._reference
        else:
            surf = self._assemble_surface(species)
            if surf is not None:
                w, h = surf.get_size()
                surf = _scaled(surf, min((REF_W - 70) / w, 320 / h))
        self._preview_cache[species] = surf
        return surf

    def _build_name(self):
        """(nazwa, czy_chimera) z gatunków ułożonych klocków."""
        distinct = []
        for p in self._slots:
            if p.species not in distinct:
                distinct.append(p.species)
        if len(distinct) == 1:
            return _SPECIES_NAME.get(distinct[0], distinct[0]), False
        stems = '-'.join(_SPECIES_STEM.get(s, s) for s in distinct)
        return f'chimera {stems}wa', True

    # -------------------------------------------------------------- geometria

    def _axis_x(self):
        return (TRAY_W + (config.W - REF_W)) // 2

    def _mt_y(self):
        return config.H - 96            # górna powierzchnia mikrotubuli

    @staticmethod
    def _slot_of(piece):
        return _CLASS_KEYS.index(piece.klass)

    def _next_slot(self):
        """Najniższy pusty slot (kolejny do wypełnienia) albo None gdy pełne."""
        for i in range(len(self._slots)):
            if self._slots[i] is None:
                return i
        return None

    def _lower_filled(self, i):
        """Czy wszystkie sloty poniżej i są zajęte (wymóg kolejności klas)."""
        return all(self._slots[j] is not None for j in range(i))

    def _next_class(self):
        i = self._next_slot()
        return None if i is None else _CLASS_KEYS[i]

    def _connection_point_for(self, i):
        """Punkt (screen), do którego doczepi się DÓŁ elementu w slocie i:
        powierzchnia mikrotubuli dla slotu 0, inaczej top_anchor slotu i-1."""
        if i == 0:
            return float(self._axis_x()), float(self._mt_y())
        below = self._slots[i - 1]
        return (below.rect.x + below.top_anchor[0],
                below.rect.y + below.top_anchor[1])

    def _connection_point(self):
        return self._connection_point_for(self._next_slot() or 0)

    def _topleft_for(self, piece, conn):
        """Lewy-górny róg `piece`, aby jego bottom_anchor trafił w punkt conn."""
        return (conn[0] - piece.bottom_anchor[0],
                conn[1] - piece.bottom_anchor[1])

    def _relayout(self):
        """Układa łańcuchem anchorów sloty zajęte od dołu (przerwę pomija –
        elementy nad luką zostają tam gdzie były, do czasu wypełnienia luki)."""
        conn = (float(self._axis_x()), float(self._mt_y()))
        for i in range(len(self._slots)):
            p = self._slots[i]
            if p is None:
                break
            if p.state != 'snapping':
                tx, ty = self._topleft_for(p, conn)
                p.rect.topleft = (int(round(tx)), int(round(ty)))
            conn = (p.rect.x + p.top_anchor[0], p.rect.y + p.top_anchor[1])

    def _slot_center_for(self, piece):
        """Gdzie wyląduje ŚRODEK `piece`, gdyby trafił do swojego slotu."""
        conn = self._connection_point_for(self._slot_of(piece))
        tx, ty = self._topleft_for(piece, conn)
        return (int(round(tx + piece.build.get_width() / 2)),
                int(round(ty + piece.build.get_height() / 2)))

    # -------------------------------------------------------------- events

    def _view(self):
        """Skala i offset 'letterbox' dopasowujące kanwę 1280x720 do okna."""
        w, h = config.get_size()
        s = min(w / config.W, h / config.H)
        return s, (w - config.W * s) / 2, (h - config.H * s) / 2

    def _to_canvas(self, pos):
        """Przelicza pozycję myszy z okna na współrzędne kanwy."""
        s, ox, oy = self._view()
        if s <= 0:
            return pos
        return ((pos[0] - ox) / s, (pos[1] - oy) / s)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self._on_down(self._to_canvas(e.pos))
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self._on_up(self._to_canvas(e.pos))
        elif e.type == pygame.MOUSEMOTION and self._drag:
            cx, cy = self._to_canvas(e.pos)
            self._drag.rect.center = (int(cx), int(cy))
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            # Enter = Dalej (gdy ukończone hetero) lub Zatwierdź (gdy pełne)
            if self._solved and self._target() == CORRECT_SPECIES:
                self.next(self._score)
            elif self._is_full():
                self._submit()

    def _on_down(self, pos):
        # strzałki wyboru celu – zawsze aktywne
        if self._arrow_l.collidepoint(pos):
            self._set_target(-1); return
        if self._arrow_r.collidepoint(pos):
            self._set_target(+1); return

        # zadanie ukończone (cel = hetero) – czekamy tylko na „Dalej"
        if self._solved and self._target() == CORRECT_SPECIES:
            if self._btn_next.collidepoint(pos):
                self.next(self._score)
            return

        if self._is_full() and self._btn_submit.collidepoint(pos):
            self._submit()
            return

        if not self._solved and self._btn_reset.collidepoint(pos):
            self._reset()
            return

        # 1) podnieś dowolny element struktury (od góry, gdyby się nakładały)
        for i in range(len(self._slots) - 1, -1, -1):
            p = self._slots[i]
            if p is not None and p.rect.collidepoint(pos):
                self._slots[i] = None
                p.state = 'dragging'
                p.wrong = False
                self._drag = p
                self._drag_from = i
                self._solved = False
                self._msg = None
                self._relayout()
                return

        # 2) podnieś element z tacki
        for p in reversed(self._pieces):
            if p.state == 'tray' and p.thumb_rect.collidepoint(pos):
                p.state = 'dragging'
                p.wrong = False
                p.rect = p.build.get_rect(center=pos)
                self._drag = p
                self._drag_from = None
                self._solved = False
                self._msg = None
                return

    def _return_to_tray(self, p):
        p.state = 'tray'
        p.wrong = False
        p.rect = p.build.get_rect(center=p.home)

    def _on_up(self, pos):
        if not self._drag:
            return
        p = self._drag
        from_slot = self._drag_from
        self._drag = None
        self._drag_from = None

        i = self._slot_of(p)
        # można wpiąć element tylko gdy sloty poniżej są zajęte (kolejność klas)
        if self._lower_filled(i):
            target = self._slot_center_for(p)
            dist = math.hypot(p.rect.centerx - target[0],
                              p.rect.centery - target[1])
            if dist < SNAP_RADIUS:
                old = self._slots[i]
                if old is not None and old is not p:
                    self._return_to_tray(old)        # SWAP: poprzedni wraca do tacki
                self._slots[i] = p
                p.lerp_from = p.rect.center
                p.lerp_to   = target
                p.lerp_t    = 0.0
                p.state     = 'snapping'
                self._msg   = None
                self._relayout()                     # reszta dopasowuje się do anchorów
                return

        # nie wpięto → wraca do tacki; jeśli był wyjęty ze struktury, zdejmij też
        # elementy znajdujące się nad nim (nie zostawiamy wiszących sierot)
        self._return_to_tray(p)
        if from_slot is not None:
            for j in range(from_slot + 1, len(self._slots)):
                if self._slots[j] is not None:
                    self._return_to_tray(self._slots[j])
                    self._slots[j] = None

    # -------------------------------------------------------------- logika

    def _is_full(self):
        return all(s is not None for s in self._slots)

    def _submit(self):
        target = self._target()
        placed = list(self._slots)
        ok = [target in p.match_species for p in placed]
        for p, good in zip(placed, ok):
            p.wrong = not good
        if all(ok):
            self._solved = True
            # wynik = 20 - pomyłki (liczony dla celu zadania = heterokinezyna-2)
            if target == CORRECT_SPECIES:
                self._score = max(0, 20 - self._fails)
            self._msg = None
        else:
            self._fails += 1
            name, is_chimera = self._build_name()
            tname = _SPECIES_NAME.get(target, target)
            if is_chimera:
                self._msg = (f'To niestety nie {tname} — to {name}!', False)
            else:
                self._msg = (f'To niestety nie {tname}, tylko {name}.', False)

    def _reset(self):
        """Zacznij od nowa: zdejmij wszystko do tacki (próby zostają)."""
        if self._drag is not None:
            self._return_to_tray(self._drag)
            self._drag = None
            self._drag_from = None
        for i in range(len(self._slots)):
            if self._slots[i] is not None:
                self._return_to_tray(self._slots[i])
                self._slots[i] = None
        self._solved = False
        self._msg = None

    # -------------------------------------------------------------- update

    def update(self, dt):
        self._t += dt
        for p in self._slots:
            if p is not None and p.state == 'snapping':
                p.lerp_t = min(1.0, p.lerp_t + dt * LERP_SPEED)
                fx, fy = p.lerp_from
                tx, ty = p.lerp_to
                e = 1.0 - (1.0 - p.lerp_t) ** 2
                p.rect.center = (int(fx + (tx - fx) * e), int(fy + (ty - fy) * e))
                if p.lerp_t >= 1.0:
                    p.state = 'placed'
                    self._relayout()

    # -------------------------------------------------------------- draw

    def draw(self):
        # 1) rysuj wszystko na stałej kanwie 1280x720
        w, h = config.W, config.H
        self._bg.draw(self._canvas, self._t)

        self._draw_microtubule(w, h)
        self._draw_assembly()
        self._draw_drop_hint()
        if self._drag:
            self._canvas.blit(self._drag.build, self._drag.rect)

        self._draw_tray(h)
        self._draw_reference(w, h)
        self._draw_hud(w, h)

        # 2) przeskaluj kanwę do okna (proporcjonalnie, wyśrodkowaną)
        win = self.screen
        s, ox, oy = self._view()
        scaled = pygame.transform.smoothscale(
            self._canvas,
            (max(1, int(config.W * s)), max(1, int(config.H * s))))
        win.fill(config.BG)
        win.blit(scaled, (int(ox), int(oy)))

    # ---- mikrotubula --------------------------------------------------

    def _draw_microtubule(self, w, h):
        y = self._mt_y()
        x0, x1 = TRAY_W, w - REF_W
        r = 13
        step = r * 2 - 4
        # dwa rzędy naprzemiennych koralików (dimery tubuliny)
        for row, ry in enumerate((y + r, y + r + step - 3)):
            x = x0 + r + (row * (step // 2))
            i = 0
            while x < x1 - r:
                col = MT_LIGHT if (i + row) % 2 == 0 else MT_DARK
                pygame.draw.circle(self._canvas, col, (x, ry), r)
                pygame.draw.circle(self._canvas, MT_DARK, (x, ry), r, 1)
                x += step
                i += 1

    # ---- struktura ----------------------------------------------------

    def _draw_assembly(self):
        # w etapie 1 kinezyna jest statyczna (kroczenie wydzielone do
        # src/effects.draw_walking_motor – do użycia w kolejnych etapach)
        for p in self._slots:
            if p is None or p is self._drag:
                continue
            self._canvas.blit(p.build, p.rect)
            if p.wrong:
                pygame.draw.rect(self._canvas, BAD_RED, p.rect.inflate(8, 8),
                                 3, border_radius=6)
            elif self._solved:
                pygame.draw.rect(self._canvas, OK_GREEN, p.rect.inflate(8, 8),
                                 3, border_radius=6)

    def _draw_drop_hint(self):
        if self._drag or self._solved or self._is_full():
            return
        cx, cy = self._connection_point()
        ax, bottom = int(cx), int(cy)
        key = self._next_class()
        # pulsujący znacznik miejsca + naturalny podpis nad nim
        pygame.draw.circle(self._canvas, config.ACCENT, (ax, bottom - 18),
                           SNAP_RADIUS, 1)
        txt = config.font(18, bold=True).render(
            f'Dołóż {_CLASS_ACC.get(key, "")}', True, config.ACCENT)
        self._canvas.blit(txt, txt.get_rect(center=(ax, bottom - 44)))

    # ---- tacka --------------------------------------------------------

    def _draw_tray(self, h):
        pygame.draw.rect(self._canvas, TRAY_BG, pygame.Rect(0, 0, TRAY_W, h))
        pygame.draw.line(self._canvas, config.MUTED, (TRAY_W, 0), (TRAY_W, h), 2)

        title = config.font(20, bold=True).render('Dostępne elementy', True, config.TEXT)
        self._canvas.blit(title, title.get_rect(centerx=TRAY_W // 2, y=14))
        sub = config.font(13).render('przeciągnij na mikrotubulę', True, config.MUTED)
        self._canvas.blit(sub, sub.get_rect(centerx=TRAY_W // 2, y=40))

        # nagłówki kolumn = klasy (kolejność budowania jest znana)
        col_w = (TRAY_W - 24) // 3
        for ci, (_, label) in enumerate(_CLASS_ORDER):
            cx = 12 + ci * col_w + col_w // 2
            t = config.font(13, bold=True).render(label, True, config.ACCENT)
            self._canvas.blit(t, t.get_rect(centerx=cx, y=66))

        for p in self._pieces:
            if p.state == 'tray':
                self._canvas.blit(p.thumb, p.thumb_rect)

    # ---- panel referencyjny ------------------------------------------

    def _draw_reference(self, w, h):
        x0 = w - REF_W
        pygame.draw.rect(self._canvas, REF_BG, pygame.Rect(x0, 0, REF_W, h))
        pygame.draw.line(self._canvas, config.MUTED, (x0, 0), (x0, h), 2)

        cx = x0 + REF_W // 2
        title = config.font(18, bold=True).render('Cel', True, config.TEXT)
        self._canvas.blit(title, title.get_rect(centerx=cx, y=14))

        # nazwa celu + strzałki wyboru
        tgt  = self._target()
        name = config.font(17, bold=True).render(
            _SPECIES_NAME.get(tgt, tgt), True, config.ACCENT)
        self._canvas.blit(name, name.get_rect(centerx=cx, y=42))

        self._arrow_l.center = (x0 + 22, 51)
        self._arrow_r.center = (x0 + REF_W - 22, 51)
        for rect, left in ((self._arrow_l, True), (self._arrow_r, False)):
            pygame.draw.rect(self._canvas, (205, 216, 236), rect, border_radius=6)
            cxr, cyr = rect.center
            tri = ([(cxr + 5, cyr - 7), (cxr + 5, cyr + 7), (cxr - 6, cyr)] if left
                   else [(cxr - 5, cyr - 7), (cxr - 5, cyr + 7), (cxr + 6, cyr)])
            pygame.draw.polygon(self._canvas, config.TEXT, tri)

        prev = self._target_preview(tgt)
        if prev:
            r = prev.get_rect(centerx=cx, y=78)
            self._canvas.blit(prev, r)
            note_y = r.bottom + 10
        else:
            note_y = 320
        cap = ('cel zadania – złóż ją, by przejść dalej'
               if tgt == CORRECT_SPECIES else 'złóż taką strukturę')
        note = config.font(12).render(cap, True, config.MUTED)
        self._canvas.blit(note, note.get_rect(centerx=cx, y=note_y))

    # ---- HUD ----------------------------------------------------------

    def _draw_top_text(self, text, color, size=17):
        """Napis u góry pola budowy, zawijany do jego szerokości (nie wchodzi
        na panele boczne)."""
        font  = config.font(size, bold=True)
        max_w = (config.W - REF_W) - TRAY_W - 40
        asm_cx = (TRAY_W + (config.W - REF_W)) // 2
        lines, cur = [], ''
        for word in text.split():
            trial = word if not cur else cur + ' ' + word
            if font.size(trial)[0] <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        y = 22
        for ln in lines:
            s = font.render(ln, True, color)
            self._canvas.blit(s, s.get_rect(centerx=asm_cx, y=y))
            y += s.get_height() + 2

    def _draw_hud(self, w, h):
        asm_cx = (TRAY_W + (w - REF_W)) // 2

        # tytuł w DWÓCH liniach ("Etap 1" / "Składanie") — krótka pierwsza linia
        # nie wchodzi już w komunikaty rysowane na środku górą pola budowy
        x0 = TRAY_W + 16
        self._canvas.blit(config.font(26, bold=True).render(
            'Etap 1', True, config.TEXT), (x0, 12))
        self._canvas.blit(config.font(18, bold=True).render(
            'Składanie', True, config.MUTED), (x0, 44))
        self._canvas.blit(config.font(24, bold=True).render(
            f'Wynik: {max(0, 20 - self._fails)}', True, config.ACCENT),
            (x0, 70))

        # komunikat (chimera / błąd) – u góry pola budowy, z zawijaniem
        if self._msg and not self._solved:
            self._draw_top_text(self._msg[0], BAD_RED)

        # dolny pasek – niżej, poniżej mikrotubuli (komunikaty są u góry)
        by = h - 26
        if self._solved:
            if self._target() == CORRECT_SPECIES:
                self._draw_top_text('Gotowe!', OK_GREEN, size=22)
                self._btn_next.center = (asm_cx, by)
                pygame.draw.rect(self._canvas, config.ACCENT, self._btn_next,
                                 border_radius=8)
                bt = config.font(20).render('Dalej →', True, config.WHITE)
                self._canvas.blit(bt, bt.get_rect(center=self._btn_next.center))
            else:
                self._draw_top_text(
                    'Gotowe! Złóż heterokinezynę-2, aby przejść dalej.', OK_GREEN)
        else:
            # Zatwierdź (gdy pełne) + Zacznij od nowa – obok siebie, wyśrodkowane
            row = []
            if self._is_full():
                row.append((self._btn_submit, 'Zatwierdź', OK_GREEN, config.WHITE))
            row.append((self._btn_reset, 'Zacznij od nowa', None, config.TEXT))
            gap = 16
            total = sum(r[0].width for r in row) + gap * (len(row) - 1)
            x = asm_cx - total // 2
            for rect, label, fill, txtcol in row:
                rect.center = (x + rect.width // 2, by)
                if fill is not None:
                    pygame.draw.rect(self._canvas, fill, rect, border_radius=8)
                else:
                    pygame.draw.rect(self._canvas, (224, 231, 244), rect,
                                     border_radius=8)
                    pygame.draw.rect(self._canvas, config.MUTED, rect, 1,
                                     border_radius=8)
                bt = config.font(18, bold=True).render(label, True, txtcol)
                self._canvas.blit(bt, bt.get_rect(center=rect.center))
                x += rect.width + gap
