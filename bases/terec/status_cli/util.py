import os
from typing import Any

import aiohttp
import asyncio
import requests
from urllib.parse import urlparse


def not_none(v: str, msg: str) -> str:
    if not v:
        raise ValueError(msg)
    return v


def env_terec_url() -> str:
    url = os.environ.get("TEREC_URL", None)
    url = not_none(url, "TEREC_URL is not set or empty.")
    parse_result = urlparse(url)
    if not (parse_result.scheme and parse_result.netloc):
        raise ValueError(f"{url} is not a valid TEREC_URL.")
    return url


def value_or_env(val: str, env_var: str) -> str:
    return val or os.environ.get(env_var, None)


def get_terec_rest_api(url: str, query_params: dict):
    resp = requests.get(url=url, params=query_params)
    if resp.ok:
        return resp.json()
    else:
        raise Exception(f"Error when calling {url}: {resp.text}")


async def get_terec_rest_api_json_async(
    session: aiohttp.ClientSession, url: str, query_params: dict
):
    resp = await session.request(method="GET", url=url, params=query_params)
    resp.raise_for_status()
    json = await resp.json()
    return json


async def collect_terec_rest_api_calls(calls: list[tuple[Any, str, dict]]):
    results = {}

    async def collect_task(task_name, session, url, params):
        resp = await get_terec_rest_api_json_async(
            session=session, url=url, query_params=params
        )
        results[task_name] = resp

    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, url, params in calls:
            tasks.append(
                collect_task(task_name=name, session=session, url=url, params=params)
            )
        await asyncio.gather(*tasks)

    return results


def typer_table_config(title: str, caption: str):
    from rich import box

    return {
        "show_header": True,
        "header_style": "bold magenta",
        "title": title,
        "title_justify": "left",
        "caption": caption,
        "caption_justify": "left",
        "safe_box": True,
        "box": box.ROUNDED,
    }


def ratio_str(hit: int, total: int) -> str:
    if total > 0:
        ratio = int(100 * hit / total)
        return f"[{ratio}%]"
    else:
        return ""
