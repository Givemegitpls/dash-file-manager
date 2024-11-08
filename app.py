import dash
from dash import dcc, html
from register_page import register_pages


app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div([
    dash.page_container,
])
server = app.server
app.config.suppress_callback_exceptions = True

register_pages()
if __name__ == '__main__':
    app.run_server(debug=True)
