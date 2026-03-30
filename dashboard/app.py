from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Amazon Bestsellers Analytics",
    page_icon="books",
    layout="wide",
)


ASSETS_DIR = Path(__file__).resolve().parents[1] / "pipeline" / "assets"
BOOKS_PATH = ASSETS_DIR / "bestsellers_with_categories.csv"
NATIONALITY_PATH = ASSETS_DIR / "author_nationality_seed.csv"


def load_books() -> pd.DataFrame:
    books = pd.read_csv(BOOKS_PATH)
    books.columns = (
        books.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    books["author"] = books["author"].astype(str).str.strip()
    books["genre"] = books["genre"].astype(str).str.strip()
    books["name"] = books["name"].astype(str).str.strip()
    books["year"] = pd.to_numeric(books["year"], errors="coerce").astype("Int64")
    books["reviews"] = pd.to_numeric(books["reviews"], errors="coerce")
    books["price"] = pd.to_numeric(books["price"], errors="coerce")
    books["user_rating"] = pd.to_numeric(books["user_rating"], errors="coerce")
    return books


def load_nationalities() -> pd.DataFrame:
    nationality = pd.read_csv(NATIONALITY_PATH)
    nationality["author"] = nationality["author"].astype(str).str.strip()
    nationality["nationality"] = nationality["nationality"].fillna("Unknown").astype(str).str.strip()
    return nationality


@st.cache_data
def build_metrics() -> dict[str, pd.DataFrame]:
    books = load_books()
    nationalities = load_nationalities()

    books_with_nationality = books.merge(nationalities, on="author", how="left")
    books_with_nationality["nationality"] = books_with_nationality["nationality"].fillna("Unknown")

    author_appearances = (
        books.groupby("author", as_index=False)
        .agg(
            bestseller_appearances=("name", "size"),
            distinct_books=("name", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .merge(nationalities, on="author", how="left")
        .fillna({"nationality": "Unknown"})
        .sort_values(["bestseller_appearances", "author"], ascending=[False, True])
    )

    nationality_distribution = (
        books_with_nationality.groupby("nationality", as_index=False)
        .agg(
            distinct_authors=("author", "nunique"),
            bestseller_rows=("name", "size"),
        )
        .sort_values(["bestseller_rows", "nationality"], ascending=[False, True])
    )

    genre_overall = (
        books.groupby("genre", as_index=False)
        .agg(bestseller_rows=("name", "size"))
        .sort_values(["bestseller_rows", "genre"], ascending=[False, True])
    )
    genre_overall["share_pct"] = (
        100 * genre_overall["bestseller_rows"] / genre_overall["bestseller_rows"].sum()
    ).round(2)

    genre_by_year = (
        books.groupby(["year", "genre"], as_index=False)
        .agg(bestseller_rows=("name", "size"))
        .sort_values(["year", "bestseller_rows", "genre"], ascending=[True, False, True])
    )
    genre_by_year["total_rows"] = genre_by_year.groupby("year")["bestseller_rows"].transform("sum")
    genre_by_year["pct_of_year"] = (
        100 * genre_by_year["bestseller_rows"] / genre_by_year["total_rows"]
    ).round(2)
    genre_by_year["genre_rank_in_year"] = (
        genre_by_year.groupby("year")["bestseller_rows"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    dominant_genre_by_year = genre_by_year.loc[
        genre_by_year["genre_rank_in_year"] == 1
    ].sort_values("year")

    return {
        "books": books,
        "author_appearances": author_appearances,
        "nationality_distribution": nationality_distribution,
        "genre_overall": genre_overall,
        "genre_by_year": genre_by_year,
        "dominant_genre_by_year": dominant_genre_by_year,
    }


def render_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(225, 110, 48, 0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(12, 114, 166, 0.14), transparent 28%),
                linear-gradient(180deg, #f7f2e8 0%, #fbfaf6 48%, #f3efe6 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 20px;
            background: rgba(255, 250, 240, 0.82);
            border: 1px solid rgba(87, 60, 41, 0.12);
            box-shadow: 0 18px 45px rgba(87, 60, 41, 0.08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.35rem;
            margin: 0 0 0.35rem 0;
            color: #2d241d;
        }
        .hero p {
            margin: 0;
            color: #56473b;
            font-size: 1.02rem;
        }
        .caption-card {
            padding: 0.85rem 1rem;
            border-left: 4px solid #c56d2d;
            background: rgba(255, 255, 255, 0.66);
            border-radius: 12px;
            color: #4d4137;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    render_theme()

    if not BOOKS_PATH.exists() or not NATIONALITY_PATH.exists():
        st.error("Required asset files are missing under pipeline/assets/.")
        st.stop()

    metrics = build_metrics()

    books = metrics["books"]
    genre_overall = metrics["genre_overall"]
    genre_by_year = metrics["genre_by_year"]
    dominant_genre_by_year = metrics["dominant_genre_by_year"]
    nationalities = load_nationalities()

    st.markdown(
        """
        <div class="hero">
            <h1>Amazon Bestsellers Dataset Explorer</h1>
            <p>Author presence, nationality dominance, overall genre mix, and year-by-year genre shifts from the 2009-2019 bestseller dataset.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="caption-card">
            Metrics are computed from the local CSV assets. Author spellings are source-faithful.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Controls")
        top_n = st.slider("Top authors to display", min_value=5, max_value=25, value=10)
        nationality_metric = st.radio(
            "Nationality metric",
            options=["Bestseller rows", "Distinct authors"],
            index=0,
        )
        year_range = st.slider(
            "Year range",
            min_value=int(books["year"].min()),
            max_value=int(books["year"].max()),
            value=(int(books["year"].min()), int(books["year"].max())),
        )

    filtered_books = books.loc[books["year"].between(year_range[0], year_range[1])].copy()
    filtered_nationality_distribution = (
        filtered_books.merge(nationalities, on="author", how="left")
        .fillna({"nationality": "Unknown"})
        .groupby("nationality", as_index=False)
        .agg(
            distinct_authors=("author", "nunique"),
            bestseller_rows=("name", "size"),
        )
        .sort_values(["bestseller_rows", "nationality"], ascending=[False, True])
    )

    filtered_author_appearances = (
        filtered_books.groupby("author", as_index=False)
        .agg(
            bestseller_appearances=("name", "size"),
            distinct_books=("name", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .merge(nationalities, on="author", how="left")
        .fillna({"nationality": "Unknown"})
        .sort_values(["bestseller_appearances", "author"], ascending=[False, True])
    )

    filtered_genre_by_year = genre_by_year.loc[
        genre_by_year["year"].between(year_range[0], year_range[1])
    ].copy()
    filtered_dominant_genre = dominant_genre_by_year.loc[
        dominant_genre_by_year["year"].between(year_range[0], year_range[1])
    ].copy()

    authors_chart_df = (
        filtered_books.groupby("author", as_index=False)
        .agg(bestseller_appearances=("name", "size"))
        .sort_values(["bestseller_appearances", "author"], ascending=[False, True])
        .head(top_n)
    )

    overall_genre_df = (
        filtered_books.groupby("genre", as_index=False)
        .agg(bestseller_rows=("name", "size"))
        .sort_values(["bestseller_rows", "genre"], ascending=[False, True])
    )

    overview_cols = st.columns(4)
    overview_cols[0].metric("Dataset rows", f"{len(filtered_books):,}")
    overview_cols[1].metric("Distinct authors", f"{filtered_books['author'].nunique():,}")
    overview_cols[2].metric(
        "Leading nationality",
        filtered_nationality_distribution.iloc[0]["nationality"],
    )
    overview_cols[3].metric(
        "Leading genre",
        overall_genre_df.iloc[0]["genre"],
    )

    authors_tab, nationality_tab, genres_tab, yearly_tab = st.tabs(
        ["Author Presence", "Nationality", "Genre Mix", "Genre by Year"]
    )

    with authors_tab:
        st.subheader("Which authors appear most often in the bestseller dataset?")
        st.dataframe(
            filtered_author_appearances.head(top_n),
            use_container_width=True,
            hide_index=True,
        )
        author_chart = (
            alt.Chart(authors_chart_df)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6, color="#c56d2d")
            .encode(
                x=alt.X("bestseller_appearances:Q", title="Bestseller appearances"),
                y=alt.Y("author:N", sort="-x", title=None),
                tooltip=["author", "bestseller_appearances"],
            )
            .properties(height=420)
        )
        st.altair_chart(author_chart, use_container_width=True)

    with nationality_tab:
        st.subheader("What nationality dominates in the dataset?")
        metric_column = "bestseller_rows" if nationality_metric == "Bestseller rows" else "distinct_authors"
        title = "Bestseller rows" if nationality_metric == "Bestseller rows" else "Distinct authors"
        nationality_chart = (
            alt.Chart(filtered_nationality_distribution.head(12))
            .mark_arc(innerRadius=55)
            .encode(
                theta=alt.Theta(f"{metric_column}:Q"),
                color=alt.Color("nationality:N", legend=alt.Legend(title="Nationality")),
                tooltip=["nationality", "distinct_authors", "bestseller_rows"],
            )
            .properties(height=420)
        )
        left, right = st.columns([1.2, 1])
        with left:
            st.altair_chart(nationality_chart, use_container_width=True)
        with right:
            st.metric("Dominant nationality", filtered_nationality_distribution.iloc[0]["nationality"])
            st.metric(title, int(filtered_nationality_distribution.iloc[0][metric_column]))
            st.dataframe(
                filtered_nationality_distribution,
                use_container_width=True,
                hide_index=True,
            )

    with genres_tab:
        st.subheader("Which genres dominate the dataset overall?")
        genre_chart = (
            alt.Chart(overall_genre_df)
            .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("genre:N", title=None),
                y=alt.Y("bestseller_rows:Q", title="Bestseller rows"),
                color=alt.Color("genre:N", scale=alt.Scale(range=["#0c72a6", "#d98324"]), legend=None),
                tooltip=["genre", "bestseller_rows"],
            )
            .properties(height=420)
        )
        left, right = st.columns([1.1, 0.9])
        with left:
            st.altair_chart(genre_chart, use_container_width=True)
        with right:
            st.dataframe(overall_genre_df, use_container_width=True, hide_index=True)

    with yearly_tab:
        st.subheader("Which genres dominate the dataset per year?")
        stacked_chart = (
            alt.Chart(filtered_genre_by_year)
            .mark_bar()
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("bestseller_rows:Q", title="Bestseller rows"),
                color=alt.Color("genre:N", scale=alt.Scale(range=["#0c72a6", "#d98324"])),
                tooltip=["year", "genre", "bestseller_rows", "pct_of_year"],
            )
            .properties(height=420)
        )
        dominant_line = (
            alt.Chart(filtered_dominant_genre)
            .mark_line(point=True, color="#5c3d2e", strokeWidth=3)
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("bestseller_rows:Q", title="Dominant genre rows"),
                tooltip=["year", "genre", "bestseller_rows", "pct_of_year"],
            )
        )
        st.altair_chart(stacked_chart + dominant_line, use_container_width=True)
        st.dataframe(
            filtered_dominant_genre[["year", "genre", "bestseller_rows", "pct_of_year"]],
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
