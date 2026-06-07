# KinesinQuest - Science Picnic 2026

Biologiczna gra edukacyjna o białku motorowym **kinezynie**.
Silnik gry: **Pygame** | Wizualizacja 3D: **PyMOL**

---

## Struktura gry

Ekran powitalny | Imię gracza, wybór poziomu
Level 1: Budowa kinezyny | Składanie "głowy", "nóg" i "butów" (3 kroki)
Minigra 1: Docking | Trafienie ATP do kieszeni - refleks
Minigra 2: Runner | Kinezyna na mikrotubuli - dino-runner
Ekran końcowy + Ranking

---

## Struktura kodu etapów
- Pliki `src/levels/level1/stage1.py`, `stage2.py`, `stage3.py` to szablony etapów. Każdy etap powinien implementować:
	- `handle_event(self, e)` — reaguj na input (klawiatura/mysz), wywołuj `self.next(score)` gdy etap się kończy,
	- `update(self, dt)` — logika/animacje (wywoływane co klatkę),
	- `draw(self)` — rysowanie na `self.screen`.
- Globalny wynik jest przechowywany w `GameState.score`; kontroler poziomu sumuje wartości przesłane przez `self.next(score)`.

## Wymagania

- Python **3.11**
- conda (zalecane - PyMOL najłatwiej przez conda-forge)

---

## Instalacja i uruchomienie

```bash
# 1. Sklonuj repo
git clone <repo-url>
cd science-picnic-2026

# 2. Utwórz środowisko
conda env create -f environment.yml

# 3. Aktywuj
conda activate kinesinquest

# 4. Uruchom
python main.py
```

### Opcje deweloperskie do szybszego sprawdzania poszczególnych etapów

```bash
python main.py --debug          # logi + pomiń animacje
python main.py --level 1        # zacznij od razu od poziomu 1
python main.py --minigame 1     # zacznij od minigry 1
python main.py --minigame 2     # zacznij od minigry 2
```

---

## Assety do przygotowania

- **Grafiki** → `assets/images/README.md`
- **Struktury 3D** (pliki PDB) → `assets/structures/README.md`
- Pobieranie PDB: `python tools/fetch_structures.py`

---

## Zasady współpracy

- Każdy etap → osobna gałąź: `feature/welcome`, `feature/level1-builder`, itd.
- Stan gry przez `GameState` - bez własnych globalnych zmiennych.
- Każdy ekran/minigra implementuje `handle_event()` / `update()` / `draw()`.

## Prosty workflow Git (jak tworzyć gałąź dla etapu)

1. Sklonuj repo (jeśli jeszcze tego nie zrobiłeś):

```bash
git clone <repo-url>
cd science-picnic-2026
```

2. Zaktualizuj `main` i stwórz feature branch:

```bash
git checkout main
git pull origin main
git checkout -b feature/level1-stage1
```

3. Wprowadzaj zmiany, commituj i wypychaj gałąź:

```bash
git add src/levels/level1/stage1.py
git commit -m "feat(level1): implement basic Stage1 UI and next() call"
git push -u origin feature/level1-stage1
```