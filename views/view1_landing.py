# views/view1_landing.py
from dash import html, dcc
from utils import (
                    FONT_FAMILY, NEUTRAL_100, NEUTRAL_800, NEUTRAL_600, NEUTRAL_300,
                    BRAND_NAVY, BRAND_VIBRANT, VIEW_CONFIGS, LAST_VIEW_ID, STORY_TITLE,
                    get_guitarist_data
                    )
from components.charts import create_guitarist_selection_chart

def create_view_1_landing(selected_guitarist):
    """Create View 1 - Landing/Selection page with interactive bar chart."""
    config = VIEW_CONFIGS[1]
    
    # Get data
    data = get_guitarist_data()
    
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
        
        # Header
        html.Div(style={
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
            # Top row: main title
            html.Div(style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'height': '32px'
            }, children=[
                # Left: main title
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
                
                # Right: current selection display
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
                        html.Span(id='view-1-selected-guitarist', children=selected_guitarist)
                    ])
                ])
            ]),
            
            # Bottom row: navigation
            html.Div(style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'height': '28px',
                'borderTop': '1px solid rgba(255, 255, 255, 0.1)',
                'paddingTop': '6px'
            }, children=[
                # Left: Section title
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}, children=[
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
                ]),
                
                # Right: navigation buttons
                html.Div(style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '16px'
                }, children=[
                    # Navigation guide note
                    html.Div(style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'gap': '6px',
                        'padding': '4px 10px',
                        'background': 'rgba(255, 255, 255, 0.1)',
                        'borderRadius': '4px',
                        'border': f'1px solid rgba(255, 255, 255, 0.2)',
                        'fontSize': '11px',
                        'color': 'rgba(255, 255, 255, 0.9)',
                        'fontWeight': '500',
                        'fontFamily': FONT_FAMILY
                    }, children=[
                        html.I(className="fas fa-play-circle", style={'fontSize': '9px', 'marginRight': '4px'}),
                        "Ready → go!"
                    ]),
                    
                    html.Span("|", style={
                        'color': 'rgba(255, 255, 255, 0.3)',
                        'fontSize': '14px',
                        'fontWeight': '300',
                        'fontFamily': FONT_FAMILY
                    }),

                    # View status
                    html.Span(f"View 1 of {LAST_VIEW_ID}", style={
                        'color': 'rgba(255, 255, 255, 0.9)',
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'whiteSpace': 'nowrap',
                        'fontFamily': FONT_FAMILY
                    }),
                    
                    # Navigation buttons
                    html.Div(style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'gap': '0px',
                        'background': 'rgba(255, 255, 255, 0.15)',
                        'borderRadius': '6px',
                        'overflow': 'hidden',
                        'border': '1px solid rgba(255, 255, 255, 0.2)'
                    }, children=[
                        # Previous button - disabled on view 1
                        html.Button(
                            html.I(className="fas fa-chevron-left", style={'fontSize': '11px'}),
                            style={
                                'background': 'rgba(255, 255, 255, 0.1)',
                                'border': 'none',
                                'borderRight': '1px solid rgba(255, 255, 255, 0.2)',
                                'color': 'white',
                                'width': '32px',
                                'height': '28px',
                                'cursor': 'not-allowed',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'transition': 'all 0.2s',
                                'fontWeight': 'bold',
                                'opacity': '0.5',
                                'fontFamily': FONT_FAMILY
                            },
                            id={'type': 'nav-btn', 'action': 'prev'},
                            disabled=True
                        ),
                        
                        # Next button - enabled
                        html.Button(
                            html.I(className="fas fa-chevron-right", style={'fontSize': '11px'}),
                            style={
                                'background': 'rgba(59, 130, 246, 0.3)',
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
                                'fontFamily': FONT_FAMILY
                            },
                            id={'type': 'nav-btn', 'action': 'next'}
                        )				  
                    ])
                ])
            ])
        ]),
        
        # Main content area
        html.Div(style={
            'flex': '1',
            'padding': '20px',
            'display': 'flex',
            'gap': '20px',
            'overflow': 'hidden',
            'minHeight': '0'
        }, children=[
            
                # Left panel: introduction text (50% width)
                html.Div(style={
                    'flex': '0.5',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'minHeight': '0',
                    'overflow': 'hidden'
                }, children=[ 
                    html.Div(style={
                        'background': 'white',
                        'borderRadius': '12px',
                        'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.08)',
                        'padding': '0',
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'minHeight': '0',
                        'overflow': 'hidden'
                    }, children=[
                        html.Div(style={
                            'padding': '15px 20px',
                            'borderBottom': f'2px solid {BRAND_VIBRANT}',
                            'flexShrink': '0',
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'alignItems': 'center'
                        }, children=[
                            html.H3("Welcome to the 6-Strings AI-Driven Story", style={
                                'margin': '0', 
                                'color': BRAND_NAVY, 
                                'fontSize': '18px', 
                                'fontWeight': '700',
                                'fontFamily': FONT_FAMILY
                            }),
                            html.Div(style={
                                'padding': '4px 12px',
                                'background': 'rgba(59, 130, 246, 0.1)',
                                'borderRadius': '20px',
                                'fontSize': '11px',
                                'fontWeight': '600',
                                'color': BRAND_VIBRANT,
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '6px',
                                'border': f'1px solid rgba(59, 130, 246, 0.3)',
                                'fontFamily': FONT_FAMILY
                            }, children=[
                                html.I(className="fas fa-star", style={'fontSize': '10px'}),
                                "INTERACTIVE GUIDE"
                            ])
                        ]),
                        
                        # Scrollable content with landing-scrollable class
                        html.Div(style={
                            'flex': '1',
                            'overflowY': 'auto',
                            'overflowX': 'hidden',
                            'padding': '15px 25px'
                        }, className="landing-scrollable",
                        key="landing-scroll",
                        children=[
                            html.Div(style={'marginBottom': '20px'}, children=[
                                html.H4("Technical Architecture", style={
                                    'color': BRAND_NAVY,
                                    'fontSize': '16px',
                                    'marginBottom': '8px',
                                    'fontWeight': '600',
                                    'borderBottom': f'2px solid {NEUTRAL_300}',
                                    'paddingBottom': '6px',
                                    'fontFamily': FONT_FAMILY
                                }),
                                
                                html.P("This rock media intelligence app is powered by a web scraping based data pipeline that collects coverage from sources like The New York Times, Louder, Loudwire, Ultimate Classic Rock, Kerrang!, and Planet Rock, ranging from years 2022 to 2025.", style={
                                    'color': NEUTRAL_600,
                                    'lineHeight': '1.5',
                                    'fontSize': '13px',
                                    'marginBottom': '12px',
                                    'textAlign': 'justify',
                                    'fontFamily': FONT_FAMILY
                                }),
                                
                                html.Div("The data is processed through the following NLP stages:", style={
                                    'color': NEUTRAL_600,
                                    'fontSize': '13px',
                                    'fontWeight': 'normal',
                                    'marginBottom': '8px',
                                    'marginTop': '4px',
                                    'fontFamily': FONT_FAMILY
                                }),
                                
                                html.Ul(style={
                                    'margin': '0 0 15px 0',
                                    'paddingLeft': '20px',
                                    'color': NEUTRAL_600,
                                    'fontSize': '13px',
                                    'lineHeight': '1.6',
                                    'fontFamily': FONT_FAMILY
                                }, children=[
                                    html.Li([
                                        html.Strong("Rock Artist Identification: "),
                                        "A previous Named Entity Recognition (NER) model identifies rock artists to ensure genre accuracy."
                                    ], style={'marginBottom': '6px', 'textAlign': 'justify'}),
                                    
                                    html.Li([
                                        html.Strong("Guitarist Filtering: "),
                                        "The Rock Artist NER model is cross-referenced against Guitar World's '100 Greatest Guitarists' to isolate the featured icons."
                                    ], style={'marginBottom': '6px', 'textAlign': 'justify'}),
                                    
                                    html.Li([
                                        html.Strong("Text Classification: "),
                                        "A deep learning model assigns topic labels using a weakly supervised approach derived from an antecedent rule-based system."
                                    ], style={'marginBottom': '6px', 'textAlign': 'justify'}),
                                    
                                    html.Li([
                                        html.Strong("POS Tagging: "),
                                        "Part-of-Speech tagging separates nouns, verbs, and adjectives, enabling vocabulary profiling."
                                    ], style={'marginBottom': '6px', 'textAlign': 'justify'}),
                                ]),
                                
                                html.P("While metrics are pre-calculated, CrewAI and RAG generate deep narratives for Tier-1 guitar legends. The engine leverages a Pre-Baked Intelligence model to mitigate Gemini 2.5 Flash quota constraints and ensure zero-latency performance. These narratives are served directly from the backend to keep the app responsive.", style={
                                    'color': NEUTRAL_600,
                                    'lineHeight': '1.5',
                                    'fontSize': '13px',
                                    'marginBottom': '12px',
                                    'textAlign': 'justify',
                                    'fontFamily': FONT_FAMILY
                                })
                            ])
                        ])
                    ])
                ]),
            
                # Right panel: interactive bar chart (50% width)
                html.Div(style={
                    'flex': '0.5',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'minHeight': '0',
                    'overflow': 'hidden'
                }, children=[
                    
                    html.Div(style={
                        'background': 'white',
                        'borderRadius': '12px',
                        'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.08)',
                        'padding': '0',
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'minHeight': '0',
                        'overflow': 'hidden'
                    }, children=[
                        html.Div(style={
                            'padding': '15px 20px',
                            'borderBottom': f'2px solid {BRAND_VIBRANT}',
                            'flexShrink': '0',
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'alignItems': 'center'
                        }, children=[
                            html.H3("Select your guitarist", style={
                                'margin': '0', 
                                'color': BRAND_NAVY, 
                                'fontSize': '18px', 
                                'fontWeight': '700',
                                'fontFamily': FONT_FAMILY
                            }),
                            html.Div(style={
                                'padding': '4px 12px',
                                'background': 'rgba(59, 130, 246, 0.1)',
                                'borderRadius': '20px',
                                'fontSize': '11px',
                                'fontWeight': '600',
                                'color': BRAND_VIBRANT,
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '6px',
                                'border': f'1px solid rgba(59, 130, 246, 0.3)',
                                'fontFamily': FONT_FAMILY
                            }, children=[
                                html.I(className="fas fa-mouse-pointer", style={'fontSize': '10px'}),
                                "CLICK TO SELECT"
                            ])
                        ]),
                        
                        # Main content area
                        html.Div(style={
                            'flex': '1',
                            'minHeight': '0',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'padding': '20px',
                            'width': '100%',
                            'justifyContent': 'space-between'
                        }, children=[
                            # Compact info section with bullet points
                            html.Div(style={
                                'marginBottom': '15px',
                                'padding': '10px 12px',
                                'background': 'rgba(15, 23, 42, 0.03)',
                                'borderRadius': '8px',
                                'border': f'1px solid {NEUTRAL_300}',
                                'flexShrink': '0'
                            }, children=[
                                # Current selection line
                                html.Div(style={'marginBottom': '8px'}, children=[
                                    html.Strong("Current Selection: ", style={
                                        'color': NEUTRAL_600,
                                        'fontSize': '13px',
                                        'fontFamily': FONT_FAMILY
                                    }),
                                    html.Span(id='view-1-chart-selected-guitarist', children=selected_guitarist, style={
                                        'color': BRAND_VIBRANT,
                                        'fontWeight': '600',
                                        'fontSize': '13px',
                                        'marginLeft': '5px',
                                        'fontFamily': FONT_FAMILY
                                    })
                                ]),
                                
                                # Three instructions as bullet points
                                html.Ul(style={
                                    'margin': '0',
                                    'paddingLeft': '18px',
                                    'color': NEUTRAL_600,
                                    'fontSize': '11px',
                                    'lineHeight': '1.5',
                                    'fontFamily': FONT_FAMILY
                                }, children=[
                                    html.Li("Click on any bar of the chart below to select a different guitarist. The selection will apply to all analysis views.", style={
                                        'marginBottom': '4px',
                                        'fontStyle': 'italic'
                                    }),
                                    
                                    html.Li("Selected guitarist appears in blue. Other guitarists show article count gradient.", style={
                                        'marginBottom': '4px',
                                        'fontStyle': 'italic'
                                    }),
                                    
                                    html.Li([
                                        "After your selection, click the ",
                                        html.Span("→", style={'fontWeight': '600'}),  # Just bold, no brand color
                                        " button above to explore guitarists' media coverage."
                                    ], style={
                                        'fontStyle': 'italic'
                                    })
                                ])
                            ]),
                        
                        # Chart container
                        html.Div(style={
                            'flex': '1',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'minHeight': '0',
                            'overflow': 'hidden'
                        }, children=[
                            # Interactive bar chart
                            dcc.Graph(
                                id='view-1-guitarist-chart',
                                figure=create_guitarist_selection_chart(data, selected_guitarist),
                                style={
                                    'height': '100%',
                                    'width': '100%',
                                    'display': 'flex',
                                    'justifyContent': 'center',
                                    'alignItems': 'center'
                                },
                                config={
                                    'displayModeBar': False,
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
                                    'toImageButtonOptions': {
                                        'format': 'png',
                                        'filename': 'guitarist_selection',
                                        'height': 400,
                                        'width': 600,
                                        'scale': 2
                                    }
                                }
                            )
                        ])
                    ])
                ])
            ])
        ])
    ])