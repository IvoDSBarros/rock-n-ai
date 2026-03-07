# views/analysis_view.py
from dash import html
from utils import (
    FONT_FAMILY, NEUTRAL_100, NEUTRAL_800, NEUTRAL_600, NEUTRAL_300,
    BRAND_VIBRANT, BRAND_NAVY,
    VIEW_CONFIGS
)
from components.panels import create_ai_narrative_panel, create_bar_chart_panel, create_heatmap_panel
from components.header import create_header
from utils.data_loader import get_data_bar_heatmap, get_guitarist_narrative, create_narrative_paragraphs
import pandas as pd
import numpy as np

def create_analysis_view(view_id, selected_guitarist):
    """Create a reusable analysis view for views 4, 5, and 6."""
    
    # Check if view_id is valid (4, 5, or 6)
    if view_id not in [4, 5, 6]:
        print(f"Warning: View {view_id} not in [4, 5, 6]. Defaulting to view 4.")
        view_id = 4
    
    config = VIEW_CONFIGS.get(view_id, VIEW_CONFIGS[4])
    
    # Get narrative paragrahphs from data loader
    narrative_paragraphs = get_guitarist_narrative(selected_guitarist, view_id=view_id)
    ai_content = create_narrative_paragraphs(narrative_paragraphs, selected_guitarist)

    # Get chart data
    # Handling View 6 differently: load thematic data
    if view_id == 6:
        heatmap_df, global_df, total_counts, top5_pct = get_thematic_data(selected_guitarist)
    else:
        try:
            heatmap_df, global_df, total_counts, top5_pct = get_data_bar_heatmap(view_id, selected_guitarist)
        except Exception as e:
            print(f"Error getting data for view {view_id}: {e}")
            heatmap_df, global_df, total_counts, top5_pct = None, None, 0, 0
    
    # Build right panel children list
    right_panel_children = []
    
    # Add info icon only for views 4 and 5
    if view_id in [4, 5]:
        right_panel_children.append(
            html.Div(style={
                'position': 'absolute',
                'top': '5px',
                'right': '16px',
                'zIndex': '100',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'flex-end'
            }, children=[
                html.Div(style={
                    'position': 'relative',
                    'display': 'inline-block'
                }, children=[
                    # Info Icon
                    html.Div(
                        id=f'info-icon-{view_id}',
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'width': '18px',
                            'height': '18px',
                            'backgroundColor': BRAND_VIBRANT,
                            'borderRadius': '50%',
                            'cursor': 'help',
                            'border': f'1px solid {BRAND_VIBRANT}',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
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
                            'width': '300px',
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
                            'fontSize': '13px',
                            'lineHeight': '1.5',
                            'fontFamily': FONT_FAMILY,
                            'opacity': '0',
                            'transition': 'opacity 0.2s ease'
                        },
                        children=get_tooltip_content(view_id)
                    )
                ])
            ])
        )
    
    # Add charts for all views
    if view_id == 6:
        if global_df is not None:
            right_panel_children.append(
                create_thematic_chart_panel(config, global_df, total_counts, top5_pct)
            )
        if heatmap_df is not None:
            right_panel_children.append(
                create_thematic_heatmap_panel(config, heatmap_df)
            )
    else:
        if global_df is not None:
            right_panel_children.append(
                create_bar_chart_panel(config, global_df, total_counts, top5_pct)
            )
        if heatmap_df is not None:
            right_panel_children.append(
                create_heatmap_panel(config, heatmap_df)
            )
    
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
        
        # Standardized header
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
            # Left panel: AI Narrative
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'minHeight': '0',
                'overflow': 'hidden'
            }, children=[
                create_ai_narrative_panel(view_id, ai_content)
            ]),
            
            # Right panel: visualizations
            html.Div(style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '12px',
                'minHeight': '0',
                'overflow': 'hidden',
                'position': 'relative'
            }, children=right_panel_children)
        ])
    ])

def get_thematic_data(selected_guitarist):
    """Load thematic data for View 6."""
    try:
        from utils.data_loader import get_data_bar_heatmap
        return get_data_bar_heatmap(6, selected_guitarist)
    except Exception as e:
        print(f"Error loading thematic data for {selected_guitarist}: {e}")
        return None, None, 0, 0

def create_thematic_chart_panel(config, global_df, total_counts, top5_pct):
    """Create thematic bar chart panel for View 6."""
    if global_df is None or global_df.empty:
        return html.Div("No data available")
    
    from components.panels import create_bar_chart_panel
    return create_bar_chart_panel(config, global_df, total_counts, top5_pct)

def create_thematic_heatmap_panel(config, heatmap_df):
    """Create thematic heatmap panel for View 6."""
    if heatmap_df is None or heatmap_df.empty:
        return html.Div("No data available")
    
    from components.panels import create_heatmap_panel
    return create_heatmap_panel(config, heatmap_df)

def get_tooltip_content(view_id):
    """Return tooltip content specific to each view."""
    
    if view_id == 4:
        return [
            # Main tooltip title with guitar icon
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'marginBottom': '12px'}, children=[
                html.I(className="fas fa-guitar", style={
                    'color': BRAND_VIBRANT,
                    'fontSize': '16px',
                    'backgroundColor': f'{BRAND_VIBRANT}10',
                    'padding': '8px',
                    'borderRadius': '8px'
                }),
                html.Div("GUITAR FOCUS RATIO", style={
                    'color': BRAND_NAVY,
                    'fontWeight': '700',
                    'fontSize': '13px',
                    'letterSpacing': '1px'
                })
            ]),
            
            # Explanation
            html.Div([
                html.Div("This ratio tracks the volume of articles where the subject is featured exclusively alongside other guitarists, with no non-guitarists mentioned. It identifies media coverage purely centered on technical skill, gear, and instrument-specific peer rankings.", 
                        style={'color': NEUTRAL_600, 'textAlign': 'justify', 'fontSize': '11px', 'marginBottom': '12px'})
            ]),
            
            # Note box with info icon
            html.Div(style={
                'backgroundColor': f'{BRAND_VIBRANT}08',
                'borderRadius': '6px',
                'padding': '12px',
                'border': f'1px dashed {BRAND_VIBRANT}30'
            }, children=[
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '6px', 'marginBottom': '6px'}, children=[
                    html.I(className="fas fa-info-circle", style={'color': BRAND_VIBRANT, 'fontSize': '12px'}),
                    html.Div("NOTE", style={
                        'color': BRAND_NAVY,
                        'fontWeight': '700',
                        'fontSize': '11px',
                        'letterSpacing': '0.5px'
                    })
                ]),
                html.P("This represents a percentage of article volume, not a count of individuals; it should not be compared to the Unique Guitarist metrics found in the Overview.", style={
                    'color': NEUTRAL_600,
                    'fontSize': '11px',
                    'margin': '0',
                    'lineHeight': '1.5',
                    'textAlign': 'justify'
                })
            ])
        ]
    
    else:  # view_id == 5
        return [
            # Main tooltip title with handshake icon
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'marginBottom': '12px'}, children=[
                html.I(className="fas fa-users", style={
                    'color': BRAND_VIBRANT,
                    'fontSize': '16px',
                    'backgroundColor': f'{BRAND_VIBRANT}10',
                    'padding': '8px',
                    'borderRadius': '8px'
                }),
                html.Div("CROSS-ARTIST FOCUS RATIO", style={
                    'color': BRAND_NAVY,
                    'fontWeight': '700',
                    'fontSize': '13px',
                    'letterSpacing': '1px'
                })
            ]),
            
            # Explanation
            html.Div([
                html.Div("Measures coverage where the subject appears alongside non-guitarists such as vocalists, drummers, and other instrumentalists. If a guitarist is mentioned along with a non-guitarist and the subject, the article will be assigned under this ratio. Captures broader industry presence, band dynamics, and cross-genre collaborations beyond the guitar-centric sphere.", 
                        style={'color': NEUTRAL_600, 'textAlign': 'justify', 'fontSize': '11px', 'marginBottom': '12px'})
            ]),
            
            # Note box with info icon (same as view 4)
            html.Div(style={
                'backgroundColor': f'{BRAND_VIBRANT}08',
                'borderRadius': '6px',
                'padding': '12px',
                'border': f'1px dashed {BRAND_VIBRANT}30'
            }, children=[
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '6px', 'marginBottom': '6px'}, children=[
                    html.I(className="fas fa-info-circle", style={'color': BRAND_VIBRANT, 'fontSize': '12px'}),
                    html.Div("NOTE", style={
                        'color': BRAND_NAVY,
                        'fontWeight': '700',
                        'fontSize': '11px',
                        'letterSpacing': '0.5px'
                    })
                ]),
                html.P("This metric reflects article volume percentages, distinct from the Unique Non-Guitarist counts in the Overview, which track individual collaborators.", style={
                    'color': NEUTRAL_600,
                    'fontSize': '11px',
                    'margin': '0',
                    'lineHeight': '1.5',
                    'textAlign': 'justify'
                })
            ])
        ]