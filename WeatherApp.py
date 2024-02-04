import streamlit as st
import requests
import pandas as pd
import numpy as np
import altair as alt
from geopy.geocoders import Nominatim

# API KEY
API_KEY = 'c6da42e5d91470c76cf54a258d352e30'

# Weather data from API
def get_weather_data(location):
    params = {'access_key': API_KEY, 'query': location}
    response = requests.get('http://api.weatherstack.com/current', params=params)
    return response.json()

# Celsius to Fahrenheit converter
def celsius_to_fahrenheit(celsius_temp):
    return (celsius_temp * 9/5) + 32

# LAT/LON from City
def get_lat_lon(city):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city)
    return location.latitude, location.longitude


st.set_page_config(
    page_title="Local Florida Weather App",
    page_icon=":sunny:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Background picture
background_image = 'https://cdn.lifefamilyfun.com/wp-content/uploads/Florida-Weather-in-March.jpg'
st.image(background_image, use_column_width=True)

# App Title
st.title("Local Florida Weather App")

# City name from user
user_location = st.text_input("Enter your city's name:", "Miami")

# Wind speed
show_wind_speed = st.checkbox("Show Wind Speed")

# Multi widget for city temperature comparison
cities_to_compare = st.multiselect("Select cities to compare temperatures:",
                                   ['Orlando', 'Tampa', 'Jacksonville', 'Key West', 'Tallahassee'],
                                   default=['Orlando', 'Tampa', 'Jacksonville'])
# Date and time widgets
selected_date = st.date_input("Select a date:")
selected_time = st.time_input("Select a time:")

# Weather selectbox
selected_attribute = st.selectbox("Select a weather attribute:",
                                  ['Temperature (Celsius)', 'Temperature (Fahrenheit)', 'Humidity', 'Wind Speed (km/h)'])

# Color picker widget
default_color = '#FF5733'  # Default: Coral color
selected_color = st.color_picker("Select a color:", default_color)

# Weather data button
fetch_button = st.button("Fetch Weather Data")

# Check to see if the button is clicked
if fetch_button:
    # Fetch weather data for the user location
    weather_data = get_weather_data(user_location)

    # Check to see if weather data is available
    if 'current' in weather_data:
        current_weather = weather_data['current']
        temperature_celsius = current_weather['temperature']
        temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)
        weather_description = current_weather['weather_descriptions'][0]
        humidity = current_weather['humidity']
        wind_speed = current_weather['wind_speed']
        lat, lon = get_lat_lon(user_location)

        # Create a DataFrame with weather data for the user location
        data = {
            'Location': [user_location],
            'Temperature (Celsius)': [temperature_celsius],
            'Temperature (Fahrenheit)': [temperature_fahrenheit],
            'Weather Description': [weather_description],
            'Humidity': [humidity],
            'Wind Speed (km/h)': [wind_speed],
            'LAT': [lat],
            'LON': [lon]
        }

        # Add weather data for the selected cities to compare temperatures
        for city in cities_to_compare:
            lat, lon = get_lat_lon(city)
            weather_data = get_weather_data(city)
            temperature_celsius = weather_data['current']['temperature']
            temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)
            humidity = weather_data['current']['humidity']
            wind_speed = weather_data['current']['wind_speed']
            data['Location'].append(city)
            data['Temperature (Celsius)'].append(temperature_celsius)
            data['Temperature (Fahrenheit)'].append(temperature_fahrenheit)
            data['Weather Description'].append(weather_data['current']['weather_descriptions'][0])
            data['Humidity'].append(humidity)
            data['Wind Speed (km/h)'].append(wind_speed)
            data['LAT'].append(lat)
            data['LON'].append(lon)

        weather_df = pd.DataFrame(data)

        # Display weather information
        st.write(f"Current weather in {user_location}:")
        st.write(f"Temperature: {temperature_fahrenheit:.2f}°F")
        st.write(f"Description: {weather_description}")

        if show_wind_speed:
            st.write(f"Wind speed: {wind_speed} km/h")

        # Show weather data
        st.write("Weather Data:")
        st.dataframe(weather_df)

        # City humidity expander
        with st.expander("Humidity Levels"):
            humidity_chart = alt.Chart(weather_df).mark_bar().encode(
                x='Location',
                y='Humidity',
                tooltip=['Location', 'Humidity']
            ).properties(width=600, height=400)
            st.altair_chart(humidity_chart)

        # Temperature trend expander
        with st.expander("Temperature Trend"):
            temperature_chart = alt.Chart(weather_df).mark_line().encode(
                x='Location',
                y=selected_attribute,
                color=alt.value(selected_color),
                tooltip=['Location', selected_attribute]
            ).properties(width=600, height=400)
            st.altair_chart(temperature_chart)

        # Map
        st.write("Weather Map:")
        st.map(weather_df)

        # Calculate average temperature
        temperature_celsius_values = weather_df['Temperature (Celsius)'].values
        mean_temp_celsius = np.mean(temperature_celsius_values)

        st.write(f"Average Temperature: {temperature_fahrenheit:.2f}°F ({mean_temp_celsius:.2f}°C)")

    else:
        st.write("Error. Please input a different location.")
