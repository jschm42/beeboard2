# Third-Party Notices and Attributions

This project uses third-party APIs, libraries, icons, and brand assets.

The entries below were verified against the current repository configuration and installed package metadata on 2026-05-22.

Note: This file is a practical attribution summary, not legal advice. If you distribute BeeBoard commercially, review all upstream license texts and terms directly.

## External APIs and Services

### OpenWeatherMap API

- Used for optional weather data and geocoding.
- Code reference: `backend/app/services/weather.py`
- Terms: https://openweathermap.org/terms

### OpenStreetMap Nominatim (Fallback Geocoding)

- Used as fallback geocoding service when OpenWeatherMap is unavailable.
- Code reference: `backend/app/services/weather.py`
- Usage policy: https://operations.osmfoundation.org/policies/nominatim/
- OSM attribution and license details: https://www.openstreetmap.org/copyright

Suggested attribution in app/documentation:

"Contains data from OpenStreetMap contributors, available under the Open Database License (ODbL)."

### LiteLLM and LLM Providers

- LiteLLM is used as routing layer for model providers.
- Code reference: `backend/app/services/ai_assistant.py`
- Default model configuration is provider-dependent (for example Gemini/OpenAI in environment settings).
- You must comply with provider terms and usage policies for any enabled model endpoint.

## Icons and Brand Assets

### Lucide Icons

- Package: `lucide-vue-next`
- License: ISC
- Source: https://lucide.dev

### Social/Brand Logos in `frontend/public/icons.svg`

The sprite includes logos for GitHub, Discord, X, and Bluesky.

- File reference: `frontend/public/icons.svg`
- These logos are typically protected by trademark/brand usage rules.
- Ensure your usage complies with each platform's current brand guidelines.
- BeeBoard does not imply endorsement or affiliation by these platforms.

### Custom SVG Assets Generated with Recraft

- Custom SVG illustrations/assets in `frontend/src/assets` and/or `frontend/public` were generated with Recraft.
- Generation was performed using paid credits.
- Ensure usage remains compliant with the active Recraft license/terms for your account tier at release time.

## Fonts

BeeBoard currently uses a CSS font stack:

- `Outfit`, `Inter`, then system fonts
- File reference: `frontend/src/style.css`

No webfont files are bundled in this repository at the moment.
If you later self-host or embed font files, add explicit attribution and license details here.

## Frontend Dependencies (selected)

License data was read from installed `package.json` metadata in `frontend/node_modules`.

| Package | Version | License |
| --- | --- | --- |
| vue | 3.5.34 | MIT |
| vue-router | 5.0.7 | MIT |
| pinia | 3.0.4 | MIT |
| axios | 1.16.1 | MIT |
| chart.js | 4.5.1 | MIT |
| dompurify | 3.4.5 | MPL-2.0 OR Apache-2.0 |
| marked | 18.0.3 | MIT |
| lucide-vue-next | 1.0.0 | ISC |
| vite | 8.0.13 | MIT |
| tailwindcss | 4.3.0 | MIT |

## Backend Dependencies (selected)

License data was read from Python distribution metadata in the active backend venv.

| Package | Version | License (metadata) |
| --- | --- | --- |
| fastapi | 0.110.3 | MIT (classifier) |
| uvicorn | 0.28.1 | BSD (classifier) |
| sqlalchemy | 2.0.49 | MIT |
| pydantic | 2.6.4 | MIT (classifier) |
| pydantic-settings | 2.2.1 | MIT (classifier) |
| python-jose | 3.5.0 | MIT |
| bcrypt | 5.0.0 | Apache-2.0 |
| python-multipart | 0.0.29 | Apache (classifier) |
| litellm | 1.83.0 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| email-validator | 2.3.0 | Unlicense |
| apscheduler | 3.11.2 | MIT |
