import argparse
import json
import urllib.request
from pathlib import Path

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

LINKS_FILE = Path("links.json")


def load_links():
    if not LINKS_FILE.exists():
        return []
    with LINKS_FILE.open() as f:
        return json.load(f)


def save_links(links):
    with LINKS_FILE.open("w") as f:
        json.dump(links, f, indent=2)


def cmd_add(args):
    links = load_links()
    links.append({"url": args.url, "title": args.title})
    save_links(links)
    print(f"Added: {args.title}: {args.url}")


def cmd_list(args):
    links = load_links()
    if not links:
        print("No bookmarks saved yet.")
        return
    for link in links:
        print(f"{link['title']}: {link['url']}")


def cmd_share(args):
    links = load_links()
    if not links:
        text = "No bookmarks to share."
    else:
        lines = [f"• <{link['url']}|{link['title']}>" for link in links]
        text = "My bookmarks:\n" + "\n".join(lines)

    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Shared to Slack (status {resp.status}).")


def main():
    parser = argparse.ArgumentParser(description="Linkstash bookmark manager")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    add_parser = subparsers.add_parser("add", help="Add a bookmark")
    add_parser.add_argument("url", help="URL to bookmark")
    add_parser.add_argument("title", help="Title for the bookmark")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List all bookmarks")
    list_parser.set_defaults(func=cmd_list)

    share_parser = subparsers.add_parser("share", help="Share bookmarks to Slack")
    share_parser.set_defaults(func=cmd_share)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
