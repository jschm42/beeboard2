---
description: Frontend-Regeln fuer BeeBoard 2 - Vue 3 Views/Komponenten, Pinia-Stores, zentrale API-Aufrufe, i18n und Quality-Gates.
trigger: glob
globs: "frontend/**/*.js, frontend/**/*.vue"
paths:
  - "frontend/**/*.js"
  - "frontend/**/*.vue"
---

# Frontend Guidelines (Vue 3 + Vite + Tailwind)

1. **Aufbau**: Views orchestrieren, Komponenten kapseln Darstellung und Interaktion. Wiederverwendbares gehoert in
   `components/` bzw. `utils/`.
2. **State**: Gemeinsamer State in Pinia-Stores (`src/stores/`), nicht in globalen Variablen.
3. **API**: Aufrufe zentral und nachvollziehbar ueber axios; Fehler ueber den `error`-Store anzeigen.
4. **i18n**: Keine hartcodierten UI-Texte. Neue Schluessel immer in `src/locales/de.json` **und**
   `src/locales/en.json` anlegen.
5. **Sicherheit**: Markdown/HTML aus Backend oder KI nur ueber `marked` + `DOMPurify` rendern, nie ungefiltert per
   `v-html`.
6. **Konsistenz**: Composition API und den Stil der Nachbardateien beibehalten; `const` statt `let`, wo moeglich.
   * Seitenkopf jeder View ueber `components/PageHeader.vue` (Props `title`, `subtitle`, `icon` oder gleichnamige
     Slots, Buttons im Slot `actions`). Kein "Zurueck zum Dashboard"-Link, die Sidebar uebernimmt die Navigation.
   * Typografie: kleinste Schrift `text-[11px]` (Badges), Labels/Meta `text-xs`, Fliesstext `text-sm`.
     Gewichte nur bis `font-bold`; Hierarchie ueber Groesse statt `font-black`/`font-extrabold`.
7. **Quality-Gates**: In `frontend/` muessen `npm run lint` und `npm run build` fehlerfrei durchlaufen.
