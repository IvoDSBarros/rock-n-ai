# components/charts.py
import plotly.graph_objects as go
from dash import html
from dash_holoniq_wordcloud import DashWordcloud
from collections import Counter
from utils import FONT_FAMILY, BRAND_NAVY, BRAND_VIBRANT, NEUTRAL_800, NEUTRAL_600, NEUTRAL_300, TRANSPARENT

def create_guitarist_selection_chart(guitarist_data, current_guitarist):
    """Create interactive bar chart for guitarist selection in View 1."""
    
    if guitarist_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No data available", x=0.5, y=0.5),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            font=dict(family=FONT_FAMILY, size=14, color=NEUTRAL_600)
        )
        return fig
    
    guitarist_data = guitarist_data.sort_values('total_articles', ascending=False)
    
    colors = []
    for i, guitarist in enumerate(guitarist_data['guitarist']):
        if guitarist == current_guitarist:
            colors.append(BRAND_VIBRANT)
        else:
            opacity = 0.3 + ((len(guitarist_data) - i - 1) / len(guitarist_data)) * 0.5
            colors.append(f"rgba({int(NEUTRAL_600[1:3], 16)}, {int(NEUTRAL_600[3:5], 16)}, {int(NEUTRAL_600[5:7], 16)}, {opacity})")    

    fig = go.Figure(go.Bar(
        x=guitarist_data['total_articles'],
        y=guitarist_data['guitarist'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6
        ),
        text=guitarist_data['total_articles'],
        textposition='outside',
        textfont=dict(size=12, color=NEUTRAL_800, weight='bold', family=FONT_FAMILY),
        width=0.7,
        hovertemplate='<b>%{y}</b><br>Articles: %{x}<extra></extra>',
        customdata=guitarist_data['guitarist']
    ))
    
    fig.update_layout(
        title=dict(
            text="Web Media Articles Per Guitarist", 
            font=dict(family=FONT_FAMILY, size=12), 
            x=0.5,
            y=0.99,
            yanchor='top',
            pad=dict(t=0, b=0)
        ),
        margin=dict(l=5, r=5, t=20, b=5),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        font=dict(family=FONT_FAMILY, size=12, color=NEUTRAL_600),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            gridcolor=NEUTRAL_300,
            gridwidth=0.5,
            zeroline=False,
            tickfont=dict(size=11, family=FONT_FAMILY)
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder='total ascending',
            tickfont=dict(size=11, color=NEUTRAL_600, family=FONT_FAMILY)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family=FONT_FAMILY
        ),
        showlegend=False,
        clickmode='event+select',
        dragmode=False
    )
    
    return fig

def create_compact_global_mentions_fig(data):
    """Create horizontal bar chart with count and percentage labels."""
    if data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No data available", x=0.5, y=0.5),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            font=dict(family=FONT_FAMILY, size=11, color=NEUTRAL_600)
        )
        return fig
    
    colors = [f"rgba(59, 130, 246, {0.3 + (i/len(data))*0.7})" for i in range(len(data))]
    
    possible_fields = ['members_tags', 'guitarist_tags', 'category_tags']
    target_global_field = next((elem for elem in data.columns if elem in possible_fields), 
                              data.columns[0] if len(data.columns) > 0 else 'field')
    
    if 'relative_pct' in data.columns:
        counts = data['count'].astype(int)
        percentages = (data['relative_pct'] * 100).round(1)
        text_labels = counts.astype(str) + " (" + percentages.astype(str) + "%)"
    else:
        text_labels = data['count'].astype(int).astype(str)
    
    if 'relative_pct' in data.columns:
        hovertemplate = '<b>%{y}</b><br>Count: %{x}<br>% of Total: %{customdata:.1f}%<extra></extra>'
        customdata = data['relative_pct'] * 100
    else:
        hovertemplate = '<b>%{y}</b><br>Count: %{x}<extra></extra>'
        customdata = None
    
    fig = go.Figure(go.Bar(
        x=data['count'],
        y=data[target_global_field],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6
        ),
        text=text_labels.tolist(),
        textposition='outside',
        textfont=dict(size=9, color=BRAND_VIBRANT, weight='bold', family=FONT_FAMILY),
        width=0.6,
        hovertemplate=hovertemplate,
        customdata=customdata
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=5, t=0, b=0),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        font=dict(family=FONT_FAMILY, size=10, color=NEUTRAL_600),
        xaxis=dict(
            visible=False,
            range=[0, data['count'].max() * 1.15]
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder='array',
            categoryarray=data[target_global_field].tolist(),
            tickfont=dict(size=9, color=NEUTRAL_600, family=FONT_FAMILY)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color=NEUTRAL_800
        ),
        showlegend=False
    )
    
    return fig

def create_compact_heatmap_fig(data):
    """Create compact heatmap for analysis views."""
    if data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No data available", x=0.5, y=0.5),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            font=dict(family=FONT_FAMILY, size=10, color=NEUTRAL_600)
        )
        return fig
    
    y_axis_order = data.index.tolist()
    
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=[
            [0, 'rgba(15, 23, 42, 0.1)'],
            [0.3, 'rgba(59, 130, 246, 0.3)'],
            [0.7, 'rgba(59, 130, 246, 0.7)'],
            [1, BRAND_VIBRANT]
        ],
        xgap=1,
        ygap=1,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>Quarter: %{x}<br>Count: %{z}<extra></extra>',
        showscale=False
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=5, t=0, b=0),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        font=dict(family=FONT_FAMILY, size=9, color=NEUTRAL_600),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=8, family=FONT_FAMILY),
            showgrid=False
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=y_axis_order,
            tickfont=dict(size=9, family=FONT_FAMILY)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color=NEUTRAL_800
        )
    )
    
    return fig

def create_focus_ratios_waffle_chart(ratios_df, height=180, width=180):
    """Create waffle chart."""
    
    # If no data, return empty figure
    if ratios_df is None or ratios_df.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=height,
            width=width,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(
                text="No data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color=NEUTRAL_600)
            )]
        )
        return fig
    
    try:
        labels = ratios_df['label'].tolist()
        percentages = ratios_df['percentage'].tolist()
        colors = ratios_df['color'].tolist()
        
        if len(labels) > 3:
            labels = labels[:3]
            percentages = percentages[:3]
            colors = colors[:3]
        
        # 10x10 grid
        grid_size = 10
        total_cells = grid_size * grid_size
        
        # Calculate how many circles for each category
        cell_counts = [int(round(p * total_cells / 100)) for p in percentages]
        
        # Fix any rounding errors to total exactly 100
        total_assigned = sum(cell_counts)
        if total_assigned != total_cells:
            diff = total_cells - total_assigned
            max_idx = cell_counts.index(max(cell_counts))
            cell_counts[max_idx] += diff
        
        # Create coordinates for circles
        x_coords = []
        y_coords = []
        circle_colors = []
        hover_texts = []
        
        cell_idx = 0
        for cat_idx, (count, color, label, pct) in enumerate(zip(cell_counts, colors, labels, percentages)):
            for _ in range(count):
                row = cell_idx // grid_size
                col = cell_idx % grid_size
                
                # Position circles in grid
                x_coords.append(col + 0.5)
                y_coords.append(grid_size - row - 0.5)
                circle_colors.append(color)
                hover_texts.append(f"{label}: {pct:.1f}%")
                cell_idx += 1
        
        # Create the figure
        fig = go.Figure()
        
        # Main waffle circles
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=16,             
                symbol='square-dot',  
                color=circle_colors,
                line=dict(
                    color='white',   
                    width=1
                )
            ),
            text=hover_texts,
            hoverinfo='text',
            showlegend=False
        ))
                    
        fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, size=10, color=NEUTRAL_800),
            
            # Chart area - use 100% of space
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, grid_size],
                fixedrange=True,
                scaleanchor="y",
                scaleratio=1,
                domain=[0, 1],
                constrain="domain"
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, grid_size],
                fixedrange=True,
                domain=[0, 1]
            ),
            
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family=FONT_FAMILY
            ),
            
            showlegend=False,
            title=None,
            autosize=False,
            dragmode=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating waffle chart: {e}")
        # Return minimal error figure
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=height,
            width=width,
            annotations=[dict(
                text=f"Error: {str(e)[:50]}",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='red')
            )]
        )
        return fig

def create_streamgraph(df):
    if df.empty:
        return go.Figure()

    category_order = ['Solo Focus', 'Other Narrative Focus']
    fig = go.Figure()

    # Dynamic trace genaration
    for cat in category_order:
        cat_df = df[df['ratio_category'] == cat].copy()
        if cat_df.empty: continue
        
        cat_color = cat_df['color'].iloc[0]
        
        # Liquid spline logic
        line_style = dict(width=1.5, color='#FFFFFF', shape='spline', smoothing=1.3)
        if cat == 'Other Narrative Focus':
            line_style['width'] = 0 

        fig.add_trace(go.Scatter(
            x=cat_df['year_quarter'],
            y=cat_df['ratio_value'],
            mode='lines',
            line=line_style,
            stackgroup='one',
            fillcolor=cat_color,
            hoveron='fills+points',
            hovertemplate=f"<b>{cat}</b><br>Share: %{{y:.1%}}<extra></extra>"
        ))

    # Dynamic ratio value markers
    solo_df = df[df['ratio_category'] == 'Solo Focus']
    if not solo_df.empty:
        peak_row = solo_df.loc[solo_df['ratio_value'].idxmax()]
        low_row = solo_df.loc[solo_df['ratio_value'].idxmin()]

        markers = [
            {'row': peak_row, 'icon': '▲', 'y_pos': 0.98, 'color': BRAND_NAVY},
            {'row': low_row, 'icon': '▼', 'y_pos': 0.02, 'color': NEUTRAL_600}
        ]

        for m in markers:
            val = m['row']['ratio_value'] 
            
            fig.add_annotation(
                x=m['row']['year_quarter'],
                y=m['y_pos'],           
                xref="x",
                yref="paper",
                text=f"<span style='font-family:monospace; font-weight:700;'>{val:.1%}</span> {m['icon']}",
                showarrow=False,
                font=dict(
                    size=9, 
                    color=m['color'], 
                    family=FONT_FAMILY
                ),
                bgcolor="rgba(255,255,255,0.6)",
                borderpad=3,
                opacity=0.8
            )

    fig.update_layout(
        margin=dict(l=0, r=10, t=15, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, size=9, color=NEUTRAL_600),
        hovermode="x unified",
        showlegend=False, 
        xaxis=dict(showgrid=False, tickangle=-45, linecolor=NEUTRAL_300),
        yaxis=dict(
            showgrid=True, 
            gridcolor=NEUTRAL_300, 
            tickformat='.0%', 
            range=[0, 1]
        )
    )
    
    return fig

def create_wordcloud(df, pos_category='nouns'):
    """Word cloud with proper tooltips showing actual frequencies"""
    
    filtered_df = df[df['pos'] == pos_category].copy()
    
    if filtered_df.empty:
        return html.Div(f"No {pos_category}", style={
            'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
            'height': '100%', 'color': '#666', 'fontSize': '12px'
        })
    
    # Create list with word, weight and tooltip
    words_list = []
    for _, row in filtered_df.iterrows():
        word = str(row['word']).strip()
        count = int(row['count'])
        tooltip = f"{word}: {count} mentions"
        words_list.append([word, count, tooltip])
    
    # Color based on pos category
    if pos_category == 'nouns':
        color = '#94A3B8'  
    elif pos_category == 'verbs':
        color = '#3B82F6'  
    else:
        color = '#1E40AF'
    
    return html.Div(
        style={
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'white',
            'position': 'relative',
            'overflow': 'hidden',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        },
        children=[
            html.Div(
                style={
                    'width': '600px',
                    'height': '120px',
                    'margin': '0 auto'
                },
                children=[
                    DashWordcloud(
                        id=f'wordcloud-{pos_category}',
                        list=words_list,
                        width=600,
                        height=120,
                        gridSize=8,
                        color=color,
                        backgroundColor='white',
                        shape='square',
                        rotateRatio=0.2,
                        fontFamily=FONT_FAMILY,
                        fontWeight='normal',
                        shrinkToFit=True,
                        hover=True,
                        weightFactor=1.0,
                        minSize=6
                    )
                ]
            )
        ]
    )

def create_parallel_categories(flow_data):
    """
    Creates a Parallel Categories diagram from path-based flow data.
    All dimensions sorted by category frequency (descending).
    """
    if not flow_data: 
        return go.Figure()

    # Color mapping
    WEBSITE_COLORS = {
        'Louder': 'rgba(30, 64, 175, 0.8)',      # Dark blue (#1E40AF)
        'Loudwire': 'rgba(59, 130, 246, 0.8)',    # Light blue (#3B82F6)
        'Kerrang!': 'rgba(234, 179, 8, 0.8)',     # Yellow (#EAB308) 
        'Ultimate Classic Rock': 'rgba(148, 163, 184, 0.8)', # Light grey (#94A3B8)
        'Planet Rock': 'rgba(168, 139, 115, 0.8)', # Warm taupe/brown
        'The New York Times': 'rgba(34, 197, 94, 0.8)'  # Green (#22C55E)
    } 
    
    websites = []
    editorial_formats = []
    media_focuses = []
    artist_densities = []
    topic_depths = []
    
    for record in flow_data:
        count = record.get('count', 1)
        website = record.get('website', 'Unknown')
        format_val = record.get('editorial_format', 'Unknown')
        focus_val = record.get('media_focus', 'Unknown')
        density_val = record.get('artist_density', 'Unknown')
        depth_val = record.get('topic_depth', 'Unknown')
        
        for _ in range(count):
            websites.append(website)
            editorial_formats.append(format_val)
            media_focuses.append(focus_val)
            artist_densities.append(density_val)
            topic_depths.append(depth_val)
    
    # Calculate order
    website_order = [w for w, _ in Counter(websites).most_common()]
    format_order = [f for f, _ in Counter(editorial_formats).most_common()]
    focus_order = [f for f, _ in Counter(media_focuses).most_common()]
    density_order = [d for d, _ in Counter(artist_densities).most_common()]
    depth_order = [d for d, _ in Counter(topic_depths).most_common()]
    
    # Create dimensions
    dimensions = [
        go.parcats.Dimension(
            values=websites,
            label='Website',
            categoryorder='array',
            categoryarray=website_order
        ),
        go.parcats.Dimension(
            values=editorial_formats,
            label='Editorial Format',
            categoryorder='array',
            categoryarray=format_order
        ),
        go.parcats.Dimension(
            values=media_focuses,
            label='Media Focus',
            categoryorder='array',
            categoryarray=focus_order
        ),
        go.parcats.Dimension(
            values=artist_densities,
            label='Artist Density',
            categoryorder='array',
            categoryarray=density_order
        ),
        go.parcats.Dimension(
            values=topic_depths,
            label='Topic Depth',
            categoryorder='array',
            categoryarray=depth_order
        )
    ]
    
    # Color by website
    line_colors = [WEBSITE_COLORS.get(w, 'rgba(203, 213, 225, 0.6)') for w in websites]
    
    # Create figure
    fig = go.Figure(data=[go.Parcats(
        dimensions=dimensions,
        line={'color': line_colors, 'shape': 'hspline'},
        hoveron='color',
        arrangement='freeform',
        bundlecolors=False,
        sortpaths='forward'
    )])
    
    # Layout
    fig.update_layout(
        margin=dict(l=50, r=50, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family=FONT_FAMILY, 
            size=11, 
            color=NEUTRAL_600
        ),
        autosize=True
    )
    
    # Dimension headers
    fig.update_traces(
        labelfont=dict(size=10, family=FONT_FAMILY, color=NEUTRAL_800)
    )
    
    return fig