import aiohttp

api_base = "https://www.youtube.com/api/lounge"


def get_thumbnail_url(video_id: str, thumbnail_idx=0) -> str:
    """Returns thumbnail for given video. Use thumbnail idx to get different thumbnails."""
    return f"https://img.youtube.com/vi/{video_id}/{thumbnail_idx}.jpg"


async def get_available_captions(api_key: str, video_id: str):
    """Uses the traditional YouTube API to enumerate available subtitle tracks."""
    yt_base_url = "https://www.googleapis.com/youtube/v3/captions"
    params = {"part": "snippet", "videoId": video_id, "key": api_key}

    async with aiohttp.ClientSession() as session:
        async with session.get(yt_base_url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Request failed with status {response.status}")

            data = await response.json()

            languages = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                language = snippet.get("language")
                if language and language not in languages:
                    languages.append(language)

            return languages
