import os
from dotenv import load_dotenv

import datetime
import zoneinfo

from AppOpener import open, close

from tavily import TavilyClient


def get_current_time(timezone: str = "local") -> str:
    if timezone == "local":
        now = datetime.datetime.now().astimezone()
    else:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def open_apps(apps: str) -> None:
    open(apps)


def close_apps(apps: str) -> None:
    close(apps)


def search_web(query: str) -> str:
    load_dotenv()
    token = os.getenv("TAVILY_KEY")

    tavily_client = TavilyClient(api_key=token)
    response = tavily_client.search(query)
    content = response.get("results")[0].get("content")

    return content


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "returns today's date in the format YYYY-MM-DD",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone name, or 'local' for the system timezone.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_apps",
            "description": "opens an application or multiple applications (has to be separated by commas)",
            "parameters": {
                "type": "object",
                "properties": {
                    "apps": {
                        "type": "string",
                        "description": "application(s) to open; separate by commas if opening multiple applications",
                    }
                },
                "required": ["apps"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_apps",
            "description": "closes an application or multiple applications (has to be separated by commas)",
            "parameters": {
                "type": "object",
                "properties": {
                    "apps": {
                        "type": "string",
                        "description": "application(s) to close; separate by commas if closing multiple applications",
                    }
                },
                "required": ["apps"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "searches the web for the provided query. Returns information about the query. Should be used only when other tools don't provide sufficient information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "query to search for",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

_TOOL_REFS = {
    "get_current_time": get_current_time,
    "open_apps": open_apps,
    "close_apps": close_apps,
    "search_web": search_web,
}


def call_tool(name: str, arguments: dict) -> str:
    ref = _TOOL_REFS.get(name)
    if ref is None:
        return f"Error: unknown tool '{name}'."
    try:
        return ref(**arguments)
    except Exception as e:
        return f"Error running tool '{name}': {e}"
