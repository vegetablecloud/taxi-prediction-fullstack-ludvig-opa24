from taxipred.backend.data_processing import prepare_features, UserInput
from fastapi import FastAPI
import joblib
import xgboost as xgb
from pathlib import Path
from fastapi_mcp import FastApiMCP

TAXI_ML_PATH = Path(__file__).parents[0] / "models"

app = FastAPI()

mcp = FastApiMCP(app)
mcp.mount()


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/debug/view-code")
def view_own_code():
    try:
        with open(__file__, "r") as f:
            content = f.read()
        return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}


@app.get("/taxi/")
async def read_taxi_data():
    return {"Hello": "Taxis"}


@app.post("/predict")
async def predict_taxi_price(input: UserInput):
    df, trip_info, weather = prepare_features(input_data=input)
    # Retrived the trained XGB model.
    model: xgb.XGBRegressor = joblib.load(
        TAXI_ML_PATH / "broad_responsible_xgb_model.joblib"
    )

    # Predict with the user input values
    y_pred = model.predict(df)

    # Return the predicted value
    return {
        "predicted_price": float(y_pred[0]),
        "trip_info": trip_info,
        "weather": weather,
    }


# Version 2
