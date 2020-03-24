import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# streamlit run /workspace/SSA/app.py

DATE_TIME = "date"
DATA_URL = "https://github.com/stanbiryukov/SSA/raw/master/data/SSA_hail_19792020.csv"

st.title("Hail Reports in AUS")
st.markdown(
    """
Visualize hail reports from Australia's Severe Storms Archive: 
http://www.bom.gov.au/australia/stormarchive/
"""
)
# http://www.bom.gov.au/australia/stormarchive/storm.php?attributes%5B%5D=0&attributes%5B%5D=1&attributes%5B%5D=2&attributes%5B%5D=3&attributes%5B%5D=4&attributes%5B%5D=12&search_area=N&s_day=1&s_month=Jan&s_year=1979&e_day=23&e_month=Mar&e_year=2020&output_type=web&action=form&submit=Generate+report&stormType=hail


@st.cache(persist=True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data = data[["Date/Time", "Latitude", "Longitude", "Hail size"]]
    data["date"] = pd.to_datetime(data["Date/Time"])  # .dt.date
    # drop any dups/max for the day
    data = data.groupby(["date", "Latitude", "Longitude"], as_index=False)[
        "Hail size"
    ].max()
    data = data.rename(
        columns={"Latitude": "lat", "Longitude": "lon", "Hail size": "hail_size"}
    )
    data["year"] = pd.to_datetime(data["date"]).dt.year
    # data['mx_mu'] = data.groupby(['lon', 'lat', 'year'])['hail_size'].agg('mean')
    data = data[["date", "year", "lat", "lon", "hail_size"]].dropna()
    return data


data = load_data()

boxw = data.copy()
boxw = boxw.rename(columns = {'hail_size': 'Hail Size'})

line_data = data.copy()
line_data = line_data.groupby(line_data['year'], as_index=False)['hail_size'].agg({'NReports': 'count'})

st.subheader("Number of hail reports by year")

st.altair_chart(
    alt.Chart(line_data)
    .mark_line()
    .encode(
        x=alt.X("year:O", title="Year", scale=alt.Scale(nice=True)),
        y=alt.Y("NReports:Q", title="Number of reports"),
        tooltip=["year", "NReports"],
    ),
    use_container_width=True,
)

year = st.slider("Year to look at", min_value=1979, max_value=2019, value=2019, step=1)

data = data[data[DATE_TIME].dt.year == year]

st.subheader("Geocoded data between {} and {}".format(year, (year + 1)))

midpoint = (np.nanmean(data["lat"]), np.nanmean(data["lon"]))

st.deck_gl_chart(
    viewport={"latitude": -25.274012, "longitude": 133.776910, "zoom": 3},
    layers=[
        {
            "type": "ScatterplotLayer",
            "data": data,
            "radiusScale": 200,
            "radiusMinPixels": 5,
            "getFillColor": [248, 24, 148],
        }
    ],
)

hist = np.histogram(data["hail_size"], bins=20, range=(0, 20))[0]
chart_data = pd.DataFrame({"Hail Size": range(20), "Reports": hist})

st.subheader("Reported hail size distribution between {} and {}".format(year, (year + 1)))

st.altair_chart(
    alt.Chart(chart_data)
    .mark_area(interpolate="step-after")
    .encode(
        x=alt.X("Hail Size:Q", title="Hail Size [cm]", scale=alt.Scale(nice=True)),
        y=alt.Y("Reports:Q", title="Number of reports [N]"),
        tooltip=["Hail Size", "Reports"],
    ),
    use_container_width=True,
)

if st.checkbox("Show raw data", False):
    st.subheader("Raw data between {} and {}".format(year, (year + 1)))
    st.write(data)


st.subheader("Reported hail size box plots by year") 

st.altair_chart(
    alt.Chart(boxw)
    .mark_boxplot()
    .encode(
        x=alt.X("Hail Size:Q", title="Hail Size [cm]"),
        y=alt.Y("year:O", title="Year"),
        tooltip=["year", "Hail Size"],
    ),
    use_container_width=True,
)
