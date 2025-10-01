from taxipred.backend.data_processing import prepare_features, UserInput, TaxiData
from fastapi import FastAPI
import joblib
import xgboost as xgb
from pathlib import Path

TAXI_ML_PATH = Path(__file__).parents[0] / "models"

app = FastAPI()

taxi_data = TaxiData()

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()

@app.post("/predict")
async def predict_taxi_price(input: UserInput):

    df, trip_info, weather = prepare_features(input_data=input)
    # Retrived the trained XGB model.
    model: xgb.XGBRegressor = joblib.load(TAXI_ML_PATH / "broad_responsible_xgb_model.joblib")
    
    # Predict with the user input values
    y_pred = model.predict(df)

    # Return the predicted value
    return {
        "predicted_price": float(y_pred[0]),
        "trip_info": trip_info,
        "weather": weather
    }
    
# Version 2