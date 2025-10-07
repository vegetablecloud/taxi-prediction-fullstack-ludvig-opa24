from taxipred.backend.data_processing import prepare_features, UserInput
from fastapi import FastAPI
import joblib
import xgboost as xgb
from pathlib import Path
from fastmcp import FastMCP

TAXI_ML_PATH = Path(__file__).parents[0] / "models"

fast_app = FastAPI()

@fast_app.get("/")
async def root():
    return {"Hello": "World"}


@fast_app.get("/debug/view-code")
def view_own_code():
    try:
        with open(__file__, "r") as f:
            content = f.read()
        return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}


@fast_app.get("/taxi/")
async def read_taxi_data():
    return {"Hello": "Taxis"}


@fast_app.post("/predict", operation_id="predict_taxi_price")
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


mcp = FastMCP.from_fastapi(app=fast_app, name="Taxi Price Predictor")

mcp_app = mcp.http_app(path='/mcp')

fast_app.mount("/mcp", mcp_app)

app = FastAPI(
    title="Taxi API with MCP",
    lifespan=mcp_app.lifespan,
    routes=[
        *fast_app.routes,
        *mcp_app.routes,
    ],
)