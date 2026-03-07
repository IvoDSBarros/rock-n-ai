# views/view2_intro.py
from dash import html, dcc
from utils import (
                    FONT_FAMILY, NEUTRAL_100, NEUTRAL_800, NEUTRAL_600, NEUTRAL_300,
                    BRAND_NAVY, BRAND_VIBRANT, ACCENT_EMERALD, VIEW_CONFIGS 
                    )
from utils.data_loader import get_guitarist_metrics_intro, get_guitarist_narrative, create_narrative_paragraphs
from components.charts import create_focus_ratios_waffle_chart
from components.panels import create_ai_narrative_panel
from components.header import create_header

def create_intro_view(selected_guitarist, view_id=2):
    """Create overview view with guitarist overview."""
    config = VIEW_CONFIGS[view_id]
    
    # Get data
    intro_metrics, ratios_df = get_guitarist_metrics_intro(selected_guitarist)
    
    if not intro_metrics or ratios_df is None:
        return html.Div("No data found for this guitarist", style={
            'backgroundColor': NEUTRAL_100,
            'height': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'color': NEUTRAL_800
        })
    
    # Create image filename
    guitarist_name_lower = selected_guitarist.lower()
    image_filename = f"pic_{guitarist_name_lower.replace(' ', '_')}.jpg"
    image_path = f"/assets/images/{image_filename}"
    
    # Get narrative paragraphs for the selected guitarist
    narrative_paragraphs = get_guitarist_narrative(selected_guitarist, view_id=2)
    
    # Create HTML paragraphs for crew ai content
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
            # Left panel: AI Narrative Terminal (50% width)
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'minHeight': '0',
                'overflow': 'hidden'
            }, children=[
                create_ai_narrative_panel(view_id, ai_content)
            ]),
            
            # Right panel: 20-20-60 layout with 50-50 waffle/network
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '8px',
                'minHeight': '0',
                'overflow': 'hidden',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'padding': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
                'position': 'relative'
            }, children=[
                # Info icon
                html.Div(style={
                    'position': 'absolute',
                    'top': '16px',
                    'right': '16px',
                    'zIndex': '100',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'flex-end'
                }, children=[
                    # Main container for icon and tooltip
                    html.Div(style={
                        'position': 'relative',
                        'display': 'inline-block'
                    }, children=[
                        html.Div(
                            id=f'info-icon-{view_id}',
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'width': '22px',
                                'height': '22px',
                                'backgroundColor': BRAND_VIBRANT,
                                'borderRadius': '50%',
                                'cursor': 'help',
                                'border': f'1px solid {BRAND_VIBRANT}',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                'transition': 'all 0.2s ease',
                                'fontFamily': FONT_FAMILY
                            }, children=[
                                html.Span("i", style={
                                    'color': 'white',
                                    'fontSize': '12px',
                                    'fontWeight': '700',
                                    'fontStyle': 'italic',
                                    'lineHeight': '1'
                                })
                            ]
                        ),
                        
                        # Tooltip
                        html.Div(
                            id=f'info-tooltip-{view_id}',
                            style={
                                'visibility': 'hidden',
                                'width': '340px',
                                'backgroundColor': 'white',
                                'color': NEUTRAL_800,
                                'textAlign': 'left',
                                'borderRadius': '8px',
                                'padding': '16px',
                                'position': 'absolute',
                                'zIndex': '1000',
                                'right': '0',
                                'top': '30px',
                                'boxShadow': '0 8px 24px rgba(0,0,0,0.15)',
                                'border': f'1px solid {NEUTRAL_300}',
                                'fontSize': '12px',
                                'lineHeight': '1.6',
                                'fontFamily': FONT_FAMILY,
                                'opacity': '0',
                                'transition': 'opacity 0.2s ease'
                            },
                            children=[
                                # Main tooltip title with custom icon
                                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'marginBottom': '12px'}, children=[
                                     html.I(className="fas fa-tags", style={
                                        'color': BRAND_VIBRANT,
                                        'fontSize': '16px',
                                        'backgroundColor': f'{BRAND_VIBRANT}10',
                                        'padding': '8px',
                                        'borderRadius': '8px'
                                    }),
                                    html.Div("NARRATIVE CLASSIFICATION LOGIC", style={
                                        'color': BRAND_NAVY,
                                        'fontWeight': '700',
                                        'fontSize': '13px',
                                        'letterSpacing': '1px'
                                    })
                                ]),
                                
                                # Ratio explanations
                                html.Div([
                                    # Solo focus ratio
                                    html.Div([
                                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '4px', 'marginBottom': '2px'}, children=[
                                            html.I(className="fas fa-user", style={'color': BRAND_VIBRANT, 'fontSize': '10px'}),
                                            html.Div("SOLO FOCUS RATIO", style={
                                                'color': BRAND_NAVY,
                                                'fontSize': '11px',
                                                'fontWeight': '700',
                                                'letterSpacing': '0.5px'
                                            })
                                        ]),
                                        html.Div("Articles where the subject is the only artist mentioned. Indicates individual notoriety, solo projects, or technical gear spotlights.", 
                                                style={'color': NEUTRAL_600, 'textAlign': 'justify', 'fontSize': '11px'})
                                    ], style={'marginBottom': '12px'}),

                                    # Guitar focus ratio
                                    html.Div([
                                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '4px', 'marginBottom': '2px'}, children=[
                                            html.I(className="fas fa-guitar", style={'color': BRAND_VIBRANT, 'fontSize': '10px'}),
                                            html.Div("GUITAR FOCUS RATIO", style={
                                                'color': BRAND_NAVY,
                                                'fontSize': '11px',
                                                'fontWeight': '700',
                                                'letterSpacing': '0.5px'
                                            })
                                        ]),
                                        html.Div("Articles where the subject appears with other guitarists, but no non-guitarist members. Represents guitar-centric media and peer rankings.", 
                                                style={'color': NEUTRAL_600, 'textAlign': 'justify', 'fontSize': '11px'})
                                    ], style={'marginBottom': '12px'}),

                                    # Cross-Artist focus ratio
                                    html.Div([
                                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '4px', 'marginBottom': '2px'}, children=[
                                            html.I(className="fas fa-users", style={'color': BRAND_VIBRANT, 'fontSize': '10px'}),
                                            html.Div("CROSS-ARTIST FOCUS RATIO", style={
                                                'color': BRAND_NAVY,
                                                'fontSize': '11px',
                                                'fontWeight': '700',
                                                'letterSpacing': '0.5px'
                                            })
                                        ]),
                                        html.Div("Articles where the subject is mentioned alongside at least one non-guitarist (vocalists, bassists, drummers, etc.). If a guitarist is mentioned together with a non-guitarist and the subject, the article falls under this ratio. Captures the subject's presence in broader ensemble and industry contexts.", 
                                                style={'color': NEUTRAL_600, 'textAlign': 'justify', 'fontSize': '11px'})
                                    ])
                                ], style={'marginBottom': '16px'}),
                                
                                # Network architecture note
                                html.Div(style={
                                    'backgroundColor': f'{BRAND_VIBRANT}08',
                                    'borderRadius': '6px',
                                    'padding': '12px',
                                    'border': f'1px dashed {BRAND_VIBRANT}30'
                                }, children=[
                                    html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '6px', 'marginBottom': '6px'}, children=[
                                        html.I(className="fas fa-project-diagram", style={'color': BRAND_VIBRANT, 'fontSize': '12px'}),
                                        html.Div("NETWORK ARCHITECTURE", style={
                                            'color': BRAND_NAVY,
                                            'fontWeight': '700',
                                            'fontSize': '11px',
                                            'letterSpacing': '0.5px'
                                        })
                                    ]),
                                    html.P("Highly featured guitarists like Wolfgang Van Halen and Kirk Hammett were appended to the Guitar World list to better reflect modern rock media trends.", style={
                                        'color': NEUTRAL_600,
                                        'fontSize': '11px',
                                        'margin': '0',
                                        'lineHeight': '1.5',
                                        'textAlign': 'justify'
                                    })
                                ])
                            ]
                        )
                    ])
                ]),
                
                # Section : photo + master data (20% height)
                html.Div(style={
                    'flex': '0 0 20%',
                    'minHeight': '100px',
                    'display': 'flex',
                    'gap': '16px',
                    'marginBottom': '4px'
                }, children=[
                    # Circular photo
                    html.Div(style={
                        'flex': '0 0 80px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    }, children=[
                        html.Div(style={
                            'width': '80px',
                            'height': '80px',
                            'borderRadius': '50%',
                            'overflow': 'hidden',
                            'border': f'3px solid {BRAND_VIBRANT}',
                            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
                        }, children=[
                            html.Img(
                                src=image_path,
                                style={
                                    'width': '100%',
                                    'height': '100%',
                                    'objectFit': 'cover',
                                    'objectPosition': 'center 20%'
                                },
                                alt=intro_metrics.get('guitarist', 'Guitarist')
                            )
                        ])
                    ]),
                    
                    # Master data
                    html.Div(style={
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'padding': '4px 0'
                    }, children=[
                        html.Div(intro_metrics.get('guitarist', ''), style={
                            'fontSize': '20px',
                            'fontWeight': '700',
                            'color': BRAND_VIBRANT,
                            'marginBottom': '6px',
                            'lineHeight': '1.1'
                        }),
                        # Line 1: Genre, band, status, country
                        html.Div(style={
                            'display': 'flex',
                            'flexWrap': 'wrap',
                            'gap': '8px',
                            'marginBottom': '4px',
                            'fontSize': '12px',
                            'alignItems': 'center',
                            'lineHeight': '1.4'
                        }, children=[
                            # Genre
                            html.Span([
                                html.Span("Genre: ", style={
                                    'color': NEUTRAL_600,
                                    'fontWeight': '500'
                                }),
                                html.Span(intro_metrics.get('genre_guitar_world', 'N/A'), style={
                                    'color': BRAND_NAVY,
                                    'fontWeight': '700'
                                })
                            ]),
                            html.Span("|", style={
                                'color': NEUTRAL_300,
                                'fontWeight': '300'
                            }),
                            
                            # Band
                            html.Span([
                                html.Span("Band: ", style={
                                    'color': NEUTRAL_600,
                                    'fontWeight': '500'
                                }),
                                html.Span(intro_metrics.get('band_affiliation', 'N/A'), style={
                                    'color': BRAND_NAVY,
                                    'fontWeight': '700'
                                })
                            ]),
                            html.Span("|", style={
                                'color': NEUTRAL_300,
                                'fontWeight': '300'
                            }),
                            
                            # Status with colored dot
                            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '4px'}, children=[
                                html.Span([
                                    html.Span("Status: ", style={
                                        'color': NEUTRAL_600,
                                        'fontWeight': '500'
                                    }),
                                    html.Span(intro_metrics.get('status', 'N/A'), style={
                                        'color': BRAND_NAVY,
                                        'fontWeight': '700'
                                    })
                                ]),
                                html.Div(style={
                                    'width': '6px',
                                    'height': '6px',
                                    'backgroundColor': ACCENT_EMERALD if intro_metrics.get('status') == 'Active' else '#FF4757',
                                    'borderRadius': '50%'
                                })
                            ]),
                            html.Span("|", style={
                                'color': NEUTRAL_300,
                                'fontWeight': '300'
                            }),
                            
                            # Country
                            html.Span([
                                html.Span("Country: ", style={
                                    'color': NEUTRAL_600,
                                    'fontWeight': '500'
                                }),
                                html.Span(intro_metrics.get('country', 'N/A'), style={
                                    'color': BRAND_NAVY,
                                    'fontWeight': '700'
                                })
                            ])
                        ]),
                        
                        # Line 2: Life span only
                        html.Div(style={
                            'display': 'flex',
                            'fontSize': '12px',
                            'alignItems': 'center',
                            'lineHeight': '1.4',
                            'marginTop': '2px'
                        }, children=[
                            html.Span([
                                html.Span("Life Span: ", style={
                                    'color': NEUTRAL_600,
                                    'fontWeight': '500'
                                }),
                                html.Span(intro_metrics.get('life_span', 'N/A'), style={
                                    'color': BRAND_NAVY,
                                    'fontWeight': '700'
                                })
                            ])
                        ])
                    ])
                ]),

                # Section 2: Key metrics (20% height)
                html.Div(style={
                    'flex': '0 0 20%',
                    'minHeight': '60px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'marginBottom': '0'
                }, children=[
                    html.Div("2022-2025 Media Footprint", style={
                        'fontSize': '14px',
                        'color': BRAND_NAVY,
                        'fontWeight': '600',
                        'marginBottom': '8px',
                        'textAlign': 'center'
                    }),
                    html.Div(style={
                        'flex': '1',
                        'display': 'flex',
                        'gap': '6px',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    }, children=[
                        create_metric_box(
                            title="COVERAGE RANK",
                            value=intro_metrics.get('overall_article_rank', 'N/A'),
                            value_color=BRAND_VIBRANT,
                            title_color=NEUTRAL_600
                        ),
                        create_metric_box(
                            title="COVERAGE SHARE",
                            value=intro_metrics.get('dataset_frequency_pct', 'N/A'),
                            value_color=BRAND_VIBRANT,
                            title_color=NEUTRAL_600
                        ),
                        create_metric_box(
                            title="ARTICLE VOLUME",
                            value=intro_metrics.get('total_articles', 'N/A'),
                            value_color=BRAND_VIBRANT,
                            title_color=NEUTRAL_600
                        ),
                        create_metric_box(
                            title="TOTAL WORD VOLUME",
                            value=format_number(intro_metrics.get('total_body_words', 'N/A')),
                            value_color=BRAND_VIBRANT,
                            title_color=NEUTRAL_600
                        ),
                        create_metric_box(
                            title="AVG ARTICLE DEPTH",
                            value=format_number(intro_metrics.get('avg_words_per_article', 'N/A')),
                            value_color=BRAND_VIBRANT,
                            title_color=NEUTRAL_600
                        )
                    ])
                ]),
                
                # Section 3: visualization area (60% height) with 50-50 split
                html.Div(style={
                    'flex': '0 0 55%',
                    'display': 'flex',
                    'gap': '12px',
                    'minHeight': '0',
                    'overflow': 'hidden',
                    'borderTop': f'1px solid {NEUTRAL_300}',
                    'paddingTop': '8px',
                    'maxHeight': '55%'
                }, children=[
                    
                    # Left: waffle chart area (50% width)
                    html.Div(style={
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'minHeight': '0',
                        'overflow': 'hidden',
                        'height': '100%'
                    }, children=[
                        # Title
                        html.Div("Narrative Context Distribution", style={
                            'fontSize': '14px',
                            'color': BRAND_NAVY,
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'textAlign': 'center',
                            'height': '24px',
                            'lineHeight': '24px'
                        }),
                        
                        # Waffle container
                        html.Div(style={
                            'flex': '1',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'minHeight': '0',
                            'padding': '0',
                            'margin': '0',
                            'height': 'calc(100% - 120px)'
                        }, children=[
                            dcc.Graph(
                                figure=create_focus_ratios_waffle_chart(ratios_df, height=180, width=180),
                                config={'displayModeBar': False, 'staticPlot': True},
                                style={
                                    'height': '180px',
                                    'width': '180px',
                                    'margin': '0 auto',
                                    'padding': '0',
                                    'display': 'block',
                                    'marginTop': '0'
                                }
                            )
                        ]),

                        # Legend
                        html.Div(style={
                            'height': '50px',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '6px',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'padding': '8px 0',
                            'flexShrink': 0
                        }, children=[
                            # Line 1: Solo focus and guitarist focus (side by side)
                            html.Div(style={
                                'display': 'flex',
                                'gap': '25px',
                                'justifyContent': 'center',
                                'alignItems': 'center'
                            }, children=[
                                # Solo focus
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'gap': '6px'
                                }, children=[
                                    html.Div(style={
                                        'width': '12px',
                                        'height': '12px',
                                        'backgroundColor': ratios_df.iloc[0]['color'] if len(ratios_df) > 0 else NEUTRAL_300,
                                        'borderRadius': '2px',
                                        'flexShrink': 0
                                    }),
                                    html.Span("Solo Focus: ", style={
                                        'fontSize': '11px',
                                        'fontWeight': '600',
                                        'color': NEUTRAL_600
                                    }),
                                    html.Span(f"{ratios_df.iloc[0]['percentage']:.1f}%" if len(ratios_df) > 0 else "0.0%", style={
                                        'fontSize': '11px',
                                        'fontWeight': '700',
                                        'color': NEUTRAL_600
                                    })
                                ]),
                                
                                # Guitarist focus
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'gap': '6px'
                                }, children=[
                                    html.Div(style={
                                        'width': '12px',
                                        'height': '12px',
                                        'backgroundColor': ratios_df.iloc[1]['color'] if len(ratios_df) > 1 else NEUTRAL_300,
                                        'borderRadius': '2px',
                                        'flexShrink': 0
                                    }),
                                    html.Span("Guitarist Focus: ", style={
                                        'fontSize': '11px',
                                        'fontWeight': '600',
                                        'color': NEUTRAL_600
                                    }),
                                    html.Span(f"{ratios_df.iloc[1]['percentage']:.1f}%" if len(ratios_df) > 1 else "0.0%", style={
                                        'fontSize': '11px',
                                        'fontWeight': '700',
                                        'color': NEUTRAL_600
                                    })
                                ])
                            ]),
                            
                            # Line 2: Cross-Artist focus
                            html.Div(style={
                                'display': 'flex',
                                'justifyContent': 'center',
                                'alignItems': 'center',
                                'gap': '6px'
                            }, children=[
                                html.Div(style={
                                    'width': '12px',
                                    'height': '12px',
                                    'backgroundColor': ratios_df.iloc[2]['color'] if len(ratios_df) > 2 else NEUTRAL_300,
                                    'borderRadius': '2px',
                                    'flexShrink': 0
                                }),
                                html.Span("Cross-Artist Focus: ", style={
                                    'fontSize': '11px',
                                    'fontWeight': '600',
                                    'color': NEUTRAL_600
                                }),
                                html.Span(f"{ratios_df.iloc[2]['percentage']:.1f}%" if len(ratios_df) > 2 else "0.0%", style={
                                    'fontSize': '11px',
                                    'fontWeight': '700',
                                    'color': NEUTRAL_600
                                })
                            ])
                        ])
                    ]), 

                    # Right: network architecture section
                    html.Div(style={
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'minHeight': '0',
                        'overflow': 'hidden',
                        'height': '100%'
                    }, children=[
                        # Title
                        html.Div("Network Architecture", style={
                            'fontSize': '14px',
                            'color': BRAND_NAVY,
                            'fontWeight': '600',
                            'marginBottom': '6px',
                            'textAlign': 'center',
                            'height': '20px',
                            'lineHeight': '20px',
                            'flexShrink': 0
                        }),
                        
                        # Two boxes container
                        html.Div(style={
                            'flex': '1',
                            'display': 'flex',
                            'gap': '10px',
                            'minHeight': '0',
                            'overflow': 'hidden',
                            'height': 'calc(100% - 26px)',
                            'maxHeight': 'calc(100% - 26px)'
                        }, children=[
                            # Left box: guitarists
                            html.Div(style={
                                'flex': 1,
                                'display': 'flex',
                                'flexDirection': 'column',
                                'padding': '8px 6px 6px 6px',
                                'backgroundColor': f'{BRAND_NAVY}05',
                                'borderRadius': '6px',
                                'border': f'1px solid {BRAND_NAVY}15',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
                                'overflow': 'hidden',
                                'height': '100%'
                            }, children=[
                                # Box title
                                html.Div("GUITARISTS", style={
                                    'fontSize': '12px',
                                    'fontWeight': '700',
                                    'color': BRAND_NAVY,
                                    'marginBottom': '8px',
                                    'textAlign': 'center',
                                    'textTransform': 'uppercase',
                                    'height': '16px',
                                    'lineHeight': '16px',
                                    'flexShrink': 0
                                }),
                                
                                # All 3 metrics
                                html.Div(style={
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'alignItems': 'center',
                                    'gap': '8px',
                                    'marginBottom': '8px',
                                    'flexShrink': 0
                                }, children=[
                                    # Unique artists
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('unique_co_mentioned_guitarists_count', '0')}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT,
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("UNIQUE GUITARISTS", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ]),
                                    
                                    # Total co-mentions
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('total_guitarist_co_mentions', '0')}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT,
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("TOTAL CO-MENTIONS", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ]),
                                    
                                    # Avg density
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('ratio_co_ment_by_guitarist', '0')}", style={
                                            'fontSize': '20px',
                                            'color': BRAND_VIBRANT,
                                            'fontWeight': '700',
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("AVG DENSITY", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ])
                                ]),
                                
                                # Primary peer section
                                html.Div(style={
                                    'marginTop': 'auto',
                                    'padding': '8px 0',
                                    'borderTop': f'1px solid {NEUTRAL_300}',
                                    'flexShrink': 0
                                }, children=[
                                    html.Div("PRIMARY PEER", style={
                                        'fontSize': '10px',
                                        'fontWeight': '600',
                                        'color': NEUTRAL_600,
                                        'textAlign': 'center',
                                        'marginBottom': '6px'
                                    }),
                                    html.Div(f"{intro_metrics.get('top_guitarist_name', '--')}", style={
                                        'fontSize': '12px',
                                        'color': BRAND_VIBRANT,
                                        'fontWeight': '700',
                                        'textAlign': 'center',
                                        'marginBottom': '4px',
                                        'lineHeight': '1.2'
                                    }),
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'row',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'gap': '4px'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('top_guitarist_count', '0')}", style={
                                            'fontSize': '14px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT
                                        }),
                                        html.Div("CO-MENTIONS", style={
                                            'fontSize': '8px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '500',
                                            'fontStyle': 'italic'
                                        })
                                    ])
                                ])
                            ]),
                            
                            # Right box: non-guitarists
                            html.Div(style={
                                'flex': 1,
                                'display': 'flex',
                                'flexDirection': 'column',
                                'padding': '8px 6px 6px 6px',
                                'backgroundColor': f'{BRAND_NAVY}05',
                                'borderRadius': '6px',
                                'border': f'1px solid {BRAND_NAVY}15',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
                                'overflow': 'hidden',
                                'height': '100%'
                            }, children=[
                                # Box title
                                html.Div("NON-GUITARISTS", style={
                                    'fontSize': '12px',
                                    'fontWeight': '700',
                                    'color': BRAND_NAVY,
                                    'marginBottom': '8px',
                                    'textAlign': 'center',
                                    'textTransform': 'uppercase',
                                    'height': '16px',
                                    'lineHeight': '16px',
                                    'flexShrink': 0
                                }),
                                
                                # All 3 metrics
                                html.Div(style={
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'alignItems': 'center',
                                    'gap': '8px',
                                    'marginBottom': '8px',
                                    'flexShrink': 0
                                }, children=[
                                    # Unique non-guitarists
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('unique_co_mentioned_others_count', '0')}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT,
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("UNIQUE NON-GUITARISTS", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ]),
                                    
                                    # Total co-mentions
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('total_others_co_mentions', '0')}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT,
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("TOTAL CO-MENTIONS", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ]),
                                    
                                    # Avg density
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'alignItems': 'center'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('ratio_co_ment_by_other_artist', '0')}", style={
                                            'fontSize': '20px',
                                            'color': BRAND_VIBRANT,
                                            'fontWeight': '700',
                                            'lineHeight': '1',
                                            'textAlign': 'center'
                                        }),
                                        html.Div("AVG DENSITY", style={
                                            'fontSize': '10px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '600',
                                            'marginTop': '2px',
                                            'textAlign': 'center'
                                        })
                                    ])
                                ]),
                                
                                # Primary peer section
                                html.Div(style={
                                    'marginTop': 'auto',
                                    'padding': '8px 0',
                                    'borderTop': f'0.5px solid {NEUTRAL_300}',
                                    'flexShrink': 0
                                }, children=[
                                    html.Div("PRIMARY PEER", style={
                                        'fontSize': '10px',
                                        'fontWeight': '600',
                                        'color': NEUTRAL_600,
                                        'textAlign': 'center',
                                        'marginBottom': '6px'
                                    }),
                                    html.Div(f"{intro_metrics.get('top_cross_artist_name', '--')}", style={
                                        'fontSize': '12px',
                                        'color': BRAND_VIBRANT,
                                        'fontWeight': '700',
                                        'textAlign': 'center',
                                        'marginBottom': '4px',
                                        'lineHeight': '1.2'
                                    }),
                                    html.Div(style={
                                        'display': 'flex',
                                        'flexDirection': 'row',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'gap': '4px'
                                    }, children=[
                                        html.Div(f"{intro_metrics.get('top_cross_artist_count', '0')}", style={
                                            'fontSize': '14px',
                                            'fontWeight': '700',
                                            'color': BRAND_VIBRANT
                                        }),
                                        html.Div("CO-MENTIONS", style={
                                            'fontSize': '8px',
                                            'color': NEUTRAL_600,
                                            'fontWeight': '500',
                                            'fontStyle': 'italic'
                                        })
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])

def create_simple_metric_box(value, title, color):
    """Create a simple metric box for Network Metrics grid."""
    return html.Div(style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'padding': '12px 8px',
        'backgroundColor': f'{color}10',
        'borderRadius': '8px',
        'border': f'1px solid {color}30',
        'textAlign': 'center',
        'minHeight': '70px'
    }, children=[
        html.Div(value, style={
            'fontSize': '18px',
            'fontWeight': '700',
            'color': color,
            'marginBottom': '4px',
            'lineHeight': '1'
        }),
        html.Div(title, style={
            'fontSize': '9px',
            'color': NEUTRAL_600,
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'letterSpacing': '0.2px',
            'lineHeight': '1.1'
        })
    ])

def create_metric_box(title, value, value_color=BRAND_VIBRANT, title_color=NEUTRAL_600):
    """Create a metric box."""
    return html.Div(style={
        'flex': '1',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'padding': '8px 4px',
        'backgroundColor': f'{BRAND_NAVY}08',
        'borderRadius': '8px',
        'border': f'1px solid {BRAND_NAVY}15',
        'minWidth': '0',
        'height': '60px'
    }, children=[
        html.Div(str(value), style={
            'fontSize': '16px',
            'fontWeight': '700',
            'color': value_color,
            'marginBottom': '4px',
            'lineHeight': '1'
        }),
        html.Div(title, style={
            'fontSize': '10px',
            'color': title_color,
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'letterSpacing': '0.2px',
            'textAlign': 'center',
            'lineHeight': '1.1'
        })
    ])

def format_number(value):
    """Format numbers for display."""
    try:
        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.0f}K"
            else:
                return str(int(value))
        else:
            return str(value)
    except:
        return str(value)