"""Command line interface for GetScrapper."""

import json
import sys
from pathlib import Path
from typing import List, Optional

import click

from ..core.scraper import Scraper
from ..config.settings import Settings
from ..utils.logger import setup_logger


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, output_dir, verbose):
    """GetScrapper - A powerful web scraping tool."""
    # Load settings
    if config:
        settings = Settings.from_file(config)
    else:
        settings = Settings()
    
    # Override settings with CLI options
    if output_dir:
        settings.output_dir = output_dir
    
    if verbose:
        settings.logging.level = "DEBUG"
    
    # Setup logger
    logger = setup_logger(
        level=settings.logging.level,
        log_file=settings.logging.log_file
    )
    
    # Store settings in context
    ctx.ensure_object(dict)
    ctx.obj['settings'] = settings
    ctx.obj['logger'] = logger


@cli.command()
@click.argument('url')
@click.option('--parser', type=click.Choice(['html', 'json']), help='Parser type to use')
@click.option('--selectors', help='CSS selectors for HTML parsing (JSON format)')
@click.option('--extract-links', is_flag=True, help='Extract links from the page')
@click.option('--extract-images', is_flag=True, help='Extract images from the page')
@click.option('--extract-meta', is_flag=True, help='Extract meta tags from the page')
@click.option('--output-format', type=click.Choice(['csv', 'json']), default='json', help='Output format')
@click.option('--save', is_flag=True, help='Save results to file')
@click.option('--no-process', is_flag=True, help='Skip data processing')
@click.pass_context
def scrape(ctx, url, parser, selectors, extract_links, extract_images, extract_meta, 
           output_format, save, no_process):
    """Scrape a single URL."""
    settings = ctx.obj['settings']
    logger = ctx.obj['logger']
    
    try:
        # Parse selectors if provided
        selectors_dict = {}
        if selectors:
            try:
                selectors_dict = json.loads(selectors)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for selectors", err=True)
                sys.exit(1)
        
        # Initialize scraper
        with Scraper(settings.get_scraper_config()) as scraper:
            # Scrape URL
            results = scraper.scrape_url(
                url,
                parser_type=parser,
                selectors=selectors_dict,
                extract_links=extract_links,
                extract_images=extract_images,
                extract_meta=extract_meta,
                process_data=not no_process,
                save_data=save,
                output_format=output_format
            )
            
            # Display results
            if results:
                click.echo(f"Successfully scraped {len(results)} items from {url}")
                
                if not save:
                    # Print results to stdout
                    click.echo(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                click.echo("No data extracted from the URL")
                
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--file', '-f', type=click.Path(exists=True), help='File containing URLs (one per line)')
@click.option('--parser', type=click.Choice(['html', 'json']), help='Parser type to use')
@click.option('--selectors', help='CSS selectors for HTML parsing (JSON format)')
@click.option('--output-format', type=click.Choice(['csv', 'json']), default='json', help='Output format')
@click.option('--save', is_flag=True, help='Save results to file')
@click.option('--continue-on-error', is_flag=True, help='Continue processing even if some URLs fail')
@click.pass_context
def scrape_multiple(ctx, urls, file, parser, selectors, output_format, save, continue_on_error):
    """Scrape multiple URLs."""
    settings = ctx.obj['settings']
    logger = ctx.obj['logger']
    
    try:
        # Collect URLs
        all_urls = list(urls)
        if file:
            with open(file, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip()]
                all_urls.extend(file_urls)
        
        if not all_urls:
            click.echo("No URLs provided", err=True)
            sys.exit(1)
        
        # Parse selectors if provided
        selectors_dict = {}
        if selectors:
            try:
                selectors_dict = json.loads(selectors)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for selectors", err=True)
                sys.exit(1)
        
        # Initialize scraper
        with Scraper(settings.get_scraper_config()) as scraper:
            # Scrape URLs
            results = scraper.scrape_urls(
                all_urls,
                parser_type=parser,
                selectors=selectors_dict,
                save_data=save,
                output_format=output_format,
                continue_on_error=continue_on_error
            )
            
            # Display results
            if results:
                click.echo(f"Successfully scraped {len(results)} items from {len(all_urls)} URLs")
                
                if not save:
                    # Print results to stdout
                    click.echo(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                click.echo("No data extracted from any URL")
                
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def config(ctx, output):
    """Generate or display configuration."""
    settings = ctx.obj['settings']
    
    if output:
        # Save configuration to file
        settings.to_file(output)
        click.echo(f"Configuration saved to {output}")
    else:
        # Display current configuration
        click.echo(json.dumps(settings.to_dict(), indent=2, ensure_ascii=False))


@cli.command()
@click.pass_context
def info(ctx):
    """Display GetScrapper information."""
    settings = ctx.obj['settings']
    
    click.echo("GetScrapper - Web Scraping Tool")
    click.echo("=" * 40)
    click.echo(f"Version: 1.0.0")
    click.echo(f"Output Directory: {settings.output_dir}")
    click.echo(f"Max Concurrent Requests: {settings.max_concurrent_requests}")
    click.echo(f"Session Timeout: {settings.session.timeout}s")
    click.echo(f"Request Delay: {settings.session.delay}s")
    click.echo(f"User Agent: {settings.session.user_agent}")
    click.echo("=" * 40)


def main():
    """Main entry point for CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()