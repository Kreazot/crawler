import asyncio
from typing import List

import aiohttp
from aiohttp import ClientError

from .common import logger
from .const import HEADERS


def process_sender(form_data: dict) -> None:

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(
            send_data(url, fields)
        ) for url, fields in form_data.items()
    ]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)


async def send_data(url, fields):
    """Отправка post запросов."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            payload = create_payload(fields)
            response = await send(session, url, payload)
            logger.info(f'url: {url} size: {len(response.encode())}')
        except ClientError as e:
            logger.critical(e, exc_info=True)


async def send(session, url, payload):
    async with session.post(url, data=payload, ssl=False) as response:
        return await response.text()


def create_payload(fields: List):
    """Метод заглушка, имитирует создание фейковых данных для payload."""
    payload = {}
    for field in fields:
        payload[field] = 'example data'

    return payload
