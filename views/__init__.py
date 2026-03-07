# views/__init__.py
"""
View layouts for Guitar God Analytics dashboard.
"""

from .view1_landing import create_view_1_landing
from .analysis_view import create_analysis_view

__all__ = [
    'create_view_1_landing',
    'create_analysis_view'
]