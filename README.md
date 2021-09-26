# CocoBot
## Overview
A lightweight music and utility bot written in Python.

## Usage
Prefixes: `!`, `-`

### Music Commands
| Command | Aliases | Argument | Function |
| --- | --- | --- | --- |
| `clear` | `c` | - | Clears queue.
| `join` `[arg]` | `j` | Voice channel name | Joins your voice channel. |
| `lyrics` | `l` | - | Displays subtitles for Youtube videos. |
| `play` `[arg]` | `p` | Youtube search query, video/audio link | Adds a track from url or Youtube search to queue. |
| `queue` | `q` | - | Displays tracks in queue. |
| `skip` | - | - | Skips to next track in queue. |
| `stop` | - | - | Leaves voice channel and clears the queue. |
| `volume` `[arg]` | `v` | Volume percentage | Changes music volume. |

### Utility Commands
| Command | Aliases | Argument | Function |
| --- | --- | --- | --- |
| `help` | - | - | Display bot commands. |
| `ping` | - | - | Check status of bot. |
| `say` `[arg]` | - | Message | Have the bot secretly say a message. |



## Execution
1. Create new bot and invite to server.
2. Create an environment variable file in source and add DISCORD_TOKEN.
3. Run [source/main.py](https://github.com/DuaLee/cocobot/blob/master/source/main.py) or use [run.bat](https://github.com/DuaLee/cocobot/blob/master/run.bat) to easily host bot on a Windows platform.
