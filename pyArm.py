'''
    File name: pyArm.py
    Author: Ardavan Bidgol
    Date created: 04/--/2021
    Date last modified: 08/10/2021
    Python Version: 3.7.7
    License: MIT
'''
##########################################################################################
###### Import 
##########################################################################################
import dash
# import dash_core_components as dcc
from dash import dcc
from dash import html
# import dash_html_components as html
import plotly.express as px
# from dash_html_components.P import P
from dash.dependencies import Input, Output, State
#import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.CardBody import CardBody

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px
# import cairosvg
from io import BytesIO


import numpy as np
from numpy.core.fromnumeric import size

import serial 

import re
import base64
import io
import os
import platform
import json
import argparse
import webbrowser
import threading
import time

from src.pydexarm import Dexarm
from src.josn_interface import Drawing_processor
from axisParser import generate_drawing_json as generate_drawing_json
from axisParser import letter_coordinates as letter_coordinates
from textGenerator import request_openai as request_openai


######################################################################
### Arguments
######################################################################
parser = argparse.ArgumentParser(prog='Робо-рука',
                                description="A Dash app to communicate with Rotric Robotic Arms")
parser.add_argument('-mode', 
                        help="Run the App in \"debug\", \"local\", or \"remote\" mode (str)", 
                        default= "debug",
                        nargs='?',
                        type=str)

args = parser.parse_args()
mode_selection = args.mode
isTrue = False  # Initialize the boolean variable

##########################################################################################
###### Global Variables
##########################################################################################
port = "COM5"

print(platform.uname().system)

mac_port = "/dev/tty.usbmodem3068365D30311"

if platform.uname().system == "Darwin":
    port = mac_port    

arm = None

path_data = None

json_drawing_data = None

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8050/")


#######################
## Default variables
#######################
z_val = -64
z_val_adjusted = z_val + 0

scale = 25
x_offset = 0
y_offset = 250
x_default = 0
y_default = 300
z_clear_height = -61

pressure_factor = 5

default_JSON_file_Path = "path_data.json"

dp = Drawing_processor(base_z = z_val, safe_z_val = z_clear_height, slider = False)

##########################################################################################
###### The app!
##########################################################################################
external_stylesheets=[dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##########################################################################################
###### Initial GUI setup
##########################################################################################
def init_canvas():
    """
    Making the initial canvas
    """
    img = np.ones(shape=(140*scale,160*scale,3))*220.
    fig = px.imshow(img, binary_string=True)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(dragmode="drawopenpath",
                    newshape_line_color='black',
                    newshape_line_width = 3,
                    )
    return fig

config = {"modeBarButtonsToAdd": [
                                "drawopenpath",
                                "eraseshape",
                                ]}

def insert_square_as_layer(fig, center_x, center_y, size):
    """
    Function to add a square as an SVG layer to the figure.
    """
    half_size = size / 2
    x0 = center_x - half_size
    y0 = center_y - half_size

    # Define the SVG square as a string
    square_svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
        <rect x="0" y="0" width="{size}" height="{size}"
              style="fill:none;stroke:black;stroke-width:3" />
    </svg>
    """

    # Overlay the SVG as an image layer
    fig.add_layout_image(
        dict(
            source=f"data:image/svg+xml;base64,{square_svg.encode('utf-8').hex()}",
            x=x0,
            y=y0 + size,
            xref="x",
            yref="y",
            sizex=size,
            sizey=size,
            xanchor="left",
            yanchor="bottom",
            layer="above"
        )
    )

    return fig

# Initialize the canvas
fig = init_canvas()

# Adjust for the scale factor
scale = 23
center_x = 4000 // 2  # Center X at 2000
center_y = 3500 // 2  # Center Y at 1750
size = 50 * 10  # Adjust the size based on the scale factor

# Insert a square as an SVG layer centered at (2000, 1750) with scaled size
# fig = insert_square_as_layer(fig, center_x=center_x, center_y=center_y, size=size)



##########################################################################################
###### Cards
##########################################################################################
header_card = dbc.Card([
    dbc.CardBody([
        html.Div([
            html.Img(src="/assets/logo.png", height="60px", style={"float": "left", "margin-right": "10px"}),  # Line 178: Insert this line
            html.H1("Робо-рука", className="card-title", style={"display": "inline-block"}),  # Line 179: Modify this line
        ]),
        html.Hr(),
        html.P("Создано Максимом Никифоровым, v.0.1.2, 2024")
    ])
])

drawing_tabs = dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Tabs(
                                [
                                    dbc.Tab([
                                                html.Br(),
                                                html.H3("Центр рисования"),
                                                html.P("Рисуйте используя трекпад или мышь вашего устройства на холсте ниже"),
                                                dcc.Graph(
                                                        id="graph_pic", 
                                                        figure=fig, config=config,
                                                        style={'width': '100%',
                                                                'height':"800px",
                                                                'visibility':'visible'},
                                                        ),
                                                html.Br(),
                                                dbc.Checklist(
                                                        options=[
                                                            {"label": "Вписать текст", "value": 1},
                                                        ],
                                                        value=[],
                                                        id="slider_ai",
                                                        inline= True,
                                                        switch=True,
                                                    ),   
                                                html.Br(),
                                                html.Div(id='text_input_container', children=[
                                                    dbc.Input(id='text_input', placeholder="Введите текст...", type="text")
                                                ], style={'display': 'none'}),  # Initially hidden
                                                html.Br(),
                                                dbc.Button(id='draw_now_canvas', 
                                                            children= "Рисовать", 
                                                            color="dark",
                                                            block=True, 
                                                            className="mr-1"),     
                                                html.Br(), 
                                                dbc.Button(id='clear_draw', 
                                                            children= "Очистить холст", 
                                                            # color="dark",
                                                            block=True, 
                                                            className="mr-1"),  
                                                
                                                html.Br(), 
                                                html.Hr(),            
                                                html.P("", id="annotations-data-pre"),                                           
                                            ],
                                            label="Рисование", 
                                            tab_id="drawing_tab"),

                                    dbc.Tab([
                                                html.Br(),
                                                html.H3("Draw from a JSON File"),
                                                html.P("Load a JSON file and hit Draw Now"),
                                                dcc.Upload(
                                                            id="json_upload", 
                                                            children= [html.A('Drag and Drop JSON File Here')],
                                                            style= {'borderStyle': 'dashed',
                                                                    'borderRadius': '5px',
                                                                    'color': '#343a40', 
                                                                    'borderColor': '#aaa', 
                                                                    # 'backgroundColor': '#343a40',
                                                                    'height': "60px",
                                                                    'lineHeight': '60px',
                                                                    'textAlign': 'center',
                                                                    },
                                                            ),
                                                html.Br(),
                                                dbc.Button(id='draw_now_JSON', 
                                                            children= "Draw Now", 
                                                            color="dark",
                                                            block=True, 
                                                            className="mr-1"),     
                                                html.Br(), 
                                                dcc.Graph(
                                                        id="graph_json", 
                                                        figure=fig, config=config,
                                                        style={'width': '1000px',
                                                                'height':"800px",
                                                                'visibility':'hidden'},
                                                        ),
                                                html.P("", id="json_upload_detail"),
                                                html.Br(),
                                                
                                            ],
                                            label="Загрузка файла", 
                                            tab_id="loading_tab",),        
                                ],
                                id="card_tabs",
                                card=True,
                                active_tab="drawing_tab",
                            )
                        ),
                        dbc.CardBody(html.P(id="card-content", className="card-text")),
                    ]
                )
controls_card = dbc.Card([
                        dbc.CardBody([
                                html.H6("Центр подключения", className="card-title"),
                                html.Hr(),
                                dbc.Row([
                                    dbc.Col([
                                            dbc.Button(id='robot_connect', 
                                                        children= "Подключить робота", 
                                                        color="dark", 
                                                        block=True,
                                                        className="mr-1"),   
                                            html.P("Робот ожидает подключения", id="robot_status"),
                                            html.Br(),
                                            html.Hr(),
                                            dbc.Checklist(
                                                        options=[
                                                            {"label": "Использовать слайдер", "value": 1},
                                                            {"label": "Инициализировать слайдер", "value": 2},
                                                        ],
                                                        value=[],
                                                        id="slider_toggle",
                                                        inline= True,
                                                        switch=True,
                                                    ),

                                            html.P("", id="slider_toggle_status"),
                                            html.Br(),
                                            html.Hr(),
                                            dbc.Button(id='robot_disconnect', 
                                                        children= "Прервать соединение", 
                                                        color="dark", 
                                                        block=True,
                                                        className="mr-1"),   
                                            
                                            html.P("", id="robot_disconnect_status"),
                                            html.Br(),
                                            html.Hr(),
                                            dbc.DropdownMenu(
                                                            id="port_name",
                                                            label="Порт",
                                                            children=[
                                                                    dbc.DropdownMenuItem(id='COM1', children="COM1"),
                                                                    dbc.DropdownMenuItem(id='COM3', children="COM3"),
                                                                    dbc.DropdownMenuItem(id='COM5', children="COM5"),
                                                                    dbc.DropdownMenuItem(id='MAC', children="MAC"),
                                                                    ],
                                                            color="dark", 
                                                            className="mr-1"),
                                            html.P("", id="port_status"),
                                            ]),
                                         ])
                                    ])
                        ])

calibration_card = dbc.Card([
                            dbc.CardBody([
                                        html.H6("Добавление высоты", className="card-title"),
                                        html.Hr(),
                                        dbc.Row([
                                            dbc.Col([
                                                    dbc.Button(id='touch_paper', 
                                                                children= "Докоснуться до холста", 
                                                                color="dark",
                                                                block=True, 
                                                                className="mr-1"),   
                                                    html.Br(),
                                                    html.P("", id="touch_paper_status"),

                                                    html.Hr(),
                                                    dcc.Slider(id="z_adjust",
                                                                min = -5,
                                                                max = 5,
                                                                value =0,
                                                                step = .25),
                                                    html.P(id="z_adjust_status", children= "Смещение: 0"),
                                                    
                                                    html.Hr(),
                                                    dcc.Slider(id="pressure_factor",
                                                                min = 0,
                                                                max = 20,
                                                                value = pressure_factor,
                                                                step = .1),
                                                    html.P(id="pressure_factor_status", children= "Давление: -5"),

                                                    html.Hr(),
                                                    dbc.Button(id='stop', 
                                                                children= "Экстренная остановка", 
                                                                color="danger",
                                                                block=True, 
                                                                className="mr-1"),   
                                                    html.Br(),
                                                    html.P("", id="stop_status"),
                                                    ])
                                                ])
                                        ])
                            ])

control_cards_deck =  dbc.Card([
                                dbc.CardBody([
                                                html.H4("Контрольная панель", className="card-title"),
                                                dbc.CardDeck([
                                                            dbc.Col([controls_card]),
                                                            dbc.Col([calibration_card]),
                                                            # dbc.Col([]),
                                                            ]),
                                                html.P("", id='draw_now_status'),
                                            ]),
                                ])
                                
##########################################################################################
###### Ok, let's assemble the layout
##########################################################################################
app.layout = dbc.Container([  
                            html.Br(),  
                            header_card,
                            html.Br(),
                            control_cards_deck,
                            html.Br(),
                            drawing_tabs,
                            ])
                            
##########################################################################################
###### Callbacks
##########################################################################################
@app.callback(
    Output('text_input_container', 'style'),
    [Input('slider_ai', 'value')]
)
def toggle_text_input(value):
    global isTrue
    if value:  # If the checklist is checked
        isTrue = True
        return {'display': 'block'}  # Show the input field
    else:
        isTrue = False
        return {'display': 'none'}  # Hide the input field


# @app.callback(
#     Output('lowercase_store', 'data'),
#     Input('text_input', 'value')
# )
# def convert_to_lowercase(input_text):
#     if input_text:
#         lowercase_text = input_text.lower()
#         return lowercase_text
#     return ''  # Return empty string if input is empty

@app.callback(
                Output('stop_status', 'children'),
                Input('stop', 'n_clicks'),
                prevent_initial_call=True)
def clear_drawing_canvas(value):
    arm._send_cmd("G4")
    return "Рука остановлена"

@app.callback(
                Output('graph_pic', 'figure'),
                Input('clear_draw', 'n_clicks'),
                prevent_initial_call=True)
def clear_drawing_canvas(value):
    """
    Clears the drawing canvas
    """
    global default_JSON_file_Path, path_data
    print(f"path_data is {path_data}")
    dp.reset_JSON_file(json_path = default_JSON_file_Path)
    tmp_fig = init_canvas()
    print(f"path_data is {path_data}")
    path_data = None
    return tmp_fig


@app.callback([
                Output('json_upload_detail', 'children'),
                Output('graph_json', 'style'),
                Output('graph_json', 'figure')],
                Input('json_upload', 'contents'),
                State('json_upload', 'filename'),
                State('json_upload', 'last_modified'),
                prevent_initial_call=True)
def json_file_upload(contents, file_names, dates):
    """
    Reads a JSON file from disk and saves it in the default path
    The goal is to keep that file over there for the Draw JSON 
    Function to read and draw it.
    
    Args:
    ontents, file_names, dates: inputs from the Dash UI
    """
    global arm, dp
    global default_JSON_file_Path
    if contents is not None:
        msg = "{} is loaded".format(file_names)
        print (msg)
        try:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            data =decoded.decode('utf-8')
            data = str(data)
        except:
            print ("Couldn\'t read the JSON file")

        dp.write_dic_to_json_file(data, default_JSON_file_Path)

        fig = quick_draw_graph(default_JSON_file_Path)
        return (html.Div([html.Pre(data)]), {'visibility': 'visible'}, fig)

    return "No file is loaded yet"

@app.callback(
    Output("port_status", "children"),
    [Input("COM1", "n_clicks"),
    Input("COM3", "n_clicks"),
    Input("COM5", "n_clicks"),
    Input("MAC", "n_clicks")]
)
def set_com_port(c1, c3, c5, mac):
    """
    Sets the active port to connect to the robot
    For Ubuntu (Raspberry Pi, find the exact name of port i.e.: '/dev/ttyACM0')
    """
    global port, mac_port 

    ctx = dash.callback_context
    if not ctx.triggered:
        return "Active port: {}".format(port)
    else:
        port = ctx.triggered[0]["prop_id"].split(".")[0] 
        print (port)
        if port == "MAC":
            port = mac_port
        return "Active port: {}".format(port)

################################
###### Connect/Disconnect ######
################################
@app.callback(
    Output('robot_status', 'children'),
    Input('robot_connect', 'n_clicks'),
    prevent_initial_call=True, 
)
def connect_robot(value):
    """
    Initializes the serial connection with the robot.
    """
    global arm, port
    global x_default, y_default

    if value == 0:
        return "Nothing is clicked"

    else:
        print ("Contacting the robot for the {}th time!".format(value))

        arm = Dexarm(port=port)
        arm.go_home()
        arm.set_module_type(0)
        arm.move_to(x_default, y_default, z_clear_height+ 10)
        arm.go_home()
        x, y, z, e, a, b, c = arm.get_current_position()
        message = "x: {}, y: {}, z: {}, e: {}\na: {}, b: {}, c: {}".format(x, y, z, e, a, b, c)

        data = html.Div([html.P("Робот подключен к порту {}".format(port)),
                        html.Br(),
                        html.P(message)])
        return data


@app.callback(
    Output('robot_disconnect_status', 'children'),
    Input('robot_disconnect', 'n_clicks'),
    prevent_initial_call=True, 
)
def disconnect_arm(value):
    """
    Disconnects the robot serial connection.
    """
    global arm 

    if value == 0:
        return ""
    else:
        if arm is not None:
            if arm.ser.is_open:
                arm.go_home()
            arm.close()
            arm = None
            return "Робот отключен"
        else:
            return "No arm is available"

@app.callback(
    Output("slider_toggle_status", "children"),
    Input("slider_toggle", "value"),
    prevent_initial_call=True, 
)
def init_slider(slider_toggle_val):
    """
    Initializes the slider track if a robot exist and connected
    """
    global arm 

    print (slider_toggle_val)

    if 1 in slider_toggle_val:
        print ("Using slider")
        dp.slider = True
        
    else:
        dp.slider = False
        return "Слайдер не ипользуется"

    if 2 in slider_toggle_val:
        if arm is not None:
            print ("arm is not None")
            if arm.ser.is_open:
                print ("arm.ser is open")
                print ("going home")
                arm.go_home()
                print ("initing rail")
                arm.sliding_rail_init()
                dp.slider = True
                print ("done with slider start!")
                return "Slider is initiated and in use"
        
    return "Слайдер используется"
    

#################################
########## Adjustments ##########
#################################
@app.callback(
    Output("z_adjust_status","children"),
    Input("z_adjust", 'value'),
    prevent_initial_call=True, 
)
def adjust_z_val(value):
    """
    Reads the value from z_adjust slider (offset value) and changes the 
    z_val (the height where the paper is located). Also moves the robot
    to show the user the new z_val.
    """
    global z_val, z_val_adjusted 
    global arm, dp

    z_val_adjusted = z_val + value 

    if dp.slider:
        arm.move_to(e= 0, y= y_default, z= z_val_adjusted)
    else:
        arm.move_to(0, y_default, z_val_adjusted)
    dp.base_z = z_val_adjusted

    return "Z: {}, Offset: {}".format (z_val_adjusted, value)

@app.callback(
    Output("pressure_factor_status","children"),
    Input("pressure_factor", 'value'),
    prevent_initial_call=True, 
)
def adjust_pressure_factor(value):
    """
    Reads the value from pressure_factor slider (Pressure factor) and Changes 
    the pressure range between the lower and highest pressure
    """
    global pressure_factor 
    global arm, dp

    pressure_factor = -value
    dp.pressure_factor = pressure_factor
    if dp.slider:
        arm.move_to(e= 0, y= y_default, z= z_val_adjusted+pressure_factor)
        arm.dealy_s(0.5)
        arm.move_to(e= 0, y= y_default, z= z_val_adjusted-pressure_factor)
        arm.dealy_s(0.5)
        arm.move_to(e= 0, y = y_default, z= z_val_adjusted)

    else:
        arm.move_to(0, y_default, z_val_adjusted+pressure_factor)
        arm.dealy_s(0.5)
        arm.move_to(0, y_default, z_val_adjusted-pressure_factor)
        arm.dealy_s(0.5)
        arm.move_to(0, y_default, z_val_adjusted)

    return "Pressure: {}".format (pressure_factor)

@app.callback(
    Output('touch_paper_status', 'children'),
    Output('touch_paper', 'children'),
    Input('touch_paper', 'n_clicks'),
    prevent_initial_call=True, 
)
def adjust_marker(value):
    """
    Forces the robot to touch the z_val, user can use this function
    to adjust its marker or pen height.
    """
    global arm
    global z_val, z_val_adjusted, x_default, y_default

    if value == 0:
        return "Marker not adjusted", dash.no_update

    elif arm:
        if value%2 == 1:
            # on odd clicks the robot touch the paper
            if dp.slider:
                arm.move_to(e= x_default, y= y_default, z= z_val_adjusted)
            else:
                arm.move_to(x_default, y_default, z_val_adjusted)
            return "Adjust the marker", "Вернуться на исходную позицию"
        else:
            # on even clicks the robot comes back to normal height
            if dp.slider:
                arm.move_to(e= x_default, y= y_default, z= z_clear_height)
            else:
                arm.move_to(x_default, y_default, z_clear_height)
            return "", "Докоснуться до бумаги"
    else:
        return "Робо-рука не подключена", dash.no_update


##########################################################################################
###### Drawing
##########################################################################################
@app.callback(
    Output('draw_now_status', 'children'),
    [Input('draw_now_canvas', 'n_clicks'),
     Input('draw_now_JSON', 'n_clicks')],
    [State('text_input', 'value')],
    prevent_initial_call=True
)
def draw_now(value_graph, value_JSON, text_input_value):
    """
    Reads the saved JSON file in the default path and draws it
    """
    # global isTrue
    # ctx = dash.callback_context
    global path_data
    lowercased_text = text_input_value.lower() if text_input_value else ""
    print("S'IL VOUS PLAÎTE !!!!")

    # if draw != "Информация сохранена в json файл":
    if path_data == None:
        print(lowercased_text)

        if isTrue:
            generate_drawing_json(add_new_line(lowercased_text), letter_coordinates)
            print("HumanWritten text")

        else:
            request_openai(add_line=add_new_line)
            

    global arm, dp
    global default_JSON_file_Path

    polyLines = dp.extract_ploylines(default_JSON_file_Path)
    dp.draw(arm, polyLines)

    return ("Drawing copmleted")

def add_new_line(lowercasedText):
    spaceCounter = 0
    newMessage = []
    for char in lowercasedText:
        if char == " ":
            spaceCounter += 1
            if spaceCounter % 2 == 0:
                newMessage.append("/")
                continue
        newMessage.append(char)

    return ''.join(newMessage)                   

def quick_draw_graph(json_path= None):
    """
    Reads a JSON file from a given path and plots it in a graph object
    """
    global dp
    global default_JSON_file_Path

    if json_path is None:
        json_path = default_JSON_file_Path

    polyLines = dp.extract_ploylines(json_path=json_path)
    
    xs=[]
    ys=[]
    colors = []

    for c, pl in enumerate(polyLines):
        for target in pl:
            xs.append(target[0])
            ys.append(target[1])
            colors.append(c)

    fig = px.line(x=xs, y=ys, color=colors)

    fig.update_xaxes(range=[0, 1000])
    fig.update_yaxes(range=[0, 500], 
                    scaleanchor = "x",
                    scaleratio = 1)

    return fig




@app.callback(
    Output("annotations-data-pre", "children"),
    Input("graph_pic", "relayoutData"),
    prevent_initial_call=True,
)
def draw(relayout_data):
    global arm
    global path_data
    global z_val, z_val_adjusted, x_offset, y_offset
    global default_JSON_file_Path
    
    wait_key = True
    
    drawing_dic = {"drawing": {"strokes":[]}}

    drawing_dic["drawing"]["strokes"]

    if "shapes" in relayout_data:
        path_data = relayout_data["shapes"]
        
        if type(path_data) is 'list':
            print (relayout_data["shapes"][0]['path'])
        
        else:
            print ("Number of strokes:", len(path_data))
            data =  relayout_data["shapes"]
            # refer to https://plotly.com/python/reference/layout/shapes/#layout-shapes-items-shape-path
            # and: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
            # M: Move to
            # L: line to gets X and Y and draws a line from here to there!   
 
            for i, d in enumerate(data):
                tmp_path = []
                # iterating over pathes
                d_tmp = d['path']
                d_tmp = re.split(r'[, M L Z]\s*', d_tmp)[1:]
                d_tmp = [float(d) for d in d_tmp]

                targets = np.array(d_tmp)
                x = (4000 - targets[::2])/scale + x_offset
                y = targets[1::2]/scale + y_offset
                
                for i in range (x.shape[0]):
                    x_loc = x[i]
                    y_loc = y[i]
                    tmp_target = {"x": x_loc, "y": y_loc, "a": 0, "p": 0.0}
                    tmp_path.append(tmp_target)
                drawing_dic["drawing"]["strokes"].append(tmp_path)
            
            json_data = json.dumps(drawing_dic, indent = 4)
            dp.write_dic_to_json_file(json_data, default_JSON_file_Path)

        return "Информация сохранена в json файл"
    
    # if json_data != None:
    else:
        return "Холст пуст"


# if __name__ == "__main__":
#     app.run_server(debug=True)
    # app.run_server(debug=False)
    # app.run_server(debug= False , port=8080, host='0.0.0.0')

######################################################################
### Dash App Running!
######################################################################
mode_options = {'debug':'d', 'local':'l', 'remote':'r'}

if __name__ == '__main__':
        mode = mode_options[mode_selection]
        if mode == 'd':
                # for test and debug
                threading.Thread(target=open_browser).start()
                app.run_server(debug=True)
        
        elif mode == 'l':
                # to run on local device
                threading.Thread(target=open_browser).start()
                app.run_server(debug=False)

        elif mode == 'r':
                """
                To run and access it over network
                Access it over network on Chrome at:
                server_ip:8080
                i.e.: 192.168.86.34:8080
                """
                app.run_server(debug=False, port=8050, host='0.0.0.0')