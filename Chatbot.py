from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)
messages = []

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information of the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat history
try:
    with open(r"Data\\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\\ChatLog.json", "w") as f:
        dump([], f)


def RealtimeInformation():
    """Return current date/time info as text."""
    now = datetime.datetime.now()
    data = (
        f"Please use this realtime information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )
    return data


def AnswerModifier(Answer):
    """Remove empty lines from answer."""
    lines = Answer.split('\n')
    non_empty = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty)


def ChatBot(Query):
    """Send query to Groq chatbot and return the answer."""
    try:
        with open(r"Data\\ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query
        messages.append({"role": "user", "content": Query})

        # Create completion (non-streaming for fast response)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile"
,
            messages=SystemChatBot
            + [{"role": "system", "content": RealtimeInformation()}]
            + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False,
            stop=None
        )

        # Get final answer
        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")

        # Save assistant response to log
        messages.append({"role": "assistant", "content": Answer})
        with open(r"Data\\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print("Error:", e)
        with open(r"Data\\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "Something went wrong. Please try again."


if __name__ == "__main__":
    while True:
        query = input("Enter Your Question : ")
        if query.lower() in ["exit", "quit", "close"]:
            print("Goodbye!")
            break
        print(ChatBot(query))
