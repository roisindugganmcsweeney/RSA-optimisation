from dash import dcc

def slide():
    slider = dcc.Slider(
        id='my-slider',
        min=1764,
        max=59850,
        step=1,
        value=30807,
    )
    return slider