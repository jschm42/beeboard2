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
7. **Quality-Gates**: In `frontend/` muessen `npm run lint` und `npm run build` fehlerfrei durchlaufen.
