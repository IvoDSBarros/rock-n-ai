# components\header.py
from dash import html
from utils import (
    FONT_FAMILY, 
    STORY_TITLE, 
    VIEW_CONFIGS,
    BRAND_VIBRANT,
    BRAND_NAVY,
    ACCENT_EMERALD,
    LAST_VIEW_ID
)

def create_header(view_id, selected_guitarist, 
                  show_live_indicator=None,
                  show_view_status=True,
                  enable_navigation=True,
                  custom_guitarist_id=None):
    """
    Create a standardized app header for all views.
    
    Args:
        view_id (int): Current view ID (1-to last view)
        selected_guitarist (str): Currently selected guitarist
        show_live_indicator (bool): Force show/hide. If None, auto: views 2,3,4,5
        show_view_status (bool): Show "View X of last view" text
        enable_navigation (bool): Show prev/next buttons
        custom_guitarist_id (str): Custom ID for guitarist span (for callbacks)
    """
    config = VIEW_CONFIGS[view_id]
    
    # Live indicator visibility
    if show_live_indicator is None:
        show_live_indicator = view_id in [2, 3, 4, 5, 6, 7,LAST_VIEW_ID]
    
    guitarist_span_id = custom_guitarist_id or f'view-{view_id}-selected-guitarist'
    
    # Top row
    top_row = html.Div(style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'height': '32px'
    }, children=[
        # Left: Main title with bolt icon
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
            html.Div(style={
                'width': '28px',
                'height': '28px',
                'backgroundColor': BRAND_VIBRANT,
                'borderRadius': '6px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'boxShadow': f'0 0 10px {BRAND_VIBRANT}44',
                'flexShrink': 0
            }, children=[
                html.I(className="fas fa-bolt", style={
                    'color': BRAND_NAVY,
                    'fontSize': '16px'
                })
            ]),
            html.Span(STORY_TITLE, style={
                'color': 'white', 
                'fontSize': '18px', 
                'fontWeight': '600',
                'letterSpacing': '0.3px',
                'fontFamily': FONT_FAMILY
            })
        ]),
        
        # Right: guitar icon display
        html.Div(style={
            'display': 'flex',
            'alignItems': 'center',
            'gap': '4px'
        }, children=[
            html.Span("Guitarist:", style={
                'color': 'rgba(255, 255, 255, 0.7)',
                'fontSize': '11px',
                'whiteSpace': 'nowrap',
                'fontFamily': FONT_FAMILY,
                'marginRight': '0px'
            }),
            html.Div(style={
                'color': 'white',
                'padding': '6px 0px',
                'fontSize': '12px',
                'fontWeight': '600',
                'whiteSpace': 'nowrap',
                'fontFamily': FONT_FAMILY
            }, children=[
                html.Span(
                    id=guitarist_span_id,
                    children=selected_guitarist
                )
            ])
        ])
    ])
    
    # Bottom row
    bottom_row_children = []
    
    # Left: Section title
    bottom_row_left = html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}, children=[
        html.Div(style={
            'width': '4px',
            'height': '18px',
            'background': BRAND_VIBRANT,
            'borderRadius': '2px'
        }),
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}, children=[
            html.H1(config['title'], style={
                'margin': '0',
                'color': 'white',
                'fontSize': '17px',
                'fontWeight': '700',
                'letterSpacing': '0.2px',
                'whiteSpace': 'nowrap',
                'fontFamily': FONT_FAMILY
            }),
            html.Span("|", style={
                'color': 'rgba(255, 255, 255, 0.4)',
                'fontSize': '14px',
                'fontWeight': '300',
                'fontFamily': FONT_FAMILY
            }),
            html.Span(config['subtitle'], style={
                'color': 'rgba(255, 255, 255, 0.85)',
                'fontSize': '14px',
                'fontWeight': '500',
                'whiteSpace': 'nowrap',
                'fontFamily': FONT_FAMILY
            })
        ])
    ])
    
    # Right: Navigation area
    right_children = []
    
    # Live Indicator
    if show_live_indicator:
        right_children.extend([
            html.Div(style={
                'display': 'flex',
                'alignItems': 'center',
                'gap': '6px'
            }, children=[
                html.Div(style={
                    'width': '8px',
                    'height': '8px',
                    'background': ACCENT_EMERALD,
                    'borderRadius': '50%',
                    'boxShadow': f'0 0 8px {ACCENT_EMERALD}',
                    'animation': 'pulse 2s infinite'
                }),
                html.Span("Live", style={
                    'color': ACCENT_EMERALD,
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'textShadow': '0 1px 2px rgba(0,0,0,0.3)',
                    'fontFamily': FONT_FAMILY
                })
            ]),
            
            # Separator
            html.Span("|", style={
                'color': 'rgba(255, 255, 255, 0.3)',
                'fontSize': '14px',
                'fontWeight': '300',
                'fontFamily': FONT_FAMILY
            })
        ])
    
    # View status
    if show_view_status:
        right_children.append(
            html.Span(f"View {view_id} of {LAST_VIEW_ID}", style={
                'color': 'rgba(255, 255, 255, 0.9)',
                'fontSize': '13px',
                'fontWeight': '600',
                'whiteSpace': 'nowrap',
                'fontFamily': FONT_FAMILY
            })
        )
    
    # Navigation buttons
    if enable_navigation:
        right_children.append(_create_navigation_buttons(view_id))
    
    bottom_row_right = html.Div(style={
        'display': 'flex',
        'alignItems': 'center',
        'gap': '16px'
    }, children=right_children)
    
    bottom_row = html.Div(style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'height': '28px',
        'borderTop': '1px solid rgba(255, 255, 255, 0.1)',
        'paddingTop': '6px'
    }, children=[
        bottom_row_left,
        bottom_row_right
    ])
    
    # Complete header
    return html.Div(style={
        'background': BRAND_NAVY,
        'padding': '10px 20px 8px 20px',
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '8px',
        'flexShrink': 0,
        'borderBottom': f'2px solid {BRAND_VIBRANT}',
        'minHeight': '70px',
        'boxSizing': 'border-box'
    }, children=[
        top_row,
        bottom_row
    ])

def _create_navigation_buttons(view_id):
    """Create prev/next navigation buttons using LAST_VIEW_ID from config."""
    return html.Div(style={
        'display': 'flex',
        'alignItems': 'center',
        'gap': '0px',
        'background': 'rgba(255, 255, 255, 0.15)',
        'borderRadius': '6px',
        'overflow': 'hidden',
        'border': '1px solid rgba(255, 255, 255, 0.2)'
    }, children=[
        # Previous button
        html.Button(
            html.I(className="fas fa-chevron-left", style={'fontSize': '11px'}),
            style={
                'background': 'rgba(255, 255, 255, 0.1)',
                'border': 'none',
                'borderRight': '1px solid rgba(255, 255, 255, 0.2)',
                'color': 'white',
                'width': '32px',
                'height': '28px',
                'cursor': 'pointer' if view_id > 1 else 'not-allowed',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'transition': 'all 0.2s',
                'fontWeight': 'bold',
                'opacity': '1' if view_id > 1 else '0.5',
                'fontFamily': FONT_FAMILY
            },
            id={'type': 'nav-btn', 'action': 'prev'},
            disabled=(view_id == 1)
        ),
        
        # Next button
        html.Button(
            html.I(className="fas fa-chevron-right", style={'fontSize': '11px'}),
            style={
                'background': 'rgba(255, 255, 255, 0.1)',
                'border': 'none',
                'color': 'white',
                'width': '32px',
                'height': '28px',
                'cursor': 'pointer',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'transition': 'all 0.2s',
                'fontWeight': 'bold',
                'opacity': '1',
                'fontFamily': FONT_FAMILY
            },
            id={'type': 'nav-btn', 'action': 'next'},
            disabled=False
        )				  
    ])