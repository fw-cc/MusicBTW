# MusicBTW
Music bot penned in Python can usually play media from Youtube based on a Spotify URL (if you ask nicely), is somewhat capable of dealing with playlists, albums, 
and individual tracks.

Uses
<a href=https://github.com/freyacodes/Lavalink target="_blank">Lavalink</a>
to handle voice shenanigans until such a time as they're understood by mere mortals.
Recommendation is therefore to run the bot with the supplied docker-compose
configuration, as this will save you the pain of local networking shenanigans.

## COnTRiBuTinG
🙌🙌 Wowsers, thanks 👍 for considering 🤔 contributing 📑 to the project 👷‍♂️.
😀 Since the bot 🤖 requires a fair 🎡 few dependencies 📚, it's recommended 🤓
that 👉 you test the bot 🤖 from within docker-compose 🐳.
Make sure 🤗 any additions ➕ to the codebase 👨‍💻 go in their own branches 🌳,
that way we can keep things clean 🧹.

See 👀 below 👇 for the feature hitlist 🎯!

### Feature Hitlist 🎯 (ticked ☑ when claimed, removed 👻 when done)
- [ ] Queue shuffle command
- [ ] Loop current track command
- [ ] Loop queue command
- [ ] Slash command implementation (moderately dank)
- [ ] Improving Spotify based track pulls with cross-correlation and that (highly dank)

If you like the sound of one of these to work on, we'll do a bit of that "ReqUirEmeNTs AnAlYSIs" so there's a clear target.

### Configuring your local environment
If you're on the Windows, use WSL + Docker Desktop, ensure also that you're
working in the WSL filesystem rather than /mnt/ (you can do this with `cd ~`)
and by setting your WSL Terminal profile default folder to `\\wsl$\Ubuntu\home\<username>`. 

Simply `cp example.env .env`, then add the relevant IDs, tokens, and secrets, and
`docker-compose up` to start the bot with the containers attached to CLI 
(`CTRL+C` to stop, `docker-compose up -d` for detached mode).
If it fails to launch and gives no proper errors, you've probably got the bot token
wrong (or forgotten to add it).

Credentials can be got at these URLs:

<a href=https://discord.com/developers/applications/ target="_blank">
Discord Developer Dashboard</a>
(you'll need to register an application and then a bot by entering the 
application settings).

<a href=https://developer.spotify.com/dashboard/ target="_blank">
Spotify Developer Dashboard</a>
(just set up an app in Development mode you won't ping the API enough to make
Spotify upset, probably).