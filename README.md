# telecrawler
Python/Telethon tool that scans a Telegram channel's message history for mentions of other channels (@name / t.me/name), deduplicates them, and saves the list to a text file — with optional live-monitoring mode.
# Telegram Channel Name Crawler

A Python script using [Telethon](https://docs.telethon.dev/) that scrapes a
Telegram channel's message history for mentions of *other* channels
(`@channelname` and `https://t.me/channelname` links), builds a deduplicated
list, and saves it to a text file. Useful for channel discovery, directory
building, or mapping cross-promotion networks between public channels.

## Features

- 🔎 **Regex-based extraction** of `@name` and `t.me/name` mentions from message text.
- 🧹 **Blacklist filtering** to exclude non-channel links (`joinchat`, `addstickers`, `login`, etc.).
- 💾 **Persistent deduplication** — loads previously saved names so repeated runs never produce duplicates.
- ⏱️ **Two modes:**
  - `--once` — scrape full available message history, then exit.
  - `--continuous` — scrape history, then stay connected and capture new mentions in real time.
- 📄 **Simple output** — one sorted, deduplicated channel name per line in a plain `.txt` file.

## Requirements

- Python 3.11+
- [Telethon](https://pypi.org/project/Telethon/)
- A Telegram API ID/hash from [my.telegram.org](https://my.telegram.org)

## Setup

\```bash
pip install telethon
\```

Edit the config block in `crawler.py` (or better, load from environment variables):

\```python
API_ID    = 123456          # your API ID (integer)
API_HASH  = "your_api_hash" # your API hash (string)
PHONE     = "+1234567890"   # your phone number
\```

⚠️ **Do not commit real credentials.** Use environment variables or a `.env`
file excluded via `.gitignore`.

## Usage

\```bash
python crawler.py @sourcechannel --once
python crawler.py @sourcechannel --continuous
\```

On first run, Telethon prompts for a login code and creates a local `session`
file for subsequent runs.

## Output

Results are appended to `channels.txt` — one `@name` per line, sorted and
deduplicated on every write.

## Known Limitations / Roadmap

- Currently extracts *any* `@name` / `t.me/name` mention — it does not verify
  the entity is actually a channel (as opposed to a user or bot). A planned
  improvement is to resolve each match via `client.get_entity()` and filter
  to `Channel` instances only.
- No rate-limiting/backoff beyond Telethon's defaults; large channels with
  long histories may take a while to scrape fully.

## License

MIT
