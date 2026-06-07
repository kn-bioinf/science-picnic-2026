# Kinesin Game - Lista Assetów Graficznych

Wszystkie pliki graficzne muszą być przygotowane w formacie PNG z obsługą przezroczystości (kanał alfa).

## Faza Składania (Assembly)

* **kinesin_heads.png**
  Głowy motoryczne (stopy białka). Wygenerowane z bazy PDB (id: 3KIN) przy użyciu programu PyMOL (widok powierzchniowy / surface), a następnie obrysowane wektorowo w programie Inkscape.
* **kinesin_stalk.png**
  Trzon białka. Rysowany ręcznie w programie graficznym jako dwie splecione linie (struktura coiled-coil).
* **kinesin_tail.png**
  Ogon kinezyny z charakterystycznym wgłębieniem pełniącym rolę zamka dla białek receptorowych ładunku.
* **assembly_blueprint.png**
  Szara matryca całej kinezyny o przezroczystości ustawionej na 30%. Służy jako pole docelowe do przeciągania elementów (drag and drop). Powstaje z połączenia kształtów głów, trzonu i ogona.

## Ładunki (Cargo)

* **cargo_vesicle.png**
  Pęcherzyk synaptyczny (prawidłowy ładunek). Okrągły kształt z wypustką (kluczem) pasującą idealnie do wgłębienia w ogonie kinezyny.
* **cargo_mitochondria.png**
  Mitochondrium (prawidłowy ładunek). Owalny kształt z widocznymi wewnętrznymi pofałdowaniami i wypustką kompatybilną z ogonem.
* **cargo_wrong_lysosome.png**
  Lizosom lub uszkodzony pęcherzyk (błędny ładunek). Posiada inny kształt złącza, który uniemożliwia fizyczne połączenie z kinezyną w fazie składania.

## Minigra (Runner)

* **kinesin_walk_spritesheet.png**
  Arkusz animacji chodu kinezyny (od 4 do 6 klatek). Przedstawia naprzemienny ruch główek motorycznych (zasada hand-over-hand) wzdłuż osi X wraz z doczepionym na sztywno ładunkiem.
* **microtubule_tile.png**
  Kafel toru (mikrotubuli) przystosowany do ciągłego zapętlania. Składa się z dwóch rzędów ułożonych naprzemiennie okrągłych koralików (jasna i ciemna zieleń reprezentujące dimery tubuliny).
* **bg_axon_dark.png**
  Ciemne, stonowane i delikatnie rozmyte tło przedstawiające środowisko wewnątrz aksonu komórki nerwowej.
* **obstacle_tau.png**
  Białko Tau. Statyczna przeszkoda leżąca na powierzchni mikrotubuli, blokująca ruch kinezyny i wymuszająca reakcję gracza.
* **enemy_dynein_spritesheet.png**
  Dyneina. Ruchoma przeszkoda nadchodząca z naprzeciwka po tym samym torze. Wizualnie masywniejsza od kinezyny, w innym kolorze, niosąca własny pęcherzyk.