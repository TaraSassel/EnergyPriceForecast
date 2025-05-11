import streamlit as st

import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

from io import BytesIO

COUNTRY_DATA = {
    'Country': ["Netherlands", "Belgium", "France"], # "Germany"
    'Zone': ['NL', 'BE', "FR"], #De-LU
    'Forecast': ['nl', 'be', 'fr']
}

FILE_PATH = './ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'

def select_country():
    # Creating a selection box
    country_df = pd.DataFrame(COUNTRY_DATA)
    selected_country = st.selectbox('**Select Country**',country_df['Country'].unique())
    selected_country_df = country_df[country_df['Country'] == selected_country].reset_index()

    # Reading data for geopandas
    world = gpd.read_file(FILE_PATH)

    # Filter European countries
    europe = world[world['CONTINENT'] == 'Europe']
    europe = europe[~europe['ADMIN'].isin(['Russia', 'Iceland'])]

    # Defining covered countries
    covered_countries = country_df.Country.to_list()
    country_coverage = pd.DataFrame(europe['ADMIN'])
    country_coverage['coverage'] = country_coverage['ADMIN'].apply(
        lambda x: 1 if x in covered_countries else 0.1
    )
    country_coverage.loc[country_coverage['ADMIN'] == selected_country, 'coverage'] = 2
    europe = europe.merge(country_coverage, on= "ADMIN", how='left')

    return selected_country_df, europe

def create_country_selection_plot(europe):
    # Cretaing Plot
    fig, ax = plt.subplots(figsize=(6, 3))

    cmap = cm.Greens
    norm = mcolors.Normalize(vmin=0, vmax=2)
    europe.plot(ax=ax, column="coverage", cmap=cmap, norm=norm, edgecolor='black')

    ax.set_xlim(-15, 45)
    ax.set_ylim(32, 74)
    ax.axis('off')

    fig.patch.set_facecolor('none')
    ax.set_facecolor('none') 

    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)