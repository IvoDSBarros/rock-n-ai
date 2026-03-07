# components/styles.py
from utils import (FONT_FAMILY, BRAND_NAVY, BRAND_VIBRANT, NEUTRAL_800, NEUTRAL_100)

def get_base_styles():
    """Return base styles dictionary."""
    return {
        'app_container': {
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
        },
        'header': {
            'background': BRAND_NAVY,
            'padding': '10px 20px 8px 20px',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '8px',
            'flexShrink': 0,
            'borderBottom': f'2px solid {BRAND_VIBRANT}',
            'minHeight': '70px',
            'boxSizing': 'border-box'
        },
        'panel': {
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.08)',
            'padding': '0',
            'display': 'flex',
            'flexDirection': 'column',
            'minHeight': '0',
            'overflow': 'hidden'
        },
        'panel_header': {
            'padding': '15px 20px',
            'borderBottom': f'2px solid {BRAND_VIBRANT}',
            'flexShrink': '0',
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center'
        },
        'content_area': {
            'flex': '1',
            'padding': '20px',
            'display': 'flex',
            'gap': '20px',
            'overflow': 'hidden',
            'minHeight': '0'
        }
    }

def get_button_styles(disabled=False, is_next=False):
    """Return button styles based on state."""
    base = {
        'border': 'none',
        'color': 'white',
        'width': '32px',
        'height': '28px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'transition': 'all 0.2s',
        'fontWeight': 'bold',
        'fontFamily': FONT_FAMILY
    }
    
    if disabled:
        base.update({
            'background': 'rgba(255, 255, 255, 0.1)',
            'cursor': 'not-allowed',
            'opacity': '0.5'
        })
    elif is_next:
        base.update({
            'background': 'rgba(59, 130, 246, 0.3)',
            'cursor': 'pointer'
        })
    else:
        base.update({
            'background': 'rgba(255, 255, 255, 0.1)',
            'cursor': 'pointer'
        })
    
    return base