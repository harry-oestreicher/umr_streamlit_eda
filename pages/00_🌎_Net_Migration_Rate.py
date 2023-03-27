import datetime
import os
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb

st.set_page_config(layout="wide")

# STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
# # We create a downloads directory within the streamlit static asset directory
# # and we write output files to it
# DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
# if not DOWNLOADS_PATH.is_dir():
#     DOWNLOADS_PATH.mkdir()

link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/umr/"

data_links = {
    "reference": {
        "countries": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
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
    
    new_gdf = new_gdf[~new_gdf["id"].isna()]
    new_gdf = new_gdf.drop(columns=["REF_AREA", "INDICATOR"])
    return new_gdf



def join_indicators(gdf, df, indicator):
    new_gdf = None
    if indicator == "DM_":
        new_gdf = gdf.merge(df, left_on=["id", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "ECON_":
        new_gdf = gdf.merge(df, left_on=["id", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "HVA_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "MG_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "MNCH_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "PT_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "PV_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")
    elif indicator == "WS_":
        new_gdf = gdf.merge(df, left_on=["ISO_A3", "TIME_PERIOD"], right_on=["REF_AREA", "TIME_PERIOD"], how="outer")

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

    st.title("Net Migration Rate Analysis")
    st.write(
        """Several open-source packages are used to process the data and generate the visualizations, e.g., [streamlit](https://streamlit.io),
          [geopandas](https://geopandas.org), [leafmap](https://leafmap.org), and [pydeck](https://deckgl.readthedocs.io).
        """
    )

    row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(
        [0.5, 0.5, 1.2, 0.8, 1]
    )

    years_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

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
        st.write(indicator_df.head(3))
        # ind_list = indicator_df["INDICATOR"].unique()
        # st.write(indicator_df)


    with row1_col5:
        # get_indicator_dict(name)
        show_desc = "no"
        show_desc = st.checkbox("Show indicator description")
        if show_desc:
            try:
                # label, desc = get_indicator_dict(indicator.strip())
                # markdown = f"""
                # **{label}**: {desc}
                # """
                # st.markdown(markdown)

                for i in indicator_df["INDICATOR"].unique():
                    st.write(f"{get_indicator_dict(i)}")
                    pass

            except:
                st.warning("No description available for selected attribute")

    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5, row2_col6 = st.columns(
        [0.6, 0.68, 0.7, 0.7, 1.5, 0.8]
    )

    palettes = cm.list_colormaps()
    with row2_col1:
        palette = st.selectbox("Color palette", palettes, index=palettes.index("Blues"))
    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
    with row2_col3:
        show_nodata = st.checkbox("Show nodata areas", value=True)
    with row2_col4:
        show_3d = st.checkbox("Show 3D view", value=False)
    with row2_col5:
        if show_3d:
            elev_scale = st.slider(
                "Elevation scale", min_value=1, max_value=10000, value=1, step=10
            )
            with row2_col6:
                st.info("Press Ctrl and move the left mouse button.")
        else:
            elev_scale = 1


    # First JOIN
    gdf = join_attributes(gdf, inventory_df, scale.lower())


    gdf_null = select_null(gdf, selected_col)
    gdf = select_non_null(gdf, selected_col)
    gdf = gdf.sort_values(by=selected_col, ascending=True)


    colors = cm.get_palette(palette, n_colors)
    colors = [hex_to_rgb(c) for c in colors]

    for i, ind in enumerate(gdf.index):
        index = int(i / (len(gdf) / len(colors)))
        if index >= len(colors):
            index = len(colors) - 1
        gdf.loc[ind, "R"] = colors[index][0]
        gdf.loc[ind, "G"] = colors[index][1]
        gdf.loc[ind, "B"] = colors[index][2]

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

    min_value = gdf[selected_col].min()
    max_value = gdf[selected_col].max()
    color = "color"
    # color_exp = f"[({selected_col}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
    color_exp = f"[R, G, B]"

    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        pickable=True,
        opacity=0.5,
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

    # tooltip = {"text": "Name: {NAME}"}

    # tooltip_value = f"<b>Value:</b> {median_listing_price}""
    tooltip = {
        "html": "<b>Name:</b> {id}<br><b>Value:</b> {"
        + selected_col
        + "}<br><b>Year:</b> "
        + str(selected_year)
        + "",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    layers = [geojson]
    if show_nodata:
        layers.append(geojson_null)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style="light",
        tooltip=tooltip,
    )

    row3_col1, row3_col2 = st.columns([6, 1])

    with row3_col1:
        st.pydeck_chart(r)
    with row3_col2:
        st.write(
            cm.create_colormap(
                palette,
                label="Net Migration Rate\n per 1k population", #selected_col.replace("_", " ").title(),
                width=0.2,
                height=3,
                orientation="vertical",
                vmin=min_value,
                vmax=max_value,
                font_size=10,
            )
        )
    # row4_col1, row4_col2, row4_col3 = st.columns([1, 2, 3])
    # with row4_col1:
    #     show_data = st.checkbox("Show raw data")
    # with row4_col2:
    #     show_cols = st.multiselect("Select columns", data_cols)
    # with row4_col3:
    #     show_colormaps = st.checkbox("Preview all color palettes")
    #     if show_colormaps:
    #         st.write(cm.plot_colormaps(return_fig=True))
    # if show_data:
    #     if scale == "National":
    #         st.dataframe(gdf[["NAME", "GEOID"] + show_cols])
    #     elif scale == "State":
    #         st.dataframe(gdf[["NAME", "STUSPS"] + show_cols])
    #     elif scale == "County":
    #         st.dataframe(gdf[["NAME", "STATEFP", "COUNTYFP"] + show_cols])
    #     elif scale == "Metro":
    #         st.dataframe(gdf[["NAME", "CBSAFP"] + show_cols])
    #     elif scale == "Zip":
    #         st.dataframe(gdf[["GEOID10"] + show_cols])


app()
