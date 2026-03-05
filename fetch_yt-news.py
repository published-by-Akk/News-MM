import requests
import xml.etree.ElementTree as ET
import json
import sys
import os

# Set console encoding (for Windows)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

CHANNELS = [
    "UCKud809KUMIyNhqwuy5JeFw",  # Myanmar Now News
    "UCd9maKo3B6jX8pCPzLa2hvA",  # BBC News မြန်မာ
    "UCuaRmKJLYaVMDHrnjhWUcHw",  # DVB TV News
    "UCktBWlYbAf4en-pWyyTqRwg",  # Khit Thit Media
    "UCk9f0cLiMmtchQySOogzoig",  # MizzimaTV
    "UCfi9cXgZK2YXPAqyyf4mAPg",  # Mratt Channel
]

CHANNEL_NAMES = {
    "UCKud809KUMIyNhqwuy5JeFw": "Myanmar Now News",
    "UCd9maKo3B6jX8pCPzLa2hvA": "BBC News မြန်မာ",
    "UCuaRmKJLYaVMDHrnjhWUcHw": "DVB TV News",
    "UCktBWlYbAf4en-pWyyTqRwg": "Khit Thit Media",
    "UCk9f0cLiMmtchQySOogzoig": "MizzimaTV",
    "UCfi9cXgZK2YXPAqyyf4mAPg": "Mratt Channel",
}

def fetch_videos_from_channel(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    print(f"  Requesting {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"  Network error: {e}")
        return []

    # Parse XML with proper namespace handling
    try:
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }

        root = ET.fromstring(response.text)
        entries = root.findall('atom:entry', namespaces)
        print(f"  Found {len(entries)} entries")

        videos = []
        for entry in entries:
            try:
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text if title_elem is not None else "No title"

                video_id_elem = entry.find('yt:videoId', namespaces)
                video_id = video_id_elem.text if video_id_elem is not None else None

                published_elem = entry.find('atom:published', namespaces)
                published = published_elem.text if published_elem is not None else ""

                if not video_id or not published:
                    print("  Skipping entry: missing videoId or published date")
                    continue

                date_part = published[:10]
                time_part = published[11:19]

                youtube_link = f"https://www.youtube.com/watch?v={video_id}"
                channel_name = CHANNEL_NAMES.get(channel_id, channel_id)

                video = {
                    "title": title,
                    "video_id": video_id,
                    "published": published,
                    "channel": channel_name,
                    "channel_id": channel_id,
                    "time": time_part,
                    "date": date_part,
                    "youtube_link": youtube_link
                }
                videos.append(video)

            except Exception as e:
                print(f"  Error parsing entry: {e}")
                continue

        return videos

    except ET.ParseError as e:
        print(f"  XML parse error: {e}")
        return []

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        ascii_text = text.encode('ascii', 'replace').decode('ascii')
        print(ascii_text)

def load_existing_videos(filename):
    """Load existing videos from JSON file. Return list and a set of existing video_ids."""
    if not os.path.exists(filename):
        return [], set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"Warning: {filename} does not contain a list. Starting fresh.")
            return [], set()
        existing_ids = {v["video_id"] for v in data if "video_id" in v}
        return data, existing_ids
    except Exception as e:
        print(f"Error reading {filename}: {e}. Starting fresh.")
        return [], set()

def merge_and_save(new_videos, display_file="videos.json", archive_file="all_history.json"):
    """
    Merge new videos into the archive, then save a trimmed version for the website.
    - archive_file: contains all videos ever fetched (the vault)
    - display_file: contains only the latest 100 videos (fast loading)
    """
    # Load the full history archive
    all_history_list, existing_ids = load_existing_videos(archive_file)

    added = 0
    for v in new_videos:
        if v["video_id"] not in existing_ids:
            all_history_list.append(v)
            existing_ids.add(v["video_id"])
            added += 1

    # Sort by published date descending (newest first)
    all_history_list.sort(key=lambda v: v["published"], reverse=True)

    # Save the full archive
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(all_history_list, f, indent=2, ensure_ascii=False)

    # Create display version (latest 200 videos)
    display_list = all_history_list[:200]
    with open(display_file, "w", encoding="utf-8") as f:
        json.dump(display_list, f, indent=2, ensure_ascii=False)

    print(f"\nAdded {added} new videos.")
    print(f"Archive total: {len(all_history_list)}")
    print(f"Display file now contains {len(display_list)} videos.")

def main():
    all_new_videos = []
    for ch in CHANNELS:
        name = CHANNEL_NAMES.get(ch, ch)
        safe_print(f"\nFetching channel {ch} ({name})...")

        channel_videos = fetch_videos_from_channel(ch)
        all_new_videos.extend(channel_videos)
        safe_print(f"  -> Got {len(channel_videos)} videos from this channel")

    # Merge with archive and save both files
    merge_and_save(all_new_videos, "videos.json", "all_history.json")

    print("\n✅ Update complete. Both files are ready.")

if __name__ == "__main__":
    main()
