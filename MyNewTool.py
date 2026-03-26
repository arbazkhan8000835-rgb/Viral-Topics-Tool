import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# --------------------------
# YouTube API Key
# --------------------------
API_KEY = "AIzaSyDKBxqXFE8ktMBkjaYUORER3T3wL0ODPaU"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# --------------------------
# Streamlit App Title
# --------------------------
st.title("YouTube Viral Topics Tool (US + Faceless Filtered)")

# --------------------------
# Input: Days to Search
# --------------------------
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# --------------------------
# Improved Keywords (Faceless / Animation)
# --------------------------
keywords = [
    "personal finance",
    "investing explained",
    "investing",
    "VOO",
    "VTI",
    "SCHD",
    "Vanguard",
    "Charles Schwab",
    "S&P 500",
    "ETF Strategy",
    "ETFS",
    "Retirement",
    "Mutual Funds",
    "Hedge Funds",
    "Index Funds",
    "Dividends",
    "Fidelity",
    "Money",
    "Rich",
    "QQQM",
    "QQQ",
    "SPY",
    "Social Security",
    "Tax Torpedo",
    "Build Wealth",
    "$100,000",
    "$20,000",
    "$500K",
    "Payment",
    "Income",
    "Savings",
    "saving",
    "Savings Account",
    "Tax",
    "dividend investing",
    "passive income investing",
    "etf investing strategy",
    "index fund investing",
    "compound interest investing",
    "financial freedom investing",
    "monthly dividend income",
    "VOO investing",
    "SCHD dividend",
    "Vanguard ETF investing",
    "Charles Schwab ETF",
    "Fidelity investing"
]

# --------------------------
# Faceless Keywords for Filtering
# --------------------------
faceless_keywords = [
    "animation", "animated", "explained",
    "whiteboard", "doodle", "explainer",
    "visual", "infographic"
]

# --------------------------
# Helper Functions
# --------------------------
def is_english(text):
    """Check if text contains only ASCII characters (English)"""
    return re.match(r'^[\x00-\x7F]+$', text) is not None

def is_faceless(title, description):
    """Check if title or description contains faceless keywords"""
    text = (title + " " + description).lower()
    return any(word in text for word in faceless_keywords)

# --------------------------
# Fetch Data
# --------------------------
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching: {keyword}")

            # --------------------------
            # Search Parameters
            # --------------------------
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,
                "relevanceLanguage": "en",
                "regionCode": "US",
                "videoDuration": "medium",
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            # --------------------------
            # Fetch Video Statistics
            # --------------------------
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_data = requests.get(YOUTUBE_VIDEO_URL, params=stats_params).json()

            # --------------------------
            # Fetch Channel Statistics
            # --------------------------
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_data = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params).json()

            # --------------------------
            # Collect Results
            # --------------------------
            for video, stat, channel in zip(videos, stats_data.get("items", []), channel_data.get("items", [])):

                title = video["snippet"].get("title", "")
                description = video["snippet"].get("description", "")[:200]

                # --------------------------
                # Filters
                # --------------------------
                if not is_english(title):
                    continue

                if not is_faceless(title, description):
                    continue

                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # Subscriber filter (small + growing channels)
                if 1000 < subs < 300000:
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    viral_score = views / (subs + 1)  # simple viral metric

                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "ViralScore": round(viral_score, 2)
                    })

        # --------------------------
        # Sort Results by Viral Score
        # --------------------------
        all_results = sorted(all_results, key=lambda x: x["ViralScore"], reverse=True)

        # --------------------------
        # Display Results
        # --------------------------
        if all_results:
            st.success(f"Found {len(all_results)} filtered results!")

            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}  \n"
                    f"**Viral Score:** {result['ViralScore']}"
                )
                st.write("---")
        else:
            st.warning("No faceless English US results found.")

    except Exception as e:
        st.error(f"Error: {e}")
