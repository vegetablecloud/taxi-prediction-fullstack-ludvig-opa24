from taxipred.backend.data_processing import prepare_features, UserInput, TaxiData
from fastapi import FastAPI
import joblib
import xgboost as xgb
from pathlib import Path

TAXI_ML_PATH = Path(__file__).parents[0] / "models"

app = FastAPI()

taxi_data = TaxiData()

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()

@app.post("/predict")
async def predict_taxi_price(input: UserInput):
    
    df = prepare_features(input_data=input)
    # Retrived the trained XGB model. 
    model: xgb.XGBRegressor = joblib.load(TAXI_ML_PATH / "broad_responsible_xgb_model.joblib")
    
    # Predict with the user input values
    y_pred = model.predict(df)

    # Return the predicted value
    return float(y_pred[0])
    