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

external_stylesheets = ['https://codepen.io/ziscore/pen/NWxVaxy.css', 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# server for gunicorn
server = app.server

app.layout = html.Div([
    html.H1("Sarayu: Chat Insights"),
    html.P("Upload a report generated by Verloop Platform. \
    You can upload any CSV file as long as it has a RecipeFlow column. \
    Tip: Make sure to filter only a single recipe to avoid messy diagrams", className="leadin"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'background-color': '#ffffff',
            'width': '600px',
            'margin': '0 auto',
            'padding': '20px',
            'border': '4px dashed #1FB264',
            'margin-bottom': '50px'
        },
    ),
    dcc.Graph(id='sankey')
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
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
            blocks, links = prepare_data_for_sankey(flow, dropoffs=True)
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
            width=2000,
            height=1200,
            font_size=14
        )
        return fig
    
    return error_graph("Please upload a file to see something here")

if __name__ == '__main__':
    app.run_server(debug=True)

