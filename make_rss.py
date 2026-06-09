import feedparser
from datetime import datetime, timedelta
import re
import html
from rfeed import Item, Feed, Guid
from googlenewsdecoder import gnewsdecoder

# 방화벽 우회용 브라우저 위장
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

urls = [
    # 모빌리티 & EV 전문 매체 (전체수집)
    "https://carapp-news.com/feed/",
    "https://electrek.co/feed/",
    "https://www.notateslaapp.com/rss/",
    "https://cleantechnica.com/feed/",
    "https://www.greencarreports.com/news/rss-feed",
    "https://news.google.com/rss/search?q=site:greencarcongress.com&hl=en-US&gl=US&ceid=US:en",
    
    # 종합 자동차 및 테크 전문 매체 (선별 수집)
    "https://www.autonews.com/arc/outboundfeeds/sitemap-news/",
    "https://techcrunch.com/category/transportation/feed/",
    "https://www.smartcitiesdive.com/feeds/news/",
    
    # 종합 기술 동향 매체 (선별 수집)
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.feedburner.com/harvardbusinessreview",
    "https://www.technologyreview.com/feed/",
    "https://news.google.com/rss/search?q=site:news.naver.com/main/read.nhn%20OR%20site:news.naver.com/article%20%22sid=105%22&hl=ko&gl=KR&ceid=KR:ko",
    
    # 종합 앱 동향 매체 (선별 수집)
    "https://news.google.com/rss/search?q=site:surfit.io&hl=ko&gl=KR&ceid=KR:ko",
    "https://techcrunch.com/category/apps/feed/",
    "https://www.lennysnewsletter.com/feed",
    "https://productmindset.substack.com/feed",
    "https://uxdesign.cc/feed",
    
    # 키워드 기반 및 전용 앱 피드
    "https://news.google.com/rss/search?q=%22카카오모빌리티%22%20OR%20%22티맵%22%20OR%20%22커넥티드카%22%20OR%20%22쏘카%22&hl=ko&gl=KR&ceid=KR:ko",
    "https://9to5mac.com/guides/carplay/feed",
    "https://9to5google.com/guides/android-auto/feed/",
    "https://www.teslarati.com/category/tesla-software-updates/feed/",
    "https://news.google.com/rss/search?q=%22Mercedes+me%22+OR+%22myVW%22+OR+%22myAudi%22&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=%22Stellantis+app%22+OR+%22My+Jeep%22+OR+%22My+Ram%22+OR+%22Connect+ONE%22&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=%22My+BMW+app%22+OR+%22BMW+ConnectedDrive%22&hl=en-US&gl=US&ceid=US:en"
]

mobility_keywords = ['transport', 'car', 'ev', 'av', 'electronic', 'vehicle', 'autonomous', 'mobility', 'robotaxi', 'fleet', 'automotive', 'ota', 'over-the-air', 'ccs', 'connected car', 'fod', 'kakao mobility', 'socar', 'tmap', '차', '전기차', '자율주행', '모빌리티', '로보택시', '커넥티드카', '카카오모빌리티', '쏘카', '티맵']
technology_keywords = ['app', 'superapp', 'platform', 'membership', 'fintech', 'subscription', 'subscribe', 'payment', 'ai', 'agent', 'artificial intelligence', 'personalization', 'llm', 'large language model', 'model', 'assistant', 'os', 'ux', '앱', '슈퍼앱', '플랫폼', '멤버십', '핀테크', '구독', '결제', '에이전트', '인공지능', '개인화', '모델', '어시스턴트', '사용자경험']
all_target_keywords = mobility_keywords + technology_keywords

# 🚨 끝판왕 텍스트 청소기
def clean_text(raw_text):
    if not raw_text: return ""
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = html.unescape(text)
    text = text.replace('\xa0', ' ')
    
    # 1. 꼬리표가 숨지 못하게 앞뒤 줄바꿈/공백부터 완전히 벗겨냅니다.
    text = text.strip()
    
    # 2. 짧은 대시(-), 긴 대시(–, —), 파이프(|) 뒤에 붙은 네이버를 대소문자 무관하게 싹둑 자릅니다.
    text = re.sub(r'[\s\-–—|]+(네이버|NAVER|Naver)\s*$', '', text, flags=re.IGNORECASE)
    
    # 3. 만약 제목 자체가 ' - NAVER' 이런 식으로만 되어있는 쓰레기 데이터라면 아예 비워버립니다.
    if re.fullmatch(r'[\s\-–—|]*(네이버|NAVER|Naver)\s*', text, flags=re.IGNORECASE):
        return ""
        
    return re.sub(r'\s+', ' ', text).strip()

raw_items = []
now_utc = datetime.utcnow()
retention_days = now_utc - timedelta(days=14)

print(f"[{now_utc.strftime('%Y-%m-%d %H:%M:%
