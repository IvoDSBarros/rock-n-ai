# views/view8_media_flow.py
from dash import html, dcc
from utils import (FONT_FAMILY, NEUTRAL_100, NEUTRAL_800, NEUTRAL_300, BRAND_NAVY, VIEW_CONFIGS)
from utils.data_loader import get_guitarist_media_flow, get_guitarist_narrative, create_narrative_paragraphs
from components.charts import create_parallel_categories
from components.panels import create_ai_narrative_panel
from components.header import create_header

def create_media_flow_view(selected_guitarist, view_id=8):
    """Create media flow view."""
    config = VIEW_CONFIGS[view_id]
    
    # Get data
    par_cat_data = get_guitarist_media_flow(selected_guitarist)

    # Fallback approach
    if not par_cat_data:
        return html.Div("No data found for this guitarist", style={
            'backgroundColor': NEUTRAL_100,
            'height': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'color': NEUTRAL_800
        })
    
    # Get crew ai narrative
    narrative_paragraphs = get_guitarist_narrative(selected_guitarist, view_id=8)
    
    # Create HTML paragraphs for ai_content
    ai_content = create_narrative_paragraphs(narrative_paragraphs, selected_guitarist)

    return html.Div(style={
        'backgroundColor': NEUTRAL_100,
        'height': '100vh',
        'width': '100vw',
        'fontFamily': FONT_FAMILY,
        'color': NEUTRAL_800,
        'overflow': 'hidden',
        'display': 'flex',
        'flexDirection': 'column',
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0'
    }, children=[        
        create_header(
            view_id=view_id,
            selected_guitarist=selected_guitarist,
            show_live_indicator=True,
            show_view_status=True,
            enable_navigation=True
        ),
        # Main content area
        html.Div(style={
            'flex': '1',
            'padding': '12px',
            'display': 'flex',
            'gap': '12px',
            'overflow': 'hidden',
            'minHeight': '0'
        }, children=[
            # Left panel: AI narrative terminal (50% width)
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'minHeight': '0',
                'overflow': 'hidden'
            }, children=[
                create_ai_narrative_panel(view_id, ai_content)
            ]),
            # Right panel: parallel categories
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '12px',
                'height': '100%',
                'minHeight': '0',
                'overflow': 'hidden'
            }, children=[
                html.Div(style={
                    'background': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'flex': '1',
                    'minHeight': '0'
                }, children=[
                    # Header
                    html.Div(style={
                        'padding': '5px 10px', 
                        'borderBottom': f'1px solid {NEUTRAL_300}',
                        'flexShrink': '0', 
                        'height': '28px', 
                        'display': 'flex', 
                        'alignItems': 'center',
                        'backgroundColor': 'white'
                    }, children=[
                        html.H3(config['title_top_viz'], style={
                            'margin': '0', 
                            'fontSize': '12px', 
                            'color': BRAND_NAVY, 
                            'fontWeight': '600',
                            'letterSpacing': '0.5px'
                        })
                    ]),     
                    # Graph container
                    html.Div(style={
                        'flex': '1',
                        'minHeight': '0',
                        'minWidth': '0',
                        'padding': '0px',
                        'height': '100%',
                        'width': '100%',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    }, children=[
                        dcc.Graph(
                            figure=create_parallel_categories(par_cat_data),
                            config={'displayModeBar': False}, 
                            style={'height': '98%', 'width': '95%'}
                        )
                    ])
                ])
            ])
        ])
    ])