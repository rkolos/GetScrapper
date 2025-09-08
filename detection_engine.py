"""
Движок Детекции блокировок и анти-бот систем
Анализирует результаты локального рендеринга и определяет необходимость эскалации
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Класс для детекции блокировок и анти-бот систем"""
    
    def __init__(self):
        # Ключевые слова в заголовке страницы (высокий приоритет)
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
        
        # URL паттерны для челленджей (высокий приоритет)
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
        
        # HTML селекторы известных блокировщиков (высокий приоритет)
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
        
        # Фразы в контенте (средний приоритет)
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
        
        # Компилируем регулярные выражения для производительности
        self.title_regex = re.compile('|'.join(self.title_blocking_keywords), re.IGNORECASE)
        self.url_regex = re.compile('|'.join(self.url_challenge_patterns), re.IGNORECASE)
        self.content_regex = re.compile('|'.join(self.content_blocking_phrases), re.IGNORECASE)
    
    def analyze(self, render_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Анализирует результат рендеринга и определяет, заблокирован ли запрос
        
        Args:
            render_result: Результат от fetch_js_local()
            
        Returns:
            Tuple[bool, Dict]: (is_blocked, analysis_details)
        """
        analysis = {
            'is_blocked': False,
            'blocking_reasons': [],
            'confidence_score': 0.0,
            'rule_results': {}
        }
        
        # Проверяем наличие ошибки рендеринга
        if render_result.get('error'):
            analysis['is_blocked'] = True
            analysis['blocking_reasons'].append(f"Render error: {render_result['error']}")
            analysis['confidence_score'] = 1.0
            return True, analysis
        
        # Правило 1: Анализ заголовка (высокий приоритет)
        title_result = self._check_title_blocking(render_result.get('page_title', ''))
        analysis['rule_results']['title_check'] = title_result
        if title_result['blocked']:
            analysis['blocking_reasons'].extend(title_result['reasons'])
            analysis['confidence_score'] += 0.4
        
        # Правило 2: Анализ URL (высокий приоритет)
        url_result = self._check_url_blocking(render_result.get('final_url', ''))
        analysis['rule_results']['url_check'] = url_result
        if url_result['blocked']:
            analysis['blocking_reasons'].extend(url_result['reasons'])
            analysis['confidence_score'] += 0.4
        
        # Правило 3: Структурный анализ HTML (критический приоритет)
        html_result = self._check_html_blocking(render_result.get('html_content', ''))
        analysis['rule_results']['html_check'] = html_result
        if html_result['blocked']:
            analysis['blocking_reasons'].extend(html_result['reasons'])
            # HTML-анализ имеет максимальный приоритет - если найден критический селектор
            if any('Critical' in reason for reason in html_result['reasons']):
                analysis['confidence_score'] = 1.0  # 100% уверенность
            else:
                analysis['confidence_score'] += 0.5  # Высокий приоритет
        
        # Правило 4: Анализ контента (средний приоритет)
        content_result = self._check_content_blocking(render_result.get('html_content', ''))
        analysis['rule_results']['content_check'] = content_result
        if content_result['blocked']:
            analysis['blocking_reasons'].extend(content_result['reasons'])
            analysis['confidence_score'] += 0.2
        
        # Правило 5: Эвристика "пустой страницы" (низкий приоритет)
        empty_result = self._check_empty_page(render_result)
        analysis['rule_results']['empty_page_check'] = empty_result
        if empty_result['blocked']:
            analysis['blocking_reasons'].extend(empty_result['reasons'])
            analysis['confidence_score'] += 0.1
        
        # Определяем финальное решение
        # Специальная логика для пустых страниц - только если это единственная причина
        if empty_result['blocked'] and len(analysis['blocking_reasons']) == 1:
            analysis['is_blocked'] = True
        else:
            analysis['is_blocked'] = analysis['confidence_score'] >= 0.3
        
        analysis['confidence_score'] = min(analysis['confidence_score'], 1.0)
        
        return analysis['is_blocked'], analysis
    
    def _check_title_blocking(self, title: str) -> Dict[str, Any]:
        """Проверяет заголовок страницы на признаки блокировки"""
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
        """Проверяет URL на признаки челленджей"""
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
        """Проверяет HTML на структурные признаки блокировщиков"""
        result = {'blocked': False, 'reasons': [], 'found_selectors': []}
        
        if not html_content:
            return result
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Критически важные селекторы - 100% блокировка
            critical_selectors = [
                # Cloudflare challenge
                soup.find("div", id=re.compile(r"cf-challenge", re.IGNORECASE)),
                soup.find("form", id="challenge-form"),
                # reCAPTCHA и hCaptcha
                soup.find("iframe", src=re.compile(r"hcaptcha\.com|recaptcha\.net|recaptcha\.com")),
                # Дополнительные критические селекторы
                soup.find("div", class_=re.compile(r"cf-challenge", re.IGNORECASE)),
                soup.find("div", id=re.compile(r"challenge", re.IGNORECASE)),
                soup.find("div", class_=re.compile(r"challenge", re.IGNORECASE)),
                soup.find("div", id=re.compile(r"captcha", re.IGNORECASE)),
                soup.find("div", class_=re.compile(r"captcha", re.IGNORECASE)),
            ]
            
            # Проверяем критические селекторы
            for element in critical_selectors:
                if element:
                    result['blocked'] = True
                    result['found_selectors'].append(f"Critical: {element.name}#{element.get('id', '')}.{element.get('class', [])}")
                    result['reasons'].append(f"Critical blocking element found: {element.name}")
                    # Если найден критический селектор, сразу возвращаем True
                    return result
            
            # Проверяем остальные селекторы
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
        """Проверяет содержимое на фразы блокировки"""
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
        """Проверяет на пустую страницу (эвристика)"""
        result = {'blocked': False, 'reasons': []}
        
        status_code = render_result.get('status_code', 0)
        content_length = render_result.get('content_length', 0)
        html_content = render_result.get('html_content', '')
        
        # Проверяем на наличие meta refresh (может указывать на редирект)
        if html_content and 'meta http-equiv="refresh"' in html_content.lower():
            result['blocked'] = True
            result['reasons'].append("Meta refresh tag found (possible redirect)")
        
        # Проверяем на очень маленькую страницу ТОЛЬКО если нет контента
        if status_code == 200 and content_length < 200:
            # Дополнительная проверка - если есть хотя бы какой-то контент, не блокируем
            if html_content:
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.find('body')
                    if body:
                        text_content = body.get_text(strip=True)
                        # Блокируем только если контент действительно пустой
                        if len(text_content) < 10:
                            result['blocked'] = True
                            result['reasons'].append(f"Very small page ({content_length} bytes) with minimal content")
                except Exception:
                    # Если не можем распарсить, блокируем маленькие страницы
                    result['blocked'] = True
                    result['reasons'].append(f"Very small page ({content_length} bytes) with parsing error")
        
        return result


# Пример использования
if __name__ == "__main__":
    # Тестовые данные
    test_cases = [
        {
            'name': 'Normal page',
            'data': {
                'html_content': '<html><head><title>Normal Page</title></head><body><h1>Hello World</h1></body></html>',
                'page_title': 'Normal Page',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 100
            }
        },
        {
            'name': 'Cloudflare challenge',
            'data': {
                'html_content': '<html><head><title>Just a moment...</title></head><body><div id="cf-challenge">Checking your browser</div></body></html>',
                'page_title': 'Just a moment...',
                'final_url': 'https://example.com/cdn-cgi/challenge',
                'status_code': 200,
                'content_length': 200
            }
        },
        {
            'name': 'reCAPTCHA challenge',
            'data': {
                'html_content': '<html><head><title>Verify you are human</title></head><body><iframe src="https://www.google.com/recaptcha/api2/anchor"></iframe></body></html>',
                'page_title': 'Verify you are human',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 300
            }
        },
        {
            'name': 'hCaptcha challenge',
            'data': {
                'html_content': '<html><head><title>Security Check</title></head><body><iframe src="https://hcaptcha.com/1/api.js"></iframe></body></html>',
                'page_title': 'Security Check',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 250
            }
        },
        {
            'name': 'Empty page',
            'data': {
                'html_content': '<html><head><title></title></head><body></body></html>',
                'page_title': '',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 80
            }
        }
    ]
    
    engine = DetectionEngine()
    
    for test_case in test_cases:
        logger.info(f"\n=== {test_case['name']} ===")
        is_blocked, analysis = engine.analyze(test_case['data'])
        logger.info(f"Blocked: {is_blocked}")
        logger.info(f"Confidence: {analysis['confidence_score']:.2f}")
        logger.info(f"Reasons: {analysis['blocking_reasons']}")