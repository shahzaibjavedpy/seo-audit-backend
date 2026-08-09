import requests
from bs4 import BeautifulSoup
import time

def audit_url(url: str) -> dict:
    report = {
        "url": url,
        "status_code": None,
        "response_time_sec": None,
        "issues": [],
        "passed": [],
        "details": {}
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        end_time = time.time()
        
        report["status_code"] = response.status_code
        report["response_time_sec"] = round(end_time - start_time, 2)
        
        if response.status_code != 200:
            report["issues"].append(f"Status code: {response.status_code}")
            return report

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Title Check
        title = soup.find('title')
        if not title or not title.text.strip():
            report["issues"].append("Missing Title Tag")
        else:
            title_text = title.text.strip()
            report["details"]["title"] = title_text
            if len(title_text) > 60:
                report["issues"].append(f"Title too long ({len(title_text)} chars)")
            else:
                report["passed"].append("Title tag length is good")

        # 2. Meta Description Check
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            report["issues"].append("Missing Meta Description")
        else:
            desc_text = meta_desc.get('content').strip()
            report["details"]["meta_description"] = desc_text
            if len(desc_text) < 50 or len(desc_text) > 160:
                report["issues"].append(f"Meta Description length ({len(desc_text)}) not optimal")
            else:
                report["passed"].append("Meta Description length is good")

        # 3. H1 Check
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            report["issues"].append("Missing H1 Heading")
        elif len(h1_tags) > 1:
            report["issues"].append(f"Multiple H1 tags found ({len(h1_tags)})")
        else:
            report["passed"].append("Single H1 tag found")
            report["details"]["h1"] = h1_tags[0].text.strip()

        # 4. Canonical Tag Check
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical and canonical.get('href'):
            report["passed"].append("Canonical tag present")
            report["details"]["canonical"] = canonical.get('href')
        else:
            report["issues"].append("Missing Canonical Tag")

        # 5. Image Alt Text Audit
        images = soup.find_all('img')
        missing_alt = [img.get('src') for img in images if not img.get('alt')]
        report["details"]["total_images"] = len(images)
        report["details"]["missing_alt_count"] = len(missing_alt)
        
        if missing_alt:
            report["issues"].append(f"{len(missing_alt)} images missing 'alt' attributes")
        else:
            report["passed"].append("All images have 'alt' attributes")

        # 6. Open Graph (OG Title) Check
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            report["passed"].append("Open Graph Title found")
        else:
            report["issues"].append("Missing Open Graph (og:title) tag")

    except Exception as e:
        report["issues"].append(f"Fetch failed: {str(e)}")

    return report