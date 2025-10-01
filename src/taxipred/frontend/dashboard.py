import streamlit as st
import datetime
import base64
from pathlib import Path
from taxipred.utils.helpers import post_api_endpoint

# Helper function to select an icon based on the weather description
def get_weather_icon(weather_text: str) -> str:
    """Returns a weather emoji based on keywords in the weather description."""
    weather = weather_text.lower()
    if "rain" in weather:
        return "🌧️"
    if "snow" in weather:
        return "❄️"
    if "sun" in weather or "clear" in weather:
        return "☀️"
    if "cloud" in weather or "overcast" in weather:
        return "☁️"
    return "❓" # Default icon

# --- App Layout ---
st.set_page_config(page_title="Taxi Fare Predictor", page_icon="🚕", layout="centered")
bg_image = Path(__file__).resolve().parent / "images" / "background.jpg"
encoded_bg = base64.b64encode(bg_image.read_bytes()).decode()
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('data:image/jpeg;base64,{encoded_bg}');
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("<h1 style='text-align: center;'>🚕 Taxi Fare Predictor</h1>", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        pickup = st.text_input("📍 Pickup location", value="NBI handelsakdemin Västra Frölunda")
    with col2:
        destination = st.text_input("🏁 Destination", value="Nordstan Göteborg")

    col3, col4, col5 = st.columns([1, 2, 2])
    with col3:
        nr_passengers = st.number_input("👥", 1, 4, 1, help="Number of passengers")
    with col4:
        date = st.date_input("📅 Date", datetime.date.today())
    with col5:
        time = st.time_input("🕒 Time", datetime.datetime.now().time())

    # Prediction logic
    if st.button("Predict Fare"):
        with st.spinner('Calculating fare...'):
            datetime_str = f"{date} {time.strftime('%H:%M:%S')}"
            user_input = {
                "pickup": pickup, "destination": destination,
                "nr_passengers": nr_passengers, "date": datetime_str
            }
            response = post_api_endpoint("/predict", json=user_input)

            if response.status_code == 200:
                api_data = response.json()
                predicted_price = api_data.get("predicted_price", 0)
                trip_info = api_data.get("trip_info", {})
                weather = api_data.get("weather", "")

                # Display the main prediction with custom markdown for better styling
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="font-size: 1.1rem; color: grey;">Predicted Fare</p>
                    <p style="font-size: 2.2rem; font-weight: bold;">${predicted_price:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()

                # Display trip details in columns
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric("Distance", trip_info.get('distance', {}).get('text', 'N/A'))
                res_col2.metric("Duration", trip_info.get('duration', {}).get('text', 'N/A'))
                res_col3.metric("Weather", get_weather_icon(weather), help=weather.capitalize())
            else:
                st.error(f"Error fetching prediction: {response.text}")
