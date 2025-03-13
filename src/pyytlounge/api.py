api_base = "https://www.youtube.com/api/lounge"


def get_thumbnail_url(video_id: str, thumbnail_idx=0) -> str:
    """Returns thumbnail for given video. Use thumbnail idx to get different thumbnails."""
    return f"https://img.youtube.com/vi/{video_id}/{thumbnail_idx}.jpg"
