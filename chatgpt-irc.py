import asyncio
from collections import namedtuple
import functools
import json
import requests
import uuid

options = {
    # irc
    "server": "internetrelaychat.net",
    "port": 6697,
    "ssl": True,
    "nickname": "chatgpt",
    "ident": "chatgpt",
    "realname": "chatgpt",
    "channel": "#rj1",

    # openai
    "access_token": "",
    "conversation_id": "",
    "parent_message_id": "",
}


class ChatGPT:
    def __init__(self):
        self.access_token = options["access_token"]
        self.conversation_id = options["conversation_id"]
        self.parent_message_id = options["parent_message_id"]
        self.message_id = self.parent_message_id

    def reset(self):
        self.message_id = self.parent_message_id

    def prompt(self, message):
        self.parent_message_id = self.message_id
        self.message_id = str(uuid.uuid4())

        url = "https://chat.openai.com/backend-api/conversation"

        payload = json.dumps(
            {
                "action": "next",
                "messages": [
                    {
                        "id": self.message_id,
                        "role": "user",
                        "content": {"content_type": "text", "parts": [message]},
                    }
                ],
                "conversation_id": self.conversation_id,
                "parent_message_id": self.parent_message_id,
                "model": "text-davinci-002-render",
            }
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        query = requests.request("POST", url, headers=headers, data=payload)
        response = query.text

        try:
            last = response.split(("data:"))[-2]
            items = json.loads(last)["message"]["content"]["parts"][0]
            lines = items.split("\n")
            return lines
        except IndexError:
            # raise IndexError()
            return ["We couldn't get a response for you, please try again"]


# irc
Message = namedtuple("Message", "prefix command params")
Prefix = namedtuple("Prefix", "nick ident host")


def parse_line(line):
    prefix = None

    if line.startswith(":"):
        prefix, line = line.split(None, 1)
        name = prefix[1:]
        ident = None
        host = None
        if "!" in name:
            name, ident = name.split("!", 1)
            if "@" in ident:
                ident, host = ident.split("@", 1)
        elif "@" in name:
            name, host = name.split("@", 1)
        prefix = Prefix(name, ident, host)

    command, *line = line.split(None, 1)
    command = command.upper()

    params = []
    if line:
        line = line[0]
        while line:
            if line.startswith(":"):
                params.append(line[1:])
                line = ""
            else:
                param, *line = line.split(None, 1)
                params.append(param)
                if line:
                    line = line[0]

    return Message(prefix, command, params)


def send_line_to_writer(writer: asyncio.StreamWriter, line):
    print("->", line)
    writer.write(line.encode("utf-8") + b"\r\n")


def send_cmd_to_writer(writer: asyncio.StreamWriter, cmd, *params):
    params = list(params)
    if params:
        if " " in params[-1]:
            params[-1] = ":" + params[-1]
    params = [cmd] + params
    send_line_to_writer(writer, " ".join(params))


def send_msg(writer: asyncio.StreamWriter, target, msg):
    send_cmd_to_writer(writer, "PRIVMSG", target, msg)


async def main_loop(**options):
    print(options.get("host"))
    reader, writer = await asyncio.open_connection(
        host=options.get("server"), port=options.get("port"), ssl=options.get("ssl")
    )

    sendline = functools.partial(send_line_to_writer, writer)
    sendcmd = functools.partial(send_cmd_to_writer, writer)

    sendline("NICK {nickname}".format(**options))
    sendline("USER {ident} * * :{realname}".format(**options))

    chatgpt = ChatGPT()

    while not reader.at_eof():
        line = await reader.readline()
        try:
            line = line.decode("utf-8")
        except UnicodeDecodeError:
            line = line.decode("latin1")

        line = line.strip()
        if line:
            message = parse_line(line)
            if message.command.isdigit() and int(message.command) >= 400:
                # error?
                print(message)

            if message.command == "PING":
                sendcmd("PONG", *message.params)
            elif message.command == "001":
                sendcmd("JOIN", options["channel"])

            elif message.command == "PRIVMSG":
                target = str(message.params[0])  # channel or nick
                text = str(message.params[1])  # msg text
                host = str(message.prefix.host)  # user's hostname
                source = str(message.prefix.nick)  # nick
                print(f"[{target}] <{source}> {text}")

                parts = text.split()

                if len(parts) == 0:
                    continue

                if parts[0] == "!reset":
                    sendcmd(
                        "PRIVMSG", options["channel"], f"{source}: Let's start fresh"
                    )
                    chatgpt.reset()
                    continue

                if len(parts) <= 1:
                    continue

                if parts[0] == f"{options['nickname']}:":
                    sendcmd(
                        "PRIVMSG",
                        options["channel"],
                        f"{source}: hold on, I'm thinking..",
                    )
                    prompt = parts[1:]
                    prompt = " ".join(prompt)

                    lines = chatgpt.prompt(prompt)
                    messages = []

                    for line in lines:
                        if len(line) > 350:
                            messages.append(line[:350])
                            messages.append(line[350:])
                        else:
                            messages.append(line)

                    for i, message in enumerate(messages):
                        if i == 0:
                            message = f"{source}: {message}"
                        sendcmd("PRIVMSG", options["channel"], f"{message}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main_loop(**options))
