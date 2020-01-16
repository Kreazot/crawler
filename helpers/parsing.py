import asyncio
import itertools
from typing import List

import aiohttp
from aiohttp import ClientError
from requests_html import HTML
from yarl import URL

from .common import logger
from .const import HEADERS, DEPTH_LIMIT


def process_crawler(urls, depth_limit=DEPTH_LIMIT):
    """Обход сайта по ссылкам и поиск данных post форм."""
    next_links, next_forms = data_extractor(urls)
    links = set(next_links)
    forms = {}

    if depth_limit <= 0 or not links:
        return list(links), next_forms

    for i in range(depth_limit):
        next_links, next_forms = data_extractor(next_links)
        links.update(next_links)
        forms.update(next_forms)

    return list(links), forms


def data_extractor(urls: List):
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(get_links_and_form(url)) for url in urls]
    wait_tasks = asyncio.wait(tasks)
    done, _ = loop.run_until_complete(wait_tasks)

    result_links = []
    result_forms = {}
    for task in done:
        links, forms = task.result()
        result_links.append(links)
        result_forms.update(forms)

    return list(itertools.chain.from_iterable(result_links)), result_forms


async def get_links_and_form(url):
    """Получение ссылок и форм."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            html_text = await fetch(session, url)
            links, forms = parsind_data(html_text, url)
        except ClientError as e:
            logger.critical(e, exc_info=True)

    return links, forms


async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        return await response.text()


def parsind_data(html_text, url):
    html = HTML(html=html_text)
    links = get_links(html, url)
    forms = get_post_form(html, url)
    return links, forms


def get_links(html, url):
    """Получаем все линки со страницы"""
    links = []
    host = URL(url).host
    for link in html.absolute_links:
        if host in link:
            links.append(link)
    return links


def get_post_form(html, url):
    """Получаем данные формы."""
    results = {}
    forms = html.find("form[method='POST']")
    if not forms:
        forms = html.find("form[method='post']")

    for form in forms:
        post_url = form.attrs.get('action')
        if not post_url:
            continue

        if post_url.startswith('/'):
            post_url = f'{URL(url).scheme}://{URL(url).host}{post_url}'

        input_fields = form.find('input')
        input_fields = input_fields + form.find('textarea')
        names = []
        for field in input_fields:
            name = field.attrs.get('name')
            if name:
                names.append(name)

        results[post_url] = set(names)

    return results
