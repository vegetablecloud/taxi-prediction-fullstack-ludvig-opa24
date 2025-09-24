from importlib.resources import files

TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

TAXI_MODEL_PATH = files("taxipred").joinpath("models/broad_responsible_xgb_model.joblib")

# DATA_PATH = Path(__file__).parents[1] / "data"

if __name__ == "__main__":
    print(TAXI_MODEL_PATH)