# Czcionki (assets/fonts/)

Opcjonalne pliki czcionek TrueType/OpenType.

## Zalecane czcionki

- **Orbitron** – nowoczesna, sci-fi, pasuje do motywu biologiczno-tech
  - Pobierz: https://fonts.google.com/specimen/Orbitron
  - Plik: `Orbitron-Regular.ttf`, `Orbitron-Bold.ttf`

- **Share Tech Mono** – monospace, czytelna
  - Pobierz: https://fonts.google.com/specimen/Share+Tech+Mono

## Jak użyć

Po dodaniu pliku czcionki zaktualizuj `src/config.py`:

```python
FONT_PATH = FONTS_DIR / "Orbitron-Regular.ttf"
```

Jeśli `FONT_PATH = None`, Pygame używa własnej domyślnej czcionki.
