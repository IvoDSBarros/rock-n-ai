# components/panels.py
from dash import html, dcc
from utils import FONT_FAMILY, BRAND_NAVY, BRAND_VIBRANT, NEUTRAL_600, NEUTRAL_300
from components.charts import create_compact_global_mentions_fig, create_compact_heatmap_fig

def create_ai_narrative_panel(view_id, ai_content):
    """Create AI narrative panel for analysis views."""
    return html.Div(style={
        'background': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
        'padding': '0',
        'flex': '1',
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '0',
        'overflow': 'hidden',
        'className': 'ai-narrative-container'
    }, children=[
        html.Div(style={
            'padding': '5px 10px',
            'borderBottom': f'1px solid {NEUTRAL_300}',
            'flexShrink': '0',
            'height': '28px',
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center'
        }, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}, children=[
                html.Div(style={'display': 'flex', 'gap': '4px'}, children=[
                    html.Div(style={
                        'width': '10px',
                        'height': '10px',
                        'background': '#FF5F57',
                        'borderRadius': '50%',
                        'cursor': 'pointer'
                    }),
                    html.Div(style={
                        'width': '10px',
                        'height': '10px',
                        'background': '#FFBD2E',
                        'borderRadius': '50%',
                        'cursor': 'pointer'
                    }),
                    html.Div(style={
                        'width': '10px',
                        'height': '10px',
                        'background': '#27C93F',
                        'borderRadius': '50%',
                        'cursor': 'pointer'
                    })
                ]),
                html.H3("AI Narrative Terminal", style={
                    'margin': '0', 
                    'color': BRAND_NAVY, 
                    'fontSize': '12px', 
                    'fontWeight': '600',
                    'fontFamily': FONT_FAMILY
                })
            ]),
            html.Div(style={
                'padding': '2px 8px',
                'background': 'rgba(59, 130, 246, 0.1)',
                'borderRadius': '4px',
                'fontSize': '8px',
                'fontWeight': '600',
                'color': BRAND_VIBRANT,
                'display': 'flex',
                'alignItems': 'center',
                'gap': '4px',
                'border': f'1px solid rgba(59, 130, 246, 0.3)',
                'fontFamily': FONT_FAMILY
            }, children=[
                html.I(className="fas fa-robot", style={'fontSize': '7px'}),
                "SYNTHESIZING"
            ])
        ]),
        
        # Scrollable div
        html.Div(style={
            'flex': '1',
            'overflowY': 'auto',
            'overflowX': 'hidden',
            'padding': '12px 16px',
            'paddingRight': '20px'
        }, 
        className="ai-narrative-scrollable",
        key=f"narrative-scroll-{view_id}",
        children=ai_content)
    ])

def create_bar_chart_panel(view_config, global_df, total_counts, top5_pct):
    """Create bar chart panel for analysis views."""
    return html.Div(style={
        'background': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
        'overflow': 'hidden',
        'flex': '1',
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '0'
    }, children=[
        html.Div(style={
            'padding': '5px 10px',
            'borderBottom': f'1px solid {NEUTRAL_300}',
            'flexShrink': '0',
            'height': '28px',
            'display': 'flex',
            'alignItems': 'center'
        }, children=[
            html.H3(view_config['title_bar'], style={
                'margin': '0', 
                'color': BRAND_NAVY, 
                'fontSize': '12px', 
                'fontWeight': '600',
                'fontFamily': FONT_FAMILY
            })
        ]),
        
        html.Div(style={
            'flex': '1',
            'minHeight': '0',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'overflow': 'hidden'
        }, children=[
            dcc.Graph(
                id={'type': 'bar-chart', 'index': view_config['view_number']},
                figure=create_compact_global_mentions_fig(global_df),
                style={'height': '90%', 'width': '90%'},
                config={'displayModeBar': False, 'responsive': True}
            )
        ]),
        
        html.Div(style={
            'padding': '5px 10px',
            'borderTop': f'1px solid {NEUTRAL_300}',
            'fontSize': '9px',
            'color': NEUTRAL_600,
            'flexShrink': '0',
            'height': '22px',
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'fontFamily': FONT_FAMILY
        }, children=[
            html.Span(f"#{total_counts} {view_config['bar_footnote_01']} | Top 5 {view_config['bar_footnote_02']} account for {top5_pct * 100:.1f}% of total"),
        ])
    ])

def create_heatmap_panel(view_config, heatmap_df):
    """Create heatmap panel for analysis views."""
    return html.Div(style={
        'background': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
        'overflow': 'hidden',
        'flex': '1',
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '0'
    }, children=[
        html.Div(style={
            'padding': '5px 10px',
            'borderBottom': f'1px solid {NEUTRAL_300}',
            'flexShrink': '0',
            'height': '28px',
            'display': 'flex',
            'alignItems': 'center'
        }, children=[
            html.H3(view_config['title_heatmap'], style={
                'margin': '0', 
                'color': BRAND_NAVY, 
                'fontSize': '12px', 
                'fontWeight': '600',
                'fontFamily': FONT_FAMILY
            })
        ]),
        
        html.Div(style={
            'flex': '1',
            'minHeight': '0',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'overflow': 'hidden'
        }, children=[
            dcc.Graph(
                id={'type': 'heatmap', 'index': view_config['view_number']},
                figure=create_compact_heatmap_fig(heatmap_df),
                style={'height': '90%', 'width': '90%'},
                config={'displayModeBar': False, 'responsive': True}
            )
        ]),
        
        html.Div(style={
            'padding': '5px 10px',
            'borderTop': f'1px solid {NEUTRAL_300}',
            'fontSize': '9px',
            'color': NEUTRAL_600,
            'flexShrink': '0',
            'height': '22px',
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '8px',
            'fontFamily': FONT_FAMILY
        }, children=[
            html.Span("Intensity", style={'marginRight': '8px'}),
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '6px'}, children=[
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '2px'}, children=[
                    html.Div(style={'width': '8px', 'height': '8px', 'background': 'rgba(15, 23, 42, 0.1)', 'borderRadius': '1px'}),
                    html.Span("Low", style={'fontSize': '8px', 'fontFamily': FONT_FAMILY})
                ]),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '2px'}, children=[
                    html.Div(style={'width': '8px', 'height': '8px', 'background': BRAND_VIBRANT, 'borderRadius': '1px'}),
                    html.Span("High", style={'fontSize': '8px', 'fontFamily': FONT_FAMILY})
                ])
            ])
        ])
    ])