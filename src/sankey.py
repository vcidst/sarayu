import pandas as pd
import numpy as np
import plotly.graph_objects as go
from random import randint

def get_random_color():
    """ helper method to get a random color """
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    block = f"rgb({r}, {g}, {b})"
    link = f"rgba({r}, {g}, {b}, 0.3)"
    return block, link

def label_index(blocks, label):
    """ helper method to get index of an element """
    try:
        return blocks.Label.to_list().index(label)
    except:
        return -1

def prepare_data_for_sankey(flow, dropoffs = False):
    blocks = []
    for fl in flow['RecipeFlow']:
        blocks.append(fl.split(" -> "))

    flow['blocks'] = blocks

    block_labels = pd.DataFrame(columns=['Label', 'Color', 'ColorLink'])
    for userflow in flow.blocks:
        for b in userflow:
            if b not in block_labels.Label.to_list():
                c_b, c_l = get_random_color()
                row = {
                    "Label": b,
                    "Color": c_b,
                    "ColorLink": c_l
                }
                block_labels = block_labels.append(row, ignore_index=True)

    if dropoffs:
        row = {
            "Label": "Dropped Off",
            "Color": "#444444",
            "ColorLink": "rgba(70, 70, 70, 0.3)"
        }
        block_labels = block_labels.append(row, ignore_index=True)
        dropped_off = "Dropped Off"
    else:
        dropped_off = ""
    
    links = pd.DataFrame(columns=['Source', 'SourceInt', 'Target', 'TargetInt', 'Frequency', 'Color'])
    for userflow in flow.blocks:
        userflow_len = len(userflow)
        for i, block in enumerate(userflow):
            # end of array
            if i == (userflow_len-1):
                target = dropped_off
            # everywhere else
            else:
                target = userflow[i+1]
                
            # check if a row already exists with block name and target block name
            if ((links.loc[(links['Source'] == block) & (links['Target'] == target)].shape[0]) == 0):
                entry = {
                        'Source': block, 
                        'SourceInt': label_index(block_labels, block),
                        'Target': target, 
                        'TargetInt': label_index(block_labels, target),
                        'Frequency': 1,
                        'Color': block_labels.loc[block_labels['Label'] == block, 'ColorLink'].values[0]
                    }
                links = links.append(entry, ignore_index=True)
            else:
                links.loc[
                    (links['Source'] == block) & (links['Target'] == target), 
                    'Frequency'
                ] += 1

    # remove rows where Target is -1
    links_cleanup = links.query("TargetInt != -1")
    return block_labels, links_cleanup

def make_sankey(blocks, links, title, width, height, font_size):
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = blocks.Label,
            color = blocks.Color
        ),
        link = dict(
            source = links.SourceInt, # indices correspond to labels, eg A1, A2, A2, B1, ...
            target = links.TargetInt,
            value = links.Frequency,
            color = links.Color
        )
    )])

    fig.update_layout(title_text=title, autosize=False, width=width, height=height, font_size=font_size)
    return fig