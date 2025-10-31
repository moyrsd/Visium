import yt_dlp
import os


def download_audio_playlist(playlist_url, number_of_tracks):
    extract_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(extract_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    entries = info.get("entries", [])
    total = len(entries)
    print(f"Found {total} videos in playlist: {info.get('title', 'Unknown Playlist')}")

    audio_paths = []
    for idx, entry in enumerate(entries, start=1):
        if idx == number_of_tracks + 1:
            break
        video_url = entry["url"]
        outtmpl = f"{idx}.%(ext)s"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": False,
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        print(f"\n[{idx}/{total}] Downloading: {entry.get('title', 'Unknown Title')}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        path = os.path.relpath(f"{idx}.mp3")
        if os.path.exists(path):
            audio_paths.append(path)
    return audio_paths


if __name__ == "__main__":
    playlist_link = (
        "https://www.youtube.com/playlist?list=PLcdkT0k7NzKNxMHHnorkmJ5MjGXHO5jdj"
    )
    audio_paths = download_audio_playlist(playlist_link, 10)
    print(audio_paths)
