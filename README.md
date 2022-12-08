# 🤖 chatgpt-irc

chat with chatgpt on irc!

## configuration

- head to the [chatgpt website](https://chat.openai.com/chat) and sign in
- open the network tab in devtools (press F12)
- say "hi" to chatgpt
- collect your auth token from the *headers* tab
- create `config.json` using [the example configuration](#example-config)
  below or by copying `example-config.json`
- run the bot: `python chatgpt-irc.py`

![](https://rj1.su/img/chatgpt-irc-sshot1.png)

## example config

```
{
    "server": "internetrelaychat.net",
    "port": 6697,
    "ssl": true,
    "nickname": "chatgpt",
    "ident": "chatgpt",
    "realname": "chatgpt",
    "channels": ["#rj1"],
    "auth_token": "",
}
```
