from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel, Field
from datetime import datetime
import joblib
import xgboost as xgb
import pandas as pd
from pathlib import Path
import googlemaps
from googlemaps.directions import directions
import os
from dotenv import load_dotenv
import json
import requests
load_dotenv()


TAXI_ML_PATH = Path(__file__).parents[0] / "models"

class UserInput(BaseModel):
    pickup: str
    destination: str
    nr_passengers: int = Field(gt=0, lt=5)
    date: datetime

app = FastAPI()

taxi_data = TaxiData()

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()


def retrieve_google_direction_results(input_data: UserInput):
    """
    Takes in a validated UserInput pydantic instance object, and sends its data to google maps API and return its results
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    gmaps = googlemaps.Client(key=api_key)
    
    pickup = input_data.pickup
    destination = input_data.destination
    departure_time = input_data.date

    direction_results = directions(
        client=gmaps,
        origin=pickup,
        destination=destination,
        mode="driving",
        departure_time=departure_time
    )

    return direction_results[0]["legs"][0]

def retrieve_weather_data(input_data: UserInput):
    lat_lon_data = retrieve_google_direction_results(input_data=input_data)
    lat = lat_lon_data["start_location"]["lat"]
    lon = lat_lon_data["start_location"]["lng"]
    BASE_URL = "https://weather.googleapis.com/"
    endpoint = "v1/currentConditions:lookup"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    params = {
        "key": api_key,
        "location.latitude": lat,
        "location.longitude": lon
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    weather_data = response.json()
    weather = weather_data["weatherCondition"]["description"]["text"]

    return weather

def prepare_features(input_data: UserInput) -> pd.DataFrame:
    """
    Retrives user input in a pydantic model and convertes it to a dataframe our Ml-model can understand.
    """
    data = input_data.model_dump()

    trip_info = retrieve_google_direction_results(input_data=input_data)

    weather = retrieve_weather_data(input_data=input_data)

    feature_dict = {
        "Trip_Distance_km": trip_info["distance"]["value"] / 1000,  # API Google will deliver this
        "Passenger_Count": data["nr_passengers"],
        "Trip_Duration_Minutes": trip_info["duration"]["value"] / 60,  # API Google will deliver this
        "Time_of_Day_Evening": True if data["date"].hour >= 18 and data["date"].hour < 24 else False,
        "Time_of_Day_Morning": True if data["date"].hour >= 6 and data["date"].hour < 12 else False,
        "Time_of_Day_Night": True if data["date"].hour >= 0 and data["date"].hour < 6 else False,
        "Time_of_Day_Unknown": True if data["date"].hour < 0 else False,
        "Day_of_Week_Weekday": True if data["date"].weekday() < 5 else False,
        "Day_of_Week_Weekend": True if data["date"].weekday() >= 5 else False,
        "Weather_Rain": True if weather.lower() == "rain" else False,
        "Weather_Snow": True if weather.lower() == "snow" else False,
        "Weather_Unknown": True if weather.lower() not in ["rain", "snow", "clear", "sunny"] else False
    }

    df = pd.DataFrame([feature_dict])

    return df

@app.post("/predict")
async def predict_taxi_price(input: UserInput):
    
    df = prepare_features(input_data=input)
    # Retrived the trained XGB model. 
    model: xgb.XGBRegressor = joblib.load(TAXI_ML_PATH / "broad_responsible_xgb_model.joblib")
    
    # Predict with the user input values
    y_pred = model.predict(df)

    # Return the predicted value
    return float(y_pred[0])
    


if __name__ == "__main__":
    # Example and test of the function
    user_input = UserInput(
        pickup="Dunderbergsvägen 2 sjömarken",
        destination="Värmlandsgatan 2 Göteborg",
        nr_passengers=2,
        # date should be during rushhour for better testing wedsnesday 8am 2025
        date=datetime.now()
    )

    result = prepare_features(user_input)
    print(result)