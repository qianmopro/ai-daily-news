import feedparser
import json
import time
import os
import socket
import random
from datetime import datetime, timedelta
from time import mktime

# 配置
SOURCE_FILE = "my_sources.txt"
OUTPUT_FILE = "raw_news.json"
TIME_WINDOW_HOURS = 24  # 每天跑一次，抓24小时的就够了
socket.setdefaulttimeout(30)

# 伪装头
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def load_sources(filepath):
    sources = []
    if not os.path.exists(filepath):
        print(f"❌ 找不到 {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "|" in line:
                title, url = line.split("|", 1)
                sources.append({"name": title.strip(), "url": url.strip()})
    return sources

def is_recent(entry_date_struct):
    if not entry_date_struct: return True
    try:
        pub_date = datetime.fromtimestamp(mktime(entry_date_struct))
        cutoff = datetime.now() - timedelta(hours=TIME_WINDOW_HOURS)
        return pub_date > cutoff
    except:
        return True

def fetch_all():
    sources = load_sources(SOURCE_FILE)
    print(f"🚀 开始抓取 {len(sources)} 个源...")
    
    collected_news = []
    
    for i, source in enumerate(sources):
        print(f"[{i+1}/{len(sources)}] {source['name']} ... ", end="", flush=True)
        time.sleep(2) # 稍微休息，防封
        
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            feed = feedparser.parse(source['url'], request_headers=headers)
            
            if not feed.entries:
                print("⚠️ 空")
                continue

            count = 0
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed'):
                    if not is_recent(entry.published_parsed): continue
                
                title = entry.title if hasattr(entry, 'title') else "无标题"
                link = entry.link if hasattr(entry, 'link') else ""
                
                collected_news.append({
                    "source": source['name'],
                    "title": title,
                    "link": link
                })
                count += 1
            
            print(f"✅ {count} 条")
                
        except Exception as e:
            print(f"❌ 错: {str(e)[:20]}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(collected_news, f, ensure_ascii=False, indent=4)
    print(f"🎉 抓取完成！数据存入 {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_all()