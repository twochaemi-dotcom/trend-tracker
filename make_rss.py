import feedparser
from datetime import datetime, timedelta
import time
from rfeed import Item, Feed

# 1. 수집 대상 피드 리스트 (누락된 쉼표 모두 수정)
urls = [
    # 모빌리티 & EV 전문 매체 (전체수집)
    "https://carapp-news.com/feed/",
    "https://electrek.co/feed/",
    "https://www.notateslaapp.com/rss/",
    "https://cleantechnica.com/feed/",
    "https://www.greencarreports.com/news/rss-feed",
    "https://news.google.com/rss/search?q=site:greencarcongress.com&hl=en-US&gl=US&ceid=US:en",
    
    # 종합 자동차 및 테크 전문 매체 (카테고리/키워드 선별 수집)
    "https://www.autonews.com/arc/outboundfeeds/sitemap-news/",
    "https://techcrunch.com/category/transportation/feed/",
    "https://www.smartcitiesdive.com/feeds/news/",
    
    # 종합 기술 동향 매체 (키워드 선별 수집)
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.feedburner.com/harvardbusinessreview",
    "https://www.technologyreview.com/feed/",
    "https://news.google.com/rss/search?q=site:news.naver.com/main/read.nhn%20OR%20site:news.naver.com/article%20%22sid=105%22&hl=ko&gl=KR&ceid=KR:ko",
    
    # 종합 앱 동향 매체 (키워드 선별 수집)
    "https://news.google.com/rss/search?q=site:surfit.io&hl=ko&gl=KR&ceid=KR:ko",
    "https://techcrunch.com/category/apps/feed/",
    "https://www.lennysnewsletter.com/feed",
    "https://productmindset.substack.com/feed",
    "https://uxdesign.cc/feed",
    
    # 키워드 기반 수집
    "https://news.google.com/rss/search?q=%22카카오모빌리티%22%20OR%20%22티맵%22%20OR%20%22커넥티드카%22%20OR%20%22쏘카%22&hl=ko&gl=KR&ceid=KR:ko",
    
    # 모빌리티 앱 피드
    "https://9to5mac.com/guides/carplay/feed",
    "https://9to5google.com/guides/android-auto/feed/",
    "https://www.teslarati.com/category/tesla-software-updates/feed/",
    "https://news.google.com/rss/search?q=%22Mercedes+me%22+OR+%22myVW%22+OR+%22myAudi%22&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=%22Stellantis+app%22+OR+%22My+Jeep%22+OR+%22My+Ram%22+OR+%22Connect+ONE%22&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=%22My+BMW+app%22+OR+%22BMW+ConnectedDrive%22&hl=en-US&gl=US&ceid=US:en"
]

# 필터링할 모빌리티 관련 키워드 리스트
mobility_keywords = [
    'transport', 'car', 'ev', 'av', 'electronic', 'vehicle', 'autonomous', 'mobility', 'robotaxi', 'fleet', 'automotive', 
    'ota', 'over-the-air', 'ccs', 'connected car', 'fod', 'kakao mobility', 'socar', 'tmap',
    '차', '전기차', '자율주행', '모빌리티', '로보택시', '커넥티드카', '카카오모빌리티', '쏘카', '티맵'
]

# 필터링할 기술, 서비스 관련 키워드 리스트 (오타 및 따옴표 수정)
technology_keywords = [
    'app', 'superapp', 'platform', 'membership', 'fintech', 'subscription', 'subscribe', 'payment', 'ai', 'agent', 
    'artificial intelligence', 'personalization', 'llm', 'large language model', 'model', 'assistant', 'os', 'ux',
    '앱', '슈퍼앱', '플랫폼', '멤버십', '핀테크', '구독', '결제', '에이전트', '인공지능', '개인화', '모델', '어시스턴트', '사용자경험'
]

# 두 개의 키워드 리스트를 하나로 결합
all_target_keywords = mobility_keywords + technology_keywords

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
                    
                    # 2차 필터링이 필요한 도메인 리스트
                    filter_required_domains = [
                        "autonews.com", "techcrunch.com", "smartcitiesdive.com", 
                        "theverge.com", "harvardbusinessreview", "technologyreview.com", 
                        "news.naver.com", "surfit"
                    ]
                    
                    # 2차 필터: 메인 피드 계열인 경우에만 통합 키워드 검사 진행
                    if any(domain in url for domain in filter_required_domains):
                        # content_text가 이미 소문자이므로, 대소문자 매칭 문제를 완벽히 방지
                        is_mobility_news = any(keyword in content_text for keyword in all_target_keywords)
                    else:
                        is_mobility_news = True  # 전문 매체 및 전용 앱 피드는 조건 없이 통과
                    
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
