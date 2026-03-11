# app.py
from dash import Dash, dcc, html, ALL, callback_context
from dash.dependencies import Input, Output
import json

from utils import get_top_guitarist, FONT_FAMILY, BRAND_VIBRANT, get_guitarist_data, LAST_VIEW_ID
from views.view1_landing import create_view_1_landing
from views.analysis_view import create_analysis_view
from views.view2_intro import create_intro_view
from views.view3_media_focus_solo import create_media_solo_focus_view
from views.view7_vocabulary_profile import create_vocabulary_profile_view
from views.view8_media_flow import create_media_flow_view

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

DEFAULT_GUITARIST = get_top_guitarist()
nav_state = {'current_view': 1, 'current_guitarist': DEFAULT_GUITARIST}

def get_view_layout(view_id, selected_guitarist):
    """Get layout for specific view and guitarist."""
    nav_state['current_guitarist'] = selected_guitarist
    nav_state['current_view'] = view_id

    if view_id == 1:
        return create_view_1_landing(selected_guitarist)
    if view_id == 2:
        return create_intro_view(selected_guitarist, view_id)
    if view_id == 3:
        return create_media_solo_focus_view(selected_guitarist, view_id)
    if view_id in [4, 5, 6]:
        return create_analysis_view(view_id, selected_guitarist)
    if view_id == 7:
        return create_vocabulary_profile_view(selected_guitarist, view_id)
    if view_id == 8:
        return create_media_flow_view(selected_guitarist, view_id)

    return create_view_1_landing(selected_guitarist)

#------------------------------------------------------------------------------
# APP LAYOUT
#------------------------------------------------------------------------------
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='selected-guitarist-store', data=DEFAULT_GUITARIST),
    html.Div(id='dummy-output', style={'display': 'none'})
])

#------------------------------------------------------------------------------
# PYTHON CALLBACKS
#------------------------------------------------------------------------------

# 1. Update guitarist from chart click
@app.callback(
    Output('selected-guitarist-store', 'data'),
    Input('view-1-guitarist-chart', 'clickData'),
    prevent_initial_call=True
)
def update_selected_guitarist_from_chart(clickData):
    if clickData and 'points' in clickData and clickData['points']:
        selected_guitarist = clickData['points'][0]['customdata']
        nav_state['current_guitarist'] = selected_guitarist
        return selected_guitarist
    return nav_state['current_guitarist']

# 2. Update View 1 displays
@app.callback(
    [Output('view-1-selected-guitarist', 'children'),
     Output('view-1-chart-selected-guitarist', 'children')],
    Input('selected-guitarist-store', 'data')
)
def update_view_1_display(selected_guitarist):
    return selected_guitarist, selected_guitarist

# 3. Update chart figure
@app.callback(
    Output('view-1-guitarist-chart', 'figure'),
    Input('selected-guitarist-store', 'data')
)
def update_chart_highlight(selected_guitarist):
    from components.charts import create_guitarist_selection_chart

    try:
        data = get_guitarist_data()
        return create_guitarist_selection_chart(data, selected_guitarist)
    except Exception as e:
        print(f"Error updating chart: {e}")
        import plotly.graph_objects as go
        return go.Figure()

# 4. Main navigation callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input({'type': 'nav-btn', 'action': ALL}, 'n_clicks'),
     Input('selected-guitarist-store', 'data')],
    prevent_initial_call=True
)
def handle_navigation(pathname, nav_clicks, selected_guitarist):
    ctx = callback_context

    if not ctx.triggered:
        return get_view_layout(1, DEFAULT_GUITARIST)

    trigger = ctx.triggered[0]
    prop_id = trigger['prop_id']

    if 'selected-guitarist-store' in prop_id:
        nav_state['current_guitarist'] = selected_guitarist

    if 'url' in prop_id:
        nav_state['current_view'] = 1
        return get_view_layout(1, selected_guitarist)

    if 'nav-btn' in prop_id:
        button_info = json.loads(prop_id.split('.')[0])
        action = button_info.get('action')

        if action == 'prev':
            if nav_state['current_view'] > 1:
                nav_state['current_view'] -= 1
        elif action == 'next':
            current = nav_state['current_view']
            if current == LAST_VIEW_ID:
                nav_state['current_view'] = 1
            elif current == 1:
                nav_state['current_view'] = 2
            elif current < LAST_VIEW_ID:
                nav_state['current_view'] += 1

    return get_view_layout(nav_state['current_view'], nav_state['current_guitarist'])

# 5. Initial page load
@app.callback(
    Output('page-content', 'children', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate'
)
def initial_load(pathname):
    return get_view_layout(1, DEFAULT_GUITARIST)

#------------------------------------------------------------------------------
# HTML TEMPLATE
#------------------------------------------------------------------------------
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            html, body {{
                height: 100%;
                width: 100%;
                overflow: hidden !important;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                font-family: {FONT_FAMILY};
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}

            #react-entry-point {{
                height: 100vh !important;
                width: 100vw !important;
                overflow: hidden !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
            }}

            button {{
                transition: all 0.2s ease !important;
            }}

            [id*="nav-btn"]:hover {{
                transform: scale(1.05);
            }}

            button:disabled {{
                opacity: 0.5 !important;
                cursor: not-allowed !important;
            }}

            button:disabled:hover {{
                transform: none !important;
            }}

            /* ===== MOBILE/TABLET WARNING ===== */
            .device-warning {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(0, 0, 0, 0.95);
                z-index: 10000;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                box-sizing: border-box;
                font-family: {FONT_FAMILY};
                text-align: center;
            }}

            /* Show on screens smaller than 1024px (tablets and phones) */
            @media (max-width: 1024px) {{
                .device-warning {{
                    display: flex !important;
                }}
                #page-content {{
                    display: none !important;
                }}
            }}

            .device-warning h2 {{
                color: white;
                margin-bottom: 15px;
                font-size: 24px;
            }}

            .device-warning p {{
                color: white;
                text-align: center;
                margin-bottom: 0;
                max-width: 400px;
                line-height: 1.6;
                font-size: 16px;
            }}

            .device-warning .icon {{
                font-size: 60px;
                margin-bottom: 20px;
            }}
            /* ===== END OF DEVICE WARNING STYLES ===== */

            /* ===== TOOLTIP STYLES ===== */
            [id^="info-tooltip-"] {{
                visibility: hidden !important;
                opacity: 0 !important;
                transition: opacity 0.2s ease !important;
                pointer-events: auto !important;
                z-index: 9999 !important;
            }}

            [id^="info-icon-"]:hover + [id^="info-tooltip-"] {{
                visibility: visible !important;
                opacity: 1 !important;
            }}

            [id^="info-tooltip-"]:hover {{
                visibility: visible !important;
                opacity: 1 !important;
            }}

            [id^="info-icon-"]:hover {{
                transform: scale(1.1) !important;
                background-color: {BRAND_VIBRANT} !important;
                cursor: help !important;
            }}

            /* ===== NARRATIVE PANEL SCROLLBAR ===== */
            .ai-narrative-scrollable {{
                scrollbar-width: thin !important;
                scrollbar-color: #cbd5e1 #f1f5f9 !important;
            }}

            .ai-narrative-scrollable::-webkit-scrollbar {{
                width: 6px !important;
            }}

            .ai-narrative-scrollable::-webkit-scrollbar-track {{
                background: #f1f5f9 !important;
                border-radius: 6px !important;
            }}

            .ai-narrative-scrollable::-webkit-scrollbar-thumb {{
                background: #cbd5e1 !important;
                border-radius: 6px !important;
                border: 1px solid #e2e8f0 !important;
            }}

            .ai-narrative-scrollable::-webkit-scrollbar-thumb:hover {{
                background: #94a3b8 !important;
            }}

            /* ===== LANDING PAGE SCROLLBAR ===== */
            .landing-scrollable {{
                scrollbar-width: thin !important;
                scrollbar-color: #cbd5e1 #f1f5f9 !important;
            }}

            .landing-scrollable::-webkit-scrollbar {{
                width: 6px !important;
            }}

            .landing-scrollable::-webkit-scrollbar-track {{
                background: #f1f5f9 !important;
                border-radius: 6px !important;
            }}

            .landing-scrollable::-webkit-scrollbar-thumb {{
                background: #cbd5e1 !important;
                border-radius: 6px !important;
                border: 1px solid #e2e8f0 !important;
            }}

            .landing-scrollable::-webkit-scrollbar-thumb:hover {{
                background: #94a3b8 !important;
            }}

            /* ===== NARRATIVE TEXT FORMATTING ===== */
            .ai-narrative-scrollable em {{
                font-style: italic;
            }}

            .ai-narrative-scrollable .citation {{
            }}
        </style>
    </head>
    <body>
        <!-- DEVICE WARNING - SHOWN ON TABLETS AND PHONES (NO CONTINUE BUTTON) -->
        <div class="device-warning" id="device-warning">
            <div class="icon">⚠️</div>
            <h2>Desktop View Recommended</h2>
            <p>For optimal performance and full access to all interactive features, please view this application on a desktop or laptop computer.</p>
        </div>

        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

#------------------------------------------------------------------------------
# RUN THE APP
#------------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("🎸 Rock N' AI: An AI Narrative Engine for Guitar Icon Media Intelligence")
    print("=" * 60)
    print(f"\nStarting app at: http://localhost:8050")
    print("=" * 60)
    print(f"Views available:")
    print(f"  1 - Landing ")
    print(f"  2 - Intro")
    print(f"  3 - Solo Focus Narrative")
    print(f"  4 - Guitarist Focus Narrative")
    print(f"  5 - Cross-Artist Focus Narrative")
    print(f"  6 - Thematic Patterns Analysis")
    print(f"  7 - Vocabulary Profile")
    print(f"  8 - Media Flow Overview")
    print("=" * 60)

    app.run(debug=True, port=8050)