import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from utils import get_recommendations


app = Dash(__name__,external_stylesheets=[dbc.themes.QUARTZ])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Welcome to the movie recommendation engine!", style={"textAlign": "center"}))]),
    dbc.Row([
        dbc.Col(dcc.Input(id="movie-title", type="text",
                  placeholder="Please enter the movie title ", style={"width": "80vh", "height":"3vh"})),
        dbc.Col(html.Button("Search", id="search-button", n_clicks=0, style={"height":"3vh", "border":"none", "text-align":"center"}))
]),
    dbc.Row(html.Div(id="movie-recommendation"))
],style={"width": "200vh", "height": "20vh", "marginTop": "35vh", "marginLeft": "40vh"})

@callback(
    Output("movie-recommendation", "children"),
    Input("search-button", "n_clicks"),
    State("movie-title", "value"),
)
def update_recommendations(n_clicks, movie_name):
    if n_clicks > 0:
        if movie_name:
            recommendations = get_recommendations(movie_name)
            return [html.Div("You might also like: {}".format(recommendations))]
        else: 
            return "Please enter a movie title!"



if __name__ == "__main__":
    app.run(port=8051,debug=True)