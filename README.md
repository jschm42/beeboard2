# 🐝 BeeBoard 2 — Reactive Beekeeping Log & AI Assistant

Welcome to **BeeBoard 2**, a modern, reactive beekeeping log (Stockkarte) and AI assistant designed to help beekeepers manage their apiaries (Standorte), hives (Bienenvölker), and inspections (Stockkarten-Einträge) with ease. 

By combining a fast **FastAPI + SQLite** backend with an intuitive, dynamic **Vue 3 + Vite + Tailwind CSS** frontend, BeeBoard 2 delivers a premium digital companion for modern apiculture. It also features a contextual **AI Assistant** (powered by LiteLLM) that answers complex questions about your hives and parses natural language notes into structured records.

---

## 🚀 Key Features

*   **🍯 Apiary & Location Management**: Track geographic locations, addresses, and custom notes for multiple apiaries.
*   **🐝 Hive Management**: Record setup dates, frame types (e.g., Zander, Dadant), active status, and queen information (year of birth, marking color, breed).
*   **📋 Inspection Logbook (Stockkarte)**: Record frame-level details (brood, food, and bees), swarm instinct, temperament, queen sightings, varroa drop rates, and autumn/winter treatments.
*   **🤖 AI Bee Assistant**: Context-aware AI chatbot that reads your apiary data, hive configurations, and historical inspection logs to provide diagnostics and apicultural advice.
*   **🎙️ Natural Language Drafts**: Dictate or type a simple note (e.g., *"Volk 1 had 5 frames of brood and 3 food, temper was fine"*), and let the AI automatically structure it into a logbook entry draft!
*   **📊 Rich Statistics & Charts**: Visual data analysis of honey yields, varroa mite progression, frame metrics, and colony health trends.
*   **🔐 User Authentication**: Secure, role-based registration and login with JWT tokens.

---

## 📂 Project Architecture

BeeBoard is organized as a clean **monorepo**:

*   **`backend/`**: Python FastAPI app with SQLAlchemy ORM, LiteLLM integrations, SQLite database storage, and a robust test suite.
*   **`frontend/`**: Vue 3 SPA powered by Vite, Pinia for reactive state management, Tailwind CSS for responsive styling, and Chart.js for data visualization.

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

### 3. Docker Setup (Backend + Frontend + Nginx)

You can also run BeeBoard 2 via Docker with an Nginx reverse proxy in front of the backend and the built frontend.

All Docker-related files live in the `docker/` directory:

* `docker/Dockerfile.backend` – builds the Python FastAPI backend image.
* `docker/Dockerfile.frontend` – builds the Vue frontend and serves it via Nginx.
* `docker/nginx.conf` – Nginx configuration (serves SPA and proxies `/api/` to the backend).
* `docker/docker-compose.yml` – defines the `backend`, `frontend` (build stage) and `nginx` services.
* `docker/setup.ps1` – convenience script to start the stack.
* `docker/update.ps1` – convenience script to rebuild/update the stack.

#### 🔧 Configurable Ports & Data Directory

The Docker setup is controlled via the following environment variables (with defaults):

* `BEEBOARD_HTTP_PORT` – external HTTP port for Nginx (default: `8080`).
* `BEEBOARD_BACKEND_PORT` – external port mapped to the backend container (default: `8000`).
* `BEEBOARD_DOCKER_DATA` – host directory for persistent data (default: `./data` inside `docker/`).

These are set automatically by the PowerShell helper scripts.

#### ▶️ Start the Docker Stack (Windows / PowerShell)

From the repository root, open PowerShell and run:

```powershell
cd docker
./setup.ps1
```

This will:

1. Build the backend and frontend images.
2. Start the backend, build the frontend, and run Nginx as reverse proxy.
3. Expose the app at `http://localhost:8080` (or your configured `BEEBOARD_HTTP_PORT`).

You can override ports and data directory via parameters, e.g.:

```powershell
./setup.ps1 -HttpPort 80 -BackendPort 9000 -DataDir "D:\\beeboard-data"
```

#### 🔁 Update / Rebuild the Docker Stack

To rebuild images and restart the stack after code changes:

```powershell
cd docker
./update.ps1 -HttpPort 8080 -BackendPort 8000 -DataDir "data"
```

This will run `docker compose up -d --build` with the given configuration.

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
