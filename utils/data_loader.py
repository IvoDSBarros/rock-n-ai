# utils/data_loader.py
import pandas as pd
import json
import os
import ast
from utils.config import ANALYSIS_TABLE_PATH, CREW_AI_NARRATIVE_PATH 
# from config import ANALYSIS_TABLE_PATH

def get_guitarist_data():
    """Get list of guitarists with article counts from the data file."""
    try:
        if os.path.exists(ANALYSIS_TABLE_PATH):
            df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
            
            if 'total_articles' in df_analysis.columns:
                guitarist_data = df_analysis[['guitarist', 'total_articles']].copy()
                guitarist_data = guitarist_data.dropna()
                guitarist_data = guitarist_data.sort_values('total_articles', ascending=False)
                print(f"Found {len(guitarist_data)} guitarists with article counts")
                return guitarist_data
            else:
                guitarists = df_analysis['guitarist'].dropna().unique().tolist()
                print(f"Warning: 'total_articles' column not found. Found {len(guitarists)} guitarists")
                return pd.DataFrame({
                    'guitarist': guitarists,
                    'total_articles': [100] * len(guitarists)
                })
        else:
            print(f"Warning: Data file not found: {ANALYSIS_TABLE_PATH}")
            return pd.DataFrame({
                'guitarist': ["Slash", "Brian May", "James Hetfield"],
                'total_articles': [500, 300, 400]
            })
    except Exception as e:
        print(f"Error loading guitarist data: {str(e)}")
        return pd.DataFrame({
            'guitarist': ["Slash"],
            'total_articles': [500]
        })

def get_top_guitarist():
    """Get the top guitarist (most articles)."""
    guitarist_data = get_guitarist_data()
    if not guitarist_data.empty:
        top_guitarist = guitarist_data.iloc[0]['guitarist']
        print(f"Top guitarist: {top_guitarist} with {guitarist_data.iloc[0]['total_articles']} articles")
        return top_guitarist
    else:
        return "Slash"

def get_data_bar_heatmap(view_id, guitarist):
    """Loads and processes data for a specific view."""
    from utils.config import VIEW_CONFIGS
    
    if view_id not in VIEW_CONFIGS or VIEW_CONFIGS[view_id].get('is_landing'):
        view_id = 2
    
    config = VIEW_CONFIGS[view_id]
    var_name_global = config['var_global']
    var_name_long = config['var_long']
    
    if not os.path.exists(ANALYSIS_TABLE_PATH):
        print(f"Error: Data file not found: {ANALYSIS_TABLE_PATH}")
        empty_heatmap = pd.DataFrame()
        empty_global = pd.DataFrame(columns=['field', 'count'])
        return empty_heatmap, empty_global, 0, 0
    
    try:
        df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
        df_analysis_subset = df_analysis[df_analysis['guitarist'] == guitarist]
        
        if df_analysis_subset.empty:
            print(f"Warning: No data found for guitarist: {guitarist}")
            empty_heatmap = pd.DataFrame()
            empty_global = pd.DataFrame(columns=['field', 'count'])
            return empty_heatmap, empty_global, 0, 0
        
        json_str_glob_cat = df_analysis_subset[var_name_global].iloc[0]
        df_global_cat = pd.DataFrame(json.loads(json_str_glob_cat))
        top5_pct = df_global_cat['relative_pct'].sum()

        possible_fields = ['members_tags', 'guitarist_tags', 'category_tags']
        target_global_field = next((elem for elem in df_global_cat.columns if elem in possible_fields), 
                                  df_global_cat.columns[0])
        
        list_unique_artists = df_global_cat[target_global_field].tolist()

        json_str_long_cat = df_analysis_subset[var_name_long].iloc[0]
        df_long_cat = pd.DataFrame(json.loads(json_str_long_cat))
        total_counts = df_long_cat['count'].sum()
        df_long_cat = df_long_cat[df_long_cat[target_global_field].isin(list_unique_artists)]
        
        global_mentions = df_global_cat.sort_values(by='count', ascending=True).tail(10)
        bar_chart_order = global_mentions[target_global_field].tolist()
        
        heatmap_data = df_long_cat.pivot_table(
            index=target_global_field, 
            columns='year_quarter', 
            values='count', 
            aggfunc='sum', 
            fill_value=0
        )
        
        heatmap_data = heatmap_data.reindex(bar_chart_order)
        
        if len(heatmap_data) > 12:
            heatmap_data = heatmap_data.head(12)
            
        return heatmap_data, global_mentions, total_counts, top5_pct
    
    except Exception as e:
        print(f"Error loading data for view {view_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        empty_heatmap = pd.DataFrame()
        empty_global = pd.DataFrame(columns=['field', 'count'])
        return empty_heatmap, empty_global, 0, 0

def get_guitarist_metrics_intro(guitarist):
    """Loads and processes data for a specific guitarist.
    Returns tuple: (intro_metrics_dict, ratios_df)"""
    
    if not os.path.exists(ANALYSIS_TABLE_PATH):
        print(f"Error: Data file not found: {ANALYSIS_TABLE_PATH}")
        return {}, None
    
    try:
        df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
        df_analysis_subset = df_analysis[df_analysis['guitarist'] == guitarist]
        
        if df_analysis_subset.empty:
            print(f"Warning: No data found for guitarist: {guitarist}")
            return {}, None
        
        # Extract json columns and convert to dicts
        guitarist_md_json = df_analysis_subset["guitarist_md_json"].iloc[0]
        guitarist_md_dict = eval(guitarist_md_json)
        
        ratios_json = df_analysis_subset["ratios_json"].iloc[0]
        ratios_dict = eval(ratios_json)
        
        overall_metrics_json = df_analysis_subset["overall_metrics_json"].iloc[0]
        overall_metrics_dict = eval(overall_metrics_json)
        
        network_metrics = df_analysis_subset["network_metrics"].iloc[0]
        
        intro_metrics = (
            {'guitarist': guitarist}
            | guitarist_md_dict
            | {
                'overall_article_rank': f"#{overall_metrics_dict.get('overall_article_rank')}",
                'total_articles': f'{df_analysis_subset["total_articles"].iloc[0]}',
                'dataset_frequency_pct': f"{overall_metrics_dict.get('dataset_frequency_pct') * 100:.1f}%",
                'total_body_words': f"{overall_metrics_dict.get('total_body_words'):,.0f}",
                'avg_words_per_article': f"{overall_metrics_dict.get('avg_words_per_article'):,.1f}",
                'ratio_solo_focus_display': f"{ratios_dict.get('solo_focus_ratio') * 100:.1f}%",
                'ratio_guitar_focus_display': f"{ratios_dict.get('guitar_focus_ratio') * 100:.1f}%",
                'ratio_cross_artist_focus_display': f"{ratios_dict.get('cross_artist_focus_ratio') * 100:.1f}%",
            }
            | network_metrics
        )
        
        # Create ratios dataframe for the stacked bar chart
        ratios_data = {
            'category': ['Solo Focus', 'Guitarist Focus', 'Cross-Artist Focus'],
            'label': ['Solo', 'Guitarist', 'Cross-Artist'],  
            'ratio': [
                ratios_dict.get('solo_focus_ratio', 0),  
                ratios_dict.get('guitar_focus_ratio', 0), 
                ratios_dict.get('cross_artist_focus_ratio', 0)
            ],
            'percentage': [
                ratios_dict.get('solo_focus_ratio', 0) * 100,
                ratios_dict.get('guitar_focus_ratio', 0) * 100,
                ratios_dict.get('cross_artist_focus_ratio', 0) * 100
            ],
            'color': ['#94A3B8', '#3B82F6', '#1E40AF']
        } 
        
        ratios_df = pd.DataFrame(ratios_data)
        
        return intro_metrics, ratios_df
    
    except Exception as e:
        print(f"Error loading data for guitarist {guitarist}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}, None
    
def get_media_focus_solo(guitarist):
    """Loads and processes data, merging categories into a 2-way 'Ghost' narrative."""
    if not os.path.exists(ANALYSIS_TABLE_PATH):
        return pd.DataFrame()
    
    try:
        df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
        df_analysis_subset = df_analysis[df_analysis['guitarist'] == guitarist]
        
        if df_analysis_subset.empty:
            return pd.DataFrame()

        # Load the specific json string from the subset
        longitudinal_ratios_json = df_analysis_subset["longitudinal_ratios_json"].iloc[0]
        df_longitudinal_ratios = pd.DataFrame(json.loads(longitudinal_ratios_json))

        # Melt into a long format for processing
        df_long = df_longitudinal_ratios.melt(
            id_vars=['year_quarter'], 
            var_name='raw_key', 
            value_name='ratio_value'
        )

        # Merge all non-solo into 'Other Narrative Focus'
        df_long['ratio_category'] = df_long['raw_key'].apply(
            lambda x: 'Solo Focus' if x == 'ratio_solo_focus' else 'Other Narrative Focus'
        )

        df_final = df_long.groupby(['year_quarter', 'ratio_category'], as_index=False)['ratio_value'].sum()

        color_map = {
            'Solo Focus': '#94A3B8', 
            'Other Narrative Focus': '#3B82F6'
        }
        df_final['color'] = df_final['ratio_category'].map(color_map)

        # Force stacking order
        df_final['ratio_category'] = pd.Categorical(
            df_final['ratio_category'], 
            categories=['Solo Focus', 'Other Narrative Focus'], 
            ordered=True
        )

        return df_final.sort_values(['year_quarter', 'ratio_category'])
    
    except Exception as e:
        print(f"Loader Error: {e}")
        return pd.DataFrame()

def get_vocabulary_profile(guitarist):
    """Loads and processes vocabulary related data"""
    if not os.path.exists(ANALYSIS_TABLE_PATH):
        return pd.DataFrame()
    
    try:
        df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
        df_analysis_subset = df_analysis[df_analysis['guitarist'] == guitarist]
        
        if df_analysis_subset.empty:
            return pd.DataFrame()

        # Load the specific json string from the subset
        vocabulary_profile_json = df_analysis_subset["vocabulary_profile_json"].iloc[0]
        df_vocabulary_profile = pd.DataFrame(json.loads(vocabulary_profile_json))

        return df_vocabulary_profile
    
    except Exception as e:
        print(f"Loader Error: {e}")
        return pd.DataFrame()

def get_guitarist_media_flow(guitarist):
    """Retrieves the narrative flow for a specific guitarist.
    Returns list of path records with website, editorial_format, media_focus, 
    artist_density, topic_depth, and count.
    """
    if not os.path.exists(ANALYSIS_TABLE_PATH):
        return []

    try:
        df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
        df_analysis_subset = df_analysis[df_analysis['guitarist'] == guitarist]
        
        if df_analysis_subset.empty:
            return []

        # Load the specific json string from the subset
        raw_flow_data = df_analysis_subset["media_flow_json"].iloc[0]
        
        if pd.isna(raw_flow_data) or raw_flow_data == "":
            return []

        # Use ast.literal_eval to safely parse the python-style string
        flow_data = ast.literal_eval(raw_flow_data)

        # Optional: Validate structure (each record should have the expected keys)
        expected_keys = ['website', 'editorial_format', 'media_focus', 
                         'artist_density', 'topic_depth', 'count']
        
        if flow_data and isinstance(flow_data, list):
            # Check first record to ensure structure
            first_record = flow_data[0]
            if not all(key in first_record for key in expected_keys):
                print(f"Warning: Unexpected structure in media_flow_json for {guitarist}")
        
        return flow_data
    
    except Exception as e:
        print(f"Media Flow Loader Error: {e}")
        return []

#------------------------------------------------------------------------------
# CREW AI NARRATIVE 
#------------------------------------------------------------------------------
# Global cache for all paragraphs
_GUITARIST_NARRATIVES = None

def load_crew_ai_narrative(force_reload=False):
    """
    Load Crew AI narratives from the JSON file.
    """
    global _GUITARIST_NARRATIVES
    
    if _GUITARIST_NARRATIVES is not None and not force_reload:
        return _GUITARIST_NARRATIVES
    
    if not os.path.exists(CREW_AI_NARRATIVE_PATH):
        print(f"Narrative file not found: {CREW_AI_NARRATIVE_PATH}")
        return []
    
    try:
        with open(CREW_AI_NARRATIVE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract the paragraphs array
        _GUITARIST_NARRATIVES = data.get('paragraphs', [])
        print(f"Loaded {len(_GUITARIST_NARRATIVES)} paragraphs")
        return _GUITARIST_NARRATIVES
        
    except Exception as e:
        print(f"Error loading {CREW_AI_NARRATIVE_PATH}: {e}")
        return []

def get_guitarist_narrative(guitarist, view_id):
    """
    Get narrative paragraphs for a specific guitarist and view.
    Returns list of paragraph texts in correct order.
    """
    narratives = load_crew_ai_narrative()
    
    if not narratives:
        return []
    
    # Filter by guitarist and view
    filtered = [
        p for p in narratives 
        if p.get('guitarist') == guitarist and p.get('view') == view_id
    ]
    
    # Sort by paragraph number
    filtered.sort(key=lambda x: x.get('paragraph', 0))
    
    # Return just the text in order
    return [p.get('text', '') for p in filtered]

def create_narrative_paragraphs(paragraph_texts, guitarist_name, max_paragraphs=3):
    """
    Convert narrative paragraph texts into styled HTML paragraphs.
    Text contains HTML tags (<em>, <span>) that need to be rendered.
    """
    from dash import html, dcc
    from utils import FONT_FAMILY, NEUTRAL_600
    
    ai_content = []
    
    for para_text in paragraph_texts[:max_paragraphs]:
        if para_text.strip():
            ai_content.append(
                html.Div(
                    dcc.Markdown(
                        para_text,
                        dangerously_allow_html=True,
                        link_target="_blank"
                    ),
                    style={
                        'color': NEUTRAL_600,
                        'lineHeight': '1.5',
                        'fontSize': '13px',
                        'textAlign': 'justify',
                        'fontFamily': FONT_FAMILY,
                        'marginBottom': '6px',
                        'marginTop': '0'
                    }
                )
            )
    
    return ai_content or [
        html.Div(
            f"No narrative available for {guitarist_name}",
            style={
                'color': NEUTRAL_600,
                'fontStyle': 'italic',
                'fontFamily': FONT_FAMILY
            }
        )
    ]

# df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
# df_analysis_subset = df_analysis[df_analysis['guitarist'] == 'Slash']

# test = get_vocabulary_profile('Slash')
# print(test)

# test = get_guitarist_media_flow('Slash')
# print(test)

# intro_metrics, ratios_df = get_guitarist_metrics_intro('Slash')

# for k,v in intro_metrics.items():
#     print(f"{k}: {v}")

# # Right after getting the data:
# print("=== RATIOS_DF DEBUG ===")
# print(f"Type: {type(ratios_df)}")
# print(f"Is DataFrame: {isinstance(ratios_df, pd.DataFrame)}")
# if isinstance(ratios_df, pd.DataFrame):
#     print(f"Shape: {ratios_df.shape}")
#     print(f"Columns: {ratios_df.columns.tolist()}")
#     print(f"Data:\n{ratios_df}")
# else:
#     print(f"Value: {ratios_df}")
# print("======================")