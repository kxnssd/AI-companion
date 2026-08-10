import datetime
from AppOpener import open, close


def get_current_time(timezone: str = "local") -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def open_apps(apps: str):
    open(apps)


def close_apps(apps: str):
    close(apps)


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
            "name": "open_apps",
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
]

_TOOL_REFS = {
    "get_current_time": get_current_time,
    "open_apps": open_apps,
    "close_apps": close_apps,
}


def call_tool(name: str, arguments: dict) -> str:
    ref = _TOOL_REFS.get(name)
    if ref is None:
        return f"Error: unknown tool '{name}'."
    try:
        return ref(**arguments)
    except Exception as e:
        return f"Error running tool '{name}': {e}"
