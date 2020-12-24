"""
Script that will recreate all desired plots and save to Reports/Figures
when run.

When I've finished playing with a plot, I finalise it here so that it comes
out the same every time and I can save them all in a loop.

Add each figure variable to the list 'figs' under the __name__ = __main__ clause.

Author: Tom Fleet
Created: 24/12/2020
"""
import altair as alt
from altair_saver import save

from src.config import FIGURES
from src.data.load_data import GenerationCapacity

# Datasets loading #

clean_cap = GenerationCapacity().load_cleaned()
totals = GenerationCapacity().load_cleaned(level="total")
types = GenerationCapacity().load_cleaned(level="type")
fuels = GenerationCapacity().load_cleaned(level="fuel")

# /Datasets loading #


def png_name(fig: alt.Chart) -> str:
    """
    Takes an altair chart, extracts the title and converts this
    to a filename with a .png extension for saving.

    Args:
        fig (alt.Chart): Altair chart object to convert.

    Returns:
        str: Formatted filename (png).
    """

    if fig.title:
        fname = (
            fig.title.strip()
            .replace(" ", "_")
            .replace("-", "")
            .replace(":", "")
            .lower()
            + ".png"
        )
    else:
        raise ValueError("In order to save the chart, it must have a title!")

    return fname


def save_altair_plot(fig: alt.Chart) -> None:

    fname = png_name(fig)

    save(
        chart=fig,
        fp=str(FIGURES.joinpath(fname)),
        fmt="png",
        method="selenium",
        scale_factor=6.0,
    )


fig1 = (
    alt.Chart(data=totals)
    .mark_bar()
    .encode(
        x=alt.X("country:N", title="Country", sort="-y"),
        y=alt.Y("sum(capacity):Q", title="Generation Capacity (MW)"),
    )
    .properties(
        width=750,
        height=500,
        title="Total Generation Capacity by Country (1990 - 2020)",
    )
)

fig2 = (
    alt.Chart(data=types)
    .mark_bar()
    .encode(
        x=alt.X("country:N", title="Country", sort="-y"),
        y=alt.Y("mean(capacity):Q", title="Generation Capacity (MW)", stack=True),
        color=alt.Color("technology:N", title="Technology"),
    )
    .properties(
        height=500,
        width=750,
        title="Mean Energy Generation Capacity by Source and Country (1990 - 2020)",
    )
)

if __name__ == "__main__":
    figs = [fig1, fig2]
    for fig in figs:
        save_altair_plot(fig)
        print(f"Figure: {png_name(fig)} saved successfuly!")
