from dash import html
import dash_bootstrap_components as dbc

# KPMG visual identity
LOGO = 'assets/KPMG_NoCP_White.png'
kpmgBlue = '#00338D'

# this example that adds a logo to the navbar brand
logo = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=LOGO, height="40px")),
                        dbc.Col(dbc.NavbarBrand("Resources Optimisation tool", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler2", n_clicks=0),
        ],
    ),
    color=kpmgBlue,
    dark=True,
    className="mb-5",
    fixed ='top'
)
