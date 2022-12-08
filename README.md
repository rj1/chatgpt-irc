# 🤖 chatgpt-irc

chat with chatgpt on irc!

## configuration

- head to the [chatgpt website](https://chat.openai.com/chat) and sign in
- open the network tab in devtools (press F12)
- say "hi" to chatgpt
- collect your auth token from the *headers* tab
- collect your conversation id & parent message id from the *payload* tab 
- create `config.json` using [the example configuration](#example-config.json)
  below or by copying `example-config.json`
- run the bot: `python chatgpt-irc.py`

![](https://rj1.su/img/chatgpt-irc-sshot1.png)
![](https://rj1.su/img/chatgpt-irc-sshot2.png)

## example config.json

```
{
    "server": "internetrelaychat.net",
    "port": 6697,
    "ssl": true,
    "nickname": "chatgpt",
    "ident": "chatgpt",
    "realname": "chatgpt",
    "channels": ["#rj1"],
    "access_token": "",
    "conversation_id": "",
    "parent_message_id": ""
}
```
