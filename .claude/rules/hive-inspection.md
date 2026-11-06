---
description: Fachregel Beuteninspektion nach der Achtel-Schaetzmethode - Eingabe je Zarge, Validierung (max. 300) und Berechnung ueber die Multiplikatoren des Wabenmasses (FrameType).
trigger: model_decision
paths:
  - "backend/app/services/calculations.py"
  - "backend/app/models/logbook.py"
  - "backend/app/models/administration.py"
  - "backend/app/routers/logbook.py"
  - "frontend/src/views/LogbookView.vue"
  - "frontend/src/components/LogbookEntryModal.vue"
---

# Beuteninspektion (Achtel-Schaetzmethode)

* **Konzept**: Der Imker verwendet einen Schaetzrahmen, der in 8 Teile unterteilt ist, um die Achtel von Brut,
  Bienen, Futter, Drohnen, Drohnenbrut und Pollen auf beiden Seiten einer Wabe zu schaetzen.
* **Datenerfassung**: Im Modus "in Achteln" (`eighths`) gibt der Imker die **Gesamtanzahl der Achtel je Zarge**
  (Summe ueber alle Waben der Zarge, beide Seiten) ein.
* **Validierung**: Der Wert je Kategorie und Zarge ist auf maximal **300** begrenzt (deckt alle ueblichen
  Wabenmasse ab).
* **Berechnung der Gesamtmenge (Zellenzahl/Gramm)**: Jede Kategorie hat einen Multiplikator am Wabenmass
  (`FrameType`), Beispielwerte fuer Zander:

  | Kategorie | Feld | Zander |
  | --- | --- | --- |
  | Brut | `brood_multiplier` | 400.0 |
  | Bienen | `bee_multiplier` | 125.0 |
  | Futter | `food_multiplier` | 125.0 |
  | Drohnen | `drone_multiplier` | 100.0 |
  | Drohnenbrut | `drone_brood_multiplier` | 230.0 |
  | Pollen | `pollen_multiplier` | 40.0 |

* Formel, identisch im Backend (`services/calculations.py`) und Frontend
  (`components/LogbookEntryModal.vue`: `calculatedBoxTotals` und `submitEntryForm`):

  `Gesamtmenge = Eingegebene Achtel * Multiplikator des Wabenmasses`

* Aenderungen an der Formel oder den Grenzen immer in Backend **und** Frontend nachziehen und
  `tests/test_calculations.py` anpassen. Standard-Wabenmasse kommen aus `app/scripts/seed.py`.
