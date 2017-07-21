About
===
Once hosted and started, you can give this bot any website via Chat:
```
/set http://www.exapmle.eg
```
It will fetch the Site every 5 Minutes and CHeck for changes, if even
the smallest differenze is found, you will get an notification that
something changed (Currently not what changes).

You can disable the bot action via
```
/unset
```

ToDo
===
Create a diff of the website to Inform the user of the changes.


Installation
===
 - Clone this repo
 - use the [BotFather](https://telegram.me/BotFather) to create a access Token for your Bot
 - copy `config_dummy.py` to `config_private.py`
 - Edit `config_private.py` and insert your token there
Requirements
===

```
python-telegram-bot
urllib
```