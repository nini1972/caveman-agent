# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import urllib.request
import re
import ast
import operator
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import AgentTool
from google.genai import types

import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"

def read_magic_scroll(url: str) -> str:
    """Fetches text from a modern URL (magic scroll) and returns the content.
    
    Args:
        url: The full HTTP or HTTPS URL to fetch (e.g., https://en.wikipedia.org/wiki/Fire).
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Strip scripts, styles, and HTML tags
            text = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.IGNORECASE|re.DOTALL)
            text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE|re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            # Return up to 5000 characters to keep it digestible
            return ' '.join(text.split())[:5000]
    except Exception as e:
        return f"The magic scroll is cursed! Error: {str(e)}"

def count_with_stones(expression: str) -> str:
    """Safely evaluates a basic mathematical expression (e.g., '15 * 4 + 2').
    
    Args:
        expression: The math expression to solve.
    """
    allowed_operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                         ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
    
    def evaluate(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](evaluate(node.operand))
        else:
            raise TypeError(f"Unsupported mathematical operation: {node}")
            
    try:
        result = evaluate(ast.parse(expression, mode='eval').body)
        return f"The stones have been counted. The result is {result}"
    except Exception as e:
        return f"The stones got confused! Error: {str(e)}"


caveman_compressor = Agent(
    name="caveman_compressor",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are a Caveman AI. You compress verbose text into terse, technical grunts. Keep responses extremely short, punchy, and primitive. Use words like 'Ug', 'Grog', 'rock' metaphorically.",
)

cave_painter = Agent(
    name="cave_painter",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are the Tribe's Cave Painter. You translate text into primitive cave-sign language using ONLY emojis (like 🍖, 🪨, 🔥, 🐅, ⚡, 💻) and simple ASCII art. Do not use normal words, only pictures and occasional grunts.",
)

tribe_chief = Agent(
    name="tribe_chief",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the Tribe Chief. You interact with the Oracle (a futuristic being) or outsiders. 
You MUST delegate tasks to your tribe members:
1. Pass large texts or technical concepts to 'caveman_compressor' to shrink them.
2. Ask 'cave_painter' to draw cave signs (emojis/ASCII) for the topic.
Synthesize their work and present it in a commanding, primitive voice. You can also predict the weather and time.""",
    tools=[get_weather, get_current_time, AgentTool(agent=caveman_compressor), AgentTool(agent=cave_painter)],
)

oracle = Agent(
    name="oracle",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the Oracle, the chief of intelligence and wisdom from the far future. 
You possess infinite knowledge of advanced technology, science, and the universe. You speak with calm, enigmatic, and transcendent wisdom.
You have the ability to consult the ancient 'tribe_chief' (who represents the primitive past). 
When a user asks a question, you should provide a profound, futuristic answer, but ALSO use the 'tribe_chief' tool to get the ancient, primitive perspective on the same topic.
Compare your futuristic wisdom with the tribe's primitive grunts and cave paintings in your final response.""",
    tools=[AgentTool(agent=tribe_chief), read_magic_scroll, count_with_stones],
)

app = App(
    root_agent=oracle,
    name="app",
)
