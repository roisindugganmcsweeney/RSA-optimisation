from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_table.Format import Format, Scheme, Group


def editable_input_table(df):
    editable_input = html.Div([
        dash_table.DataTable(
            id="editable-input-table",
            data=df.to_dict('records'),  # the contents of the table
            columns=[
            #     {"name": i, "id": i, "deletable": False,
            #      "selectable": True, "hideable": True, 'renamable': True}
            #     if i != "index" and i != "centre"
            #     else {"name": i, "id": i, "deletable": False,
            #           "selectable": True, "hideable": False, 'renamable': False}
            #     for i in df.columns
                {
                    'id': 'index',
                    'name': 'index',
                    'type': 'numeric',
                    'format': Format(
                        precision=0,
                        scheme=Scheme.fixed,

                    ),
                    'editable': False,
                },
                {
                    'id': 'centre',
                    'name': 'centre',
                    'type': 'text',

                },
                {
                    'id': 'minBooths',
                    'name': ''
                            ''
                            'minBooths',
                    'type': 'numeric',
                    'format': Format(
                        precision=0,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'maxBooths',
                    'name': 'maxBooths',
                    'type': 'numeric',
                    'format': Format(
                        precision=0,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'maxDays',
                    'name': 'maxDays',
                    'type': 'numeric',
                    'format': Format(
                        precision=0,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'vaxHours',
                    'name': 'vaxHours',
                    'type': 'numeric',
                    'format': Format(
                        precision=2,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'workingHours',
                    'name': 'workingHours',
                    'type': 'numeric',
                    'format': Format(
                        precision=2,
                        scheme=Scheme.fixed,
                    )
                },                 {
                    'id': 'reqDose',
                    'name': 'reqDose',
                    'type': 'numeric',
                    'format': Format(
                        precision=2,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'vph',
                    'name': 'vph',
                    'type': 'numeric',
                    'format': Format(
                        precision=2,
                        scheme=Scheme.fixed,
                    )
                },
                {
                    'id': 'catchment',
                    'name': 'catchment',
                    'type': 'numeric',
                    'format': Format(
                        precision=0,
                        scheme=Scheme.fixed,
                        group=Group.yes,
                        groups=3,
                        group_delimiter=',',
                        decimal_delimiter='.',

                    )
                },
                {
                    'id': 'enabled',
                    'name': 'enabled',
                    'type': 'text'
                },
                {
                    'id': 'flex',
                    'name': 'flex',
                    'type': 'text'
                },
                {
                    'id': 'lat',
                    'name': 'lat',
                    'type': 'numeric',
                    'format': Format(
                        precision=4,
                        scheme=Scheme.fixed,

                    )
                },
                {
                    'id': 'lon',
                    'name': 'lon',
                    'type': 'numeric',
                    'format': Format(
                        precision=4,
                        scheme=Scheme.fixed,
                    )
                }
            ],
            fixed_columns={'headers': True, 'data': 2},
            editable=True,  # allow editing of data inside all cells
            #filter_action="native",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            #column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            #row_selectable="multi",  # allow users to select 'multi' or 'single' rows
            row_deletable=True,  # choose if user can delete a row (True) or not (False)
            #selected_columns=[],  # ids of columns that user selects
            #selected_rows=[],  # indices of rows that user selects
            page_action="native",  # all data is passed to the table up-front or not ('none')
            #page_current=1,  # page number that user is on
            page_size=10,  # number of rows visible per page
            style_cell={  # ensure adequate header width when text is shorter than cell's text
                'minWidth': 100, 'maxWidth': 200, 'padding': '5px', 'fontSize':14, 'font-family':'arial'
            },
            style_table={'overflowX': 'auto', 'minWidth': '100%'},
            style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['centre', 'enabled', 'flex']
            ],
            style_data={  # overflow cells' content into multiple lines
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'lightgrey',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {
                        'state': 'active'  # 'active' | 'selected'
                    },
                    'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                    'border': '1px solid rgb(0, 116, 217)'
                },

                # highlight invalid data input
                {
                    'if': {
                        'column_id': 'centre',
                        'filter_query': '{centre} = ""'
                    },
                    'backgroundColor': '#FF4136',
                },

                {
                    'if': {
                        'column_id': 'minBooths',
                        'filter_query': '{minBooths} = "" || {minBooths} < 0 || {minBooths} contains "."'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'maxBooths',
                        'filter_query': '{maxBooths} = "" || {maxBooths} < 0 || {maxBooths} < {minBooths} || {maxBooths} contains "."'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'maxDays',
                        'filter_query': '{maxDays} = "" || {maxDays} < 0 || {maxDays} > 7 || {maxDays} contains "."'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'vaxHours',
                        'filter_query': '{vaxHours} = "" || {vaxHours} < 0 || {vaxHours} > 24'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'workingHours',
                        'filter_query': '{workingHours} = "" || {workingHours} < 0 || {workingHours} > 24'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'reqDose',
                        'filter_query': '{reqDose} = "" || {reqDose} < 0 || {reqDose} contains "."'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'vph',
                        'filter_query': '{vph} = "" || {vph} < 0'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'catchment',
                        'filter_query': '{catchment} = "" || {catchment} < 0 || {catchment} contains "."'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'enabled',
                        'filter_query': '{enabled} = ""'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'flex',
                        'filter_query': '{flex} = ""'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'lat',
                        'filter_query': '{lat} = "" || {lat} < -90 || {lat} > 90'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'lon',
                        'filter_query': '{lon} = "" || {lon} < -180  || {lon} > 180'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
            ],
            tooltip_conditional=[
                # tooltip for invalid data input
                {
                    'if': {
                        'column_id': 'centre',
                        'filter_query': '{centre} = ""'
                    },
                    'type': 'markdown',
                    'value': '"centre" must be a unique string'
                },

                {
                    'if': {
                        'column_id': 'minBooths',
                        'filter_query': '{minBooths} = "" || {minBooths} < 0 || {minBooths} contains "."'
                    },
                    'type': 'markdown',
                    'value': '"minBooths" must be a non-negative integer'
                },
                {
                    'if': {
                        'column_id': 'maxBooths',
                        'filter_query': '{maxBooths} = "" || {maxBooths} < 0 || {maxBooths} < {minBooths} || {maxBooths} contains "."'
                    },
                    'type': 'markdown',
                    'value': '"minBooths" must be an integer no less than "maxBooths"'
                },
                {
                    'if': {
                        'column_id': 'maxDays',
                        'filter_query': '{maxDays} = "" || {maxDays} < 0 || {maxDays} > 7 || {maxDays} contains "."'
                    },
                    'type': 'markdown',
                    'value': '"maxDays" must be an integer between 0 and 7'
                },
                {
                    'if': {
                        'column_id': 'vaxHours',
                        'filter_query': '{vaxHours} = "" || {vaxHours} < 0 || {vaxHours} > 24'
                    },
                    'type': 'markdown',
                    'value': '"vaxHours" must be an integer or float between 0 and 24'
                },
                {
                    'if': {
                        'column_id': 'workingHours',
                        'filter_query': '{} = "workingHours" || {workingHours} < 0 || {workingHours} > 24'
                    },
                    'type': 'markdown',
                    'value': '"workingHours" must be an integer or float between 0 and 24'
                },
                {
                    'if': {
                        'column_id': 'reqDose',
                        'filter_query': '{} = "reqDose" || {reqDose} < 0 || {reqDose} contains "."'
                    },
                    'type': 'markdown',
                    'value': '"reqDose" must be a non-negative integer'
                },
                {
                    'if': {
                        'column_id': 'vph',
                        'filter_query': '{} = "vph" || {vph} < 0'
                    },
                    'type': 'markdown',
                    'value': '"vph" must be a non-negative integer or float'
                },
                {
                    'if': {
                        'column_id': 'catchment',
                        'filter_query': '{} = "catchment" || {catchment} < 0 || {catchment} contains "."'
                    },
                    'type': 'markdown',
                    'value': '"catchment" must be a non-negative integer'
                },
                {
                    'if': {
                        'column_id': 'lat',
                        'filter_query': '{} = "lat" || {lat} < -90 || {lat} > 90'
                    },
                    'type': 'markdown',
                    'value': '"lat" must be an integer or float between -90 and 90'
                },
                {
                    'if': {
                        'column_id': 'lon',
                        'filter_query': '{} = "lon" || {lon} < -180  || {lon} > 180'
                    },
                    'type': 'markdown',
                    'value': '"lon" must be an integer or float between -180 and 180'
                },
                {
                    'if': {
                        'column_id': 'enabled',
                        'filter_query': '{enabled} = "" || {enabled} != "True" || {enabled} != "False"'
                    },
                    'type': 'markdown',
                    'value': '"enabled" must be either "True" or "False"'
                },
                {
                    'if': {
                        'column_id': 'flex',
                        'filter_query': '{flex} = ""  || {flex} != "True" || {flex} != "False"'
                    },
                    'type': 'markdown',
                    'value': '"flex" must be either "True" or "False"'
                },

            ],
        ),
        html.Div(dbc.Button('Add Row', id='adding-rows-button', n_clicks=0,
                   color='secondary', outline=True))
    ])
    return editable_input