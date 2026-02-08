import os
import sys
import asyncio

# ------------------- Auto-install -------------------
def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] '{package}' not found. Installing...")
        os.system(f'"{sys.executable}" -m pip install {package}')

install_if_missing("telethon")
install_if_missing("colorama")
# -----------------------------------------------------

from telethon import TelegramClient
from telethon.tl.types import Channel
from colorama import init, Fore

init(autoreset=True)

# ---------------- CONFIG -----------------
api_id = 24246861
api_hash = '051c244c7893e9f9072be2453b4b0120'
download_path = os.path.join(os.getcwd(), 'downloads')
max_concurrent = 8
chunk_size = 200
delay_between_requests = 0.2
# ---------------------------------------

os.makedirs(download_path, exist_ok=True)

# ----------------- Helpers -----------------
async def download_message(message, path):
    media = getattr(message, "media", None)
    if not media:
        return
    return await message.download_media(path)

# ----------------- Main download -----------------
async def download_media_progress(group, download_videos=True, download_images=True):
    group_name = group.title.replace('/', '_')
    group_folder = os.path.join(download_path, group_name)
    if download_videos:
        os.makedirs(os.path.join(group_folder, 'videos'), exist_ok=True)
    if download_images:
        os.makedirs(os.path.join(group_folder, 'images'), exist_ok=True)

    tasks = []
    counter = 0
    total_found = 0

    async for message in client.iter_messages(group):
        counter += 1
        if download_videos and message.video:
            total_found += 1
            path = os.path.join(group_folder, 'videos', message.date.strftime('%Y-%m-%d'))
            os.makedirs(path, exist_ok=True)
            tasks.append(download_message(message, path))
        elif download_images and message.photo:
            total_found += 1
            path = os.path.join(group_folder, 'images', message.date.strftime('%Y-%m-%d'))
            os.makedirs(path, exist_ok=True)
            tasks.append(download_message(message, path))

        if counter % chunk_size == 0:
            print(Fore.CYAN + f"[SCANNING] Checked {counter} messages in {group_name} | Found {total_found} media...")
            await asyncio.sleep(delay_between_requests)

        if len(tasks) >= max_concurrent:
            await asyncio.gather(*tasks)
            tasks = []

    if tasks:
        await asyncio.gather(*tasks)

# ----------------- Main -----------------
async def main():
    await client.start()
    print(Fore.GREEN + "[INFO] Fetching all groups from your account...")
    dialogs = await client.get_dialogs()
    groups = [d.entity for d in dialogs if isinstance(d.entity, Channel) and (d.entity.megagroup or d.entity.broadcast)]
    if not groups:
        print(Fore.RED + "[INFO] No groups found.")
        return

    print("\nAvailable groups:")
    for i, g in enumerate(groups, start=1):
        print(f"{i}: {g.title}")

    selection = input("\nSelect groups to download (comma-separated numbers) or 0 for all groups: ").strip()
    download_groups = groups if selection == '0' else [groups[int(x)-1] for x in selection.split(',')]

    print("\nDownload options:")
    print("1: Videos only")
    print("2: Images only")
    print("3: Both videos and images")
    choice = input("Enter option (1/2/3): ").strip()
    download_videos = choice in ['1','3']
    download_images = choice in ['2','3']

    for group in download_groups:
        print(Fore.BLUE + f"[INFO] Starting download for group: {group.title}")
        await download_media_progress(group, download_videos, download_images)
        print(Fore.GREEN + f"[INFO] Completed group: {group.title}")

    print(Fore.GREEN + "[INFO] All downloads complete!")

# ----------------- Run -----------------
client = TelegramClient('session_all_groups', api_id, api_hash)
asyncio.run(main())
