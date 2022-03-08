import dash
from dash.dependencies import Input, Output, State
from page import html_page
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from build import build

# KPMG visual identity
kpmgBlue = '#00338D'
kpmgMediumBlue = '#005EB8'
kpmgLightBlue = '#0091DA'
kpmgViolet = '#483698'
kpmgPurple = '#470A68'
kpmgLightPurple = '#6D2077'
kpmgGreen = '#00A3A1'


df = pd.read_csv("centres.csv")
res = build(df, 30000)
#page layout, would normally have headers and footers here
def page(res):
    layout = html_page(res)
    return layout

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "HSE"}],
    external_stylesheets= [dbc.themes.BOOTSTRAP]
)

# initialise the server and configs
server = app.server

app.layout = page(res)

#all of our callbacks
# @app.callback(
#     Output('info-table','data'),
#     Input('button','nclicks')
# )
# def display_table(test):
#     return res.to_dict("records")


@app.callback(
    Output('editable-input-table', 'data'),
    #Output('editable-input-table', 'children')],
    Input('adding-rows-button', 'n_clicks'),
    #Input('editable-input-table', 'data_timestamp')],
    [State('editable-input-table', 'data'),
    State('editable-input-table', 'columns')]
)
def add_validate_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' if columns.index(c) != 0 else len(rows) for c in columns})

    # for row in rows[-n_clicks:]:
    #     if not (type(row['centre']) == str) or row['centre']== ""\
    #     or not (type(row['minBooths']) in {int, np.int64} and row['minBooths'] > 0)\
    #     or not (type(row['maxBooths']) in {int, np.int64} and row['maxBooths'] > row['minBooths'])\
    #     or not (type(row['maxDays']) in {int, np.int64} and row['maxDays'] >= 0 and row['maxDays'] <= 7)\
    #     or not (type(row['vaxHours']) in {int, np.int64, float} and row['vaxHours'] >= 0 and row['vaxHours'] <= 24)\
    #     or not (type(row['workingHours']) in {int, np.int64, float} and row['workingHours'] >= 0 and row['workingHours'] <= 24)\
    #     or not (type(row['reqDose']) in {int, np.int64} and row['reqDose'] >= 0)\
    #     or not (type(row['vph']) in {int, np.int64, float, np.float64} and row['vph'] >= 0)\
    #     or not (type(row['catchment']) in {int, np.int64} and row['catchment'] >= 0)\
    #     or not (row['enabled'] in {'true', 'false'})\
    #     or not (row['flex'] in {'true', 'false'})\
    #     or not (type(row['lat']) in {int, np.int64, float, np.float64} and row['lat'] >= -90 and row['lat'] <= 90)\
    #     or not (type(row['lon']) in {int, np.int64, float, np.float64} and row['lon'] >= -180 and row['lon'] <= 180):
    #         return dash.no_update

    return rows


@app.callback(
    [Output('slider-output', 'children'),
    Output('info-table','data'),
    Output('bar-chart', 'figure'),
    Output('pie-chart', 'figure')],
    [Input('my-slider', 'value'),
    Input('editable-input-table', 'data'),
    Input('editable-input-table', 'columns')],
)
def update_output(value, rows, columns):
    df = pd.DataFrame([[row.get(c['id'], None) for c in columns] for row in rows],
                      columns=[c['name'] for c in columns])
    #df = pd.DataFrame([[row.get(c['id'], None) for c in columns] for row in rows])

    res = build(df, value)

    # Make bar chart
    df1 = res[["Centre Name", "Booths Open"]]

    df1 = df1.rename({"Centre Name": "Centre", 'Booths Open': 'Open'}, axis=1)

    df2 = df[['centre', 'maxBooths']]
    df2 = df2.rename({'centre': 'Centre'}, axis=1)
    df2['Closed'] = df2['maxBooths'].subtract(df1['Open'])

    df = pd.merge(df1, df2, on='Centre')

    bar_fig = go.Figure()

    bar_fig.add_trace(go.Bar(x=df['Centre'],
                         y=df['Open'],
                         name='Open Booths',
                         marker_color=kpmgBlue))

    bar_fig.add_trace(go.Bar(x=df['Centre'],
                         y=df['Closed'],
                         name='Closed Booths',
                         marker_color=kpmgLightPurple))

    bar_fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 0)',
        title='Number of Open and Closed booths ',
        title_x=0.5,
        xaxis=dict(
            title='Centres',
            linecolor='rgba(0, 0, 0)',
            titlefont_size=16,
            tickfont_size=14
        ),
        yaxis=dict(
            title='Booths',
            linecolor='rgba(0, 0, 0)',
            titlefont_size=16,
            tickfont_size=14,
            range=(0, round(df['maxBooths'].max()*1.2, -1))
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    # Make pie chart

    df = res[["Centre Name", "Total Vaccines"]].iloc[:-1]


    pie_fig = px.pie(df, values="Total Vaccines", names="Centre Name",
                     color_discrete_sequence=[kpmgBlue, kpmgLightBlue,
                                              kpmgGreen,
                                              kpmgPurple, kpmgLightPurple,
                                              kpmgMediumBlue, kpmgViolet],
                     title='Allocated Percentage for Centres')

    return '{}'.format(value), res.to_dict("records"), bar_fig, pie_fig


# @app.callback(
#     dash.dependencies.Output('line-chart', 'figure'),
#     dash.dependencies.Input('info-table', 'data') #take in input from the datatable for now
# )
# def make_line_chart(input):
#
#     df = [{"day" :"Monday", "vaccines" : 10000},{"day" :"Tuesday", "vaccines" : 14000},{"day" :"Wednesday", "vaccines" : 18000},{"day" :"Thursday", "vaccines" : 22000},{"day" :"Friday", "vaccines" : 26000},{"day" :"Saturday", "vaccines" : 30000},{"day" :"Sunday", "vaccines" : 34000}]
#     df = pd.DataFrame(df)
#     fig = px.line(df, x="day", y="vaccines", title='Number of Vaccines Needed', range_y=[0,40000])
#     return fig


if __name__ == "__main__":
    app.run_server(debug=True,
                   dev_tools_ui=False,
                   use_reloader=False,
                   host="127.0.0.1",
                   port=8053)