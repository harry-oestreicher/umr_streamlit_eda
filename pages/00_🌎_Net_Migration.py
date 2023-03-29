import datetime
import os
import time
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb

# load the world dataset
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))



# Begin Streamlit
# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")

# Show title and description of the app.
st.title("Unaccompanied Minor Research")
st.sidebar.write("""
**Sidebar**

`This` is an example **Streamlit** app to show how to expand and collapse the sidebar programmatically.

To run this example:

```bash
$ streamlit run Home.py
```

""")


link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/umr/"

data_links = {
    "reference": {
        "countries": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
        "countries_hires": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
    },
    "indicator": {
        "DM_": link_prefix + "umr_data_DM_.csv",
        "ECON_": link_prefix + "umr_data_ECON_.csv",
        "HVA_": link_prefix + "umr_data_HVA_.csv",
        "MG_": link_prefix + "umr_data_MG_.csv",
        "MNCH_": link_prefix + "umr_data_MNCH_.csv",
        "PT_": link_prefix + "umr_data_PT_.csv",
        "PV_": link_prefix + "umr_data_PV_.csv",
        "WS_": link_prefix + "umr_data_WS_.csv",
    },
}

def get_data_columns(df, category="world", frequency="annual"):
    cols = df.columns.values.tolist()
    return cols[1:]

@st.cache_data
def get_reference_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0", "AGE"], inplace=True)
    df = df[df.TIME_PERIOD>2011]
    # url = url.lower()
    return df

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    # url = url.lower()
    return df


@st.cache_data
def get_geom_data(category):
    prefix = (
        "https://raw.githubusercontent.com/harry-oestreicher/gis-data/main/"
    )
    links = {
        "continents": prefix + "world/continents.geojson",
        "countries": prefix + "world/countries.json",
        "countries_hires": prefix + "world/countries_hires.geojson",
        "world_cities_5000": prefix + "world/cities5000.csv",
        "world_cities": prefix + "world/world_cities.geojson",
        "us": prefix + "us/us_nation.geojson",
        "state": prefix + "us/us_states.geojson",
        "county": prefix + "us/us_counties.geojson",
        "metro": prefix + "us/us_metro_areas.geojson",
    }

    gdf = gpd.read_file(links[category])

    return gdf


def join_attributes(gdf, df, category):
    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="GEOID", right_on="county_fips", how="outer")
    elif category == "state":
        new_gdf = gdf.merge(df, left_on="STUSPS", right_on="STUSPS", how="outer")
    elif category == "us":
        if "geo_country" in df.columns.values.tolist():
            df["country"] = None
            df.loc[0, "country"] = "United States"
        new_gdf = gdf.merge(df, left_on="NAME", right_on="country", how="outer")
    elif category == "countries":
        new_gdf = gdf.merge(df, left_on="id", right_on="REF_AREA", how="outer")
    elif category == "countries_hires":
        new_gdf = gdf.merge(df, left_on="ISO_A3", right_on="REF_AREA", how="outer")
        new_gdf.rename(columns={'ISO_A3': 'id'}, inplace=True)
    
    new_gdf = new_gdf[~new_gdf["id"].isna()]
    new_gdf = new_gdf.drop(columns=["REF_AREA", "INDICATOR"])
    return new_gdf


def join_indicator(gdf, df, indicator):
    new_gdf = None
    if indicator == "DM_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "ECON_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "HVA_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "MG_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "MNCH_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "PT_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "PV_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "WS_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
        # new_gdf.rename(columns={'OBS_VALUE': f"{this_indicator}"}, inplace=True)
        new_gdf = new_gdf[~new_gdf["id"].isna()]
        new_gdf = new_gdf.drop(columns=["REF_AREA", "INDICATOR"])

    new_gdf = new_gdf[~new_gdf["geometry"].isna()]

    return new_gdf


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf


def select_null(gdf, col_name):
    new_gdf = gdf[gdf[col_name].isna()]
    return new_gdf


def get_indicator_dict(name):
    in_csv = os.path.join(os.getcwd(), "src/data/umr/umr_data_dict_INDICATOR.csv")
    df = pd.read_csv(in_csv)
    value = df[df.key==name]["value"].values[0]
    return value


def get_indicators(df):
    indicator_list = df["INDICATOR"].unique()
    return indicator_list

def app():
    # st.title("Unaccompanied Minor Research")
    st.write(
        """
        ## Net Migration Rate (per 1000 population)

        ### Exploratory Data Analysis

        Several open-source packages are used to process the data and generate the visualizations, e.g., [streamlit](https://streamlit.io),
          [geopandas](https://geopandas.org), [leafmap](https://leafmap.org), and [pydeck](https://deckgl.readthedocs.io).
          
        """
    )

    row1_col1, row1_col2, row1_col3  = st.columns(
        [0.5, 0.5, 2]
    )

    years_list = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

    with row1_col1:
        selected_year = st.selectbox("Year", years_list )

    with row1_col2:
        indicator = st.selectbox("Indicator Group", ["DM_", "ECON_", "HVA_", "MG_", "MNCH_", "PT_", "PV_", "WS_"])

    # manually setting these for now
    frequency = "annual"
    scale = "countries"
    gdf = get_geom_data(scale.lower())

    # Get Net Migration Data
    inventory_df = get_reference_data(data_links["reference"][scale.lower()])

    # Filter by selected year
    inventory_df = inventory_df[inventory_df.TIME_PERIOD==selected_year]

    # Calculate columns
    data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())

    indicator_df = get_indicator_data(data_links["indicator"][indicator])
    indicator_df = indicator_df[indicator_df.TIME_PERIOD==selected_year]

    with row1_col3:
        selected_col = "OBS_VALUE" #st.selectbox("Attribute", data_cols, 4)
        # st.write(indicator_df.head(3))
        this_ind_list = indicator_df["INDICATOR"].unique().tolist()
        this_indicator = st.selectbox("Indicator:", this_ind_list)
        this_indicator_text = get_indicator_dict(this_indicator)
        # Display the indicator full text
        st.write(this_indicator_text)


    show_tables = "no"
    show_tables = st.checkbox("Show Dataframes")

    row1a_col1, row1a_col2 = st.columns([4, 4])

    if show_tables:
        with row1a_col1:
            st.write("#### DM_NET_MG_RATE Layer")
            st.write(inventory_df)

        with row1a_col2:
            indicator_data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())
            indicator_df = indicator_df[indicator_df.INDICATOR==this_indicator]
            st.write(f"#### {this_indicator} Layer")
            st.write(indicator_df)


    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5, row2_col6 = st.columns(
        [0.6, 0.68, 0.7, 0.7, 1.5, 0.8]
    )

    palettes = cm.list_colormaps()

    with row2_col1:
        palette1 = st.selectbox("Net Migration Color palette", palettes, index=palettes.index("Blues"))
        palette2 = st.selectbox(f"{this_indicator} Color palette", palettes, index=palettes.index("Greens"))

    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
    with row2_col3:
        # show_nodata = st.checkbox("Show nodata areas", value=True)
        show_indicator = st.checkbox("Show indicator areas", value=False)

    with row2_col4:
        show_3d = st.checkbox("Show 3D view", value=False)
    with row2_col5:
        if show_3d:
            elev_scale = st.slider(
                "Elevation scale", min_value=1, max_value=1000, value=1, step=10
            )
            with row2_col6:
                st.info("Press Ctrl and move the left mouse button.")
        else:
            elev_scale = 1


    # ###################### The `JOINS` ###############################################

    gdf = join_attributes(gdf, inventory_df, scale.lower())
    gdf_null = select_null(gdf, selected_col)
    gdf = select_non_null(gdf, selected_col)
    gdf = gdf.sort_values(by=selected_col, ascending=True)

    gdf2 = get_geom_data(scale.lower())
    gdf2 = join_indicator(gdf2, indicator_df, indicator)
    # # # Create centroids projection on flat projection, then back
    # gdf2["country_centroids"] = gdf2.to_crs("+proj=cea").centroid.to_crs(gdf2.crs)
    # gdf2.drop(columns=["geometry"], inplace=True)
    # gdf2["long"] = gdf2.country_centroids.map(lambda p: p.x)
    # gdf2["lat"] = gdf2.country_centroids.map(lambda p: p.y)
    # gdf2.drop(columns=["country_centroids"], inplace=True)

    gdf2_null = select_null(gdf2, selected_col)
    gdf2 = select_non_null(gdf2, selected_col)
    gdf2 = gdf2.sort_values(by=selected_col, ascending=True)

    # st.write(gdf2)




    # ###################### Colors
 
    geo_colors_1 = cm.get_palette(palette1, n_colors)
    geo_colors_2 = cm.get_palette(palette2, n_colors)


    def gen_colors(gdf, colors):
        colors = [hex_to_rgb(c) for c in colors]

        for i, ind in enumerate(gdf.index):
            index = int(i / (len(gdf) / len(colors)))
            if index >= len(colors):
                index = len(colors) - 1
            gdf.loc[ind, "R"] = colors[index][0]
            gdf.loc[ind, "G"] = colors[index][1]
            gdf.loc[ind, "B"] = colors[index][2]
            pass

        min_value = gdf[selected_col].min()
        max_value = gdf[selected_col].max()

        return gdf, min_value, max_value, colors

    geo_layer_1, min1, max1, colors1 = gen_colors(gdf, geo_colors_1)
    geo_layer_2, min2, max2, colors2 = gen_colors(gdf2, geo_colors_2)

    # min_ind_value = gdf2[selected_col].min()
    # max_ind_value = gdf2[selected_col].max()

    color = "color"
    # color_exp = f"[({selected_col}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
    color_exp = f"[R, G, B]"

    initial_view_state = pdk.ViewState(
        latitude=40,
        longitude=-0,
        zoom=2,
        max_zoom=16,
        pitch=0,
        bearing=0,
        height=900,
        width=None,
    )

    # ###################  Make Leaflet layers
    geojson = pdk.Layer(
        "GeoJsonLayer",
        geo_layer_1,
        pickable=True,
        opacity=0.6,
        stroked=True,
        filled=True,
        extruded=show_3d,
        wireframe=True,
        get_elevation=f"{selected_col}",
        elevation_scale=elev_scale,
        # get_fill_color="color",
        get_fill_color=color_exp,
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    geojson_null = pdk.Layer(
        "GeoJsonLayer",
        gdf_null,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        # get_elevation="properties.ALAND/100000",
        # get_fill_color="color",
        get_fill_color=[200, 200, 200],
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    geojson_indicator = pdk.Layer(
        "GeoJsonLayer",
        geo_layer_2,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        extruded=show_3d,
        wireframe=True,
        get_elevation=f"{selected_col}",
        elevation_scale=elev_scale/2,
        # get_fill_color="color",
        get_fill_color=color_exp,
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )
    
    # geojson_indicator = pdk.Layer(
    #     'HexagonLayer',  # `type` positional argument is here
    #     geo_layer_2,
    #     get_position=['long', 'lat'],
    #     auto_highlight=True,
    #     elevation_scale=50,
    #     pickable=True,
    #     elevation_range=[0, 3000],
    #     extruded=True,
    #     coverage=1)





    # tooltip = {"text": "Name: {NAME}"}
    # tooltip_value = f"<b>Value:</b> {median_listing_price}""

    tooltip1 = {
        "html": "<b>Name:</b> {id}<br><b>Value:</b> {"
        + selected_col
        + "}<br><b>Year:</b> "
        + str(selected_year)
        + "",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    layers = [geojson]
    # if show_nodata:
    #     layers.append(geojson_null)
    
    if show_indicator:
        layers.append(geojson_indicator)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style="light",
        tooltip=tooltip1,
    )

    row3_col1, row3_col2 = st.columns([6, 1])


    with row3_col1:
        st.pydeck_chart(r)
        st.write(
            cm.create_colormap(
                palette1,
                label="Net Migration Rate per 1k population", #selected_col.replace("_", " ").title(),
                height=0.1,
                vmin=min1,
                vmax=max1,
                font_size=5,
            )
        )

    with row3_col2:
        st.write(
            cm.create_colormap(
                palette2,
                label=f"{this_indicator_text}", #selected_col.replace("_", " ").title(),
                width=0.05,
                height=2.5,
                orientation="vertical",
                vmin=min1,
                vmax=max1,
                font_size=5,
            )
        )

    return None


app()
