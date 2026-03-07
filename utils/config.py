# utils/config.py
import os

# --------------------------------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------------------------------
# Get project root directory (dash_ui_project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory and paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
ANALYSIS_TABLE_PATH = os.path.join(DATA_DIR, 'master_analysis_table.parquet')
CREW_AI_NARRATIVE_PATH = os.path.join(DATA_DIR, 'crew_ai_narrative.json')
os.makedirs(DATA_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# FONT CONFIGURATION
# --------------------------------------------------------------------------
FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
STORY_TITLE = "Rock N' AI: An AI Narrative Engine for Guitar Icon Media Intelligence"

# --------------------------------------------------------------------------
# COLOR PALETTE
# --------------------------------------------------------------------------
BRAND_NAVY = "#0F172A"
BRAND_VIBRANT = "#3B82F6"
ACCENT_CYAN = "#06B6D4"
ACCENT_EMERALD = "#10B981"
NEUTRAL_800 = "#1E293B"
NEUTRAL_600 = "#475569"
NEUTRAL_300 = "#CBD5E1"
NEUTRAL_100 = "#F1F5F9"
TRANSPARENT = "rgba(0,0,0,0)"

# --------------------------------------------------------------------------
# VIEW CONFIGURATIONS
# --------------------------------------------------------------------------
LAST_VIEW_ID = 8

VIEW_CONFIGS = {
    1: {
        'title': "Guitarist Inventory",
        'subtitle': "Choose a guitarist to map their digital landscape",
        'view_number': '1',
        'is_landing': True
    },
    2: {
        'title': "Overview",
        'subtitle': "Integrated Profile Analysis",
        'view_number': '2',
        'is_landing': False
    },

    3: {
        'title': 'Media Focus Breakdown',
        'subtitle': 'Solo Focus Narrative',
        'title_top_viz': "Solo Context Share",
        'title_bottom_viz': "Solo Context Over Time",
        'view_number': '3',
        'is_landing': False
    },

    4: {
        'var_global': 'global_guitar_json',
        'var_long': 'longitudinal_guitar_json',
        'title': 'Media Focus Breakdown',
        'subtitle': 'Guitar-Exclusive Peerage Co-Mentions',
        'title_bar': "Top 5 Co-Mentioned Guitarists",
        'bar_footnote_01': "co-mentions",
        'bar_footnote_02': "co-mentioned guitarists",
        'title_heatmap': "Guitarist-Exclusive Co-Mentions Over Time (Top 5)",
        'view_number': '4',
        'is_landing': False
    },
    5: {
        'var_global': 'global_cross_artist_json',
        'var_long': 'longitudinal_cross_artist_json',
        'title': 'Media Focus Breakdown',
        'subtitle': 'Cross Artist Co-Mentions',
        'title_bar': "Top 5 Co-Mentioned Cross-Artists",
        'bar_footnote_01': "co-mentions",
        'bar_footnote_02': "co-mentioned cross artists",
        'title_heatmap': "Cross-Artist Co-Mentions Over Time (Top 5)",
        'view_number': '5',
        'is_landing': False
    },
    6: {
        'var_global': 'global_category_json',
        'var_long': 'longitudinal_category_json',
        'title': 'Thematic Analysis',
        'subtitle': 'Thematic Patterns',
        'title_bar': "Top 5 Thematic Categories",
        'bar_footnote_01': "theme occurrences",
        'bar_footnote_02': "thematic categories",
        'title_heatmap': "Thematic Categories Over Time (Top 5)",
        'view_number': '6',
        'is_landing': False
    },

    7: {
        'title': 'Vocabulary Profile',
        'subtitle': 'Semantic Composition',
        'title_top_viz': "Substantive Core",
        'title_middle_viz': "Action Dynamics",
        'title_bottom_viz': "Adjectives",
        'view_number': '7',
        'is_landing': False
    },

    7: {
        'title': 'Vocabulary Profile',
        'subtitle': 'Semantic Composition',
        'title_top_viz': "Substantive Core",
        'title_middle_viz': "Action Dynamics",
        'title_bottom_viz': "Qualitative Tones",
        'view_number': '7',
        'is_landing': False
    },

    8: {
        'title': 'Media Flow',
        'subtitle': 'Media Flow Overview',
        'title_top_viz': "Cross-Dimensional Mapping",
        'view_number': '8',
        'is_landing': False
    }
}