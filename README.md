# 🐝 BeeBoard 2 — Reactive Beekeeping Log & AI Assistant

Welcome to **BeeBoard**, a modern beekeeping logbook (Stockkarte) with an integrated AI assistant.

The project helps beekeepers manage apiaries (Standorte), hives (Bienenvölker), inspections (Stockkarten-Einträge), honey harvests, sales, and recurring tasks in one place.

BeeBoard 2 combines a fast **FastAPI + SQLite** backend with an intuitive **Vue 3 + Vite + Tailwind CSS** frontend. A context-aware **AI Assistant** (powered by LiteLLM) can answer questions about your data and convert natural-language notes into structured entries.

> [!WARNING]
> **Current scope:** BeeBoard is currently primarily in **German language** and aligned with **German beekeeping practices**.
> 
> **Planned direction:** Internationalization is planned, and most core features are already broadly applicable across regions.
> 
> **Community support wanted:** Help with translations, regional defaults, domain validation, and UX adaptation for non-German beekeeping workflows is very welcome.

---

## 🚀 Key Features

*   **🍯 Multi-Apiary & Location Management**: Manage multiple stands with addresses, geo-context, notes, and ownership information.
*   **🐝 Hive Lifecycle Management**: Track setup date, status, frame system (e.g., Zander, Dadant), queen metadata, and per-hive history.
*   **📋 Detailed Inspection Logbook (Stockkarte)**: Capture brood/food/bee frame metrics, temperament, swarm signs, queen sightings, varroa counts, and seasonal treatments.
*   **🧠 AI Assistant for Beekeeping Decisions**: Ask contextual questions based on your actual hive and inspection data to get practical diagnostics and suggestions.
*   **🎙️ Natural-Language Entry Drafting**: Convert free text or dictated notes into structured logbook drafts to reduce manual input.
*   **🍯 Honey Batch Management**: Record harvest and bottling data, batch metadata, and traceability information.
*   **💶 Sales Tracking**: Track products, sales channels, pricing, and sales records connected to honey batches.
*   **✅ Task Planning & Reminders**: Organize recurring and seasonal tasks for locations and hives.
*   **📊 Statistics & Visual Analytics**: Analyze trends for yield, varroa progression, colony strength, and operational outcomes.
*   **🔐 Secure Authentication & Roles**: JWT-based auth with role-aware access for protected areas.
*   **🛠️ API-First Backend**: Well-structured REST endpoints with Pydantic schemas and SQLAlchemy models for maintainable integrations.

---

## 📂 Project Architecture

BeeBoard is organized as a clean **monorepo**:

*   **`backend/`**: Python FastAPI app with SQLAlchemy ORM, LiteLLM integrations, SQLite database storage, and a robust test suite.
*   **`frontend/`**: Vue 3 SPA powered by Vite, Pinia for reactive state management, Tailwind CSS for responsive styling, and Chart.js for data visualization.

---

## Third-Party Licenses and Attributions

BeeBoard uses third-party APIs, open-source dependencies, icon sets, and brand assets.

Please review [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for:

1. A dependency license summary for frontend and backend packages.
2. API and service attribution requirements (including OpenWeatherMap and OpenStreetMap Nominatim/ODbL references).
3. Icon and brand asset usage notes.
4. Font usage notes and future self-hosting guidance.
5. Provenance notes for custom SVG assets generated with Recraft (paid credits).

An in-app About dialog is available from the sidebar and summarizes the same attribution context for end users.

For a practical pre-release process, use [RELEASE_COMPLIANCE_CHECKLIST.md](RELEASE_COMPLIANCE_CHECKLIST.md).

For production and commercial deployments, verify all upstream license and terms pages directly as part of your release process.

---

## 🛠️ Getting Started: Step-by-Step Guide

Follow the quick automated setup below to get everything up and running in seconds, or scroll down for the manual setup steps.

---

### 🚀 Quick Automated Setup (Recommended)

We provide interactive setup scripts for both **PowerShell (Windows)** and **Bash (macOS / Linux / Git Bash)**. These scripts will:
1. Verify your Python installation (**Python 3.13**).
2. Create a Python Virtual Environment (`.venv`) inside the `backend/` directory.
3. Upgrade `pip` and install all required dependencies from `backend/requirements.txt`.
4. Copy the environment configuration template `backend/.env.example` to `backend/.env`.
5. Automatically generate a secure, random `SECRET_KEY` for JWT authentication.
6. Interactively prompt you for your `GEMINI_API_KEY` (optional) and save it directly to `.env`.

#### 💻 On Windows (PowerShell)
Open a PowerShell terminal in the repository root and run:
```powershell
.\scripts\setup.ps1
```
*Note: If script execution is blocked on your system, you can bypass it for this run with:*
`PowerShell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`

#### 🐧 On macOS / Linux / Git Bash
Open a terminal in the repository root and run:
```bash
./scripts/setup.sh
```

**Next Steps:**
Once the setup script finishes, you are ready to seed the database and start the backend! Go to [🌱 Seed the Database](#-seed-the-database) below and then jump straight to the [2. Frontend Setup (Vue 3 + Vite)](#2-frontend-setup-vue-3--vite) guide!

---

### 1. Manual Backend Setup (Alternative)

The backend is built with **Python 3.13** and FastAPI.

#### 📁 Navigate to the backend directory
```bash
cd backend
```

#### 🐍 Create & Activate a Python Virtual Environment

A Virtual Environment (`venv`) isolates your python interpreter and packages for this project. This prevents version conflicts with other projects on your machine.

##### Step 1: Create the Virtual Environment
Ensure you are in the `backend/` directory, then run:
```bash
# Windows / macOS / Linux
python -m venv venv
```
*Note: If `python` is not recognized, try `python3` or `py`.*

##### Step 2: Activate the Virtual Environment
Activate the environment based on your operating system and terminal:

*   **On Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*   **On Windows (Command Prompt):**
    ```cmd
    .\venv\Scripts\activate.bat
    ```
*   **On macOS / Linux (Bash/Zsh):**
    ```bash
    source venv/bin/activate
    ```

Once activated, your terminal prompt will be prefixed with `(venv)`.

---

##### ⚠️ Troubleshooting Windows PowerShell Activation
If you receive the error:
> *"Script.ps1 cannot be loaded because running scripts is disabled on this system..."*

This is due to Windows execution policies. You can resolve it in one of three ways:

1.  **Temporary Bypass (Recommended)**: Allow script execution only for your current terminal window:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .\venv\Scripts\Activate.ps1
    ```
2.  **Permanent User Bypass**: Allow it for all your PowerShell sessions on this user account:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
3.  **Use Command Prompt**: If PowerShell continues to block scripts, simply open a classic Command Prompt (`cmd`) and run:
    ```cmd
    .\venv\Scripts\activate.bat
    ```

##### 🔄 Upgrading Pip (Optional but Recommended)
After activating, ensure your package manager is up to date:
```bash
python -m pip install --upgrade pip
```

#### 📦 Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 🔑 Configure Environment Variables
Create a file named `.env` in the `backend/` directory to configure your secret keys and LLM providers.

Create `backend/.env`:
```env
# Security settings (change in production)
SECRET_KEY=supersecretkeychangeinproduction1234567890
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database URL (SQLite)
DATABASE_URL=sqlite:///./data/beeboard.db

# LiteLLM Configuration
# By default, Gemini 2.5 Flash is configured
LITELLM_MODEL=gemini/gemini-2.5-flash

# API Key for Gemini (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# Alternatively, if you want to use OpenAI:
# LITELLM_MODEL=openai/gpt-4o-mini
# OPENAI_API_KEY=your_openai_api_key_here
```

#### 🧱 Run Database Migrations (Alembic)
Before seeding data, apply the database schema migrations using Alembic:

```bash
alembic upgrade head
```

#### 🌱 Seed the Database
After the schema is in place, execute the seed script to set up default configurations (e.g., default Hive Frame Types like *Zander* or *Dadant*, and Seasonal Varroa Multipliers):

```bash
python -m app.scripts.seed
```

#### ⚡ Start the Backend Server (Uvicorn)
Start the FastAPI application with automatic reloading on change:

```bash
uvicorn app.main:app --reload --port 8000
```
Your backend API will now be running at **`http://localhost:8000`**.
*   **Swagger API Docs**: You can explore and test the endpoints directly at **`http://localhost:8000/docs`**.
*   **Redoc**: Alternative API documentation is available at **`http://localhost:8000/redoc`**.

---

### 2. Frontend Setup (Vue 3 + Vite)

The frontend is an SPA built with Vue 3, Vite, and Tailwind CSS. It is configured to proxy all `/api` and `/uploads` requests automatically to the backend on `http://localhost:8000`.

#### 📁 Navigate to the frontend directory
Open a new terminal window or tab and run:
```bash
cd frontend
```

#### 📦 Install Node Modules
Make sure you have Node.js (version 18+ recommended) installed, then run:
```bash
npm install
```

#### 🚀 Start the Vite Development Server
```bash
npm run dev
```
The frontend will start instantly and be accessible at **`http://localhost:3000`** (as configured in `vite.config.js`). 

Open your browser and navigate to **`http://localhost:3000`** to register your beekeeping account and start log-keeping!

#### 📦 Production Build & Deployment (Optional)
To compile and minify the static application assets for production, run:
```bash
npm run build
```
This saves the compiled, production-ready assets into the `dist/` directory.

To preview and test the production build locally, run:
```bash
npm run preview
```
This hosts the compiled files on a local static web server (typically port `4173`).

---

### 3. Docker Setup (Backend + Frontend + Nginx with HTTPS/SSL)

You can run BeeBoard 2 via Docker with an Nginx reverse proxy serving the frontend, proxying API requests to the backend, and securing all traffic with HTTPS (SSL).

All Docker-related files live in the `docker/` directory:

* `docker/Dockerfile.backend` – builds the Python FastAPI backend image and runs migrations automatically at startup.
* `docker/Dockerfile.frontend` – builds the Vue frontend and copies static assets to Nginx.
* `docker/nginx.conf` – Nginx configuration (handles SSL, redirects HTTP to HTTPS, supports WebSockets, and proxies `/api/` to the backend).
* `docker/docker-compose.yml` – defines the backend, frontend (build stage), and Nginx reverse proxy services.
* `docker/setup.ps1` / `docker/setup.sh` – convenience scripts (PowerShell & Bash) to generate SSL certificates and start the stack.
* `docker/update.ps1` / `docker/update.sh` – convenience scripts to pull, rebuild, and restart the stack.

#### 🔧 Configurable Ports & Data Directory

The Docker setup is controlled via the following environment variables (defined in `backend/.env` or passed to scripts):

* `BEEBOARD_HTTP_PORT` – external HTTP port (default: `8080`, redirects to HTTPS).
* `BEEBOARD_HTTPS_PORT` – external HTTPS port for Nginx (default: `8443` or `443` for standard HTTPS).
* `BEEBOARD_BACKEND_PORT` – external port mapped directly to the backend container (default: `8000`).
* `BEEBOARD_DOCKER_DATA` – host directory for persistent database and upload data (default: `./docker/data`).

#### 🔑 SSL Certificates

The setup scripts will automatically check if SSL certificates exist in `docker/certs/`. If they do not, they will start an ephemeral Docker container to generate a secure, self-signed SSL certificate (`nginx.crt` / `nginx.key`) automatically. No local OpenSSL installation is required.

#### ▶️ Start the Docker Stack

##### 💻 On Windows (PowerShell)
From the repository root, run:
```powershell
cd docker
.\setup.ps1
```
You can override configuration using parameters:
```powershell
.\setup.ps1 -HttpPort 80 -HttpsPort 443 -BackendPort 9000 -DataDir "C:\beeboard-data"
```

##### 🐧 On macOS / Linux / Git Bash
From the repository root, run:
```bash
cd docker
chmod +x *.sh
./setup.sh
```

##### 🌐 Accessing the Application
Once the stack is up, you can access the application securely:
* **HTTPS**: **`https://localhost:8443`** (or your configured `BEEBOARD_HTTPS_PORT`)
* **HTTP**: `http://localhost:8080` (automatically redirects to the HTTPS address)

> [!NOTE]
> Since the SSL certificate is self-signed for local development, your browser will show a security warning. You can safely bypass this warning (click "Advanced" and "Proceed to localhost") to access the app.

#### 🔁 Update / Rebuild the Docker Stack

To pull new base images, rebuild after code changes, and restart the stack:

##### 💻 On Windows (PowerShell)
```powershell
cd docker
.\update.ps1
```

##### 🐧 On macOS / Linux / Git Bash
```bash
cd docker
./update.sh
```


---

### 🧪 Running Tests

BeeBoard includes a comprehensive test suite for the backend. To run the automated tests:

1.  Make sure you are in the `backend/` directory.
2.  Activate your virtual environment.
3.  Run the tests using `pytest`:
    ```bash
    pytest
    ```

---

## 🗃️ Database & Uploads Data

All persistent data is stored in the `backend/data/` folder:
*   **`beeboard.db`**: The SQLite database file.
*   **`uploads/`**: User-uploaded photos of hives and inspections, which are automatically served by FastAPI.

> [!NOTE]
> The `backend/data` folder is automatically created on app startup if it does not already exist.

---

## 🐝 Quick Beekeeper Tips
1.  **Create your first Apiary (Standort)** under the **Standorte** tab.
2.  **Add a Hive (Volk)** under the **Bienenvölker** tab. Be sure to specify the frame dimensions.
3.  **Start Logging** under the **Stockkarte** tab. You can type natural text and click the *AI Draft* button to let the AI auto-fill the form for you!
4.  Ask the **AI Assistant** on the Dashboard for diagnostics: e.g. *"Is my Varroa drop rate too high for spring?"* or *"Give me a summary of Volk 1's health."*
