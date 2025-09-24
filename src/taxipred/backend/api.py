from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel, Field
from datetime import datetime
from taxipred.backend import models
import joblib
from taxipred.utils.constants import TAXI_MODEL_PATH
import xgboost as xgb
import pandas as pd
from pathlib import Path


TAXI_ML_PATH = Path(__file__).parents[0] / "models"

class TripInput(BaseModel):
    distance: float
    passenger_count: int = Field(gt=0, lt=5)
    weather: str
    duration_minutes: float
    date: datetime


app = FastAPI()

taxi_data = TaxiData()

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()


@app.post("/predict")
def predict_taxi_price(input: TripInput):
    
    dict_values = input.model_dump()

    # Logic here to convert the user inputs to be able to to be converted so it matches the feats
    """
	Trip_Distance_km	Passenger_Count	Trip_Duration_Minutes	Time_of_Day_Evening	Time_of_Day_Morning	Time_of_Day_Night	Time_of_Day_Unknown	Day_of_Week_Weekday	Day_of_Week_Weekend	Weather_Rain	Weather_Snow	Weather_Unknown
    0	19.35	3.0	53.82	False	True	False	False	True	False	False	False	False
    """
    # Here we need to map the values. We need this row finnsihed perhaps..

    dict_for_model = {
        "Trip_Distance_km": dict_values["distance"],
        "Passenger_Count": dict_values["passenger_count"],
        "Trip_Duration_Minutes": dict_values["duration_minutes"],
        "Time_of_Day_Evening": True if dict_values["date"].hour >= 18 and dict_values["date"].hour < 24 else False,
        "Time_of_Day_Morning": True if dict_values["date"].hour >= 6 and dict_values["date"].hour < 12 else False,
        "Time_of_Day_Night": True if dict_values["date"].hour >= 0 and dict_values["date"].hour < 6 else False,
        "Time_of_Day_Unknown": True if dict_values["date"].hour < 0 else False,
        "Day_of_Week_Weekday": True if dict_values["date"].weekday() < 5 else False,
        "Day_of_Week_Weekend": True if dict_values["date"].weekday() >= 5 else False,
        "Weather_Rain": True if dict_values["weather"] == "Rain" else False,
        "Weather_Snow": True if dict_values["weather"] == "Snow" else False,
        "Weather_Unknown": True if dict_values["weather"] not in ["Rain", "Snow", "Clear"] else False
    }

    # Convert dict_for_model to dataframe
    df_input_values = pd.DataFrame([dict_for_model])
    
    print(df_input_values)

    model: xgb.XGBRegressor = joblib.load(TAXI_ML_PATH / "broad_responsible_xgb_model.joblib")
    
    y_pred = model.predict(df_input_values)

    return f" Din resa kostar uppskattningsvis {y_pred[0]:.2f} dollar!"
    


