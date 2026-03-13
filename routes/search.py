import requests
import re
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify, Response
from urllib.parse import unquote

search_bp = Blueprint('search', __name__)

@search_bp.route('/check-frame', methods=['GET'])
def check_frame():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    try:
        # VIP High-Security List: These sites ALWAYS block iframes or have complex JS protection.
        # Hardcoding these ensures 100% success for popular sites.
        vip_sites = ["youtube.com", "youtu.be", "google.com", "opensea.io", "uniswap.org", "github.com", "twitter.com", "x.com", "facebook.com", "instagram.com"]
        domain = url.lower()
        if any(site in domain for site in vip_sites):
            return jsonify({
                "url": url,
                "frameable": False,
                "reason": "VIP Restrictive Site",
                "can_proxy": True
            }), 200

        # Use GET request with stream=True to check headers more reliably than HEAD
        # We only download the first few bytes (headers + start of body)
        with requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }, timeout=5, allow_redirects=True, stream=True) as res:
            
            headers = {k.lower(): v.lower() for k, v in res.headers.items()}
            
            frameable = True
            reason = ""
            
            # Check X-Frame-Options
            if 'x-frame-options' in headers:
                val = headers['x-frame-options']
                if 'deny' in val or 'sameorigin' in val:
                    frameable = False
                    reason = "X-Frame-Options"
                    
            # Check Content-Security-Policy frame-ancestors
            if frameable and 'content-security-policy' in headers:
                csp = headers['content-security-policy']
                if 'frame-ancestors' in csp:
                    frameable = False
                    reason = "Content-Security-Policy"

            return jsonify({
                "url": url,
                "frameable": frameable,
                "reason": reason,
                "can_proxy": True
            }), 200
        
    except Exception as e:
        # On connection failure, default to proxying to be safe
        return jsonify({
            "url": url,
            "frameable": False,
            "reason": f"Connection error: {str(e)}",
            "can_proxy": True
        }), 200

@search_bp.route('/proxy', methods=['GET'])
def proxy_view():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    try:
        # Fetch the content with a generic User-Agent
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }, timeout=10, verify=False)
        
        # Prepare headers to strip security and other problematic headers
        excluded_headers = [
            'content-encoding', 'content-length', 'transfer-encoding', 'connection',
            'x-frame-options', 'content-security-policy', 'frame-ancestors', 'strict-transport-security'
        ]
        headers = [(name, value) for (name, value) in res.headers.items() if name.lower() not in excluded_headers]
        
        content = res.content
        
        # If it's HTML, inject a <base> tag to help find relative resources (CSS, JS, Images)
        content_type = res.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            soup = BeautifulSoup(content, 'html.parser')
            if not soup.find('base'):
                base_tag = soup.new_tag('base', href=url)
                if soup.head:
                    soup.head.insert(0, base_tag)
                else:
                    head = soup.new_tag('head')
                    head.append(base_tag)
                    soup.insert(0, head)
            content = str(soup).encode('utf-8')

        return Response(content, res.status_code, headers)
    except Exception as e:
        print(f"Proxy Error for {url}: {e}")
        return jsonify({"error": str(e)}), 500

@search_bp.route('', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    results = []
    
    # --- SOURCE 1: DuckDuckGo HTML Lite ---
    try:
        ddg_url = "https://html.duckduckgo.com/html/"
        response = requests.post(ddg_url, data={'q': query}, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_='result__body'):
                title_el = item.find('a', class_='result__url')
                snippet_el = item.find('a', class_='result__snippet')
                if title_el and snippet_el:
                    href = title_el.get('href', '')
                    # Clean DDG redirect
                    if 'uddg=' in href:
                        href = unquote(href.split('uddg=')[-1].split('&')[0])
                    
                    results.append({
                        "title": title_el.text.strip(),
                        "description": snippet_el.text.strip(),
                        "url": href,
                        "domain": href.split("//")[-1].split("/")[0] if "//" in href else "Web Link"
                    })
    except Exception as e:
        print(f"DDG Error: {e}")

    # --- SOURCE 2: Google Search (Mobile Lite) ---
    try:
        # Use a mobile UA to get simpler HTML from Google
        google_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        google_url = f"https://www.google.com/search?q={query}&num=15"
        res = requests.get(google_url, headers={"User-Agent": google_ua}, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Look for standard mobile result blocks
            for item in soup.find_all('div', recursive=True):
                # Google mobile results often use specific a tags with h3 inside
                a_tag = item.find('a')
                h3_tag = item.find('h3')
                if a_tag and h3_tag and a_tag.get('href', '').startswith('http'):
                    url = a_tag.get('href')
                    # Don't add if already in results (deduplicate by URL)
                    if not any(r['url'] == url for r in results):
                        # Find snippet (usually a div with specific style or following the h3)
                        snippet = ""
                        # Rough heuristic for google mobile snippets
                        next_div = item.find('div', class_=lambda x: x and len(x) > 0)
                        if next_div: snippet = next_div.text.strip()
                        
                        results.append({
                            "title": h3_tag.text.strip(),
                            "description": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                            "url": url,
                            "domain": url.split("//")[-1].split("/")[0]
                        })
    except Exception as e:
        print(f"Google Error: {e}")

    # Final touch: limit and return
    return jsonify(results[:25]), 200

@search_bp.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]), 200
        
    suggestions = []
    
    # 1. Match against internal DApps (Simulation of history/bookmarks)
    from models.dapp_model import Dapp
    try:
        # Search for names or URLs that start with or contain the query
        internal_matches = Dapp.query.filter(
            (Dapp.name.ilike(f'%{query}%')) | (Dapp.url.ilike(f'%{query}%'))
        ).limit(3).all()
        
        for d in internal_matches:
            suggestions.append({
                "phrase": d.name,
                "type": "internal",
                "subtitle": d.url
            })
    except Exception as e:
        print(f"Internal suggest error: {e}")

    # 2. Web Predictions from DuckDuckGo
    url = f"https://duckduckgo.com/ac/?q={query}&type=list"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        res = requests.get(url, headers=headers, timeout=3)
        res.raise_for_status()
        data = res.json()
        if len(data) > 1 and isinstance(data[1], list):
            for s in data[1]:
                # Don't duplicate internal matches
                if not any(m["phrase"].lower() == s.lower() for m in suggestions):
                    suggestions.append({
                        "phrase": s,
                        "type": "web",
                        "subtitle": "Web Search"
                    })
        return jsonify(suggestions[:8]), 200
    except Exception as e:
        print(f"Suggestions error: {e}")
        return jsonify(suggestions), 200 # Return at least internal ones if web fails
