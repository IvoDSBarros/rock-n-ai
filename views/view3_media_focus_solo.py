# views/view3_media_focus_solo.py
from dash import html, dcc
from utils import (FONT_FAMILY, NEUTRAL_100, NEUTRAL_800, NEUTRAL_600, NEUTRAL_300, BRAND_NAVY, VIEW_CONFIGS)
from utils.data_loader import get_guitarist_metrics_intro, get_media_focus_solo, get_guitarist_narrative, create_narrative_paragraphs
from components.charts import create_focus_ratios_waffle_chart, create_streamgraph
from components.panels import create_ai_narrative_panel
from components.header import create_header

grey_solo_focus = '#94A3B8'

def create_media_solo_focus_view(selected_guitarist, view_id=3):
    """Create overview view with guitarist overview."""
    config = VIEW_CONFIGS[view_id]
    
    # Get data: intro metrics
    intro_metrics, ratios_df = get_guitarist_metrics_intro(selected_guitarist)
    
    # Get data: longitudinal ratios
    longitudinal_ratios_df = get_media_focus_solo(selected_guitarist)

    # Override for the specific "solo focus" narrative
    narrative_colors = ['#94A3B8',
                        '#3B82F6',
                        '#3B82F6']
    
    ratios_df = ratios_df.copy()
    ratios_df['color'] = narrative_colors

    # Fallback approach
    if not intro_metrics or ratios_df is None:
        return html.Div("No data found for this guitarist", style={
            'backgroundColor': NEUTRAL_100,
            'height': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'color': NEUTRAL_800
        })
    
    # Get crew ai narrative
    narrative_paragraphs = get_guitarist_narrative(selected_guitarist, view_id=3)
    
    # Create HTML paragraphs for ai_content
    ai_content = create_narrative_paragraphs(narrative_paragraphs, selected_guitarist)
    
    # Extract solo focus ratio from data
    solo_focus_value = f"{ratios_df.iloc[0]['percentage']:.1f}%" if len(ratios_df) > 0 else "0.0%"
    
    # Ensuring the KPI block is mathematically centered to the grey area midpoint
    try:
        focus_val = float(solo_focus_value.replace('%', ''))
    except:
        focus_val = 0

    # Calculated for the 180px waffle scale
    # Adjusted formula: start at waffle top (10px) + half of grey section height
    grey_section_height = 180 * (focus_val / 100)
    dynamic_kpi_top = 10 + (grey_section_height / 2) - 25

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

            # Right panel: positioning for 1:1 alignment
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '15px',
                'height': '100%'
            }, children=[

                # 1. Top panel: global solo focus narrative
                html.Div(style={
                    'background': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'flex': '1'
                }, children=[
                    # Header
                    html.Div(style={
                        'padding': '5px 10px', 
                        'borderBottom': f'1px solid {NEUTRAL_300}',
                        'flexShrink': '0', 
                        'height': '28px', 
                        'display': 'flex', 
                        'alignItems': 'center'
                    }, children=[
                        html.H3(config['title_top_viz'], style={
                            'margin': '0', 
                            'fontSize': '12px', 
                            'color': BRAND_NAVY, 
                            'fontWeight': '600'
                        })
                    ]),
                    
                    # Anchor
                    html.Div(style={
                        'flex': '1',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                    }, children=[
                        
                        html.Div(style={
                            'width': '360px',
                            'height': '200px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'gap': '20px',
                            'marginLeft': '-20px',
                        }, children=[
                            
                            # KPI block
                            html.Div(style={
                                'width': '170px',
                                'height': '180px',
                                'position': 'relative',
                                'display': 'flex',
                                'flexDirection': 'column',
                                'justifyContent': 'center',
                                'alignItems': 'flex-end',
                            }, children=[
                                html.Div(style={
                                    'position': 'absolute',
                                    'top': f'{dynamic_kpi_top}px',
                                    'transition': 'top 0.3s ease-out',
                                    'textAlign': 'right',
                                    'width': '100%',
                                }, children=[
                                    html.Div(solo_focus_value, style={
                                        'fontSize': '52px', 
                                        'fontWeight': '900', 
                                        'color': grey_solo_focus,
                                        'lineHeight': '0.8', 
                                        'letterSpacing': '-2px',
                                        'textAlign': 'right',
                                    }),
                                    html.Div("Solo Focus Ratio", style={
                                        'fontSize': '12px', 
                                        'fontWeight': '700', 
                                        'color': BRAND_NAVY,
                                        'textTransform': 'uppercase', 
                                        'marginTop': '6px',
                                        'textAlign': 'right',
                                    }),
                                ])
                            ]),

                            # Waffle chart
                            html.Div(style={
                                'width': '170px',
                                'height': '180px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                            }, children=[
                                dcc.Graph(
                                    figure=create_focus_ratios_waffle_chart(ratios_df, height=180, width=180),
                                    config={'displayModeBar': False, 'staticPlot': True},
                                    style={'height': '180px', 'width': '180px'}
                                )
                            ])
                        ])
                    ])
                ]),

                # 2. Bottom panel: solo focus narrative over time
                html.Div(style={
                    'background': 'white', 
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.04)',
                    'overflow': 'hidden', 
                    'flex': '1', 
                    'display': 'flex', 
                    'flexDirection': 'column'
                }, children=[
                    html.Div(style={
                        'padding': '5px 10px', 
                        'borderBottom': f'1px solid {NEUTRAL_300}',
                        'flexShrink': '0', 
                        'height': '28px', 
                        'display': 'flex', 
                        'alignItems': 'center'
                    }, children=[
                        html.H3(config['title_bottom_viz'], style={
                            'margin': '0', 
                            'color': BRAND_NAVY, 
                            'fontSize': '12px', 
                            'fontWeight': '600'
                        })
                    ]),
                    html.Div(style={
                        'flex': '1', 
                        'display': 'flex', 
                        'alignItems': 'center', 
                        'justifyContent': 'center'
                    }, children=[
                        dcc.Graph(
                            figure=create_streamgraph(longitudinal_ratios_df),
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
                        # Single reference label
                        html.Div(style={
                            'display': 'flex', 
                            'alignItems': 'center', 
                            'gap': '6px'
                        }, children=[
                            html.Div(style={
                                'width': '8px', 
                                'height': '8px', 
                                'background': '#94A3B8',
                                'borderRadius': '1px'
                            }),
                            # Clean, bolded label
                            html.Span("Solo Focus Ratio", style={
                                'fontSize': '8px', 
                                'fontFamily': FONT_FAMILY,
                                'fontWeight': '600',
                                'letterSpacing': '0.02em'
                            })
                        ])
                    ])
                ])
            ])
        ])
    ])