# KinesinQuest - Science Picnic 2026

Biologiczna gra edukacyjna o białku motorycznym **kinezynie**.
Silnik gry: **Pygame** | Struktury białek renderowane offline w **PyMOL**

---

## Struktura gry

Menu | Imię gracza, wybór trybu, ranking, wiedza i instrukcja
Level 1:
    Etap 1 - Składanie | Złóż heterokinezynę-2 z domen (głowa motoryczna → trzon → ogon), wybierając właściwe warianty
    Etap 2 - Dokowanie | Zrzuć ładunek (pęcherzyk / mitochondrium / lizosom) dokładnie na ogon kinezyny - refleks
    Etap 3 - Transport | Kinezyna biegnie po mikrotubuli i omija przeszkody (białka MAP, dyneinę, luki w torze) - styl dino-runner
Ekran końcowy + Ranking

---

## Struktura kodu etapów
- Pliki `src/levels/level1/stage1.py`, `stage2.py`, `stage3.py` to szablony etapów. Każdy etap powinien implementować:
	- `handle_event(self, e)` - reaguj na input (klawiatura/mysz), wywołuj `self.next(score)` gdy etap się kończy,
	- `update(self, dt)` - logika/animacje (wywoływane co klatkę),
	- `draw(self)` - rysowanie na `self.screen`.
- Każdy etap przekazuje swój wynik przez `self.next(score)`. `Level1Controller` zbiera wyniki kolejnych etapów, a `GameManager.finish_full` sumuje je do `GameState.score` (w trybie pojedynczego etapu zapisywany jest tylko wynik danego etapu). Konwencja wyniku jest tak dobrana, by był w miarę spójny i porównywalny między etapami (szczegóły w docstringu `GameState`).

## Wymagania

- Python **3.11**
- conda

---

## Instalacja i uruchomienie

```bash
# 1. Sklonuj repo
git clone git@github.com:kn-bioinf/science-picnic-2026.git
cd science-picnic-2026

# 2. Utwórz środowisko
conda env create -f environment.yml

# 3. Aktywuj
conda activate kinesinquest

# 4. Uruchom
python main.py
```

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
