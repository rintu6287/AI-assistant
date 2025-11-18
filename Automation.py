from webbrowser import open as webopen
from pywhatkit.misc import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from typing import cast

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message for AI
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {env_vars.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."
}]

messages = []

# User agent and constants
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# 🌐 List of popular links
most_popular_links = [
    "https://www.google.com", "https://www.youtube.com", "https://www.instagram.com",
    "https://www.twitter.com", "https://www.facebook.com", "https://www.wikipedia.org",
    "https://www.amazon.com", "https://www.spotify.com", "https://www.github.com",
    "https://www.linkedin.com", "https://www.netflix.com", "https://www.stackoverflow.com",
    "https://www.canva.com", "https://www.coursera.org", "https://www.gmail.com"
]

# ---------- FUNCTION DEFINITIONS ---------- #

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    topic_str = Topic.strip()
    ContentByAI = ContentWriterAI(topic_str)

    # Ensure Data folder exists
    os.makedirs("Data", exist_ok=True)
    filename = rf"Data\{topic_str.lower().replace(' ', '_')}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filename)
    return True

def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app):
    app_lower = app.lower()
    for url in most_popular_links:
        if app_lower in url.lower():
            print(f"Opening {url} in your browser...")
            webopen(url)
            return True
    print(f"No matching link found for '{app}'.")
    return False

# ---------- SMART COMMAND HANDLER ---------- #

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        cmd = command.lower().strip()

        # Smart intent detection
        if cmd.startswith(("open ", "launch ")):
            funcs.append(asyncio.to_thread(OpenApp, cmd.split(" ", 1)[1]))
        elif cmd.startswith(("play ", "listen ")):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd.split(" ", 1)[1]))
        elif cmd.startswith(("google search ", "search on google ")):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd.split(" ", 2)[-1]))
        elif cmd.startswith(("youtube search ", "search on youtube ")):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd.split(" ", 2)[-1]))
        elif cmd.startswith(("write ", "make ", "create ", "generate ", "content ")):
            funcs.append(asyncio.to_thread(Content, cmd))
        else:
            print(f"[red]⚠️ No matching function for '{command}'.[/red]")

    # Run all asynchronously
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True

# ---------- RUN MAIN ---------- #

if __name__ == "__main__":
    commands = [

      

        
        
    ]
    asyncio.run(Automation(commands))
