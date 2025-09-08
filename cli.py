#!/usr/bin/env python3
"""
CLI интерфейс для универсального рендерера
"""

import asyncio
import argparse
import json
import sys
from typing import Optional
from main_controller import UniversalRenderer, get_universal_html
from config import config, validate_config


async def render_url(url: str, 
                    output_file: Optional[str] = None,
                    show_analysis: bool = False,
                    browserbase_api_key: Optional[str] = None,
                    browserbase_project_id: Optional[str] = None) -> None:
    """
    Рендерит URL и выводит результат
    
    Args:
        url: URL для рендеринга
        output_file: Файл для сохранения HTML (опционально)
        show_analysis: Показывать детальный анализ детекции
        browserbase_api_key: API ключ Browserbase
        browserbase_project_id: ID проекта Browserbase
    """
    print(f"Rendering URL: {url}")
    print("-" * 50)
    
    try:
        result = await get_universal_html(
            url, 
            browserbase_api_key, 
            browserbase_project_id
        )
        
        # Основная информация
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Title: {result.get('page_title', 'N/A')}")
        print(f"Final URL: {result.get('final_url', 'N/A')}")
        print(f"Status Code: {result.get('status_code', 'N/A')}")
        print(f"Content Length: {result.get('content_length', 0)} bytes")
        print(f"Render Time: {result.get('render_time', 0):.2f} seconds")
        
        # Информация об эскалации
        if result.get('escalation_reason'):
            print(f"Escalation Reason: {result['escalation_reason']}")
        
        # Детальный анализ детекции
        if show_analysis and result.get('detection_analysis'):
            analysis = result['detection_analysis']
            print(f"\nDetection Analysis:")
            print(f"  Confidence Score: {analysis.get('confidence_score', 0):.2f}")
            print(f"  Is Blocked: {analysis.get('is_blocked', False)}")
            
            if analysis.get('blocking_reasons'):
                print(f"  Blocking Reasons:")
                for reason in analysis['blocking_reasons']:
                    print(f"    - {reason}")
            
            if analysis.get('rule_results'):
                print(f"  Rule Results:")
                for rule, result_data in analysis['rule_results'].items():
                    print(f"    {rule}: {'BLOCKED' if result_data.get('blocked') else 'OK'}")
        
        # Ошибки
        if result.get('error'):
            print(f"\nError: {result['error']}")
            sys.exit(1)
        
        # Сохранение HTML в файл
        if output_file and result.get('html_content'):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['html_content'])
            print(f"\nHTML saved to: {output_file}")
        
        # Вывод HTML в консоль (если не сохранен в файл)
        elif not output_file and result.get('html_content'):
            print(f"\nHTML Content (first 500 chars):")
            print("-" * 30)
            print(result['html_content'][:500])
            if len(result['html_content']) > 500:
                print("... (truncated)")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


async def batch_render(urls_file: str, 
                      output_dir: str = "output",
                      browserbase_api_key: Optional[str] = None,
                      browserbase_project_id: Optional[str] = None) -> None:
    """
    Пакетный рендеринг URL из файла
    
    Args:
        urls_file: Файл с URL (по одному на строку)
        output_dir: Директория для сохранения результатов
        browserbase_api_key: API ключ Browserbase
        browserbase_project_id: ID проекта Browserbase
    """
    import os
    
    # Создаем директорию для результатов
    os.makedirs(output_dir, exist_ok=True)
    
    # Читаем URL из файла
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Batch rendering {len(urls)} URLs...")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            result = await get_universal_html(
                url, 
                browserbase_api_key, 
                browserbase_project_id
            )
            
            # Сохраняем HTML
            safe_filename = f"page_{i:03d}.html"
            output_file = os.path.join(output_dir, safe_filename)
            
            if result.get('html_content'):
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['html_content'])
            
            # Сохраняем метаданные
            metadata = {
                'url': url,
                'source': result.get('source'),
                'title': result.get('page_title'),
                'final_url': result.get('final_url'),
                'status_code': result.get('status_code'),
                'content_length': result.get('content_length'),
                'render_time': result.get('render_time'),
                'escalation_reason': result.get('escalation_reason'),
                'html_file': safe_filename,
                'error': result.get('error')
            }
            
            results.append(metadata)
            
            print(f"  Source: {result.get('source')}")
            print(f"  Title: {result.get('page_title', 'N/A')}")
            print(f"  Content Length: {result.get('content_length', 0)} bytes")
            print(f"  Render Time: {result.get('render_time', 0):.2f}s")
            
            if result.get('escalation_reason'):
                print(f"  Escalation: {result['escalation_reason']}")
            
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            results.append({
                'url': url,
                'error': str(e)
            })
    
    # Сохраняем сводку
    summary_file = os.path.join(output_dir, 'summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nBatch rendering completed!")
    print(f"Results saved in: {output_dir}")
    print(f"Summary: {summary_file}")


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Universal HTML Renderer with Intelligent Escalation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render single URL
  python cli.py https://example.com
  
  # Render with detailed analysis
  python cli.py https://example.com --analysis
  
  # Save HTML to file
  python cli.py https://example.com --output page.html
  
  # Batch render from file
  python cli.py --batch urls.txt --output-dir results/
  
  # With Browserbase credentials
  python cli.py https://example.com --browserbase-key YOUR_KEY --browserbase-project YOUR_PROJECT
        """
    )
    
    # Основные аргументы
    parser.add_argument('url', nargs='?', help='URL to render')
    parser.add_argument('--output', '-o', help='Output file for HTML content')
    parser.add_argument('--analysis', '-a', action='store_true', 
                       help='Show detailed detection analysis')
    
    # Пакетный режим
    parser.add_argument('--batch', help='Batch mode: file with URLs (one per line)')
    parser.add_argument('--output-dir', default='output', 
                       help='Output directory for batch mode (default: output)')
    
    # Browserbase настройки
    parser.add_argument('--browserbase-key', 
                       help='Browserbase API key (or set BROWSERBASE_API_KEY env var)')
    parser.add_argument('--browserbase-project', 
                       help='Browserbase project ID (or set BROWSERBASE_PROJECT_ID env var)')
    
    # Настройки рендерера
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--timeout', type=int, default=30000,
                       help='Timeout in milliseconds (default: 30000)')
    
    # Информация
    parser.add_argument('--version', action='version', version='Universal Renderer 1.0.0')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    
    # Показ конфигурации
    if args.config:
        print("Current Configuration:")
        print(json.dumps(config, indent=2))
        return
    
    # Валидация конфигурации
    if not validate_config(config):
        print("Error: Invalid configuration")
        sys.exit(1)
    
    # Пакетный режим
    if args.batch:
        asyncio.run(batch_render(
            args.batch,
            args.output_dir,
            args.browserbase_key,
            args.browserbase_project
        ))
        return
    
    # Одиночный URL
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    asyncio.run(render_url(
        args.url,
        args.output,
        args.analysis,
        args.browserbase_key,
        args.browserbase_project
    ))


if __name__ == "__main__":
    main()