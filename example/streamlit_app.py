import itertools
from typing import List

import pandas as pd
import pydeck as pdk
import streamlit as st


def example_inputs():
    col1, col2 = st.columns(2)
    name = col1.text_input("What is your name?", placeholder="John Doe")
    if name != "": col1.write(f"Hi {name}!")

    # Sharing variables between reruns :O
    if "counter" not in st.session_state:
        st.session_state["counter"] = 0

    if col2.button("Click me!"): st.session_state["counter"] += 1
    col2.write(f"Total clicks: {st.session_state['counter']}")


# Cache so there is no need to constantly load the dataframe!
@st.cache()
def get_dataframe() -> pd.DataFrame:
    return pd.read_csv("./dataset.csv")


def beautify_string(s: str) -> str:
    return s.replace('_', ' ').title()


def kpis(df: pd.DataFrame, descriptions: List[str]):
    streamlit_cols = st.columns(len(descriptions))
    for index, description in enumerate(descriptions):
        streamlit_cols[index].metric(
            f"Total {beautify_string(description)}:",
            len(df[df["description"] == description])
        )


def show_colored_circle(rgb_color: List[int], loc=st):
    # HTML, ugly, but can be done :O
    loc.markdown(
        f"""
        <div style="
            width: 25px;
            height: 25px;
            -webkit-border-radius: 25px;
            -moz-border-radius: 25px;
            border-radius: 25px;
            background: rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]});
            display: inline-block;">
        </div>
        """,
        unsafe_allow_html=True
    )


def choose_layers(df: pd.DataFrame, descriptions: List[str]) -> List[pdk.Layer]:
    foo = [[2, 1] for _ in descriptions]
    streamlit_cols = st.columns(list(itertools.chain(*foo)))
    colors = [
        [117, 208, 223],
        [102, 203, 119],
        [203, 115, 102],
        [246, 228, 137]
    ]

    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=df[df["description"] == description],
            pickable=True,
            get_position=["longitude", "latitude"],
            get_color=colors[index],
            get_radius=35,
        )
        for index, description in enumerate(descriptions)
        # Components can be used in list comprehensions :O
        if streamlit_cols[2 * index].checkbox(beautify_string(description), True)
    ]

    for index, color in enumerate(colors):
        show_colored_circle(color, loc=streamlit_cols[1 + 2 * index])

    return layers


def plot_map(df: pd.DataFrame, descriptions: List[str]):
    layers = choose_layers(df, descriptions)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=41.4,
            longitude=2.17,
            zoom=12,
            bearing=0,
            pitch=0,
        ),
        layers=layers,
        tooltip={"text": "{name}"}
    ))


def main():
    st.markdown("""
        # Streamlit Demo!

        Streamlit is a Python library that makes creating simple websites (such
        as dashboards) incredibly easy! No front-end knowledge required!
        We have created a quick demo of what can be done 😁. For more advanced
        stuff such as multipage apps check out the [docs](https://docs.streamlit.io/).
        """
    )
    st.markdown("""
        ---
        ### Inputs
        """
    )
    example_inputs()
    df = get_dataframe()
    descriptions = ["elderly_homes", "day_centers", "hospitals", "pharmacies"]
    st.markdown("""
        ---
        ### KPIs
    """
    )
    kpis(df, descriptions)
    st.markdown("""
        ---
        ### Maps / plots

        It is incredibly easy to show plots with Streamlit. Matplotlib, plotly,
        altair charts and many more are compatible! Below you can find an
        example of a map made with the PyDeck library.
    """
    )
    plot_map(df, descriptions)

if __name__ == "__main__":
    # st.set_page_config(layout="wide")
    main()