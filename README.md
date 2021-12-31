# MusicBTW

Music bot penned in Python can usually play media from Youtube based on a Spotify URL (if you ask nicely), is somewhat capable of dealing with playlists, albums,
and individual tracks.

Uses
[Lavalink](https://github.com/freyacodes/Lavalink)
to handle voice shenanigans until such a time as they're understood by mere mortals.
Recommendation is therefore to run the bot with the supplied docker-compose
configuration, as this will save you the pain of local networking not working.

## COnTRiBuTinG

🙌🙌 Wowsers, thanks 👍 for considering 🤔 contributing 📑 to the project 👷‍♂️.
😀 Since the bot 🤖 requires a fair 🎡 few dependencies 📚, it's recommended 🤓
that 👉 you test the bot 🤖 from within docker-compose 🐳.
Make sure 🤗 any additions ➕ to the codebase 👨‍💻 go in their own branches 🌳,
that way we can keep things clean 🧹.
A good 👍 format 📄 for branch 🌲 names would 🪓 be 🐝 `<base-branch>-<feature-name>`
where `<base-branch>` is, `master`, `1.0-dev`, or something of the sort 🧙‍♂️ and
`<feature-name>` may be `shuffle-queue` such that your branch 🎄 would end up being
called 💬 `1.0-dev-shuffle-queue`.

See 👀 below 👇 for the feature hitlist 🎯!

### Feature Hitlist 🎯 (ticked ☑ when claimed, removed 👻 when done)

Feature Hitlist 🎯 has moved to a [new home](https://github.com/Pytato/MusicBTW/projects/2#column-17243427)
in the Projects tab.

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

[Discord Developer Dashboard](https://discord.com/developers/applications/)
(you'll need to register an application and then a bot by entering the
application settings).

[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
(just set up an app in Development mode you won't ping the API enough to make
Spotify upset, probably).
