# filename: crawler.py
# Purpose: Crawl a Telegram channel for unique @username addresses and save to a txt file

import re
import sys
import asyncio
from telethon import TelegramClient, events

# ── Config ────────────────────────────────────────────────────────────────────
API_ID    =           # ← replace with your API ID (integer)
API_HASH  = ""  # ← replace with your API hash (string)
PHONE     = ""   # ← replace with your phone number
OUTPUT    = "channels.txt"
# ─────────────────────────────────────────────────────────────────────────────

PATTERN = re.compile(
    r"(?:(?:https?://)?t\.me/|@)([a-zA-Z][a-zA-Z0-9_]{3,30}[a-zA-Z0-9])",
    re.IGNORECASE,
)

BLACKLIST = {"joinchat", "share", "addstickers", "login", "auth", "privacy", "tos"}

client = TelegramClient("session", API_ID, API_HASH)


def extract(text: str) -> set[str]:
    """Pull all @usernames out of a message."""
    found = set()
    for match in PATTERN.finditer(text):
        name = match.group(1).lower()
        if name not in BLACKLIST:
            found.add("@" + name)
    return found


def load_existing() -> set[str]:
    """Load already-saved addresses so we never duplicate across runs."""
    try:
        with open(OUTPUT, "r") as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def save_new(addresses: set[str], seen: set[str]) -> int:
    """Append only addresses we haven't seen before. Returns count added."""
    new = [a for a in addresses if a.lower() not in seen]
    if new:
        with open(OUTPUT, "a") as f:
            for addr in sorted(new):
                f.write(addr + "\n")
        seen.update(a.lower() for a in new)
        print(f"  ✚ Saved {len(new)} new: {new}")
    return len(new)


# ── Mode 1: scrape once ───────────────────────────────────────────────────────

async def scrape_once(channel: str):
    seen = load_existing()
    total_new = 0
    count = 0

    print(f"Scraping {channel} …")
    async for message in client.iter_messages(channel, limit=None):
        if message.text:
            found = extract(message.text)
            if found:
                total_new += save_new(found, seen)
        count += 1
        if count % 500 == 0:
            print(f"  … {count} messages scanned")

    print(f"\nDone. Scanned {count} messages. Added {total_new} new addresses.")
    print(f"Total unique addresses in {OUTPUT}: {len(seen)}")


# ── Mode 2: scrape history then keep listening ────────────────────────────────

async def scrape_continuous(channel: str):
    seen = load_existing()

    # First scrape the full history
    await scrape_once(channel)

    # Then listen for new messages live
    entity = await client.get_entity(channel)
    print(f"\nNow listening for new messages in {channel} … (Ctrl-C to stop)\n")

    @client.on(events.NewMessage(chats=entity))
    async def handler(event):
        if event.message.text:
            found = extract(event.message.text)
            if found:
                save_new(found, seen)

    await client.run_until_disconnected()


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python crawler.py @channel --once")
        print("  python crawler.py @channel --continuous")
        sys.exit(1)

    channel = sys.argv[1]
    mode    = sys.argv[2]

    await client.start(phone=PHONE)

    if mode == "--once":
        await scrape_once(channel)
    elif mode == "--continuous":
        await scrape_continuous(channel)
    else:
        print(f"Unknown mode: {mode}. Use --once or --continuous")
        sys.exit(1)

    await client.disconnect()


asyncio.run(main())
