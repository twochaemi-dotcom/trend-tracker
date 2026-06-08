# 실행 전 터미널에 아래 명령어를 입력하여 필수 라이브러리를 설치하세요:
# pip install feedparser rfeed

import feedparser
from datetime import datetime, timedelta
import time
from rfeed import Item, Feed

# 1. 수집 대상 피드 리스트 (제공해주신 URL 반영)
urls = [
    "https://carapp-news.com/feed/",
    "https://electrek.co/feed/",
    "https://www.notateslaapp.com/rss/",
    "https://www.autonews.com/arc/outboundfeeds/sitemap-news/",
    "https://techcrunch.com/category/transportation/feed/",
]

items = []
# 기준 시간: 일관된 비교를 위해 현재 시간(시간대 제외)을 구합니다.
now = datetime.now()
one_week_ago = now - timedelta(days=7)

print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] RSS 피드 수집 및 필터링 시작 (최근 7일 기준)...")

for url in urls:
    try:
        feed = feedparser.parse(url)
        
        # 피드 파싱 실패 처리
        if feed.bozo:
            print(f"⚠️ 경고: {url} 파싱 중 일부 문제가 발생했으나 진행합니다.")
            
        print(f"🔄 수집 중: {feed.feed.get('title', url)}")
        
        for entry in feed.entries:
            # 게시글 날짜 파싱 (다양한 포맷 대응)
            published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
            
            if published_parsed:
                # 구조적 결함을 막기 위해 struct_time을 datetime 객체(naive)로 변환
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                
                # 2. 최근 일주일 이내의 게시글만 필터링
                if published_dt > one_week_ago:
                    # description이 비어있을 경우 고유한 대안 값 탐색
                    description = entry.get("summary") or entry.get("description") or entry.get("title")
                    
                    item = Item(
                        title=entry.title,
                        link=entry.link,
                        description=description,
                        pubDate=published_dt
                    )
                    items.append(item)
                    
    except Exception as e:
        print(f"❌ 에러 발생 ({url}): {e}")

# 최신순으로 정렬 (최근에 올라온 글이 위로 오도록)
items.sort(key=lambda x: x.pubDate, reverse=True)

# 3. 하나의 새 RSS 피드로 병합
new_feed = Feed(
    title="Custom Transportation & EV News (Last 7 Days)",
    link="https://yourdomain.com",  # 추후 배포할 사이트가 있다면 변경 가능
    description="Filtered mobility & tech news from 5 major sites",
    language="ko",
    items=items
)

# 4. XML 파일로 저장
output_filename = "filtered_feed.xml"
try:
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(new_feed.rss())
    print(f"✅ 성공: 총 {len(items)}개의 최신 게시글이 '{output_filename}' 파일로 저장되었습니다.")
except Exception as e:
    print(f"❌ 파일 저장 실패: {e}")
