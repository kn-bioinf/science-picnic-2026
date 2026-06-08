# KinesinQuest - Science Picnic 2026

Biologiczna gra edukacyjna o białku motorowym **kinezynie**.
Silnik gry: **Pygame** | Wizualizacja 3D: **PyMOL**

---

## Struktura gry

Ekran powitalny | Imię gracza, wybór poziomu
Level 1:
    Budowa kinezyny | Składanie "głowy", "nóg" i "butów" (3 kroki)
    Minigra 1: Docking | Trafienie ATP do kieszeni - refleks
    Minigra 2: Runner | Kinezyna na mikrotubuli - dino-runner
Ekran końcowy + Ranking

---

## Struktura kodu etapów
- Pliki `src/levels/level1/stage1.py`, `stage2.py`, `stage3.py` to szablony etapów. Każdy etap powinien implementować:
	- `handle_event(self, e)` — reaguj na input (klawiatura/mysz), wywołuj `self.next(score)` gdy etap się kończy,
	- `update(self, dt)` — logika/animacje (wywoływane co klatkę),
	- `draw(self)` — rysowanie na `self.screen`.
- Globalny wynik jest przechowywany w `GameState.score`; kontroler poziomu sumuje wartości przesłane przez `self.next(score)`. Co do implementacji wyniku możemy się zastanowić tak, aby wynik pomiędzy etapami był w miarę spójny i skalowalny.

## Wymagania

- Python **3.11**
- conda

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

Będą potrzebne grafiki i może kilka poglądowych struktur 3D z pdb do wyświetlania użytkownikom. Reszta informacji w readme w poszczególnych katalogach
- **Grafiki** → `assets/images/README.md`
- **Struktury 3D** (pliki PDB) → `assets/structures/README.md`

---

## Mini tutorial git

Każdy implementowany etap powinien mieć swoją gałąź np: `welcome`, `level1-builder`


1. Klonowanie repozytorium przez SSH
```bash
git clone git@github.com:kn-bioinf/science-picnic-2026.git
cd science-picnic-2026
```
2. Aktualizacja gałęzi głównej i stworzenie nowej gałęzi (feature branch) - tu dla przykładu stage 1 levelu 1
```bash
git switch main
git pull
git switch -c level1-stage1
```
3. Dodawanie zmian, commit i pierwsze wypchnięcie gałęzi
```bash
git add src/levels/level1/stage1.py
git commit -m "komentarz do commita"
git push -u origin level1-stage1
```