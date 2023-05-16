import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
from src.sankey import prepare_data_for_sankey, make_sankey

external_stylesheets = ['https://codepen.io/ziscore/pen/jOqagow.css', 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# server for gunicorn
server = app.server

# SAMPLE CONSTANT
MAX_SAMPLES = 150
app.title = 'Sarayū: Chat Insights'

app.layout = html.Div([
    html.H1("Sarayū: Chat Insights"),
    html.P([
        "This is not a general purpose tool it is meant to be used with a specific format of chat reports. This server currently samples ~100 rows from dataframe for faster processing",
    ], className="leadin"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag & drop here or ',
            html.A('Select a file'), ' for upload'
        ]),
        style={
            'width': '600px',
            'margin': '0 auto',
            'padding': '20px',
            'border': '4px dashed #1FB264',
            'margin-bottom': '50px'
        },
        max_size=-1
    ),
    dcc.Graph(id='sankey', style={'width': '96vw', 'height': '100vh'}),
    html.Footer(["Made by Lunar Void (Udit & ", html.A("Shailendra", href="https://shailendra.me"), ")"], style={'padding-top': '5%'})
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # sample 150 rows if too many rows
        row = df.shape[0]
        if row > MAX_SAMPLES + 50:
            df_sampled = df.sample(n=MAX_SAMPLES) 
            return df_sampled
        
        return df
    else:
        raise TypeError

def error_graph(text):
    return {
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }

@app.callback(Output('sankey', 'figure'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    if contents:
        try:
            flow = parse_contents(contents, filename)
        except:
            er = "Did you upload the correct file? " + filename
            return error_graph(er)
        
        try:
            blocks, links = prepare_data_for_sankey(flow, dropoffs=False)
        except KeyError:
            er = f"The file you uploaded doesn't have the column 'RecipeFlow'. Try again with a different file?"
            return error_graph(er)
        except Exception as e:
            er = f"Something went wrong, see if this helps? {e}"
            return error_graph(er)

        fig = make_sankey(
            blocks=blocks, 
            links=links,
            title=filename,
            font_size=14
        )
        return fig
    
    return error_graph("upload a report to see something here")

if __name__ == '__main__':
    app.run_server(debug=True)

