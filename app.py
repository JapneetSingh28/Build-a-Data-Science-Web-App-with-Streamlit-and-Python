import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# loading dataset, already downloaded from internet
DATA_URL = (
    r"C:\Users\japne\Downloads\Courses\Build a Data Science Web App with Streamlit and Python\my ver\Motor_Vehicle_Collisions_-_Crashes.csv"
)

# Web app python code goes from Where
st.title("Motor Vehicle Collisions in New York City.")
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze motor vehicle collisions in NYC 🗽💥🚗")

'''
using @st.cache(persist=True) function so that the data is stored in
cache memory in order to increase user experience , as it boosts the
speed of queries
'''
@st.cache(persist=True)

# def load_data(nrows) : this function selects specific rows from dataset
# here nrows are the number of rows that we requires from the dataset
def load_data(nrows):
    # loading nrows into dataframe "data" from DATA_URL, and explicitly adding timeseries columns from DATA_URL
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])

    # droping the NaN entries from dataset columns LATITUDE and LONGITUDE
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

    # lowercasing the columns names of dataset
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)

    # renaming the complex named columns
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)

    # returning the clean dataframe
    return data

# loading 1 hundred thousand rows into data
data = load_data(100000)

st.header("Where are the most people injured in NYC?")

# making slider for selecting the Number of persons injured in vehicle collisions
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)

# visualizing the selected injured people on the map of New York City
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")

# making slider for selecting the Hour to look at the Number of persons injured in vehicle collisions
hour = st.slider("Hour to look at", 0, 23)
original_data = data

# quering selected "hour" on dataset bosed on timeseries
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# making the mid point of the map so that it initially load on that latitude and longitude
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

# visualizing the 3D map
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
        },
        # providing 3D layer on the map to make it interactive
        layers=[
            pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
            ),
        ],
    )
)

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# filertering the dataset on hour
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

# spliting the hour into minutes timeseries , binning it into 60 and selecting number of crashes
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]

# making clean and concise "chart_data" variable suitable for histogram
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

# visualizing the histogram
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)


st.header("Top 5 dangerous streets by affected class")

# making dropdown for selecting 'Pedestrians', 'Cyclists' and ;'Motorists'
select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    # displaying the top 5 dangerous streets for the Pedestrians, the table is sorted in descending order and dropping the NaN data from dataset
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    # displaying the top 5 dangerous streets for the Cyclists, the table is sorted in descending order and dropping the NaN data from dataset
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    # displaying the top 5 dangerous streets for the Motorists, the table is sorted in descending order and dropping the NaN data from dataset
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])

# making a checkbox for displaying the Raw Data of our dataset
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
