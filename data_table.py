from dash import html
from dash import dash_table
from dash_table.Format import Format, Scheme, Group

def table(df):
    datatable = html.Div(
        dash_table.DataTable(
            id='info-table',
            columns=[{
                         'id': x,
                         'name': x,
                         'type': 'numeric',
                          'format': Format(
                              precision=0,
                              scheme=Scheme.fixed,
                              group=Group.yes,
                              groups=3,
                              group_delimiter=',',
                              decimal_delimiter='.',
                          )
                      }
                if x not in ['Centre Name']
                else
                     {
                         'id': x,
                         'name': x,
                         'type': 'text',
                     }
                     for x in df.columns
            ],
            data=df.to_dict('records'),  # the contents of the table
            fixed_columns={'headers': True, 'data': 1},
            filter_action="native",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            page_action="native",  # all data is passed to the table up-front or not ('none')
            page_current=1,  # page number that user is on
            page_size=10,  # number of rows visible per page
            style_table={'overflowX': 'auto', 'minWidth': '100%'},
            style_as_list_view=True,
            style_cell={'padding': '5px', 'fontSize':14, 'font-family':'arial'},
            style_data={  # overflow cells' content into multiple lines
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            style_data_conditional=[

                #set bold fontweight for the total row
                {
                    'if': {
                        'column_id': 'Centre Name',
                        'filter_query': '{Centre Name} = "Totals"',
                    },
                    'fontWeight': 'bold',
                },
                {
                    'if': {
                        'state': 'active'  # 'active' | 'selected'
                    },
                    'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                    'border': '1px solid rgb(0, 116, 217)'
                },
                # {
                #     'if': {
                #         'column_id': col,
                #         'filter_query': '{{{}}} == {}'.format(col, df[col].max())
                #     },
                #     'fontWeight': 'bold',
                # } for col in df.columns if col not in ['Centre Name']
            ],
            style_header={
                'backgroundColor': 'lightgrey',
                'fontWeight': 'bold'
            },
            export_format='xlsx',
            export_headers='display'
        )
    )
    return datatable