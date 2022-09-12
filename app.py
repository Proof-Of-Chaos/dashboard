import os
import time
import warnings
from flask_caching import Cache

import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import requests
import json
import dash_daq as daq
from tabs.main_tab import *


from utils.data_preparation import (
    preprocessing_referendum,
    preprocessing_votes,
    get_df_new_accounts,
    get_substrate_live_data,
)
from utils.plotting import data_perc_bars

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    # external_stylesheets=external_stylesheets,
)
server = app.server
app.config["suppress_callback_exceptions"] = True


mongodb_url = os.getenv("MONGODB_URL")
db_name = os.getenv("DB_NAME")
table_name = os.getenv("TABLE_NAME")

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

theme = {
    "dark": True,
    "detail": "#2d3038",  # Background-card
    "primary": "#007439",  # Green
    "secondary": "#FFD15F",  # Accent
}

# read from subsquid endpoint

cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})

# save all expired referenda to cache

# update cache on referendum expiry

# subSquid_endpoint = "https://squid.subsquid.io/kusama-proposals/v/v1/graphql"
#
# queryExpired = """query MyQuery {
#   proposals(
#     where: {type_eq: Referendum, status_in: Passed, OR: {status_eq: NotPassed}}
#     orderBy: endedAtBlock_DESC
#   ) {
#     createdAt
#     createdAtBlock
#     endedAt
#     endedAtBlock
#     updatedAt
#     updatedAtBlock
#     index
#     threshold {
#       ... on ReferendumThreshold {
#         type
#       }
#     }
#     status
#     voting(orderBy: blockNumber_DESC) {
#       timestamp
#       blockNumber
#       balance {
#         ... on SplitVoteBalance {
#           aye
#           nay
#         }
#         ... on StandardVoteBalance {
#           value
#         }
#       }
#       lockPeriod
#       voter
#       decision
#     }
#   }
# }"""
#
# queryCurrent = """query MyQuery {
#   proposals(
#     where: {type_eq: Referendum, status_eq: Started}
#     orderBy: endedAtBlock_DESC
#   ) {
#     createdAt
#     createdAtBlock
#     endedAt
#     endedAtBlock
#     updatedAt
#     updatedAtBlock
#     index
#     threshold {
#       ... on ReferendumThreshold {
#         type
#       }
#     }
#     status
#     voting(orderBy: blockNumber_DESC) {
#       timestamp
#       blockNumber
#       balance {
#         ... on SplitVoteBalance {
#           aye
#           nay
#         }
#         ... on StandardVoteBalance {
#           value
#         }
#       }
#       lockPeriod
#       voter
#       decision
#     }
#   }
# }"""
#
#
#
# def save_expired_to_file():
#     r = requests.post(subSquid_endpoint, json={"query": queryExpired})
#     f = open("referenda.json", "w")
#     f.write(r.text)
#     f.close()
#
#
# save_expired_to_file()
#
# with open("./referenda.json", "r") as f:
#     data = json.loads(f.read())

# @cache.cached(300)
# def get_current_ref_data():
#     r = requests.post(subSquid_endpoint, json={'query': queryCurrent})
#     return json.loads(r.text)
#
# json_data = get_current_ref_data()


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.H1("Kusama Governance Dashboard - Referendum Analysis"),
        ],
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab1",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Main-tab",
                        label="Main Dashboard",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled_style={
                            "backgroundColor": "#2d3038",
                            "color": "#95969A",
                            "borderColor": "#23262E",
                            "display": "flex",
                            "flex-direction": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                        disabled=False,
                    ),
                    dcc.Tab(
                        id="Referendum-tab",
                        label="Single Referendum View",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled_style={
                            "backgroundColor": "#2d3038",
                            "color": "#95969A",
                            "borderColor": "#23262E",
                            "display": "flex",
                            "flex-direction": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                        disabled=False,
                    ),
                    dcc.Tab(
                        id="Single-account-tab",
                        label="Single Account View",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled_style={
                            "backgroundColor": "#2d3038",
                            "color": "#95969A",
                            "borderColor": "#23262E",
                            "display": "flex",
                            "flex-direction": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                        disabled=False,
                    ),
                ],
            )
        ],
    )


#
# def load_raw_data():
#     df_raw = pd.read_csv("test_data.csv")
#     print("raw data loaded!")
#     return df_raw.to_dict('record')


def load_refined_referenda_data():
    # df_raw = load_data(mongodb_url=mongodb_url, db_name=db_name, table_name=table_name)
    df_raw = pd.read_csv("referendum_data.csv")
    df_referendum = preprocessing_referendum(df_raw)
    print("referendum data loaded!")
    return df_referendum.to_dict("record")


def load_refined_votes_data():
    # df_raw = load_data(mongodb_url=mongodb_url, db_name=db_name, table_name=table_name)
    df_raw = pd.read_csv("votes_data.csv")
    df_votes = preprocessing_votes(df_raw)
    print("votes data loaded!")
    return df_votes.to_dict("record")


#
# df_raw = load_raw_data()
# referenda_dict = load_refined_referenda_data(df_raw)
# votes_dict = load_refined_votes_data(df_raw)


def build_tab_2():
    return [
        html.Div(className="twelve columns", children=[html.Br()]),
        html.Div(className="twelve columns", children=[html.Br()]),
        html.Div(
            className="section-banner",
            children=[
                html.Div(
                    className="twelve columns",
                    children=[
                        html.P(
                            "Type in the Referendum index: ",
                            style={"display": "inline-block", "margin-right": "8px"},
                        ),
                        dcc.Input(id="referendum_input", placeholder="number"),
                        html.Div(id="referendum_input_warning", children=[]),
                    ],
                ),
                html.Button(
                    "Confirm",
                    id="referendum-trigger-btn",
                    n_clicks=0,
                    style={"display": "inline-block", "float": "middle"},
                ),
            ],
        ),
        dcc.Store(id="specific-referendum-data", data=[], storage_type="memory"),
        dcc.Store(id="specific-referendum-votes-data", data=[], storage_type="memory"),
    ]


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=0,
            disabled=True,
        ),
        dcc.Interval(
            id="interval-component-live",
            interval=300,  # in milliseconds
            n_intervals=0,
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        # Main app
        dcc.Store(id="raw-data", data=[], storage_type="memory"),
        dcc.Store(id="votes-data", data=[], storage_type="memory"),
        dcc.Store(
            id="referenda-data",
            data=[],
            storage_type="memory",
        ),
        dcc.Store(id="ongoing-referenda-data", data=[], storage_type="memory"),
        dcc.Store(id="n-interval-stage", data=0),
    ],
)


# Callback to update the historical data
@app.callback(
    [
        Output("referenda-data", "data"),
        Output("votes-data", "data"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_historical_data(n_intervals):
    if n_intervals >= 0:
        refined_referenda_data = load_refined_referenda_data()
        refined_votes_data = load_refined_votes_data()

        return (
            refined_referenda_data,
            refined_votes_data,
        )

@app.callback(
    Output("id-rangebar", "children"),
    [Input("referenda-data", "data")],
)
def create_rangeslider(refined_referenda_data):
    df = pd.DataFrame(refined_referenda_data)
    range_min = df["referendum_index"].min()
    range_max = df["referendum_index"].max()
    return dcc.RangeSlider(id="selected-ids", min=range_min, max=range_max)


# Callback to update the referendum df
@app.callback(
    [
        Output("specific-referendum-data", "data"),
        Output("specific-referendum-votes-data", "data"),
        Output("referendum_input_warning", "children"),
    ],
    [
        Input("referendum-trigger-btn", "n_clicks"),
        Input("referendum_input", "value"),
        Input("referenda-data", "data"),
        Input("votes-data", "data"),
    ],
)
def update_specific_referendum_data(
    n_clicks, referendum_input, referenda_data, votes_data
):
    warning = None
    df_specific_referendum = pd.DataFrame()
    if referendum_input:
        df_referenda = pd.DataFrame(referenda_data)
        df_votes = pd.DataFrame(votes_data)
        try:
            df_specific_referendum = df_referenda[
                df_referenda.referendum_index == int(referendum_input)
            ]
            df_specific_referendum_votes = df_votes[
                df_votes.referendum_index == int(referendum_input)
            ]
        except:
            warning = html.P(
                className="alert alert-danger", children=["Invalid input"]
            )
        if df_specific_referendum.empty:
            warning = html.P(
                className="alert alert-danger", children=["Invalid input"]
            )
        return (
            df_specific_referendum.to_dict("record"),
            df_specific_referendum.to_dict("record"),
            [warning],
        )


# Callback to update the live data
@app.callback(
    Output("ongoing-referenda-data", "data"),
    Input("interval-component-live", "n_intervals"),
)
def update_live_data(n_intervals):
    if n_intervals >= 0:
        df_ongoing_referenda = get_substrate_live_data()
        return df_ongoing_referenda.to_dict("record")


@app.callback(
    Output("live-data-table", "children"), Input("ongoing-referenda-data", "data")
)
def create_live_data_table(data):
    dff = pd.DataFrame(data[:])
    print(f"live data updated {time.time()}")
    dff = dff[["referendum_index", "threshold", "ayes_perc", "turnout"]]

    my_table = dash_table.DataTable(
        data=dff.to_dict("records"),
        columns=[{"name": i, "id": i} for i in dff.columns],
        sort_action="native",
        style_data_conditional=(
            [
                {
                    "if": {
                        "column_id": "referendum_index",
                    },
                    "fontWeight": "bold",
                    "color": "black",
                }
            ]
            + data_perc_bars(dff, "ayes_perc")
        ),
        style_cell={
            "width": "100px",
            "minWidth": "100px",
            "maxWidth": "100px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
    )
    return my_table


@app.callback(
    Output("table-placeholder", "children"),
    [Input("referenda-data", "data"), Input("selected-ids", "value")],
)
def create_graph1(data, selected_ids):
    dff = pd.DataFrame(data[:])
    if selected_ids:
        dff = dff[
            (dff["referendum_index"] >= selected_ids[0])
            & (dff["referendum_index"] <= selected_ids[1])
        ]
    dff = dff[["referendum_index", "turnout_perc"]]
    # 2. convert string like JSON to pandas dataframe
    # dff = pd.read_json(data, orient='split')
    my_table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in dff.columns], data=dff.to_dict("records")
    )
    return my_table


#
# @app.callback(Output("id-rangebar", "children"), Input("referenda-data", "data"))
# def create_index_range_bar(data):
#     df = pd.DataFrame(data[:])
#     range_min = df["referendum_index"].min()
#     range_max = df["referendum_index"].max()
#     # 2. convert string like JSON to pandas dataframe
#     # dff = pd.read_json(data, orient='split')
#     return dcc.RangeSlider(id="selected-ids", min=range_min, max=range_max)


@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == "tab1":
        return build_tab_1(), stopped_interval
    if tab_switch == "tab2":
        return build_tab_2(), stopped_interval
    return (
        html.Div(
            id="status-container",
            children=[
                html.H3("Tab content 1"),
                dcc.Graph(
                    figure={"data": [{"x": [1, 2, 3], "y": [3, 1, 2], "type": "bar"}]}
                ),
            ],
        ),
        stopped_interval,
    )


# # # Update interval
@app.callback(
    Output("n-interval-stage", "data"),
    [Input("app-tabs", "value")],
    [
        State("interval-component", "n_intervals"),
        State("interval-component", "disabled"),
        State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval
    if tab_switch == "tab1":
        return cur_interval
    return cur_stage

# Update first chart
@app.callback(
    output=Output("votes_counts_barchart", "figure"),
    inputs=[
        Input("interval-component", "n_intervals"),
        Input("selected-ids", "value"),
        Input("votes_counts_chart_selection", "value"),
    ],
    state=[Input("votes-data", "data"), Input("referenda-data", "data")],
)
def update_votes_counts_chart(
    n_intervals, selected_ids, selected_toggle_value, votes_data, referenda_data
):
    df_votes = pd.DataFrame(votes_data)
    df_referenda = pd.DataFrame(referenda_data).sort_values(by="referendum_index")
    if selected_ids:
        df_votes = df_votes[
            (df_votes["referendum_index"] >= selected_ids[0])
            & (df_votes["referendum_index"] <= selected_ids[1])
        ]

    df_counts_sum = (
        df_votes.groupby("referendum_index")["account_address"]
        .count()
        .reset_index(name="vote_counts")
        .sort_values(by="referendum_index")
    )
    df_counts_sum = df_counts_sum.merge(
        df_referenda, how="inner", on="referendum_index"
    ).sort_values(by="referendum_index")
    first_graph_layout = go.Layout(
        title="<b>Vote Count</b>",
        barmode="stack",
        paper_bgcolor="#161a28",
        plot_bgcolor="#161a28",
        xaxis=dict(title="Referendum ID", linecolor="#BCCCDC"),
        yaxis=dict(title="Vote counts", linecolor="#021C1E"),
        yaxis2=dict(
            title="Duration of voting",
            linecolor="#021C1E",
            anchor="x",
            overlaying="y",
            side="right",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        template="plotly_dark",
    )
    if selected_toggle_value == False:
        df_aye = df_votes[df_votes["passed"] == True]
        df_aye_count_sum = (
            df_aye.groupby("referendum_index")["account_address"]
            .count()
            .reset_index(name="vote_counts")
            .sort_values(by="referendum_index")
        )
        df_nay = df_votes[df_votes["passed"] == False]
        df_nay_count_sum = (
            df_nay.groupby("referendum_index")["account_address"]
            .count()
            .reset_index(name="vote_counts")
            .sort_values(by="referendum_index")
        )
        first_graph_data = [
            go.Bar(
                name="Aye Votes",
                x=df_aye_count_sum["referendum_index"],
                y=df_aye_count_sum["vote_counts"],
                marker_color="rgb(0, 0, 100)",
                customdata=df_counts_sum["vote_counts"],
                hovertemplate="<b>Aye Votes</b><br><br>"
                + "Referendum id: %{x:.0f}<br>"
                + "Aye vote counts: %{y:.0f}<br>"
                + "Total counts: %{customdata:.0f}<br>"
                + "<extra></extra>",
            ),
            go.Bar(
                name="Nay Votes",
                x=df_nay_count_sum["referendum_index"],
                y=df_nay_count_sum["vote_counts"],
                customdata=df_counts_sum["vote_counts"],
                marker_color="rgb(0, 200, 200)",
                hovertemplate="<b>Nay Votes</b><br><br>"
                + "Referendum id: %{x:.0f}<br>"
                + "Nay Vote counts: %{y:.0f}<br>"
                + "Total counts: %{customdata:.0f}<br>"
                + "<extra></extra>",
            ),
        ]
    if selected_toggle_value == True:
        first_graph_data = [
            go.Bar(
                name="Total Votes",
                x=df_counts_sum["referendum_index"],
                y=df_counts_sum["vote_counts"],
                customdata=df_counts_sum["duration"],
                marker=dict(
                    color=df_counts_sum[
                        "duration"
                    ],  # set color equal to a variable # one of plotly colorscales
                    colorscale="earth",
                    showscale=True,
                ),
                hovertemplate="<b>Delegated Votes</b><br><br>"
                + "Referendum id: %{x:.0f}<br>"
                + "Votes counts: %{y:.0f}<br>"
                + "Duration: %{customdata:.1f} days<br>"
                + "<extra></extra>",
            ),
        ]
    fig_first_graph = go.Figure(data=first_graph_data, layout=first_graph_layout)
    return fig_first_graph


# Update second chart
@app.callback(
    Output("turnout_scatterchart", "figure"),
    [Input("referenda-data", "data"), Input("selected-ids", "value")],
)
def update_bar_chart(referenda_data, selected_ids):
    df_referendum = pd.DataFrame(referenda_data)
    if selected_ids:
        df_referendum = df_referendum[
            (df_referendum["referendum_index"] >= selected_ids[0])
            & (df_referendum["referendum_index"] <= selected_ids[1])
        ]
    second_graph_data = go.Scatter(
        name="Turnout",
        x=df_referendum.referendum_index.astype(int),
        y=df_referendum["turnout_perc"],
        # mode="lines+markers",
        line=dict(color="rgb(0, 0, 100)"),
        # marker=dict(color="rgb(0, 0, 100)", size=8),
        hovertemplate="Referendum id: %{x:.0f}<br>"
        + "Turnout (%): %{y:.4f}<br>"
        + "<extra></extra>",
    )

    second_graph_layout = go.Layout(
        title="<b>Turnout for selected Referendum IDs</b>",
        paper_bgcolor="rgb(248, 248, 255)",
        plot_bgcolor="rgb(248, 248, 255)",
        barmode="stack",
        xaxis=dict(title="Referendum ID", linecolor="#BCCCDC"),
        yaxis=dict(title="Turnout (% of total issued Kusama)", linecolor="#021C1E"),
    )
    fig_second_graph = go.Figure(data=second_graph_data, layout=second_graph_layout)
    return fig_second_graph


# Update third chart
@app.callback(
    Output("new_accounts_barchart", "figure"),
    [
        Input("referenda-data", "data"),
        Input("votes-data", "data"),
        Input("selected-ids", "value"),
    ],
)
def update_new_accounts_chart(referenda_data, votes_data, selected_ids):
    df_new_accounts = get_df_new_accounts(referenda_data, votes_data)
    if selected_ids:
        df_new_accounts = df_new_accounts[
            (df_new_accounts["referendum_index"] >= selected_ids[0])
            & (df_new_accounts["referendum_index"] <= selected_ids[1])
        ]
    third_graph_data = [
        go.Bar(
            name="New accounts counts",
            x=df_new_accounts["referendum_index"],
            y=df_new_accounts["new_accounts"],
            marker_color="rgb(0, 200, 200)",
            hovertemplate="Referendum id: %{x:.0f}<br>"
            + "New accounts counts: %{y:.0f}<br>"
            + "<extra></extra>",
        ),
        go.Scatter(
            name="% of total votes counts",
            x=df_new_accounts["referendum_index"],
            y=df_new_accounts["perc_new_accounts"],
            # mode="lines+markers",
            yaxis="y2",
            line=dict(color="rgb(0, 0, 100)"),
            # marker=dict(color="rgb(0, 0, 100)", size=4),
            hovertemplate="Referendum id: %{x:.0f}<br>"
            + "% of total votes counts: %{y:.4f}<br>"
            + "<extra></extra>",
        ),
    ]

    third_graph_layout = go.Layout(
        title="<b>New accounts for selected Referendum IDs</b>",
        paper_bgcolor="rgb(248, 248, 255)",
        plot_bgcolor="rgb(248, 248, 255)",
        barmode="stack",
        xaxis=dict(title="Referendum ID", linecolor="#BCCCDC"),
        yaxis=dict(title="New accounts counts", linecolor="#021C1E"),
        yaxis2=dict(
            title="New accounts counts (% of total votes counts)",
            linecolor="#021C1E",
            anchor="x",
            overlaying="y",
            side="right",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    fig_third_graph = go.Figure(data=third_graph_data, layout=third_graph_layout)
    return fig_third_graph


# Update forth chart
@app.callback(
    Output("voted_ksm_scatterchart", "figure"),
    [Input("votes-data", "data"), Input("selected-ids", "value")],
)
def update_vote_amount_with_conviction_chart(votes_data, selected_ids):
    df_votes = pd.DataFrame(votes_data)
    if selected_ids:
        df_votes = df_votes[
            (df_votes["referendum_index"] >= selected_ids[0])
            & (df_votes["referendum_index"] <= selected_ids[1])
        ]
    df_vote_amount_with_conviction_mean = (
        df_votes[["referendum_index", "vote_amount_with_conviction"]]
        .groupby("referendum_index")
        .mean()
    )
    df_vote_amount_with_conviction_median = (
        df_votes[["referendum_index", "vote_amount_with_conviction"]]
        .groupby("referendum_index")
        .median()
    )
    forth_graph_data = [
        go.Scatter(
            name="mean",
            x=df_vote_amount_with_conviction_mean.index,
            y=df_vote_amount_with_conviction_mean["vote_amount_with_conviction"],
            mode="lines+markers",
            line=dict(color="rgb(0, 0, 100)", dash="dot"),
            marker=dict(color="rgb(0, 0, 100)", size=4),
            hovertemplate="Referendum index: %{x:.0f}<br>"
            + "vote amount with conviction mean: %{y:.4f}<br>"
            + "<extra></extra>",
        ),
        go.Scatter(
            name="median",
            x=df_vote_amount_with_conviction_median.index,
            y=df_vote_amount_with_conviction_median["vote_amount_with_conviction"],
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="rgb(0, 200, 200)", dash="dash"),
            marker=dict(color="rgb(0, 200, 200)", size=6),
            hovertemplate="Referendum index: %{x:.0f}<br>"
            + "vote amount with conviction median: %{y:.4f}<br>"
            + "<extra></extra>",
        ),
    ]
    forth_graph_layout = go.Layout(
        title="<b>Locked KSM Mean and Median for selected Referendum IDs</b>",
        paper_bgcolor="rgb(248, 248, 255)",
        plot_bgcolor="rgb(248, 248, 255)",
        xaxis=dict(title="Referendum ID", linecolor="#BCCCDC"),
        yaxis=dict(title="Vote Amount with Conviction - Mean", linecolor="#021C1E"),
        yaxis2=dict(
            title="Vote Amount with Conviction - Median",
            linecolor="#021C1E",
            anchor="x",
            overlaying="y",
            side="right",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    fig_forth_graph = go.Figure(data=forth_graph_data, layout=forth_graph_layout)
    return fig_forth_graph


# Update piechart
@app.callback(
    Output("call_module_piechart", "figure"),
    [Input("referenda-data", "data"), Input("selected-ids", "value")],
)
def update_pie_chart(referenda_data, selected_ids):
    df = pd.DataFrame(referenda_data)
    if selected_ids:
        df = df[
            (df["referendum_index"] >= selected_ids[0])
            & (df["referendum_index"] <= selected_ids[1])
        ]
    new_figure = {
        "data": [
            {
                "labels": df["call_module"].value_counts().index.tolist(),
                "values": list(df["call_module"].value_counts()),
                "type": "pie",
                "marker": {"li": dict(color="white", width=2)},
                "hoverinfo": "label",
                "textinfo": "label",
            }
        ],
        "layout": {
            "margin": dict(t=20, b=50),
            "uirevision": True,
            "font": {"color": "white"},
            "showlegend": False,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "autosize": True,
        },
    }
    return new_figure




# # Running the server
if __name__ == "__main__":
    warnings.filterwarnings(action="ignore")
    app.run_server(port=8088, debug=True)
