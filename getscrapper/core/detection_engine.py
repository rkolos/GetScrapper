"""Detection engine for analyzing HTML content and detecting blocking systems."""

import re
import logging
from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Engine for detecting blocking systems and anti-bot protection."""
    
    def __init__(self):
        # Keywords in page title (high priority)
        self.title_blocking_keywords = [
            r'just a moment',
            r'checking your browser',
            r'verify you are human',
            r'attention required',
            r'security check',
            r'проверка безопасности',
            r'please wait',
            r'enable javascript',
            r'loading\.\.\.',
            r'please enable javascript',
            r'browser check',
            r'cloudflare',
            r'ddos protection',
            r'access denied',
            r'blocked',
            r'captcha',
            r'challenge',
            r'verification',
            r'robot check',
            r'human verification'
        ]
        
        # URL patterns for challenges (high priority)
        self.url_challenge_patterns = [
            r'/cdn-cgi/',
            r'/challenge-platform/',
            r'[?&]chk=',
            r'/_verify/',
            r'/challenge/',
            r'/verify/',
            r'/security-check/',
            r'/bot-detection/',
            r'/captcha/',
            r'/human-verification/',
            r'[?&]cf_challenge=',
            r'[?&]challenge=',
            r'[?&]verify='
        ]
        
        # HTML selectors for known blockers (high priority)
        self.html_blocking_selectors = [
            'div[id*="cf-challenge"]',
            'div[class*="cf-challenge"]',
            'form[id="challenge-form"]',
            'iframe[src*="hcaptcha.com"]',
            'iframe[src*="recaptcha.net"]',
            'iframe[src*="recaptcha.com"]',
            'div[class*="g-recaptcha"]',
            'div[id*="recaptcha"]',
            'div[class*="captcha"]',
            'div[id*="captcha"]',
            'div[class*="challenge"]',
            'div[id*="challenge"]',
            'div[class*="verification"]',
            'div[id*="verification"]',
            'div[class*="cloudflare"]',
            'div[id*="cloudflare"]',
            'div[class*="ddos-protection"]',
            'div[id*="ddos-protection"]',
            'div[class*="security-check"]',
            'div[id*="security-check"]',
            'div[class*="bot-detection"]',
            'div[id*="bot-detection"]',
            'div[class*="human-verification"]',
            'div[id*="human-verification"]',
            'div[class*="access-denied"]',
            'div[id*="access-denied"]',
            'div[class*="blocked"]',
            'div[id*="blocked"]'
        ]
        
        # Content phrases (medium priority)
        self.content_blocking_phrases = [
            r'ddos protection by cloudflare',
            r'protected by incapsula',
            r'checking the browser',
            r'this site is protected by',
            r'please wait while we check your browser',
            r'verifying you are human',
            r'security check in progress',
            r'access denied',
            r'you have been blocked',
            r'bot detection',
            r'human verification required',
            r'please complete the security check',
            r'javascript is required',
            r'please enable javascript',
            r'browser verification',
            r'anti-bot protection',
            r'rate limit exceeded',
            r'too many requests',
            r'проверка браузера',
            r'защита от ddos',
            r'доступ запрещен',
            r'вы заблокированы',
            r'проверка безопасности'
        ]
        
        # Compile regex patterns for performance
        self.title_regex = re.compile('|'.join(self.title_blocking_keywords), re.IGNORECASE)
        self.url_regex = re.compile('|'.join(self.url_challenge_patterns), re.IGNORECASE)
        self.content_regex = re.compile('|'.join(self.content_blocking_phrases), re.IGNORECASE)
    
    def analyze(self, render_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze render result and determine if request is blocked.
        
        Args:
            render_result: Result from fetcher strategy
            
        Returns:
            Tuple[bool, Dict]: (is_blocked, analysis_details)
        """
        analysis = {
            'is_blocked': False,
            'blocking_reasons': [],
            'confidence_score': 0.0,
            'rule_results': {}
        }
        
        # Check for render error
        if render_result.get('error'):
            analysis['is_blocked'] = True
            analysis['blocking_reasons'].append(f"Render error: {render_result['error']}")
            analysis['confidence_score'] = 1.0
            return True, analysis
        
        # Rule 1: Title analysis (high priority)
        title_result = self._check_title_blocking(render_result.get('page_title', ''))
        analysis['rule_results']['title_check'] = title_result
        if title_result['blocked']:
            analysis['blocking_reasons'].extend(title_result['reasons'])
            analysis['confidence_score'] += 0.4
        
        # Rule 2: URL analysis (high priority)
        url_result = self._check_url_blocking(render_result.get('final_url', ''))
        analysis['rule_results']['url_check'] = url_result
        if url_result['blocked']:
            analysis['blocking_reasons'].extend(url_result['reasons'])
            analysis['confidence_score'] += 0.4
        
        # Rule 3: HTML structure analysis (high priority)
        html_result = self._check_html_blocking(render_result.get('html_content', ''))
        analysis['rule_results']['html_check'] = html_result
        if html_result['blocked']:
            analysis['blocking_reasons'].extend(html_result['reasons'])
            analysis['confidence_score'] += 0.3
        
        # Rule 4: Content analysis (medium priority)
        content_result = self._check_content_blocking(render_result.get('html_content', ''))
        analysis['rule_results']['content_check'] = content_result
        if content_result['blocked']:
            analysis['blocking_reasons'].extend(content_result['reasons'])
            analysis['confidence_score'] += 0.2
        
        # Rule 5: Empty page heuristic (low priority)
        empty_result = self._check_empty_page(render_result)
        analysis['rule_results']['empty_page_check'] = empty_result
        if empty_result['blocked']:
            analysis['blocking_reasons'].extend(empty_result['reasons'])
            analysis['confidence_score'] += 0.1
        
        # Determine final decision
        # Special logic for empty pages - only if it's the only reason
        if empty_result['blocked'] and len(analysis['blocking_reasons']) == 1:
            analysis['is_blocked'] = True
        else:
            analysis['is_blocked'] = analysis['confidence_score'] >= 0.3
        
        analysis['confidence_score'] = min(analysis['confidence_score'], 1.0)
        
        return analysis['is_blocked'], analysis
    
    def _check_title_blocking(self, title: str) -> Dict[str, Any]:
        """Check page title for blocking indicators."""
        result = {'blocked': False, 'reasons': [], 'matches': []}
        
        if not title:
            return result
        
        matches = self.title_regex.findall(title)
        if matches:
            result['blocked'] = True
            result['matches'] = matches
            result['reasons'].append(f"Blocking keywords in title: {', '.join(set(matches))}")
        
        return result
    
    def _check_url_blocking(self, url: str) -> Dict[str, Any]:
        """Check URL for challenge patterns."""
        result = {'blocked': False, 'reasons': [], 'matches': []}
        
        if not url:
            return result
        
        matches = self.url_regex.findall(url)
        if matches:
            result['blocked'] = True
            result['matches'] = matches
            result['reasons'].append(f"Challenge patterns in URL: {', '.join(set(matches))}")
        
        return result
    
    def _check_html_blocking(self, html_content: str) -> Dict[str, Any]:
        """Check HTML for structural blocking indicators."""
        result = {'blocked': False, 'reasons': [], 'found_selectors': []}
        
        if not html_content:
            return result
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for selector in self.html_blocking_selectors:
                elements = soup.select(selector)
                if elements:
                    result['found_selectors'].append(selector)
                    result['blocked'] = True
            
            if result['blocked']:
                result['reasons'].append(f"Blocking HTML elements found: {', '.join(result['found_selectors'])}")
        
        except Exception as e:
            logger.warning(f"HTML parsing error: {e}")
        
        return result
    
    def _check_content_blocking(self, html_content: str) -> Dict[str, Any]:
        """Check content for blocking phrases."""
        result = {'blocked': False, 'reasons': [], 'matches': []}
        
        if not html_content:
            return result
        
        matches = self.content_regex.findall(html_content)
        if matches:
            result['blocked'] = True
            result['matches'] = matches
            result['reasons'].append(f"Blocking phrases in content: {', '.join(set(matches))}")
        
        return result
    
    def _check_empty_page(self, render_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check for empty page (heuristic)."""
        result = {'blocked': False, 'reasons': []}
        
        status_code = render_result.get('status_code', 0)
        content_length = render_result.get('content_length', 0)
        html_content = render_result.get('html_content', '')
        
        # Check for meta refresh (may indicate redirect)
        if html_content and 'meta http-equiv="refresh"' in html_content.lower():
            result['blocked'] = True
            result['reasons'].append("Meta refresh tag found (possible redirect)")
        
        # Check for very small page ONLY if no content
        if status_code == 200 and content_length < 200:
            # Additional check - if there's any content, don't block
            if html_content:
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.find('body')
                    if body:
                        text_content = body.get_text(strip=True)
                        # Block only if content is truly empty
                        if len(text_content) < 10:
                            result['blocked'] = True
                            result['reasons'].append(f"Very small page ({content_length} bytes) with minimal content")
                except Exception:
                    # If can't parse, block small pages
                    result['blocked'] = True
                    result['reasons'].append(f"Very small page ({content_length} bytes) with parsing error")
        
        return result