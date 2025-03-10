import browse
import json
import memory as mem
import datetime
import agent_manager as agents
import speak
from config import Config
import ai_functions as ai
from file_operations import read_file, write_to_file, append_to_file, delete_file
from execute_code import execute_python_file
import discord
from discord.ext import commands as discommands


# Bot defintion


cfg = Config()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Create the bot instance
bot = discommands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="ask")
async def ask_question_on_discord(ctx, *, question):
    # Save the context of the original message for replying later
    original_message = ctx.message

    await ctx.send(f"Question: {question}\nWaiting for a reply...")

    def check_reply(reply):
        return reply.reference and reply.reference.message_id == original_message.id

    try:
        reply = await bot.wait_for("message", check=check_reply, timeout=60)
    except asyncio.TimeoutError:
        await ctx.send("No reply was received in time.")
    else:
        await ctx.send(f"Reply received: {reply.content}")














def get_command(response):
    try:
        response_json = json.loads(response)
        command = response_json["command"]
        command_name = command["name"]
        arguments = command["args"]

        if not arguments:
            arguments = {}

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)


def execute_command(command_name, arguments):
    try:
        if command_name == "google":
            return google_search(arguments["input"])
        elif command_name == "check_notifications":
            return check_notifications(arguments["website"])
        elif command_name == "memory_add":
            return commit_memory(arguments["string"])
        elif command_name == "memory_del":
            return delete_memory(arguments["key"])
        elif command_name == "memory_ovr":
            return overwrite_memory(arguments["key"], arguments["string"])
        elif command_name == "start_agent":
            return start_agent(
                arguments["name"],
                arguments["task"],
                arguments["prompt"])
        elif command_name == "message_agent":
            return message_agent(arguments["key"], arguments["message"])
        elif command_name == "list_agents":
            return list_agents()
        elif command_name == "delete_agent":
            return delete_agent(arguments["key"])
        elif command_name == "navigate_website":
            return navigate_website(arguments["action"], arguments["username"])
        elif command_name == "register_account":
            return register_account(
                arguments["username"],
                arguments["website"])
        elif command_name == "get_text_summary":
            return get_text_summary(arguments["url"])
        elif command_name == "get_hyperlinks":
            return get_hyperlinks(arguments["url"])
        elif command_name == "read_file":
            return read_file(arguments["file"])
        elif command_name == "write_to_file":
            return write_to_file(arguments["file"], arguments["text"])
        elif command_name == "append_to_file":
            return append_to_file(arguments["file"], arguments["text"])
        elif command_name == "delete_file":
            return delete_file(arguments["file"])
        elif command_name == "browse_website":
            return browse_website(arguments["url"])
        # TODO: Change these to take in a file rather than pasted code, if
        # non-file is given, return instructions "Input should be a python
        # filepath, write your code to file and try again"
        elif command_name == "evaluate_code":
            return ai.evaluate_code(arguments["code"])
        elif command_name == "improve_code":
            return ai.improve_code(arguments["suggestions"], arguments["code"])
        elif command_name == "write_tests":
            return ai.write_tests(arguments["code"], arguments.get("focus"))
        elif command_name == "execute_python_file":  # Add this command
            return execute_python_file(arguments["file"])
        elif command_name == "ask_question_on_discord":
            return ask_question_on_discord(arguments["question"])
        elif command_name == "task_complete":
            shutdown()
        else:
            return f"Unknown command {command_name}"
    # All errors, return "Error: + error message"
    except Exception as e:
        return "Error: " + str(e)


def get_datetime():
    return "Current date and time: " + \
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def google_search(query, num_results=8):
    search_results = []
    for j in browse.search(query, num_results=num_results):
        search_results.append(j)

    return json.dumps(search_results, ensure_ascii=False, indent=4)


def browse_website(url):
    summary = get_text_summary(url)
    links = get_hyperlinks(url)

    # Limit links to 5
    if len(links) > 5:
        links = links[:5]

    result = f"""Website Content Summary: {summary}\n\nLinks: {links}"""

    return result


def get_text_summary(url):
    text = browse.scrape_text(url)
    summary = browse.summarize_text(text)
    return """ "Result" : """ + summary


def get_hyperlinks(url):
    link_list = browse.scrape_links(url)
    return link_list


def commit_memory(string):
    _text = f"""Committing memory with string "{string}" """
    mem.permanent_memory.append(string)
    return _text


def delete_memory(key):
    if key >= 0 and key < len(mem.permanent_memory):
        _text = "Deleting memory with key " + str(key)
        del mem.permanent_memory[key]
        print(_text)
        return _text
    else:
        print("Invalid key, cannot delete memory.")
        return None


def overwrite_memory(key, string):
    if key >= 0 and key < len(mem.permanent_memory):
        _text = "Overwriting memory with key " + \
            str(key) + " and string " + string
        mem.permanent_memory[key] = string
        print(_text)
        return _text
    else:
        print("Invalid key, cannot overwrite memory.")
        return None


def shutdown():
    print("Shutting down...")
    quit()


def start_agent(name, task, prompt, model="gpt-3.5-turbo"):
    global cfg

    # Remove underscores from name
    voice_name = name.replace("_", " ")

    first_message = f"""You are {name}.  Respond with: "Acknowledged"."""
    agent_intro = f"{voice_name} here, Reporting for duty!"

    # Create agent
    if cfg.speak_mode:
        speak.say_text(agent_intro, 1)
    key, ack = agents.create_agent(task, first_message, model)

    if cfg.speak_mode:
        speak.say_text(f"Hello {voice_name}. Your task is as follows. {task}.")

    # Assign task (prompt), get response
    agent_response = message_agent(key, prompt)

    return f"Agent {name} created with key {key}. First response: {agent_response}"


def message_agent(key, message):
    global cfg
    agent_response = agents.message_agent(key, message)

    # Speak response
    if cfg.speak_mode:
        speak.say_text(agent_response, 1)

    return f"Agent {key} responded: {agent_response}"


def list_agents():
    return agents.list_agents()


def delete_agent(key):
    result = agents.delete_agent(key)
    if not result:
        return f"Agent {key} does not exist."
    return f"Agent {key} deleted."


def navigate_website(action, username):
    _text = "Navigating website with action " + action + " and username " + username
    print(_text)
    return "Command not implemented yet."


def register_account(username, website):
    _text = "Registering account with username " + \
        username + " and website " + website
    print(_text)
    return "Command not implemented yet."


def check_notifications(website):
    _text = "Checking notifications from " + website
    print(_text)
    return "Command not implemented yet."

# Run the bot
if __name__ == "__main__":
    bot.run(cfg.get("discord", "token"))
