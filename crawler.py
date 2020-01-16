import click
import validators

from helpers.common import logger
from helpers.parsing import process_crawler
from helpers.post_request import process_sender


@click.command()
@click.option('--url', '-u', help='Url сайта')
@click.option('--depth', '-d', default=1, help='Глубина обхода')
def main(url, depth):
    if not validators.url(url):
        logger.critical(f'url not valid: {url}')
        return None
    logger.info(f'start parsing: {url}, max depth: {depth}')

    links, forms = process_crawler([url], depth)
    logger.info(f'links received: {len(links)} forms received {len(forms)}')

    if forms:
        process_sender(forms)
    logger.info('end parsing')


if __name__ == '__main__':
    main()
