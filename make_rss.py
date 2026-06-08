import feedparser
from datetime import datetime, timedelta
import time
from rfeed import Item, Feed

# 1. 수집 대상 피드 리스트 (The Verge 메인 피드 포함)
urls = [
    #모빌리티 & EV 전문 매체 (전체수집)
    "https://carapp-news.com/feed/",
    "https://electrek.co/feed/",
    "https://www.notateslaapp.com/rss/",
    "https://cleantechnica.com/feed/"
    "https://www.greencarreports.com/news/rss-feed"
    "https://news.google.com/rss/search?q=site:greencarcongress.com&hl=en-US&gl=US&ceid=US:en"
    #종합 자동차 및 테크 전문 매체 (카테고리/키워드 선별 수집)
    "https://www.autonews.com/arc/outboundfeeds/sitemap-news/",
    "https://techcrunch.com/category/transportation/feed/",
    "https://www.smartcitiesdive.com/feeds/news/"
    #종합 기술 동향 매체 (키워드 선별 수집)
    "https://www.theverge.com/rss/index.xml"
    "https://feeds.feedburner.com/harvardbusinessreview"
    "https://www.technologyreview.com/feed/"
]

# 필터링할 모빌리티 관련 키워드 리스트
mobility_keywords = ['transport', 'car', 'EV', 'AV', 'electronic', 'vehicle', 'autonomous', 'mobility', 'robotaxi', 'fleet', 'automotive', 'OTA', 'Over-the-Air', 'CCS', 'connected car', 'FoD']
# 필터링할 기술, 서비스 관련 키워드 리스트
technology_keywords = ['app', 'superapp', 'platform', 'membership', 'fintech', 'subscription', 'subscribe', 'payment', 'AI', 'agent', 'Artificial Intelligence', 'personalization', 'LLM', 'Large Language Model', 'model', 'assistant', 'OS', 'UX']

items = []
now = datetime.now()
one_week_ago = now - timedelta(days=7)

print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] RSS 피드 수집 및 필터링 시작...")

for url in urls:
    try:
        feed = feedparser.parse(url)
        print(f"🔄 수집 중: {feed.feed.get('title', url)}")
        
        for entry in feed.entries:
            published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
            
            if published_parsed:
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                
                # 1차 필터: 최근 일주일 이내의 게시글인지 확인
                if published_dt > one_week_ago:
                    
                    title = entry.get("title", "")
                    summary = entry.get("summary", "") or entry.get("description", "")
                    content_text = (title + " " + summary).lower()
                    
                    # 2차 필터: 메인 피드인 경우에만 키워드 검사 진행 (타 매체는 전체 수집)
                    if "autonews.com" or "techcrunch.com" or "smartcitiesdive.com" or "theverge.com" or "harvardbusinessreview" or "technologyreview.com" in url:
                        is_mobility_news = any(keyword in content_text for keyword in mobility_keywords or technology_keywords)
                    else:
                        is_mobility_news = True  # 다른 전문 매체는 조건 없이 통과
                    
                    # 최종 매칭된 경우에만 RSS 아이템으로 추가
                    if is_mobility_news:
                        description = summary if summary else title
                        
                        item = Item(
                            title=title,
                            link=entry.link,
                            description=description,
                            pubDate=published_dt
                        )
                        items.append(item)
                        
    except Exception as e:
        print(f"❌ 에러 발생 ({url}): {e}")

# 최신순 정렬
items.sort(key=lambda x: x.pubDate, reverse=True)

# 새 RSS 피드로 병합
new_feed = Feed(
    title="Custom Transportation & EV News (Last 7 Days)",
    link="https://yourdomain.com",
    description="Filtered mobility & tech news from major sites",
    language="ko",
    items=items
)

# XML 파일 저장
output_filename = "filtered_feed.xml"
try:
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(new_feed.rss())
    print(f"✅ 성공: 총 {len(items)}개의 맞춤 뉴스 항목이 '{output_filename}'에 저장되었습니다.")
except Exception as e:
    print(f"❌ 파일 저장 실패: {e}")
