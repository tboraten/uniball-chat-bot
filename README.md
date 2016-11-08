# uniball-chat-bot
2015 - Win32 API screen scraping BRChat bot

Bot iterates through brchat instances to find the bot's client.
Bot attaches to the bot brchat client.
Iterates through the channels to find league channel.
If league channel found, the database connection is tested, upon success, the bot can take commands.
Text is parsed from channel's richtext field.
Bot outputs text to chat client's input text field and sends an sends an enter key to the client.

Connects to a mysql database. Same database populates website.

Some commands reserved for refs.

Current Commands:
- !register
- !createsquad squad_name (No spaces in squad name)
- !invite player_name
- !kick player_name
- !join rsquad_id
- !leave
- !mysquad
- !squads
- !myinvites
- !lock
- !listopen
- !listclosed
- !freeagents
- !rules
- !schedul
