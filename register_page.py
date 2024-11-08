import dash
from pages.loader.loader import file_uploader

def register_pages():

    #аплоадер
    dash.register_page('Uploader', path='/', title='uploader', layout=file_uploader())