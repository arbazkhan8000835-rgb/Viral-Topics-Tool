import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# YouTube API Key
API_KEY = "AIzaSyDKBxqXFE8ktMBkjaYUORER3T3wL0ODPaU"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

st.title("YouTube Viral Topics Tool (US + Faceless Filtered)")

days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# 🔥 UPDATED KEYWORDS (FACLESS + ANIMATION FOCUSED)
keywords = [
    "finance explained animation",
    "investing explained animation",
    "passive income animation",
    "dividend investing animation",
    "etf investing animation",
    "stock market explained animation",
    "money explained whiteboard",
    "finance whiteboard animation",
    "business explainer animation",
    "compound interest animation",
    "financial freedom animation",
    "lazy investing animation",
    "simple investing animation",
    "VOO investing animation",
    "SCHD dividend animation"
]

# 🔥 FACELESS FILTER KEYWORDS
faceless_keywords = [
    "animation", "animated", "explained",
    "whiteboard", "doodle", "explainer",
    "visual", "infographic"
]

# 🔥 CHECK ENGLISH TEXT
def is_english(text):
    return re.match(r'^[\x00-\x7F]+$', text) is not None

# 🔥 CHECK FACELESS CONTENT
def is_faceless(title):
    title = title.lower()
    return any(word in title for word in faceless_keywords)

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,

                # 🔥 IMPORTANT FILTERS
                "relevanceLanguage": "en",
                "regionCode": "US",

                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]

            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_data = requests.get(YOUTUBE_VIDEO_URL, params=stats_params).json()

            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_data = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params).json()

            for video, stat, channel in zip(videos, stats_data.get("items", []), channel_data.get("items", [])):

                title = video["snippet"].get("title", "")
                description = video["snippet"].get("description", "")[:200]

                # 🔥 FILTERS APPLY HERE
                if not is_english(title):
                    continue

                if not is_faceless(title):
                    continue

                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 50000:  # slightly increased for better data
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"

                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # SORT BY VIEWS (IMPORTANT)
        all_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)

        if all_results:
            st.success(f"Found {len(all_results)} filtered results!")

            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")

        else:
            st.warning("No faceless English US results found.")

    except Exception as e:
        st.error(f"Error: {e}")
