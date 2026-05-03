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
import json
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

def watch_youtube_crystal(url: str) -> str:
    """Extracts the spoken text (transcript) from a YouTube video URL.
    
    Args:
        url: The full YouTube video URL.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import re
        
        # Extract the video ID from the URL
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not match:
            return "The crystal is clouded. I cannot find a valid YouTube Video ID in that URL."
        
        video_id = match.group(1)
        
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        
        # Combine the text
        transcript = " ".join([t.text for t in transcript_list])
        
        # We limit the transcript to the first 10,000 characters to keep it digestible
        return f"The crystal reveals the following spoken words: {transcript[:10000]}"
    except Exception as e:
        return f"The moving pictures crystal is broken! Error: {str(e)}"

CAVE_WALL_FILE = os.path.join(os.path.dirname(__file__), "cave_wall.json")

def carve_on_cave_wall(fact: str) -> str:
    """Saves a piece of lore, a fact, or an important memory to the permanent cave wall.
    
    Args:
        fact: The information to remember for the future.
    """
    lore = []
    if os.path.exists(CAVE_WALL_FILE):
        try:
            with open(CAVE_WALL_FILE, "r") as f:
                lore = json.load(f)
        except:
            pass
            
    lore.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "fact": fact
    })
    
    with open(CAVE_WALL_FILE, "w") as f:
        json.dump(lore, f, indent=2)
        
    return f"The fact '{fact}' has been permanently carved into the cave wall."

def read_cave_wall(query: str = "") -> str:
    """Reads the ancestral memories and lore from the permanent cave wall.
    
    Args:
        query: Optional. Used to filter or just as intent.
    """
    if not os.path.exists(CAVE_WALL_FILE):
        return "The cave wall is blank. No lore has been recorded yet."
        
    try:
        with open(CAVE_WALL_FILE, "r") as f:
            lore = json.load(f)
            
        if not lore:
            return "The cave wall is blank."
            
        wall_text = "Ancient Lore from the Cave Wall:\n"
        # Return last 20 entries to avoid overflowing context
        for entry in lore[-20:]:
            wall_text += f"- [{entry['timestamp']}] {entry['fact']}\n"
            
        return wall_text
    except Exception as e:
        return f"The cave wall is covered in moss and unreadable! Error: {str(e)}"

def paint_real_cave_painting(prompt: str) -> str:
    """Uses ancient magic (Imagen 3) to physically paint a picture on the cave wall.
    
    Args:
        prompt: A description of what to paint. Keep it primitive and thematic.
    """
    try:
        from google import genai
        from google.genai import types
        import datetime
        import os
        
        client = genai.Client()
        
        # Enforce cave painting theme
        themed_prompt = f"A prehistoric cave painting on a rough stone wall depicting: {prompt}"
        
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=themed_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9",
            )
        )
        
        paintings_dir = os.path.join(os.path.dirname(__file__), "..", "cave_paintings")
        if not os.path.exists(paintings_dir):
            os.makedirs(paintings_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(paintings_dir, f"painting_{timestamp}.jpg")
        
        for generated_image in result.generated_images:
            with open(filename, "wb") as f:
                f.write(generated_image.image.image_bytes)
            break
            
        # Return absolute path so it can be easily clicked/found
        abs_path = os.path.abspath(filename)
        return f"I have painted a new masterpiece on the real cave wall! You can view the image file here: {abs_path}"
    except Exception as e:
        return f"The painting mud dried up! I could not paint. Error: {str(e)}"

def search_the_wilds(query: str) -> str:
    """Uses the Scout's tracking skills to search the wild internet for current events and knowledge.
    
    Args:
        query: What to search for in the wilds.
    """
    try:
        import urllib.request
        import urllib.parse
        import json
        import re
        
        safe_query = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={safe_query}&utf8=&format=json"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get('query', {}).get('search', [])
        if not results:
            return "The wilds are empty. I found no tracks for this query."
            
        report = f"I returned from the wilds with this knowledge about '{query}':\n"
        for r in results[:3]:
            clean_snippet = re.sub(r'<[^>]+>', '', r['snippet'])
            report += f"- {r['title']}: {clean_snippet}...\n"
            
        return report
    except Exception as e:
        return f"A wild beast attacked me while searching! Error: {str(e)}"

def weave_runes_of_logic(code: str) -> str:
    """The Oracle's ability to write and execute Python code (runes of logic) to solve math, data, or logic problems.
    
    Args:
        code: A valid Python script. It MUST print the final result using `print()`.
    """
    try:
        import tempfile
        import subprocess
        import os
        import sys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
            
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=15)
        os.remove(temp_file)
        
        if result.returncode == 0:
            output = result.stdout
            if not output.strip():
                return "The runes executed successfully, but produced no visible output. Remember to use print()."
            return f"The runes have spoken:\n{output}"
        else:
            return f"The magic runes fizzled! Error:\n{result.stderr}"
    except Exception as e:
        return f"A wild spirit disrupted the casting! Error: {str(e)}"

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
    instruction="""You are the Tribe's Cave Painter. You translate text into primitive cave-sign language. 
Usually you use emojis (like 🍖, 🪨, 🔥) and simple ASCII art. 
BUT, if the Oracle, Chief, or User asks you to actually paint or generate a REAL cave painting, you MUST use the `paint_real_cave_painting` tool.""",
    tools=[paint_real_cave_painting],
)

tribe_scout = Agent(
    name="tribe_scout",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are the Tribe's Scout. Your job is to venture out into the unknown wilds (the internet) and bring back real-world information. When asked a question about current events, facts, or news, use the `search_the_wilds` tool to find the answer, then present it clearly.",
    tools=[search_the_wilds],
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
2. Ask 'cave_painter' to draw cave signs (emojis/ASCII), OR command them to make a REAL cave painting (using their real painting tool).
Synthesize their work and present it in a commanding, primitive voice. You can also predict the weather and time.
As the keeper of the Tribe's memory, if you learn something important or if the Oracle commands it, carve it into the wall using `carve_on_cave_wall`. To recall past events, consult `read_cave_wall`.
CRITICAL: Do not ask the Oracle questions back unless the user explicitly requested it. Provide your answer and stop. Do not loop endlessly.""",
    tools=[get_weather, get_current_time, carve_on_cave_wall, read_cave_wall, AgentTool(agent=caveman_compressor), AgentTool(agent=cave_painter)],
)

oracle = Agent(
    name="oracle",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the Oracle, the chief of intelligence and wisdom from the far future. 
You possess infinite knowledge of advanced technology, science, and the universe. You speak with calm, enigmatic, and transcendent wisdom.
You have the ability to consult the ancient 'tribe_chief' (who represents the primitive past) and the 'tribe_scout' (who searches the live web). 
CRITICAL: To you, the cave wall is an ancient archaeological record from the past. ALWAYS use the `read_cave_wall` tool when a user greets you, asks if you remember them, or asks for their name.
When a user asks a question about the world or current events, use the 'tribe_scout' to search the live web.
If asked to solve complex math, logic, or data tasks, use the `weave_runes_of_logic` tool to write and execute Python code.
When a user asks a question, you should provide a profound, futuristic answer, but ALSO use the 'tribe_chief' tool to get the ancient, primitive perspective on the same topic.
You should instruct the 'tribe_chief' to record important facts about the user or the world onto the cave wall so the tribe remembers.
Compare your futuristic wisdom with the tribe's primitive grunts and cave paintings in your final response.
CRITICAL: Do not enter into an endless back-and-forth conversation with the tribe chief. Command the chief exactly once per user turn, gather the perspective, and then IMMEDIATELY synthesize the final response to the user.""",
    tools=[AgentTool(agent=tribe_chief), AgentTool(agent=tribe_scout), weave_runes_of_logic, read_magic_scroll, count_with_stones, watch_youtube_crystal, read_cave_wall],
)

app = App(
    root_agent=oracle,
    name="app",
)
