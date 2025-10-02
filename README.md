# 🚕 Taxi Prediction Fullstack 

## Overview

- End-to-end dockerised solution that answers taxi prediction.
- FastAPI backend trip inputs with Google Maps directions and current weather with scoring an XGBoost model.
- Streamlit frontend collects pickup, destination, passenger count, and datetime, then renders fares and supporting metrics.
- ML workflow lives in the `explorations/` notebooks and produces curated datasets under `src/taxipred/data/`.
- Infrastructure is ready for local docker compose as well as separate frontend and backend deployments on Render.

## 🏗️ Architecture

- `src/taxipred/frontend/dashboard.py` runs the Streamlit UI and communicates with the API through `taxipred.utils.helpers`.
- `src/taxipred/backend/api.py` exposes the REST endpoints and loads the trained `broad_responsible_xgb_model.joblib`.
- `src/taxipred/backend/data_processing.py` prepares features by calling Google Directions and Weather and applying domain logic.
- `src/taxipred/utils/constants.py` centralises paths while `helpers.py` manages the API base URL for different environments.

```
Browser -> Streamlit frontend -> FastAPI backend -> Google APIs + XGBoost model -> Prediction response
```

## 🟢 Live Services

| Service | URL | Notes |
|---------|-----|-------|
| Frontend (Render) | `https://taxi-frontend.onrender.com` | Replace with the deployed dashboard URL once provisioned. |
| Backend (Render) | `https://taxi-api-dufk.onrender.com/` | Replace with the deployed API base; docs available at `/docs`. |
| Local frontend | `http://localhost:8501` | Served when running Streamlit locally or via docker compose. |
| Local backend | `http://localhost:8000` | Uvicorn with OpenAPI docs at `/docs` and `/predict` for scoring. |

## 🚀 Quick Start

### 🐳 Docker Compose Workflow (Recommended)

1.  **Configure API Keys**

    First, copy the `.example.env` template file to a new file named `.env`.

    ```bash
    cp .example.env .env
    ```

    Next, open the new `.env` file and replace `YOUR_API_KEY_HERE` with your actual Google Maps API key.

    ```text
    # .env
    GOOGLE_MAPS_API_KEY="AIzaSy...your...real...key"
    ```

2.  **Run the Application**

    > <details>
    > <summary><strong> 🐳 First Time Using Docker? Click here for setup instructions.</strong></summary>
    >
    > 1.  **Install Docker Desktop:** Download and install Docker Desktop for your operating system from the [official website](https://www.docker.com/products/docker-desktop/).
    >
    > 2.  **For Windows Users (WSL Update):** Docker Desktop on Windows requires WSL. You may be prompted to update it after installation. Open a PowerShell or Command Prompt terminal **as an administrator** and run:
    >
    >     ```bash
    >     wsl --update
    >     ```
    >     
    >     Restart your computer after the update.
    >
    > 3.  **Verify Installation:** Open a new terminal and run the following command:
    >
    >     ```bash
    >     docker --version
    >     ```
    >     
    >     You should see the Docker version printed. Now you are ready to proceed.
    >
    > </details>

    With Docker running, start the application using Docker Compose. This command will build the images if they don't exist and then start the services..
    
    ```bash
    docker compose up --build
    ```

3.  **Access Services**

    The services are now running in containers. Docker maps the container ports to your local machine (`localhost`), allowing you to access them from your browser:

    -   **Frontend Dashboard:** `http://localhost:8501`
    -   **Backend API Docs:** `http://localhost:8000/docs`

4.  **Stop the Application**

    To stop all running services, press `Ctrl + C` in the terminal where compose is running, and then run the following command to remove the containers and networks:

    ```bash
    docker compose down
    ```

---

### 🐍 Local Python Workflow (Alternative, without Docker)
_(Prerequisite: Ensure you have `uv` installed: `pip install uv`)_

1.  **Configure API Keys and Local URL**
    
    Copy `.example.env` to `.env`. Edit the file to add your API key and the local API URL for the frontend.

    ```text
    # .env
    GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
    API_URL="http://localhost:8000"
    ```

2.  **Create Environment and Sync Dependencies**

    ```bash
    # Install dependencies from pyproject.toml and uv.lock and autocreate a venv folder
    uv sync
    
    # Activate venv bash windows
    source .venv/scripts/activate

    # Activate venv powershell windows
    .venv/scripts/activate
    ```

3.  **Run the API (Terminal 1)**

    ```bash
    uvicorn taxipred.backend.api:app --reload --port 8000
    ```

4.  **Run the UI (Terminal 2)**

    ```bash
    streamlit run src/taxipred/frontend/dashboard.py
    ```

## 🔑 Environment variables

| Name | Used by | Description | Example |
|------|---------|-------------|---------|
| `Maps_API_KEY` | Backend | Grants access to Google Directions and Weather APIs. Loaded from `.env`. | `AIza...` |
| `API_URL` | Frontend | Overrides the default `http://api:8000` URL for local Python or deployed backends. | `http://localhost:8000` |

Store secrets locally in `.env` or in the Render dashboard under Environment.

## 📁 Repository structure
```text
.
├── .env                    # Local secrets (not committed)
├── .example.env            # Template for environment variables
├── explorations/           # Notebooks covering EDA, cleaning, and model experiments
├── src/
│   └── taxipred/
│       ├── backend/        # FastAPI app, feature engineering, and trained model artifacts
│       ├── data/           # Raw and processed datasets
│       ├── frontend/       # Streamlit dashboard source
│       └── utils/          # Shared helpers and constants
├── backend.Dockerfile      # Container definition for the API service
├── frontend.Dockerfile     # Container definition for the Streamlit service
├── docker-compose.yml      # Local orchestration of frontend and backend
└── pyproject.toml          # Project dependencies
```

## 📊 Data and ML workflow

- Start with `explorations/` notebooks to profile the raw taxi dataset and document decisions.
- Cleaned outputs live in `src/taxipred/data/taxi_trip_pricing_numeric_repaired.csv` for downstream use.
- Feature engineering in `prepare_features` adds Google travel time, distance, temporal buckets, and weather flags.
- The chosen estimator is an XGBoost regressor saved as `backend/models/broad_responsible_xgb_model.joblib`.
- Retraining requires exporting a refreshed joblib file into `src/taxipred/backend/models/` for the API container.

## 🔌 API endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check for monitoring and deployment smoke tests. |
| `/taxi/` | GET | Returns the cleaned dataset as JSON for BI explorations. |
| `/predict` | POST | Accepts pickup, destination, passengers, and datetime; returns price, trip info, and weather. |
| `/docs` | GET | OpenAPI schema and interactive documentation (auto-generated). |

Example request:

```json
{
  "pickup": "NBI Handelsakademin Goteborg",
  "destination": "Nordstan Goteborg",
  "nr_passengers": 2,
  "date": "2025-09-30T08:30:00"
}
```

## ☁️ Deployment on Render

- Create two Web Services: one using `backend.Dockerfile`, one using `frontend.Dockerfile`.
- Set `Maps_API_KEY` on the backend service and redeploy to enable Google integrations.
- Note the backend public URL and set `API_URL` on the frontend service to this URL so Streamlit can reach the API.
- Trigger redeploys via Render to pick up updated containers after each push.

## ✅ Assignment alignment

- Uppgift 0: Repository bootstrapped from `a2_packaging` layout with GitHub-ready structure.
- Uppgift 1: EDA and cleaning documented in notebooks and resulting CSVs under `src/taxipred/data/`.
- Uppgift 2: Model selection culminated in the XGBoost joblib artifact consumed by the API.
- Uppgift 3: FastAPI application exposes data endpoints and prediction logic backed by Google services.
- Uppgift 4: Streamlit dashboard offers a user-facing interface that consumes the backend API.