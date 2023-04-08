import datetime
import os
import sys
import time
import math
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from pydeck.types import String

sys.path.append("..")
from data.dictionary import get_dictionary
INDICATOR_dict = get_dictionary('INDICATOR')

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
st.title("Net Migration Rate 2021")
st.sidebar.write("""
**Sidebar**

`pydeck` is used to manage layers and enumeration in some cases.

Use the filter dropdowns to alter your results.

Use the checkbox to preview data before map rendering.

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
    df = df[df.TIME_PERIOD==2021]
    return df

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    df = df[df.TIME_PERIOD==2021]
    df.replace({"INDICATOR": INDICATOR_dict}, inplace=True)

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

    # new_gdf['INDICATOR'] = 'Net Migration Rate'

    new_gdf = new_gdf[~new_gdf["id"].isna()]
    new_gdf = new_gdf.drop(columns=["REF_AREA"])
    return new_gdf


def join_indicator(gdf, df, indicator):
    new_gdf = None
    if indicator == "DM_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "ECON_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "MG_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
        # new_gdf["OBS_VALUE"] = new_gdf["OBS_VALUE"].values+100
        new_gdf["OBS_VALUE"] = new_gdf["OBS_VALUE"].astype(float)

    elif indicator == "MNCH_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "PT_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    # elif indicator == "PV_":
    #     new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
    elif indicator == "WS_":
        new_gdf = gdf.merge(df, left_on=["id"], right_on=["REF_AREA"], how="outer")
        # new_gdf.rename(columns={'OBS_VALUE': f"{this_indicator}"}, inplace=True)
        new_gdf = new_gdf[~new_gdf["id"].isna()]
        # new_gdf = new_gdf.drop(columns=["REF_AREA", "INDICATOR"])

    new_gdf = new_gdf[~new_gdf["geometry"].isna()]
    
    # # # Create centroids projection on flat projection, then back
    # gdf2["country_centroids"] = gdf2.to_crs("+proj=cea").centroid.to_crs(gdf2.crs)
    # gdf2.drop(columns=["geometry"], inplace=True)
    # gdf2["long"] = gdf2.country_centroids.map(lambda p: p.x)
    # gdf2["lat"] = gdf2.country_centroids.map(lambda p: p.y)
    
    return new_gdf


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf


def select_null(gdf, col_name):
    new_gdf = gdf[gdf[col_name].isna()]
    return new_gdf


def get_indicator_dict(name):
    in_csv = os.path.join(os.getcwd(), "data/umr_data_dict_INDICATOR.csv")
    df = pd.read_csv(in_csv)
    value = df[df.key==name]["value"].values[0]
    return value


def enumerate_column(col_in):
    if col_in == "REF_AREA":
        REF_AREA = REF_AREA_dict
        val = REF_AREA.get(col_in)

    elif col_in == "INDICATOR":
        INDICATOR = INDICATOR_dict
        val = INDICATOR.get(col_in)
    return val

def get_indicators(df):
    indicator_list = df["INDICATOR"].unique()
    return indicator_list

def app():
    # st.title("Unaccompanied Minor Research")
    st.write(
        """
        ### Exploratory Data Analysis

        Several open-source packages are used to process the data and generate the visualizations, e.g., [streamlit](https://streamlit.io),
          [geopandas](https://geopandas.org), [leafmap](https://leafmap.org), and [pydeck](https://deckgl.readthedocs.io).
          
        """
    )

    row1_col1, row1_col2, row1_col3  = st.columns(
        [1,1,6]
    )

    # Associate these group labels with thier file prefixes:
    indicator_group_dict = {
            "Demographic": "DM_",
            "Economic": "ECON_",
            "Migratory": "MG_",
            "Maternal, Newborn, and Child Health": "MNCH_",
            "Post-Trauma": "PT_",
            "Water Services": "WS_"
    }

    org_dict = {
        "UNSDG": "United Nations Sustainable Development Group",
        "UNFPA": "United Nations Population Fund Agency",
        "UNICEF": "United Nations International Children's Emergency Fund"
    }

    world_region_dict = {
        "UNFPA_AP": "Asia Pacific",
        "UNFPA_EECA": "Eastern Europe and Central Asia",
        "UNFPA_ESA": "Eastern and Southern Africa",
        "UNFPA_LAC": "Latin America and Carribean",
        "UNFPA_WCA": "Western and Central Africa",
        "UNICEF_ECARO": "Europe and Central Asia Region",
        "UNICEF_EECA": "Eastern Europe and Central Asia",
        "UNSDG_CARIBBEAN": "NAME",
        "UNSDG_CENTRALAMR": "NAME",
        "UNSDG_CENTRALASIASOUTHERNASIA": "NAME",
        "UNSDG_EASTERNAFR": "NAME",
        "UNSDG_LDC": "NAME",
        "UNSDG_LLDC": "NAME",
        "UNSDG_MIDDLEAFR": "NAME",
        "UNSDG_SIDS": "NAME",
        "UNSDG_SOUTHASIA": "NAME",
        "UNSDG_SOUTHEASTERNASIA": "NAME",
        "UNSDG_SOUTHERNAFR": "NAME",
        "UNSDG_SUBSAHARANAFRICA": "NAME",
        "UNSDG_WESTERNAFR": "NAME"

    }

    # Reserved globals for later development
    frequency = "annual"
    scale = "countries"


    #########################################################  Begin filter
    with row1_col1:
        st.write("**Year: 2021**")
        selected_year = 2021 #st.selectbox("Year", years_list )

    with row1_col2:
        # indicator_group = st.selectbox("**Risk Factor Group**", ["DM_", "ECON_", "MG_", "MNCH_", "PT_", "WS_"])
        indicator_group_selected = st.selectbox("**Indictator Group**", ["Demographic", "Economic", "Migratory", "Maternal, Newborn, and Child Health", "Post-Trauma", "Water Services"])
        indicator_group = indicator_group_dict[indicator_group_selected]
        
    # Get geometry data
    gdf = get_geom_data(scale.lower())

    # Get Net Migration Data
    inventory_df = get_reference_data(data_links["reference"][scale.lower()])

    # Filter by selected year
    inventory_df = inventory_df[inventory_df.TIME_PERIOD==selected_year]

    # Calculate columns
    data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())

    # Get Indicator Group data
    indicator_df = get_indicator_data(data_links["indicator"][indicator_group])

    #########################################
    indicator_df = indicator_df[indicator_df.INDICATOR!="Net migration rate (per 1,000 population)"]
    indicator_df = indicator_df[indicator_df.TIME_PERIOD==selected_year]

    with row1_col3:
        selected_col = "OBS_VALUE" #st.selectbox("Attribute", data_cols, 4)
        # st.write(indicator_df.head(3))

        this_ind_list = indicator_df["INDICATOR"].unique().tolist()
        this_indicator = st.selectbox(f"**{indicator_group_selected} Indicators**", this_ind_list)
        # this_indicator_text = get_indicator_dict(this_indicator)

        # Display the indicator full text
        # st.write(this_indicator_text)



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


    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(
        [1, 1, 1, 5]
    )

    palettes = cm.list_colormaps()

    with row2_col1:
        palette1 = st.selectbox("**Net Migration Rate:**", palettes, index=palettes.index("Blues"))
        palette2 = "Greens" #st.selectbox(f"{this_indicator} Color palette", palettes, index=palettes.index("Greens"))

    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
        show_3d = st.checkbox("Show 3D view", value=False)
        if show_3d:
            elev_scale = st.slider(
                "Elevation scale", min_value=1, max_value=100000, value=1, step=10
            )
            st.info("Press Ctrl and move the left mouse button.")
        else:
            elev_scale = 1
        

    with row2_col3:
        # show_nodata = st.checkbox("Show nodata areas", value=True)
        st.write("**Risk Factor:**")
        show_indicator = st.checkbox("Show Points", value=False)
        ind_scale = st.slider("Scale:", min_value=1, max_value=1000, value=1)

    with row2_col4:
        show_chloro = st.checkbox("Show **Net Migration** Chloropleth", value=True)
        show_nodata = st.checkbox("Show nodata", value=False)
        show_labels = st.checkbox("Show Heatmap", value=False)
        # heat_scale = st.slider("Heat scale:", min_value=1, max_value=20, value=4)

    # with row2_col5:
    #     st.write(".")



    # ###################### The `JOINS` ###############################################

    gdf = join_attributes(gdf, inventory_df, scale.lower())
    gdf_null = select_null(gdf, selected_col)
    gdf = select_non_null(gdf, selected_col)
    gdf.replace({"INDICATOR": INDICATOR_dict}, inplace=True)

    gdf = gdf.sort_values(by=selected_col, ascending=True)

    gdf2 = get_geom_data(scale.lower())
    gdf2 = join_indicator(gdf2, indicator_df, indicator_group)

    # # Create centroids projection on flat projection, then back
    gdf2["centroids"] = gdf2.to_crs("+proj=cea").centroid.to_crs(gdf2.crs)
    gdf2.drop(columns=["geometry"], inplace=True)
    gdf2["long"] = round(gdf2.centroids.map(lambda p: p.x),5)
    gdf2["lat"] = round(gdf2.centroids.map(lambda p: p.y),5)
    # gdf2["geometry"] = "["+ gdf2['long'].astype(str) +","+ gdf2["lat"].astype(str) +"]"
    gdf2 = gdf2.set_geometry("centroids")

    gdf2.drop(columns=["REF_AREA"], inplace=True)
    gdf2 = gdf2[["id", "name", "centroids", "TIME_PERIOD", "INDICATOR", "OBS_VALUE", "long", "lat"]]



    gdf2_null = select_null(gdf2, selected_col)
    gdf2 = select_non_null(gdf2, selected_col)
    gdf2 = gdf2.sort_values(by=selected_col, ascending=True)
    gdf2 = gdf2[gdf2.INDICATOR==this_indicator]
    # gdf2["INDICATOR"] = get_indicator_dict(gdf2["INDICATOR"])
    gdf2.replace({"INDICATOR": INDICATOR_dict}, inplace=True)
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

    # st.write(geo_layer_2.head())

    color = "color"
    # color_exp = f"[({selected_col}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
    color_exp = f"[R, G, B]"

    initial_view_state = pdk.ViewState(
        latitude=10,
        longitude=0,
        zoom=2,
        max_zoom=9,
        pitch=0,
        bearing=0,
        height=900,
        width=None,
    )

    ####################  pydeck layers

    geojson = pdk.Layer(
        "GeoJsonLayer",
        geo_layer_1,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        extruded=show_3d,
        wireframe=True,
        get_elevation=f"{selected_col}",
        elevation_scale=elev_scale,
        # get_fill_color="color",
        get_fill_color=color_exp,
        get_line_color=[255,255,255],
        get_line_width=10,
        line_width_min_pixels=2,
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
        get_fill_color=[0, 0, 0],
        get_line_color=[0, 0, 0],
        get_line_width=10,
        line_width_min_pixels=2,
    )

    # Use pandas to calculate additional data
    # st.write(geo_layer_1)

    # geo_layer_2["OBS_VALUE"] = round(geo_layer_2["OBS_VALUE"]*1000)

    # st.write(f"{round(min2*1000)} : {round(max2*1000)}")
    geo_layer_2["obs_radius"] = geo_layer_2["OBS_VALUE"].map(lambda obs_count: math.sqrt(obs_count)*ind_scale)
    # st.write(geo_layer_2.head())

    # Define a layer to display on a map
    geojson_indicator = pdk.Layer(
        "ScatterplotLayer",
        geo_layer_2,
        pickable=True,
        opacity=0.05,
        stroked=True,
        filled=True,
        radius_scale=100,
        radius_min_pixels=5,
        radius_max_pixels=500,
        line_width_min_pixels=1,
        get_position="[long, lat]",
        get_radius="obs_radius",
        get_fill_color=[255, 240, 0],
        get_line_color=[0, 0, 0],
    )


    labels_layer = pdk.Layer(
        "HeatmapLayer",
        geo_layer_2,
        opacity=0.9,
        get_position=["long", "lat"],
        aggregation=String('MEAN'),
        # get_weight=f"OBS_VALUE > 0 ? OBS_VALUE - {min2} : 0")
        get_weight="OBS_VALUE > 0 ? OBS_VALUE : 0",
        # radius= 1000
        )



    # DATA_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"


    # labels_layer = pdk.Layer(
    #     "LabeledGeoJsonLayer",
    #     data=geo_layer_2,
    #     filled=False,
    #     billboard=False,
    #     get_line_color=[180, 180, 180],
    #     get_label="properties.name",
    #     get_label_size=200000,
    #     get_label_color=[0, 255, 255],
    #     label_size_units=pdk.types.String("meters"),
    #     line_width_min_pixels=1,
    # )

    # view_state = pydeck.ViewState(latitude=0, longitude=0, zoom=1)

    # r = pydeck.Deck(custom_layer, initial_view_state=view_state, map_provider=None)

    # tooltip = {"text": "Name: {NAME}"}
    # tooltip_value = f"<b>Value:</b> {median_listing_price}""

    tooltip1 = {
        "html": "<b>Name:</b>{name}<br><b>{INDICATOR}:</b> {"
        + selected_col
        + "}<br><b>Year:</b> "
        + str(selected_year)
        + "",
        "style": {"backgroundColor": "beige", "color": "black"},
    }

    layers = []
    
    if show_chloro:
        layers.append(geojson)

    if show_nodata:
        layers.append(geojson_null)
    
    if show_indicator:
        layers.append(geojson_indicator)

    if show_labels:
        layers.append(labels_layer)



    r = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style="light",
        tooltip=tooltip1,
        # map_provider=None,
    )

    row3_col1, row3_col2 = st.columns([7, 1])


    with row3_col1:
        st.pydeck_chart(r)
        # st.write(".")


    with row3_col2:
        st.write(
            cm.create_colormap(
                palette1,
                label="Net Migration Rate (per 1000 population)", #selected_col.replace("_", " ").title(),
                width=0.05,
                height=3,
                orientation="vertical",
                vmin=min1,
                vmax=max1,
                font_size=7,
            )
        )

    return None

app()
