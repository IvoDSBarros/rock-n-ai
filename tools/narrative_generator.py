#------------------------------------------------------------------------------
# Rock N' AI - Narrative Generator

# This script uses CrewAI to generate comprehensive media analysis reports
# for rock guitarists based on pre-calculated metrics and RAG article selection.

# Usage:
#    python narrative_generator.py "Slash"
#    python narrative_generator.py "Brian May"
#------------------------------------------------------------------------------

import os
import sys
import json
import time
import requests
import pandas as pd
import random
from typing import List, Type, Dict, Any, Callable
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

#------------------------------------------------------------------------------
# CONFIGURATION
#------------------------------------------------------------------------------
load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_STRING = "gemini/gemini-2.5-flash"

if not GEMINI_API_KEY:
    print("FATAL ERROR: GEMINI_API_KEY is not set in environment or .env file.")
    sys.exit(1)

ANALYSIS_TABLE_PATH = 'data/master_analysis_table.parquet'
FACT_TABLE_PATH = 'data/rock_news_targeted_5k.parquet'

def retry_on_rate_limit(max_retries: int = 5) -> Callable:
    """
    Decorator to retry a function (API call) with exponential backoff 
    if a 429 (Too Many Requests) status code is encountered.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    
                    if response.status_code == 200:
                        return response
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt 
                        print(f"Rate limit hit (429). Attempt {attempt + 1}/{max_retries}. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"API Error: Status Code {response.status_code}. Details: {response.text}")
                        return response
                        
                except requests.RequestException as e:
                    print(f"Network Error: {e}")
                    time.sleep(2 ** attempt)
                    continue

            raise Exception(f"Failed to complete API call after {max_retries} attempts due to rate limiting or persistent errors.")
        return wrapper
    return decorator


def clean_thinking_sections(text: str, guitarist: str) -> str:
    """Remove all thinking/planning sections from output"""
    
    split_markers = [
        "Let's start drafting the report section by section.",
        "# Executive Summary",
        f"# {guitarist}: Comprehensive Media Analysis 2022/2025"
    ]
    
    for marker in split_markers:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) > 1:
                # Reconstruct with the marker
                if marker.startswith("#"):
                    text = marker + parts[1]
                else:
                    # For transition phrases, find the actual header
                    text = parts[1].strip()
                break
    
    expected_header = f"# {guitarist}: Comprehensive Media Analysis 2022/2025"
    if not text.startswith(expected_header):
        pos = text.find(expected_header)
        if pos != -1:
            text = text[pos:]
        else:
            text = expected_header + "\n\n" + text.lstrip('# ')
    
    return text.strip()

def extract_paragraphs_to_json(report_text: str, guitarist: str, timestamp: int = None) -> str:
    """
    Extract paragraphs from report and save to JSON file
    """
    def clean_raw_text(text):
        """Clean text before saving to raw JSON."""
        if not isinstance(text, str):
            return text
        
        # Preserve the clean markdown formatting
        text = text.replace('\\"', '"').replace("\\'", "'")
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('‘', "'").replace('’', "'")
        
        return text

    if timestamp is None:
        timestamp = int(time.time())
    
    # Define section headers and their corresponding view numbers
    section_views = {
        "Executive Summary": 2,
        "### Solo Coverage": 3,
        "### Guitar-Focused Coverage": 4,
        "### Cross Artist Coverage": 5,
        "## Thematic Category Analysis": 6,
        "## Vocabulary Profile": 7,
        "## Media Flow Analysis": 8
    }
    
    # Also track headers that are not views
    non_view_headers = ["## Conclusion", "## Methodological Note:", "## Media Focus Breakdown"]
    
    paragraphs = []
    lines = report_text.split('\n')
    
    current_section = None
    current_view = None
    section_paragraphs = []
    current_paragraph = []
    in_section = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Check if this is a non-view header
        is_non_view = any(line_stripped.startswith(h) for h in non_view_headers)
        if is_non_view and in_section:
            # Save current paragraph and end section
            if current_paragraph:
                section_paragraphs.append(' '.join(current_paragraph))
            
            if current_section and section_paragraphs:
                for para_idx, para_text in enumerate(section_paragraphs, 1):
                    if para_text.strip() and len(para_text.split()) > 10:
                        paragraphs.append({
                            "guitarist": guitarist,
                            "view": current_view,
                            "paragraph": para_idx,
                            "text": clean_raw_text(para_text)
                        })
                print(f" • {current_section}: extracted {len(section_paragraphs)} paragraphs")
            
            current_section = None
            current_view = None
            section_paragraphs = []
            current_paragraph = []
            in_section = False
            i += 1
            continue
        
        # Check for section headers
        matched_section = None
        matched_view = None
        for header, view_num in section_views.items():
            if line_stripped == header or line_stripped.startswith(header + " "):
                matched_section = header
                matched_view = view_num
                break
        
        if matched_section:
            if current_paragraph and in_section:
                section_paragraphs.append(' '.join(current_paragraph))
            
            if current_section and section_paragraphs:
                for para_idx, para_text in enumerate(section_paragraphs, 1):
                    if para_text.strip() and len(para_text.split()) > 10:
                        paragraphs.append({
                            "guitarist": guitarist,
                            "view": current_view,
                            "paragraph": para_idx,
                            "text": clean_raw_text(para_text)
                        })
                print(f" • {current_section}: extracted {len(section_paragraphs)} paragraphs")
            
            # Start new section
            current_section = matched_section
            current_view = matched_view
            section_paragraphs = []
            current_paragraph = []
            in_section = True
            i += 1
            continue
        
        if in_section and current_section:
            if line_stripped == "":
                if current_paragraph:
                    section_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            else:
                if line_stripped.startswith('[') or line_stripped.startswith('-'):
                    pass
                else:
                    current_paragraph.append(line)
        
        i += 1
    
    # Don't process last section
    if in_section and current_section and current_view in section_views.values():
        if current_paragraph:
            section_paragraphs.append(' '.join(current_paragraph))
        
        if section_paragraphs:
            for para_idx, para_text in enumerate(section_paragraphs, 1):
                if para_text.strip() and len(para_text.split()) > 10:
                    paragraphs.append({
                        "guitarist": guitarist,
                        "view": current_view,
                        "paragraph": para_idx,
                        "text": clean_raw_text(para_text)
                    })
            print(f"   • {current_section}: extracted {len(section_paragraphs)} paragraphs")
    
    # Create json structure
    json_data = {
        "guitarist": guitarist,
        "generated_timestamp": timestamp,
        "total_paragraphs": len(paragraphs),
        "paragraphs": paragraphs
    }
    
    safe_name = guitarist.lower().replace(' ', '_').replace('/', '_')
    json_filename = f"{safe_name}_paragraphs_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return json_filename

class RandomDataEnforcerSchema(BaseModel):
    guitarist_name: str = Field(description="Name of ANY guitarist to analyze")

class RandomDataEnforcer(BaseTool):
    name: str = "RandomDataEnforcer"
    description: str = "Provides data with TRUE RANDOM article selection for diverse analysis."
    args_schema: Type[BaseModel] = RandomDataEnforcerSchema

    def _parse_pk_list(self, data) -> List[str]:
        """Parse PK lists"""
        try:
            if hasattr(data, '__array__'):
                data = data.tolist()
            
            if data is None:
                return []
            
            if isinstance(data, list):
                return [str(item).strip() for item in data if item is not None and str(item).strip()]
            
            data_str = str(data).strip()
            if not data_str or data_str == 'nan':
                return []
            
            if data_str.startswith('['):
                try:
                    parsed = json.loads(data_str)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if item is not None and str(item).strip()]
                except:
                    pass
            
            return [data_str] if data_str else []
            
        except Exception as e:
            print(f"Warning parsing PK list: {e}")
            return []

    def _parse_json_generic(self, json_str, field_name):
        """Generic JSON parsing"""
        try:
            if json_str is None:
                return {}
            
            if hasattr(json_str, '__array__'):
                json_str = json_str.tolist()
            
            json_str = str(json_str).strip()
            if not json_str or json_str == 'nan':
                return {}
            
            json_str = json_str.replace("'", '"').replace("None", "null")
            return json.loads(json_str)
                
        except Exception as e:
            print(f"Warning parsing {field_name}: {e}")
            return {}

    def _parse_longitudinal_tag(self, json_str):
        """Parse longitudinal category data"""
        try:
            parsed = self._parse_json_generic(json_str, 'longitudinal_artist')
            
            if not parsed:
                return {}
            
            if isinstance(parsed, list):
                quarters_data = {}
                for item in parsed:
                    if isinstance(item, dict):
                        quarter = item.get('year_quarter')
                        tag = item.get('guitarist_tags') or item.get('members_tags') or item.get('category_tags')
                        count = item.get('count')
                        
                        if quarter and tag is not None and count is not None:
                            if quarter not in quarters_data:
                                quarters_data[quarter] = {}
                            quarters_data[quarter][tag] = count
                
                return quarters_data
            
            return parsed if isinstance(parsed, dict) else {}
                
        except Exception as e:
            print(f"Warning parsing longitudinal categories: {e}")
            return {}

    def _parse_global_categories(self, json_str):
        """Parse global category data"""
        try:
            parsed = self._parse_json_generic(json_str, 'global_category')
            
            if not parsed:
                return {}
            
            if isinstance(parsed, dict):
                return parsed
            
            if isinstance(parsed, list):
                result = {}
                for item in parsed:
                    if isinstance(item, dict):
                        name = item.get('name') or item.get('category') or item.get('category_tags')
                        count = item.get('count') or item.get('value')
                        
                        if name is not None and count is not None:
                            result[name] = count
                
                return result
            
            return {}
                
        except Exception as e:
            print(f"Warning parsing global categories: {e}")
            return {}

    def _parse_longitudinal_ratios(self, json_str, target_ratio="ratio_solo_focus"):
        """Parse longitudinal ratio data - extracts single ratio per quarter
        
        Args:
            json_str: JSON string containing list of quarterly data
            target_ratio: Which ratio to extract (default: "ratio_solo_focus")
        
        Returns:
            Dictionary with quarters as keys and ratio values as values
            Example: {"2022Q1": 0.5333, "2022Q2": 0.25, "2022Q3": 0.6667}
        """
        try:
            parsed = self._parse_json_generic(json_str, 'longitudinal_ratio')
            
            if not parsed or not isinstance(parsed, list):
                print("No valid longitudinal data found")
                return {}
            
            quarters_data = {}
            
            for item in parsed:
                if isinstance(item, dict):
                    quarter = item.get('year_quarter')
                    ratio = item.get(target_ratio)
                    
                    if quarter is not None and ratio is not None:
                        # Convert to float for consistency
                        try:
                            quarters_data[quarter] = float(ratio)
                        except (ValueError, TypeError):
                            quarters_data[quarter] = ratio
            
            if quarters_data:
                # Sort quarters chronologically
                sorted_quarters = sorted(quarters_data.keys(), 
                                        key=lambda x: (int(x[:4]), x[4:]))
                return {q: quarters_data[q] for q in sorted_quarters}
            
            return {}
                    
        except Exception as e:
            print(f"Warning parsing longitudinal ratios for {target_ratio}: {e}")
            return {}

    def _parse_vocabulary_profile(self, json_str):
        """Parse vocbulary profile data"""
        try:
            parsed = self._parse_json_generic(json_str, 'vocabulary_profile_json')
            
            if not parsed:
                return {}
            
            if isinstance(parsed, list):
                vocabulary_data = {}
                for item in parsed:
                    if isinstance(item, dict):
                        pos_tag = item.get('pos')
                        word = item.get('word')
                        count = item.get('count')
                        
                        if pos_tag and word is not None and count is not None:
                            if pos_tag not in vocabulary_data:
                                vocabulary_data[pos_tag] = {}
                            vocabulary_data[pos_tag][word] = count
                
                return vocabulary_data
            
            return parsed if isinstance(parsed, dict) else {}
                
        except Exception as e:
            print(f"Warning parsing longitudinal categories: {e}")
            return {}

    def _parse_media_flow_json(self, json_str):
        """Parse media flow data for parallel categories visualization"""
        try:
            parsed = self._parse_json_generic(json_str, 'media_flow_json')
            
            if not parsed:
                return []
            
            if isinstance(parsed, list):
                return parsed
                
            return []
                    
        except Exception as e:
            print(f"Warning parsing media flow data: {e}")
            return []


    def _parse_category_pk_lists(self, json_str):
        """Parse category PK lists"""
        try:
            if json_str is None:
                return []
            
            json_str = str(json_str).strip()
            if not json_str or json_str == 'nan':
                return []
            
            json_str = json_str.replace("'", '"').replace("None", "null")
            parsed = json.loads(json_str)
            
            if isinstance(parsed, list):
                return parsed
            return []
                
        except Exception as e:
            print(f"Warning parsing category PK lists: {e}")
            return {}

    def _parse_category_pk_mapping(self, category_pk_lists: List) -> Dict[str, List[str]]:
        """Parse category to PK mapping from category_pk_list_json"""
        category_to_pks = {}
        try:
            if not category_pk_lists:
                return {}
            
            for item in category_pk_lists:
                if isinstance(item, dict):
                    category = item.get('category_tags')
                    pk_list = item.get('full_pk')
                    
                    if category and pk_list:
                        if isinstance(pk_list, list):
                            clean_pks = [str(pk).strip() for pk in pk_list if pk]
                            category_to_pks[category] = clean_pks
                        else:
                            category_to_pks[category] = [str(pk_list).strip()]
            
            print(f"   • Parsed {len(category_to_pks)} category-to-PK mappings")
            return category_to_pks
            
        except Exception as e:
            print(f"Warning parsing category-PK mapping: {e}")
            return {}

    def _get_article_categories(self, article_pk: str, category_to_pks: Dict[str, List[str]]) -> List[str]:
        """Get all categories for a specific article PK"""
        article_categories = []
        try:
            if not article_pk or not category_to_pks:
                return []
            
            article_pk_clean = str(article_pk).strip()
            
            for category, pk_list in category_to_pks.items():
                if article_pk_clean in pk_list:
                    article_categories.append(category)
            
            return article_categories
            
        except Exception as e:
            print(f"Warning getting article categories: {e}")
            return []

    def _get_category_examples_from_sample(self, category_to_pks: Dict[str, List[str]], 
                                           all_sample_articles: List[Dict],
                                           random_seed: int = None) -> Dict[str, List[str]]:
        """Get example citations for each category from the actual random sample"""
        try:
            category_examples = {}
            
            if not category_to_pks or not all_sample_articles:
                return {}
            
            # Set random seed for reproducibility
            if random_seed is not None:
                 local_random = random.Random(random_seed)
            else:
                local_random = random
            
            # Create pk to article mapping
            pk_to_article = {}
            for article in all_sample_articles:
                article_pk = article.get('article_pk', '')
                if article_pk:
                    pk_to_article[article_pk] = article
            
            # Find articles that belong to the category
            for category, pk_list in category_to_pks.items():
                examples = []
                
                if not pk_list:
                    continue
                    
                # Use random.sample to get random pks from this category (limit to checking 10 PKs max, or fewer if list is shorter)
                max_to_check = min(10, len(pk_list))
                
                if max_to_check > 0:
                    # Get random pks without replacement
                    random_pks = local_random.sample(pk_list, max_to_check)
                    
                    for pk in random_pks:
                        if pk in pk_to_article:
                            article = pk_to_article[pk]
                            citation = article.get('citation', '')
                            if citation:
                                examples.append(citation)
                
                if examples:
                    # Return max 3 random examples
                    category_examples[category] = examples[:3]
            
            return category_examples
            
        except Exception as e:
            print(f"Warning getting category examples from sample: {e}")
            return {}

    def _format_date(self, date_str: str) -> str:
        """Format date correctly"""
        try:
            if date_str is None or pd.isna(date_str):
                return "Unknown"
            
            dt = pd.to_datetime(date_str, errors='coerce')
            if pd.notna(dt):
                return dt.strftime('%Y-%m-%d')
            
            return str(date_str)[:10]
        except:
            return str(date_str)[:10]

    def _format_citation(self, website: str, date: str, title: str) -> str:
        """Format citation in CONSISTENT format: website (date) - title"""
        website_clean = str(website).strip() if website else "Unknown"
        date_clean = self._format_date(date)
        title_clean = str(title).strip() if title else "No Title"
        
        return f"{website_clean} ({date_clean}) - {title_clean}"

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return len(text) // 4

    def _get_random_article_content(self, pk_list: List[str], list_name: str, max_articles: int = 25, random_seed: int = None, category_to_pks: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Get TRUE RANDOM article selection with categories
        - Different articles each run
        - Respects token limits
        - Provides diverse analysis
        """
        if not pk_list:
            return {
                "article_count": 0,
                "articles": [],
                "total_tokens": 0,
                "list_name": list_name,
                "selection_method": "random",
                "random_seed": random_seed
            }
        
        try:
            df_fact = pd.read_parquet(FACT_TABLE_PATH)
            
            clean_pks = [str(pk).strip() for pk in pk_list if pk]
            all_articles = df_fact[df_fact['full_pk'].isin(clean_pks)].copy()
                        
            if len(all_articles) == 0:
                return {
                    "article_count": 0,
                    "articles": [],
                    "total_tokens": 0,
                    "list_name": list_name,
                    "selection_method": "random",
                    "random_seed": random_seed
                }
            
            # Random selection
            if len(all_articles) <= max_articles:
                selected_articles = all_articles
                selection_method = "all_articles"
            else:
                selected_articles = all_articles.sample(n=max_articles, random_state=random_seed)
                selection_method = f"random_{max_articles}_of_{len(all_articles)}"
            
            # Prepare selected articles for llm
            article_contents = []
            total_tokens = 0
            
            for _, article in selected_articles.iterrows():
                title = str(article.get('title', '')).strip()
                description = str(article.get('description', '')).strip()
                body = str(article.get('body', '')).strip()
                website = article.get('website', 'Unknown')
                date = article.get('date')
                article_pk = article.get('full_pk', '')
                
                # Full content for analysis
                full_content = f"TITLE: {title}\n\nDESCRIPTION: {description}\n\nARTICLE CONTENT:\n{body}"
                
                # Estimate tokens
                article_tokens = self._estimate_tokens(full_content)
                total_tokens += article_tokens
                
                citation = self._format_citation(website, date, title)
                
                # Get categories for this article
                article_categories = []
                if category_to_pks and article_pk:
                    article_categories = self._get_article_categories(article_pk, category_to_pks)
                
                article_contents.append({
                    "citation": citation,
                    "title": title,
                    "complete_content": full_content,
                    "estimated_tokens": article_tokens,
                    "date": self._format_date(date),
                    "website": website,
                    "body_length": len(body),
                    "article_pk": article_pk,
                    "categories": article_categories
                })
            
            print(f" • {list_name}: Randomly selected {len(selected_articles)}/{len(all_articles)} articles")
            print(f"Seed: {random_seed}, Method: {selection_method}")
            
            return {
                "article_count": len(all_articles),
                "selected_count": len(selected_articles),
                "articles": article_contents,
                "total_tokens": total_tokens,
                "list_name": list_name,
                "selection_method": selection_method,
                "random_seed": random_seed,
                "coverage_pct": (len(selected_articles) / len(all_articles)) * 100
            }
            
        except Exception as e:
            print(f"Error getting random content for {list_name}: {e}")
            return {
                "article_count": 0,
                "selected_count": 0,
                "articles": [],
                "total_tokens": 0,
                "list_name": list_name,
                "selection_method": "error",
                "random_seed": random_seed,
                "coverage_pct": 0
            }

    @retry_on_rate_limit(max_retries=5)
    def _call_api_with_retry(self, payload: dict, url: str) -> requests.Response:
        """Make API call with rate limiting protection"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GEMINI_API_KEY}"
        }
        return requests.post(url, json=payload, headers=headers)

    def _run(self, guitarist_name: str) -> str:
        """Main function - provides rabdom data for analysis while preserving pre-calculated metrics"""
        try:
            print(f"\n Getting data for {guitarist_name}...")
            
            df_analysis = pd.read_parquet(ANALYSIS_TABLE_PATH)
            
            if guitarist_name not in df_analysis['guitarist'].values:
                return json.dumps({"error": f"Guitarist '{guitarist_name}' not found"}, indent=2)
            
            analysis_row = df_analysis.loc[df_analysis['guitarist'] == guitarist_name].iloc[0]
            total_articles = int(analysis_row.get('total_articles', 0))
            
            # Generate a new random seed for this run
            random_seed = random.randint(1, 1000000)
            print(f"Found {total_articles} total articles (pre-calculated)")
            print(f"Using RANDOM article selection with seed: {random_seed}")
            
            # Parse all pre-calculated json fields
            overall_metrics = self._parse_json_generic(analysis_row.get('overall_metrics_json'), 'overall_metrics')
            guitarist_md = self._parse_json_generic(analysis_row.get('guitarist_md_json'), 'guitarist_md')
            ratios = self._parse_json_generic(analysis_row.get('ratios_json'), 'ratios')
            longitudinal_solo_focus_ratio = self._parse_longitudinal_ratios(analysis_row.get('longitudinal_ratios_json'))
            network_metrics = self._parse_json_generic(analysis_row.get('network_metrics'), 'network_metrics')
            global_cross_artist = self._parse_json_generic(analysis_row.get('global_cross_artist_json'), 'global_cross_artist')
            longitudinal_cross_artist = self._parse_longitudinal_tag(analysis_row.get('longitudinal_cross_artist_json'))            
            global_guitar = self._parse_json_generic(analysis_row.get('global_guitar_json'), 'global_guitar')
            longitudinal_guitar = self._parse_longitudinal_tag(analysis_row.get('longitudinal_guitar_json'))  
            vocabulary_profile = self._parse_vocabulary_profile(analysis_row.get('vocabulary_profile_json')) 
            media_flow = self._parse_media_flow_json(analysis_row.get('media_flow_json')) 
        
            # Category data
            global_category = self._parse_global_categories(analysis_row.get('global_category_json'))
            longitudinal_category = self._parse_longitudinal_tag(analysis_row.get('longitudinal_category_json'))
            category_pk_lists = self._parse_category_pk_lists(analysis_row.get('category_pk_list_json'))
            
            # Parse category-pk mapping
            category_to_pks = self._parse_category_pk_mapping(category_pk_lists)
            
            # Get pk lists for random selection
            solo_pk_list = self._parse_pk_list(analysis_row.get('solo_focus_pk_list'))
            guitar_pk_list = self._parse_pk_list(analysis_row.get('guitar_focus_pk_list'))
            cross_artist_pk_list = self._parse_pk_list(analysis_row.get('cross_artist_pk_list'))
            full_pk_list = self._parse_pk_list(analysis_row.get('full_pk_list'))
            
            print(f"\n Pre-calculated metrics (unchanged):")
            print(f" • Rank: {overall_metrics.get('overall_article_rank', 'N/A')}")
            print(f" • Frequency: {overall_metrics.get('dataset_frequency_pct', 'N/A')}%")
            print(f" • Total words: {overall_metrics.get('total_body_words', 0):,}")
            print(f" • Avg words/article: {overall_metrics.get('avg_words_per_article', 0):,}")
            print(f" • Solo focus ratio: {ratios.get('solo_focus_ratio', 0)*100:.1f}%")
            print(f" • Guitar focus ratio: {ratios.get('guitar_focus_ratio', 0)*100:.1f}%")
            print(f" • Cross artist focus ratio: {ratios.get('cross_artist_focus_ratio', 0)*100:.1f}%")
            
            # Get random article content with categories
            print(f"\n Random article selection (with category mapping):")
            solo_content = self._get_random_article_content(
                solo_pk_list, "solo_focus", max_articles=15, 
                random_seed=random_seed, category_to_pks=category_to_pks
            )
            guitar_content = self._get_random_article_content(
                guitar_pk_list, "guitar_focus", max_articles=15, 
                random_seed=random_seed + 1, category_to_pks=category_to_pks
            )
            cross_artist_content = self._get_random_article_content(
                cross_artist_pk_list, "cross_artist_focus", max_articles=15, 
                random_seed=random_seed + 2, category_to_pks=category_to_pks
            )
            overall_content = self._get_random_article_content(
                full_pk_list, "overall", max_articles=20, 
                random_seed=random_seed + 3, category_to_pks=category_to_pks
            )
            
            # Get all sample articles for category examples
            all_sample_articles = []
            for content in [solo_content, guitar_content, cross_artist_content, overall_content]:
                all_sample_articles.extend(content.get("articles", []))
            
            # Get category examples from actual sample
            category_examples = self._get_category_examples_from_sample(category_to_pks, all_sample_articles)
            
            # Calculate totals for logging only
            total_selected = (
                solo_content["selected_count"] +
                guitar_content["selected_count"] +
                cross_artist_content["selected_count"] +
                overall_content["selected_count"]
            )
            
            total_tokens = (
                solo_content["total_tokens"] +
                guitar_content["total_tokens"] +
                cross_artist_content["total_tokens"] +
                overall_content["total_tokens"]
            )
            
            print(f"\n Random selection summary (for logging only):")
            print(f" • Total articles in dataset: {total_articles}")
            print(f" • Randomly selected: {total_selected} articles")
            print(f" • Estimated tokens: {total_tokens:,}")
            print(f" • Random seed: {random_seed}")
            print(f" • Found {len(category_examples)} categories with examples in random sample")
            
            if total_tokens > 150000:
                print(f"WARNING: High token count. Limiting article content previews.")
            
            # Prepare data structure with all pre-calculated metrics preserved
            data = {
                "basic_metrics": {
                    "guitarist": guitarist_name,
                    "total_articles": total_articles,
                    "overall_article_rank": overall_metrics.get('overall_article_rank', 'N/A'),
                    "dataset_frequency_pct": overall_metrics.get('dataset_frequency_pct', 'N/A'),
                    "total_body_words": overall_metrics.get('total_body_words', 0),
                    "avg_words_per_article": overall_metrics.get('avg_words_per_article', 0),
                    "genre_guitar_world": guitarist_md.get('genre_guitar_world', 'Rock'),
                    "band_affiliation": guitarist_md.get('band_affiliation', 'Various'),
                    "country": guitarist_md.get('country', 'Unknown'),
                    "born_year": guitarist_md.get('born_year', 'Unknown'),
                    "died_year": guitarist_md.get('died_year', 'Unknown'),
                },
                
                "ratios": {
                    "solo_focus_ratio": ratios.get('solo_focus_ratio', 0),
                    "guitar_focus_ratio": ratios.get('guitar_focus_ratio', 0),
                    "cross_artist_focus_ratio": ratios.get('cross_artist_focus_ratio', 0)
                },

                "longitudinal_solo_focus_ratio": {
                    "longitudinal_solo_focus_ratio": longitudinal_solo_focus_ratio
                },

                "network_metrics": {
                     'unique_co_mentioned_guitarists': network_metrics.get('unique_co_mentioned_guitarists_count', 0), 
                     'unique_co_mentioned_non_guitarists': network_metrics.get('unique_co_mentioned_others_count', 0), 
                     'total_guitarist_co_mentions': network_metrics.get('total_guitarist_co_mentions', 0), 
                     'total_non_guitarist_co_mentions': network_metrics.get('total_others_co_mentions', 0), 
                     'ratio_co_ment_by_guitarist': network_metrics.get('ratio_co_ment_by_guitarist', 0.0), 
                     'ratio_co_ment_by_non_guitarist': network_metrics.get('ratio_co_ment_by_other_artist', 0.0), 
                     'top_guitarist_name': network_metrics.get('top_guitarist_name', "-"), 
                     'top_guitarist_count': network_metrics.get('top_guitarist_count', 0), 
                     'top_non_guitarist_name': network_metrics.get('top_cross_artist_name', "-"), 
                     'top_non_guitarist_count': network_metrics.get('top_cross_artist_count', 0)
                     },

                "general_vocabulary_profile": {
                    "vocabulary_profile": vocabulary_profile},

               "media_flow_overview": {
                   "media_flow_overview": media_flow},                
                
                "global_mentions": {
                    "cross_artists": global_cross_artist,
                    "other_guitarists": global_guitar,
                    "categories": global_category
                },
                
                "longitudinal_mentions": {
                    "longitudinal_cross_artists": longitudinal_cross_artist,
                    "longitudinal_other_guitarists": longitudinal_guitar,
                    "longitudinal_cross_artist_quarters_available": list(longitudinal_cross_artist.keys()) if longitudinal_cross_artist else [],
                    "longitudinal_other_guitarists_quarters_available": list(longitudinal_guitar.keys()) if longitudinal_guitar else []
                },

                "category_analysis": {
                    "global_categories": global_category,
                    "longitudinal_categories": longitudinal_category,
                    "quarters_available": list(longitudinal_category.keys()) if longitudinal_category else [],
                    "category_pk_lists": category_pk_lists[:20] if category_pk_lists else [],
                    "top_categories": dict(sorted(global_category.items(), key=lambda x: x[1], reverse=True)[:15]),
                    "category_examples_from_sample": category_examples,
                    "category_mapping_note": "These examples show which articles in the RANDOM SAMPLE actually belong to each category. Use these to understand what types of articles are in each category."
                },
                
                # Random article selection for analysis
                "random_article_selection": {
                    "analysis_identifier": f"random_sample_{random_seed}",
                    "random_seed": random_seed,
                    "selection_note": "Articles are randomly selected for qualitative analysis. Different each run.",
                    "articles": {
                        "solo_focus": {
                            "sample_count": solo_content.get("selected_count", 0),
                            "total_available": solo_content.get("article_count", 0),
                            "articles": [{
                                "citation": article["citation"],
                                "content_preview": article["complete_content"][:1500] if len(article["complete_content"]) > 1500 else article["complete_content"],
                                "categories": article.get("categories", [])
                            } for article in solo_content["articles"][:10]]
                        },
                        "guitar_focus": {
                            "sample_count": guitar_content.get("selected_count", 0),
                            "total_available": guitar_content.get("article_count", 0),
                            "articles": [{
                                "citation": article["citation"],
                                "content_preview": article["complete_content"][:1500] if len(article["complete_content"]) > 1500 else article["complete_content"],
                                "categories": article.get("categories", [])
                            } for article in guitar_content["articles"][:10]]
                        },
                        "cross_artist_focus": {
                            "sample_count": cross_artist_content.get("selected_count", 0),
                            "total_available": cross_artist_content.get("article_count", 0),
                            "articles": [{
                                "citation": article["citation"],
                                "content_preview": article["complete_content"][:1500] if len(article["complete_content"]) > 1500 else article["complete_content"],
                                "categories": article.get("categories", [])
                            } for article in cross_artist_content["articles"][:10]]
                        },
                        "overall": {
                            "sample_count": overall_content.get("selected_count", 0),
                            "total_available": overall_content.get("article_count", 0),
                            "articles": [{
                                "citation": article["citation"],
                                "content_preview": article["complete_content"][:1500] if len(article["complete_content"]) > 1500 else article["complete_content"],
                                "categories": article.get("categories", [])
                            } for article in overall_content["articles"][:15]]
                        }
                    },
                    # Category analysis for all random articles
                    "category_analysis": {
                        "solo_focus_categories": dict(sorted(global_category.items(), key=lambda x: x[1], reverse=True)[:10]),
                        "guitar_focus_categories": dict(sorted(global_category.items(), key=lambda x: x[1], reverse=True)[:10]),
                        "cross_artist_focus_categories": dict(sorted(global_category.items(), key=lambda x: x[1], reverse=True)[:10]),
                        "overall_categories": dict(sorted(global_category.items(), key=lambda x: x[1], reverse=True)[:15]),
                        "category_note": "These categories represent thematic patterns across ALL articles in each focus type. Each article also has its specific categories listed."
                    }
                }
                }
            
            # Add sample citation with categories
            if solo_content["articles"]:
                sample_article = solo_content["articles"][0]
                sample_citation = sample_article["citation"]
                sample_categories = sample_article.get("categories", [])
                print(f"Random sample citation: {sample_citation}")
                if sample_categories:
                    print(f"Categories: {', '.join(sample_categories)}")
            
            # Show some category examples
            if category_examples:
                print(f"\n Sample category assignments:")
                for category, examples in list(category_examples.items())[:5]:
                    print(f" • {category}: {len(examples)} examples in sample")
                    if examples:
                        print(f"Example: {examples[0]}")
            
            return json.dumps(data, indent=2)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return json.dumps({"error": str(e)}, indent=2)

#------------------------------------------------------------------------------
# COMPLETE CREW (ANALYSIS OF ALL ARTICLES FROM ALL FULLL PK LISTS)
#------------------------------------------------------------------------------
def create_crew():
    """Create crew that analyzes ALL data with enforced citation format"""
    
    random_enforcer = RandomDataEnforcer()
    
    report_agent = Agent(
        role="Senior Rock Media Analyst",
        goal="Write comprehensive rock media analysis reports analyzing ALL articles from ALL PK lists and category data with proper citations",
        backstory="Expert analyst who reads and analyzes ALL articles provided with proper citations and thorough analysis",
        tools=[random_enforcer],
        allow_delegation=False,
        verbose=False,
        llm=GEMINI_MODEL_STRING,
        max_rpm=8
    )
    
    # COMPLETE TASK (ALL MANDATORY INSTRUCTIONS)
    write_report_task = Task(
        description=(                    
                    "TASK DEFINITION:\n"
                        "- Produce a comprehensive, narrative-style media analysis of {guitarist_name} that synthesizes ALL provided data into a cohesive analytical interpretation.\n"
                        "- NO PREAMBLE: No conversational filler, planning text, or thinking aloud before the header.\n"
                        "- ANALYST TONE: Write as a professional media analyst. The output must read as interpretive media analysis, not enumerated reporting.\n\n"

                    "DATA ACCESS AND SCOPE (MANDATORY):\n"
                        "- USE the RandomDataEnforcer tool to retrieve complete data, including categories.\n"
                        "- The analysis MUST incorporate:\n"
                            "1. Pre-calculated metrics and ratios\n"
                            "2. Category analysis data (global, longitudinal, top categories)\n"
                            "3. Vocabulary profile data\n"
                            "4. Global and longitudinal mention trends\n"
                            "5. Article content previews\n\n"
                    
                    "PRE-CALCULATED METRICS USAGE:\n"
                        "- basic_metrics provide quantitative context.\n"
                        "- ratios define media focus distribution.\n"
                        "- vocabulary_profile reveals the characteristic lexicon and terminology used to describe {guitarist_name}.\n"
                        "- global_mentions establish contextual and collaborative presence.\n"
                        "- longitudinal_mentions identify trends and peaks.\n"
                        "- category_analysis defines dominant and evolving themes.\n\n"
     
                    "RATIO DEFINITIONS (DO NOT MISINTERPRET):"
                    "- solo focus ratio: Articles where the subject is the ONLY artist mentioned. High values indicate individual notoriety, solo projects, or technical gear spotlights."
                    "- guitar focus ratio: Articles where the subject appears with other guitarists, but NO non-guitarist members. High values indicate a 'guitar-centric' context like specialized festivals, collaborations with peers, or instrument-specific rankings."
                    "- cross artist focus ratio: Articles where the subject is mentioned alongside at least one non-guitarist (vocalists, drummers, etc.). This represents the 'broad ensemble' context, covering band news, tours, and general music industry mentions."
                    
                    "ARTICLE ANALYSIS REQUIREMENTS:\n"
                        "- Read the content_preview of ALL articles.\n"
                        "- Analyze what the content reveals about {guitarist_name}, referencing specific passages.\n"
                        "- ALWAYS cite articles when referenced.\n"
                        "- NEVER infer or assume categories from article content.\n\n"

                    "CITATION FORMAT (NON-NEGOTIABLE):\n"
                        "- ALL article citations MUST be consistent throughout the report and use the following approved format: title (Website, YYYY-MM-DD)\n"
                        "- Mixing citation formats within the same report is NOT permitted.\n"                    

                    "STRUCTURAL AND FORMATTING CONSTRAINTS:\n"
                        "- ABSOLUTELY NO lists, bullets, numbering, asterisks, or visual structuring in the final report.\n"
                        "- All content must be written as continuous analytical prose.\n"
                        "- ALL percentages must be displayed with one decimal place (.1f)%.\n\n"
                    
                    "TERMINOLOGY CONSTRAINTS:\n"
                        "- Use 'body of work', 'text corpus', or 'collection' instead of 'dataset'.\n"
                        "- Use 'prevalence', 'regularity', or 'rhythm' instead of 'frequency'.\n"
                        "- State analytical facts directly; do not reference metrics abstractly.\n"
                        "- Do NOT use underscores when referring to metrics or ratios.\n"
                        "- Do NOT use the phrase 'random article samples'; refer to them as 'articles'.\n\n"
                    
                    "KEY THEMATIC PATTERNS AND GLOBAL MENTIONS — ANALYTICAL NOTATION STYLE:\n"
                        "- DO NOT use bullet points.\n"
                        "- First mention in a section: term (n=16, 16.0% of total articles).\n"
                        "- Subsequent mentions in the same section: term (16 mentions, 16.0%).\n"
                        "- Vary phrasing to avoid repetition; be emphatic, not monotonous.\n\n"
                    
                    "CORRECT ADOPTION OF ANALYTICAL NOTATION:\n"
                        "(1) KEY THEMATIC PATTERNS\n"
                        "The term 'album' appeared 16 times, representing 16.0% of total articles. Throughout the analysis, 'guitar' showed higher prevalence (24 mentions, 24.0%), while 'tour' appeared less frequently (12 mentions, 12.0%).\n"
                        "(2) GLOBAL MENTIONS\n"
                        "Collaborations included Artist x1 (25 mentions, 30.0% of total articles), Artist x2 (23 mentions, 12.0%), and Artist x3 (15 mentions, 10.0%).\n\n"
                    
                    "INCORRECT ADOPTION OF ANALYTICAL NOTATION:\n"
                        "(1) KEY THEMATIC PATTERNS\n"
                        "'Diverse topics' (n=106, 42.2%) dominated coverage, followed by artist career facts (n=43, 17.1%) and video (n=24, 9.6%).\n"
                        "(2) GLOBAL MENTIONS\n"
                        "Collaborations included Artist x1 (25 mentions), Artist x2 (23 mentions), and Artist x3 (15 mentions).\n\n"
           
                    "THEMATIC CATEGORY ANALYSIS (STRICT):\n"
                        "- Use ONLY category_analysis.global_categories, longitudinal_categories, and top_categories.\n"
                        "- Confirm article-to-category mapping using category_analysis.category_examples_from_sample.\n"
                        "- **Category Discussion:** When discussing categories in general (e.g., their counts, trends, or prominence), refer to them by name: e.g., the 'album' category.\n"
                        "- **Article Citation Format (CRITICAL RULE):** When you cite a specific article as an example, you MUST append its exact category using the complete parenthetical format: (topic label: category_name). Place this tag directly after the article's citation (Source, Date).\n"
                          "- Example: 'Article Title' (Source, YYYY-MM-DD) (topic label: album).\n"
                          "- This format is mandatory and must not be altered, abbreviated, or omitted.\n"
                        "- **BOUNDARY RULE (CRITICAL):** The parenthetical format `(topic label:` **MUST ONLY APPEAR** within the 'Thematic Category Analysis' section. It is **FORBIDDEN** in all other sections of the report.\n"
                        "- NEVER guess, infer, or reassign categories.\n\n"        
           
                    "STYLE REQUIREMENTS:\n"
                        "- Use professional transitional language such as 'Furthermore', 'Additionally', and 'This pattern continues'.\n"
                        "- Maintain an authoritative media analyst voice throughout.\n\n"
                    
                    "REPORT STRUCTURE:\n"
                        "# {guitarist_name}: Comprehensive Media Analysis 2022/2025\n\n"
                        
                        "## Executive Summary\n"
                        "[Synthesize ALL data into a compelling analytical narrative]\n"
                        "- **STRUCTURE & TONE:**\n"
                        "- **Start strong** with a compelling opening sentence about the guitarist's media presence\n" 

                        "- **OPENING VARIATION (CRITICAL):**\n"
                            "- SCALED INTENSITY: Tier 1 (Rank 1-3) must use an aggressive, market-leading tone focused on dominance. Tier 2 (Rank 4-10) must use a stable, institutional tone focused on consistency and long-term benchmarks.\n"
                            "- TERMINAL CONSTRAINTS (MANDATORY): Strictly avoid 'Commands', 'Commanding media presence', 'Editorial gravity', 'Narrative footprint', 'Media landscape', or 'Robust interest'.\n"
                            "- VARY THE ENTRY POINT (STRUCTURAL ROTATION):\n"
                            "  1. The Temporal Entry: Begin by identifying the 2022–2025 timeframe.\n"
                            "  2. The Positional Entry: Begin by stating the rank or standing within the volume hierarchy.\n"
                            "  3. The Metric Entry: Begin by citing the primary quantitative achievement (article count/share).\n"
                            "  4. The Scope Entry: Begin by classifying the editorial focus (e.g., long-form analysis vs. news volume).\n"
                            "- DATA-LINKED ADJECTIVES: Adjectives like 'significant', 'substantial', 'primary', or 'consistent' are permitted ONLY when directly modifying a specific data point.\n"
                            "- NATURAL FLOW: One strong verb per sentence. Never stack descriptive adjectives. If the sentence feels like a list, rewrite it.\n"
                            "- DYNAMIC ROTATION: DO NOT use the same entry point or sentence structure for more than two consecutive guitarists.\n"
                            "- ERROR CORRECTION: IF YOU CATCH YOURSELF REPEATING 'COMMANDS A PRESENCE' OR VAGUE ADJECTIVE-HEAVY PHRASES, STOP AND REWRITE FOR DATA-DRIVEN PRECISION.\n\n"

                        "- **Synthesize basic metrics with natural, journalistic flow:**\n"
                            "- Mandatory metrics: 'total_articles', 'overall_article_rank', 'dataset_frequency_pct', 'avg_words_per_article'\n\n"
                            "- Translate database fields to human terms:**\n"
                            "- `dataset_frequency_pct` = \"percentage of coverage\" / \"media share\"\n"
                            "- `overall_article_rank` = \"ranking among peers\" / \"position in coverage\"\n"
                            "- `total_articles` = \"number of articles\" / \"volume of coverage\"\n"
                            "- `avg_words_per_article` = \"article length\" / \"depth of coverage\"\n\n"
                            "- **NEVER USE THE RAW FIELD NAMES IN OUTPUT.**\n\n"
                            "- **Combine differently each time you mention similar metrics.**\n\n"        
                        "- **Flow into** focus ratios (solo/guitar/cross artist) as evidence of coverage patterns\n"
                        
                        "- **Synthesize network metrics with natural, journalistic flow:**\n"
                        "- Mandatory network metrics:**\n"
                            "- 'unique_co_mentioned_guitarists', 'unique_co_mentioned_non_guitarists' \n"
                            "- 'total_guitarist_co_mentions', 'total_non_guitarist_co_mentions' \n"
                            "- 'ratio_co_ment_by_guitarist', 'ratio_co_ment_by_non_guitarist' \n"
                            "- 'top_guitarist_name', 'top_guitarist_count' \n" 
                            "- 'top_non_guitarist_name','top_non_guitarist_count' \n\n"
                                         
                            "- Translate database fields to human terms:**\n"
                                # GUITARIST CO-MENTION METRICS
                                "- unique_co_mentioned_guitarists = \"unique guitarists\" / \"distinct guitarist connections\"\n"
                                "- total_guitarist_co_mentions = \"total co-mentions\" / \"shared coverage with peers\"\n"
                                "- ratio_co_ment_by_guitarist = \"intra-genre focus\" / \"guitarist-centric mention ratio\"\n"
                                "- top_guitarist_name = \"primary peer\" / \"most frequent guitarist association\"\n"
                                "- top_guitarist_count = \"co-mention volume\" / \"peer-to-peer pairing frequency\"\n"
                                 # NON-GUITARIST CO-MENTION METRICS
                                "- unique_co_mentioned_non_guitarists = \"unique non-guitarists\" / \"distinct industry associations\"\n"
                                "- total_non_guitarist_co_mentions = \"total co-mentions\" / \"shared coverage with non-guitarists\"\n"
                                "- ratio_co_ment_by_non_guitarist = \"crossover focus\" / \"non-guitarist mention ratio\"\n"
                                "- top_non_guitarist_name = \"primary peer\" / \"most frequent non-guitarist association\"\n"
                                "- top_non_guitarist_count = \"co-mention volume\" / \"crossover shared coverage\"\n"
                                "- **NEVER USE THE RAW FIELD NAMES IN OUTPUT.**\n\n"
                                "- **Combine differently each time you mention similar metrics.**\n\n"        

                        "- **Analyze** global thematic categories as key thematic insights\n"
                        "- Based on the articles content, write a sentence about **Cultural Impact** of the guitarist focusing on media presence as cultural significance\n"
                        "- Based on the articles content, write a sentence about **Artistic Identity:** of the guitarist focusing on how coverage reflects their artistic persona\n\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"

                        "## Media Focus Breakdown\n"
                        "### Solo Coverage\n"
                        "[Based on reading solo_focus articles]\n"
                        "- What do these selected articles reveal?\n"
                        "- Reference specific content from articles\n"
                        "- CITE articles using: title (Website, YYYY-MM-DD)\n"
                        "- GENERATE an compelling narrative when citing excerpts instead of list bullet points\n"
                        "- CONSTRAINT: Intro must be 2 concise, natural sentences. Sentence 1: Weave in current solo_focus_ratio. Sentence 2: Mention the peak quarter + value and lowest quarter(s) + value from longitudinal_solo_focus_ratio. Be data-focused but read naturally - no lengthy explanations or context.\n"                
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"
                        
                        "### Guitar-Focused Coverage\n"
                        "[Based on reading guitar_focus articles, other_guitarists from global_mentions and \
                                longitudinal_other_guitarists from longitudinal_mentions]\n"
                        "- How is {guitarist_name} framed in guitar contexts in articles?\n"
                        "- Reference specific content from articles\n"
                        "- YOU MUST USE other_guitarists from global_mentions if available\n"
                        "- YOU MUST USE longitudinal_other_guitarists from longitudinal_mentions if available\n"
                        "- How does this contextualize the coverage?\n\n"
                        "- How have mentions changed over time?\n"
                        "- Any quarterly trends?\n\n"
                        "- CITE articles using: title (Website, YYYY-MM-DD)\n"
                        "- GENERATE an compelling narrative when citing excerpts instead of list bullet points\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"
            
                        "### Cross Artist Coverage\n"
                        "[Based on reading cross_artist_focus articles, cross_artists from global_mentions and \
                                longitudinal_cross_artists from longitudinal_mentions]\n"
                        "- How is {guitarist_name} discussed alongside others in random articles?\n"
                        "- Reference specific content from articles\n"
                        "- YOU MUST USE global_cross_artist if available\n"
                        "- YOU MUST USE longitudinal_cross_artist if available\n"
                        "- How does this contextualize the coverage?\n\n"
                        "- How have mentions changed over time?\n"
                        "- Any quarterly trends?\n\n"
                        "- CITE articles using: title (Website, YYYY-MM-DD)\n"
                        "- GENERATE an compelling narrative when citing excerpts instead of list bullet points\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"
                        
                        "## Thematic Category Analysis\n"
                        "[Combine random article reading with category analysis]\n"
                        "- Use global_categories and top_categories\n"
                        "- What themes dominate coverage?\n"
                        "- How do the themes from categories manifest in article content?\n"
                        "- What narratives emerge from ALL data sources?\n"
                        "- How do categories relate to article content?\n"
                        "- Check category_analysis.category_examples_from_sample to see actual article examples for each category\n"
                        "- Include focus-specific category patterns from random_article_selection.category_analysis\n\n"
                        "- Use longitudinal_categories if available\n"
                        "- How have themes changed over time?\n"
                        "- Any quarterly trends?\n"
                        "- IMPORTANT: Only attribute articles to categories they ACTUALLY belong to.\n"
                        "- CITE articles using: title (Website, YYYY-MM-DD)\n"
                        "- GENERATE an compelling narrative when citing excerpts instead of list bullet points.\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n"
                        "- CONSTRAINT: 1 of the 3 paragraphs should emphasize patterns between media focus breakdown and thematic categories.\n\n"

                        "## Vocabulary Profile\n"
                        "[Combine total_body_words, avg_words_per_article and vocabulary_profile]\n"
                        "- NARRATIVE START: Open by synthesizing the total volume of coverage and average article depth into a statement on media exhaustiveness. Use natural language (e.g., 'cumulative linguistic footprint' or 'narrative density).\n"
                        "- PERSONA SYNTHESIS: Analyze how specific nouns, verbs and adjectives reveal the subject’s agency. (e.g., Do action-oriented verbs align with a 'technical innovator' persona, or do abstract nouns suggest a 'philosophical/artistic' framing?)\n"
                        "- THEMATIC & SENTIMENT SYNERGY: Interpret the top nouns and adjectives as the linguistic 'DNA' of the persona. Explicitly cross-reference how the dominant vocabulary validates both the 'Thematic Category Analysis' (the 'what') and the 'Sentiment & Tone' (the 'how').\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"

                        "## Media Flow Analysis\n"
                        "Analyze the multi-dimensional flow data for {guitarist_name}.\n\n"
                        "Each record is a path: website → editorial_format → media_focus → artist_density → topic_depth (with count).\n\n"
                        "**TERMINOLOGY GUIDELINES:**\n"
                        "• Use 'articles' or 'instances' instead of 'counts'\n"
                        "• Refer to 'coverage' or 'reporting' rather than 'data'\n"
                        "• Describe patterns as 'architectures', 'landscapes', or 'ecologies'\n"
                        "• Frame findings in journalistic, not statistical, language\n\n"
                        "**Analyze patterns, NOT dimensions. Find relationships:**\n"
                        "1. **OVERALL LANDSCAPE:** Start with the highest-volume sources. Establish dominant patterns across all sources before detailing specifics.\n\n"
                        "2. **CONTRASTING APPROACHES:** Compare how sources differ in their coverage strategies. Order by volume (highest to lowest).\n\n"
                        "3. **ARCHITECTURAL INSIGHTS:** Synthesize 2-3 high-level patterns. What does the complete flow reveal about media identity?\n\n"
                        "**ANALYSIS PRIORITY:** Lead with highest-volume sources, then mid-volume, then selective/niche sources. Never start with a minor source.\n\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- DEPTH REQUIREMENT: Include specific quantitative observations using the actual count data.\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"

                        "## Conclusion\n"
                        "[Synthesize ALL findings from complete data antgralysis]\n"
                        "- INCLUDE findings on Cultural Impact, Artistic Identity, Vocabulary Profile and\
                            patterns between media focus breakdown and thematic categories.\n"
                        "- ⚠️⚠️⚠️ CRITICAL WRITING GUIDELINE - MUST FOLLOW EXACTLY ⚠️⚠️⚠️\n\n"
                        "- TOTAL WORD COUNT: 440-460 words. HARD RANGE. NOT 400. NOT 500.\n"
                        "- PARAGRAPH STRUCTURE: EXACTLY 3 paragraphs.\n"
                        "- PARAGRAPH LENGTH: Each paragraph MUST be 145-155 words.\n"
                        "- PARAGRAPH BALANCE: All 3 paragraphs must be within 10 words of each other.\n"
                        "- SPACE UTILIZATION: The panel height expects 440-460 words total. Meet this target.\n"
                        "- DEPTH REQUIREMENT: Include specific examples, citations, data points, and analytical insights.\n\n"
                        "- VERIFICATION: After writing, count words per paragraph and total. Adjust if outside ranges.\n"
                        "- FAILURE: Outside ranges = REJECTED.\n\n"
                        
                        "## Methodological Note:\n"
                        "This analysis is based on articles collected from six core publications: louder,\
                        Loudwire, Ultimate Classic Rock, Kerrang!, Planet Rock, and The New York Times. The target \
                        guitarists for analysis were identified via Named Entity Recognition, drawing from Guitar \
                        World's authoritative list, 'The 100 Greatest Guitarists of All Time'.\n\n"

        ),
        expected_output="Comprehensive report analyzing pre-calculated metrics, random article samples, and category data with proper citations including actual article categories",
        agent=report_agent,
        name="Write Comprehensive Media Analysis Report",
        markdown=True
    )
    
    return Crew(
        agents=[report_agent],
        tasks=[write_report_task],
        process=Process.sequential,
        verbose=False
    )

#------------------------------------------------------------------------------
# MAIN EXECUTION
#------------------------------------------------------------------------------
def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        target_guitarist = sys.argv[1]
    else:
        target_guitarist = 'Slash'
    
    print(f"COMPREHENSIVE RANDOM ANALYSIS: {target_guitarist}")
    print("=" * 60)
    
    # Wait to respect rate limits
    print("Waiting 10 seconds before starting...")
    time.sleep(10)
    
    # Create and run crew
    crew = create_crew()
    
    inputs = {"guitarist_name": target_guitarist}
    final_report = crew.kickoff(inputs=inputs)
    
    # Clean the output
    cleaned_report = clean_thinking_sections(str(final_report), target_guitarist)
    
    filename = f"{target_guitarist.lower().replace(' ', '_').replace('/', '_')}_media_coverage_report_{int(time.time())}.md"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_report)
        print(f"Media coverage report saved to '{filename}'")
    except Exception as e:
        print(f"Error: {e}")
        return

    timestamp = int(time.time())

    # After saving markdown, save json paragraphs
    json_filename = extract_paragraphs_to_json(cleaned_report, target_guitarist, timestamp)
    
    print(f"JSON paragraphs saved to '{json_filename}'")

if __name__ == '__main__':
    main()