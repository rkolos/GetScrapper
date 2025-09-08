"""Detection controller for managing fetcher strategies and escalation logic."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from .fetchers import FetcherStrategy, StaticFetcher, LocalBrowserFetcher, BrowserbaseFetcher
from .detection_engine import DetectionEngine

logger = logging.getLogger(__name__)


class EscalationLevel(Enum):
    """Escalation levels for fetcher strategies."""
    STATIC = "static"
    LOCAL_BROWSER = "local_browser"
    BROWSERBASE = "browserbase"


class DetectionController:
    """Controller for managing fetcher strategies and detection logic."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize detection controller.
        
        Args:
            config: Configuration with keys:
                - strategies: List of strategy configurations
                - escalation_rules: Escalation rules configuration
                - detection: Detection engine configuration
        """
        self.config = config or {}
        self.logger = logger
        
        # Initialize detection engine
        detection_config = self.config.get("detection", {})
        self.detection_engine = DetectionEngine()
        
        # Initialize strategies
        self.strategies: Dict[str, FetcherStrategy] = {}
        self._initialize_strategies()
        
        # Escalation configuration
        self.escalation_config = self.config.get("escalation_rules", {})
        self.default_escalation_order = [
            EscalationLevel.STATIC,
            EscalationLevel.LOCAL_BROWSER,
            EscalationLevel.BROWSERBASE
        ]
    
    def _initialize_strategies(self) -> None:
        """Initialize available fetcher strategies."""
        strategies_config = self.config.get("strategies", {})
        
        # Static fetcher (always available)
        static_config = strategies_config.get("static", {})
        self.strategies["static"] = StaticFetcher(static_config)
        
        # Local browser fetcher
        local_browser_config = strategies_config.get("local_browser", {})
        self.strategies["local_browser"] = LocalBrowserFetcher(local_browser_config)
        
        # Browserbase fetcher
        browserbase_config = strategies_config.get("browserbase", {})
        self.strategies["browserbase"] = BrowserbaseFetcher(browserbase_config)
        
        self.logger.info(f"Initialized {len(self.strategies)} fetcher strategies")
    
    async def fetch_html_with_escalation(self, url: str, 
                                       start_level: Optional[EscalationLevel] = None,
                                       max_escalations: int = 2) -> Dict[str, Any]:
        """
        Fetch HTML with intelligent escalation.
        
        Args:
            url: URL to fetch
            start_level: Starting escalation level (default: STATIC)
            max_escalations: Maximum number of escalations allowed
            
        Returns:
            Dictionary with fetch results including escalation information
        """
        if start_level is None:
            start_level = EscalationLevel.STATIC
        
        escalation_order = self._get_escalation_order(start_level)
        escalation_history = []
        
        for i, level in enumerate(escalation_order):
            if i > max_escalations:
                break
            
            strategy_name = level.value
            strategy = self.strategies.get(strategy_name)
            
            if not strategy or not strategy.is_available():
                self.logger.warning(f"Strategy {strategy_name} not available, skipping")
                continue
            
            self.logger.info(f"Attempting fetch with {strategy_name} for: {url}")
            
            try:
                # Fetch HTML
                result = await strategy.fetch_html(url)
                result['strategy_used'] = strategy_name
                result['escalation_level'] = i
                result['escalation_history'] = escalation_history.copy()
                
                # Check for errors
                if result.get('error'):
                    self.logger.warning(f"Strategy {strategy_name} failed: {result['error']}")
                    escalation_history.append({
                        'strategy': strategy_name,
                        'error': result['error'],
                        'level': i
                    })
                    continue
                
                # Analyze result for blocking
                is_blocked, detection_analysis = self.detection_engine.analyze(result)
                result['detection_analysis'] = detection_analysis
                
                if is_blocked:
                    self.logger.warning(f"Strategy {strategy_name} detected blocking for: {url}")
                    self.logger.warning(f"Blocking reasons: {', '.join(detection_analysis['blocking_reasons'])}")
                    self.logger.warning(f"Confidence score: {detection_analysis['confidence_score']:.2f}")
                    
                    escalation_history.append({
                        'strategy': strategy_name,
                        'blocked': True,
                        'reasons': detection_analysis['blocking_reasons'],
                        'confidence': detection_analysis['confidence_score'],
                        'level': i
                    })
                    continue
                
                # Success - no blocking detected
                self.logger.info(f"Strategy {strategy_name} successful for: {url}")
                result['escalation_successful'] = True
                return result
                
            except Exception as e:
                error_msg = f"Strategy {strategy_name} exception: {str(e)}"
                self.logger.error(f"{error_msg} for URL: {url}")
                escalation_history.append({
                    'strategy': strategy_name,
                    'error': error_msg,
                    'level': i
                })
                continue
        
        # All strategies failed or were blocked
        self.logger.error(f"All strategies failed for: {url}")
        return {
            'html_content': '',
            'page_title': '',
            'final_url': url,
            'status_code': 0,
            'content_length': 0,
            'render_time': 0,
            'error': 'All strategies failed or were blocked',
            'source': 'escalation_failed',
            'strategy_used': 'none',
            'escalation_level': len(escalation_history),
            'escalation_history': escalation_history,
            'escalation_successful': False,
            'detection_analysis': None
        }
    
    def _get_escalation_order(self, start_level: EscalationLevel) -> List[EscalationLevel]:
        """Get escalation order starting from specified level."""
        start_index = self.default_escalation_order.index(start_level)
        return self.default_escalation_order[start_index:]
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names."""
        return [name for name, strategy in self.strategies.items() if strategy.is_available()]
    
    def get_strategy_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all strategies."""
        info = {}
        for name, strategy in self.strategies.items():
            info[name] = {
                'available': strategy.is_available(),
                'config': strategy.get_config(),
                'name': strategy.get_strategy_name()
            }
        return info
    
    def close(self) -> None:
        """Close all strategies."""
        for strategy in self.strategies.values():
            try:
                strategy.close()
            except Exception as e:
                self.logger.warning(f"Error closing strategy {strategy.get_strategy_name()}: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()