from dash import dcc, html, Input, Output, State, callback, ALL, MATCH, ctx, exceptions
import base64
import datetime
import os

@callback(Output('mkdir_dialog','children', allow_duplicate=True),
          Input('make_dir_dialog_trigger', 'n_clicks'),
          config_prevent_initial_callbacks=True)
def mkdir_dialog(n):
    if n is None:
        raise exceptions.PreventUpdate("cancel the callback")
    layout = html.Div([
        dcc.Input(id="mkdir_input", type="text", placeholder="Введите название папки", className='folder_up'),
        html.Div([
            html.Button('Подтвердить', id='mkdir_submit', className='button'),
            html.Button('+', id='mkdir_cancel', className='close_button', style={'margin-right': '1.5em'})
        ], style={'display': 'grid', 'grid-template-columns': '1fr max-content', 'margin-top': '-1em'}),
    ], style={'position':'absolute', 'z-index':'2', 'left':'50%', 'transform':'translate(-50%, -50%)', 'top':'50vh', 'padding': '1em', 'border-radius': '1em', 'background': '#F7F9FB'})
    return layout

@callback(Output('mkdir_dialog','children', allow_duplicate=True),
          Output('current_dir_holder', 'children', allow_duplicate=True),
          Input('mkdir_submit', 'n_clicks'),
          Input('mkdir_cancel', 'n_clicks'),
          State('mkdir_input', 'value'),
          State('current_dir', 'value'),
          config_prevent_initial_callbacks=True)
def mkdir_dialog(submit, cancel, input, path):
    if submit is None and cancel is None:
        raise exceptions.PreventUpdate("cancel the callback")
    else:
        if submit == 1 and input is not None:
            os.mkdir(f'{path}{input}')
        layout = html.Div()
        return layout, button(path)

@callback(Output('file_manager', 'children'),
          State('current_dir', 'value'),
          Input('current_dir', 'n_clicks'))
def file_manager(path, clicks):
    folders = []
    files = []
    index = 0
    files_list = os.listdir(path)
    for i in range(len(files_list)):
        title = files_list[i]
        if '.' not in title:
            folders += [html.Div([
                html.Div(id={'type': 'button_trasher', 'index': index}, style = {'display': 'none'}),
                html.Button(html.Img(src='/assets/File Manager/folder.svg', style={'width': '100%', 'margin':'auto'}), id={'type':'upload_dir', 'index': index}, value=title, className='folderbutton'),
                html.Div(title, className='title')
            ], className='cell')]
            index += 1
        else:
            files += [html.Div([
                    html.Div(html.Img(src='/assets/File Manager/document.svg', style={'width': '100%', 'margin':'auto'}), style={'padding': '0.8em'}),
                    html.Div(title, className='title')
                ], className='cell')]
    make_dir_button = [html.Div([
            html.Button(html.Img(src='/assets/File Manager/makedir.svg', style={'width': '100%', 'margin':'auto'}), id='make_dir_dialog_trigger', className='folderbutton'),
            html.Div('Создать папку', className='title')
        ], className='cell')]
    return html.Div(folders+make_dir_button+files, style={'display': 'grid', 'grid-template-columns': 'repeat(auto-fit, minmax(10em, 1fr))'})


def button(path):
    return html.Button([html.Div([path]), html.Div(['На папку вверх'], className='hover')], id='current_dir', value=path, n_clicks=0, className='folder_up')

@callback(Output({"type":"button_trasher", "index": ALL}, 'children'),
          Output('current_dir_holder', 'children', allow_duplicate=True),
          Input({"type":"upload_dir", "index": ALL}, 'n_clicks'),
          State({"type":"upload_dir", "index": ALL}, 'value'),
          State('current_dir', 'value'),
          config_prevent_initial_callbacks=True)
def button_event(n_clicks, values, current):
    buttons = []
    for i in range(len(values)):
        buttons += ['']
        if n_clicks[i] is not None:
            new_current = values[i]
            new_current = button(f'{current}{new_current}/')
            return values, new_current
    raise exceptions.PreventUpdate("cancel the callback")

@callback(Output('current_dir_holder', 'children', allow_duplicate=True),
          State('current_dir', 'value'),
          Input('current_dir', 'n_clicks'),
          config_prevent_initial_callbacks=True,)
def folder_up(value, clicks):
    if clicks != 0:
        current = value.split("/")
        current.remove('')
        if len(current) > 1:
            current = current[len(current) - 1]
            path = value.replace(f'{current}/', '')
        else:
            path = './'
        return button(path)
    else:
        raise exceptions.PreventUpdate("cancel the callback")

def parse_contents(contents, filename, date, path):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')
    f = open(f'{path}{filename}', 'w', encoding='utf-8')
    f.write(f'{decoded}')
    f.close()
    return html.Div([
        html.H5(f'Файл {filename} успешно загружен'),
        html.H6(f'Последняя загрузка файла {datetime.datetime.fromtimestamp(date)}'),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
    ])

@callback(Output('output-image-upload', 'children'),
              Output('current_dir_holder', 'children', allow_duplicate=True),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'),
              State('current_dir', 'value'),
              config_prevent_initial_callbacks=True)
def update_output(list_of_contents, list_of_names, list_of_dates, path):
    if list_of_contents is not None:
        children = [
            parse_contents(contents, names, dates, path) for contents, names, dates in
            zip(list_of_contents, list_of_names, list_of_dates)]
        updater = button(path)
        return children, updater


def file_uploader():
    layout = html.Div([
        html.Div(id='mkdir_dialog'),
        html.Div(button('./'), id='current_dir_holder'),
        html.Div(id='file_manager'),
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Перетащите сюда файл ',
                html.A('или выберите его')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-image-upload'),
    ], className='FileManager')
    return layout



