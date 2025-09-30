# Taxi Prediction Fullstack

Full-stack learning project that predicts taxi fares by combining a FastAPI backend, an XGBoost regression model, and a Streamlit dashboard. The repository also includes exploratory notebooks and Docker assets so you can learn the entire workflow end to end.

## Key Features
- FastAPI service that exposes both the cleaned training data and a `/predict` endpoint.
- XGBoost regression model trained on the processed taxi trip dataset and saved with `joblib`.
- Streamlit dashboard for collecting trip details, calling the backend, and presenting the prediction.
- Docker setup (`docker-compose`) that lets you run the backend and frontend together.
- Utility helpers for talking to the API from any client.

## Project Layout
```
.
|-- explorations/                  # Jupyter notebooks used for data exploration
|-- src/
|   |-- taxipred/
|       |-- backend/               # FastAPI app and model serving code
|       |-- data/                  # Raw and cleaned CSV files used for training
|       |-- frontend/              # Streamlit dashboard
|       |-- utils/                 # Shared constants and API helper functions
|-- backend.Dockerfile             # Backend image definition
|-- frontend.Dockerfile            # Frontend image definition
|-- docker-compose.yml             # Orchestrates both services
|-- README.md                      # You are here
```

## Running With Docker
```bash
docker compose up --build
```
- http://localhost:8000 exposes the FastAPI docs (`/docs`).
- http://localhost:8501 serves the Streamlit UI.

## Environment Variables
- `GOOGLE_MAPS_API_KEY` - required for Google Directions and Weather lookups.

> Tip: never commit secrets to Git. Store values in a local `.env` file or a secret manager.

## API Overview
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic health check |
| `/taxi/` | GET | Returns the cleaned taxi trip dataset |
| `/predict` | POST | Accepts pickup, destination, passenger count, and datetime to return a fare prediction |

Sample request body:
```json
{
  "pickup": "NBI Handelsakademin Goteborg",
  "destination": "Nordstan Goteborg",
  "nr_passengers": 2,
  "date": "2025-09-30 08:30:00"
}
```

## Model & Data
- Dataset files live in `src/taxipred/data/` (raw, cleaned, and imputed variants).
- The production model is saved in `src/taxipred/backend/models/broad_responsible_xgb_model.joblib`.
- The backend builds feature vectors using Google Maps travel time and weather metadata before scoring with XGBoost.

## Development Notes
- Exploratory analysis lives under `explorations/`; open the notebook to revisit the EDA.
- Utilities in `src/taxipred/utils/helpers.py` wrap `requests` so other clients can call the API.
- To retrain, reuse the EDA notebook or create a new one, train a model, and export with `joblib.dump` into `src/taxipred/backend/models/`.

## Next Steps / Ideas
- Add automated tests for the feature engineering pipeline and API.
- Improve error handling around external API calls (missing keys, rate limits, invalid addresses).
- Parameterize the API base URL so the Streamlit app also works outside Docker.
- Harden deployment by moving secrets into a vault or container runtime configuration.

Happy hacking and lycka till med projektet!
