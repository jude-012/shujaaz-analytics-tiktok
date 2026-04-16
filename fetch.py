"""
Shujaaz Kenya — YouTube Data Fetcher
Runs daily via GitHub Actions. Saves shujaaz_videos.json to repo.
"""
import requests, json, time, re
from datetime import datetime, timezone

API_KEY    = "PASTE_YOUR_API_KEY_HERE"
CHANNEL_ID = "UC9c-0G_FKj5L_x3teNA14qQ"
BASE       = "https://www.googleapis.com/youtube/v3"

CAMPAIGN_HASHTAGS = {
    "Free2Choose":       ["#IGotThis","#GirlCode254","#TukoWengi","#CityGirl254","#MsupaStar","#BazuuFom","#MyChoice","#SafeSpace","#JustSayIt","#Machampez","#PengTing","#MsupaSmarter","Free2Choose"],
    "GBV Awareness":     ["#SimamaNaMe","#BreakTheSilence","#EndGBV","GBV","gender based violence"],
    "MTV Shuga":         ["#MTVShuga","#MTVShugaMashariki","MTV Shuga","Shuga"],
    "MicYetu":           ["#MicYetu","MicYetu","Mic Yetu"],
    "Financial Fitness": ["#PesaYako","#ChamaSmart","#BudgetQueen","pesa yako","chama"],
    "Shujaaz TV":        ["Shujaaz TV","ShujaazTV","#ShujaazTV"],
    "ShujaazSTRA":       ["#ShujaazSTRA","ShujaazSTRA","STRA!"],
    "TukoOn":            ["#TukoOn","Tuko On"],
}

def detect_campaign(text):
    if not text: return "Uncategorised"
    tl = text.lower()
    for camp, tags in CAMPAIGN_HASHTAGS.items():
        for tag in tags:
            if tag.lower() in tl:
                return camp
    return "Uncategorised"

def parse_duration(dur):
    if not dur: return 0
    h = int(m.group(1)) if (m := re.search(r'(\d+)H', dur)) else 0
    mn = int(m.group(1)) if (m := re.search(r'(\d+)M', dur)) else 0
    s = int(m.group(1)) if (m := re.search(r'(\d+)S', dur)) else 0
    return h*3600 + mn*60 + s

def detect_type(title, dur_str):
    secs = parse_duration(dur_str)
    if "#shorts" in title.lower() or "#short" in title.lower(): return "short"
    if 0 < secs <= 60: return "short"
    return "video"

def get_uploads_playlist():
    r = requests.get(f"{BASE}/channels", params={"part":"contentDetails","id":CHANNEL_ID,"key":API_KEY})
    r.raise_for_status()
    return r.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_all_video_ids(pid):
    ids, params = [], {"part":"contentDetails","playlistId":pid,"maxResults":50,"key":API_KEY}
    while True:
        r = requests.get(f"{BASE}/playlistItems", params=params); r.raise_for_status()
        d = r.json()
        ids += [i["contentDetails"]["videoId"] for i in d.get("items",[])]
        nt = d.get("nextPageToken")
        if not nt: break
        params["pageToken"] = nt
        time.sleep(0.15)
    return ids

def get_video_details(ids):
    videos = []
    for batch in [ids[i:i+50] for i in range(0,len(ids),50)]:
        r = requests.get(f"{BASE}/videos", params={"part":"snippet,statistics,contentDetails","id":",".join(batch),"key":API_KEY})
        r.raise_for_status()
        for item in r.json().get("items",[]):
            sn = item.get("snippet",{}); st = item.get("statistics",{}); cd = item.get("contentDetails",{})
            title = sn.get("title",""); desc = sn.get("description","")
            dur = cd.get("duration","")
            videos.append({
                "id":           item["id"],
                "url":          f"https://youtube.com/watch?v={item['id']}",
                "title":        title,
                "published_at": sn.get("publishedAt","")[:10],
                "description":  desc[:300],
                "duration":     dur,
                "type":         detect_type(title, dur),
                "campaign":     detect_campaign(f"{title} {desc}"),
                "views":        int(st.get("viewCount",0)),
                "likes":        int(st.get("likeCount",0)),
                "comments":     int(st.get("commentCount",0)),
                "thumbnail":    sn.get("thumbnails",{}).get("medium",{}).get("url",""),
            })
        time.sleep(0.15)
    return videos

def build_summary(videos):
    from collections import defaultdict
    camps  = defaultdict(lambda:{"videos":0,"views":0,"likes":0,"comments":0})
    types  = defaultdict(lambda:{"count":0,"views":0})
    monthly= defaultdict(lambda:{"uploads":0,"views":0})
    for v in videos:
        c = v["campaign"]
        camps[c]["videos"]   += 1; camps[c]["views"]    += v["views"]
        camps[c]["likes"]    += v["likes"]; camps[c]["comments"] += v["comments"]
        types[v["type"]]["count"]  += 1; types[v["type"]]["views"] += v["views"]
        m = v["published_at"][:7]
        monthly[m]["uploads"] += 1; monthly[m]["views"] += v["views"]
    top15 = sorted(videos, key=lambda x:-x["views"])[:15]
    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total":      len(videos),
        "views":      sum(v["views"] for v in videos),
        "likes":      sum(v["likes"] for v in videos),
        "comments":   sum(v["comments"] for v in videos),
        "campaigns":  dict(camps),
        "monthly":    dict(sorted(monthly.items())),
        "typeBreakdown": dict(types),
        "topVideos":  top15,
        "allVideos":  videos,
    }

def main():
    import os
    key = os.environ.get("YOUTUBE_API_KEY") or API_KEY
    if key == "PASTE_YOUR_API_KEY_HERE":
        print("ERROR: Set YOUTUBE_API_KEY environment variable"); return
    global API_KEY; API_KEY = key
    print(f"Fetching Shujaaz Kenya YouTube data — {datetime.now()}")
    pid   = get_uploads_playlist()
    ids   = get_all_video_ids(pid)
    print(f"Found {len(ids)} videos")
    vids  = get_video_details(ids)
    data  = build_summary(vids)
    with open("shujaaz_videos.json","w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved shujaaz_videos.json — {len(vids)} videos, {data['views']:,} total views")

if __name__ == "__main__":
    main()
