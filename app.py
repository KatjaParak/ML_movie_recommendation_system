from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from utils import normalize_titles, cos_similarity, similarity_df, get_recommendations, extract_features, vectorizer

movies_df = extract_features()
movies_df = normalize_titles(movies_df)
tfidf_matrix = vectorizer(movies_df)
similarity_score = cos_similarity(tfidf_matrix)
sim_df = similarity_df(similarity_score,movies_df)


app = Dash(__name__,external_stylesheets=[dbc.themes.QUARTZ])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Welcome to the movie recommendation engine!", style={"textAlign": "center"}))]),
    dbc.Row([
        dbc.Col(dcc.Input(id="movie-title", type="text",
                  placeholder="Please enter the movie title ", style={"width": "75vh", "height":"3vh"})),
        dbc.Col(html.Button("Search", id="search-button", n_clicks=0, style={"height":"3vh", "border":"none", "text-align":"center"}))
]),
    dbc.Row(html.Div(id="movie-recommendation"))
],style={"width": "250vh", "height": "20vh", "marginTop": "35vh", "marginLeft": ""})

@callback(
    Output("movie-recommendation", "children"),
    Input("search-button", "n_clicks"),
    State("movie-title", "value"),
)
def update_recommendations(n_clicks, movie_name):
   if n_clicks > 0:
        if movie_name:
            recommendations = get_recommendations(movie_name,sim_df, similarity_score, movies_df)
            columns = [dbc.Col(rec) for rec in recommendations]

            return [html.Div([
                dbc.Row(html.H6(" "), style={"height": "3vh"}),
                dbc.Row(columns, style={"width": "100vh","margin": "", "marginTop": "3vh"})
                ],style={"width": "100vh", "marginRight": "5vh"})

            ]
        else: 
            return "Please enter a movie title!"



if __name__ == "__main__":
    app.run(port=8051,debug=True)