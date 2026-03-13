import requests
import re
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify, Response

search_bp = Blueprint('search', __name__)

@search_bp.route('/check-frame', methods=['GET'])
def check_frame():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    try:
        # Special hardcoded overrides for known difficult sites that block via JS 
        # or have complex bot protection that prevents HEAD requests from seeing true headers
        domain = url.lower()
        if "youtube.com" in domain or "youtu.be" in domain or "opensea.io" in domain or "github.com" in domain or "twitter.com" in domain or "x.com" in domain or "google.com" in domain:
            return jsonify({
                "url": url,
                "frameable": False,
                "reason": "Known restrictive SPA",
                "status_code": 200
            }), 200
            
        # Use HEAD request to quickly check headers without downloading body
        res = requests.head(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }, timeout=5, allow_redirects=True)
        
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
            if 'frame-ancestors' in csp and ("'none'" in csp or "http" not in csp): # Rough heuristic
                frameable = False
                reason = "Content-Security-Policy"

        return jsonify({
            "url": url,
            "frameable": frameable,
            "reason": reason,
            "status_code": res.status_code
        }), 200
        
    except Exception as e:
        # If we can't even connect (e.g. timeout, DNS error), assume it's not frameable
        return jsonify({
            "url": url,
            "frameable": False,
            "reason": f"Connection error: {str(e)}"
        }), 200

@search_bp.route('', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # DuckDuckGo HTML Lite parameters for true web search scraping
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.post(url, data={'q': query}, headers=headers, timeout=5)
        if response.status_code == 403 or response.status_code == 429:
             # Handle being blocked by DDG without crashing the app
             return jsonify({
                 "results": [], 
                 "warning": "Search is currently rate-limited by DuckDuckGo. Please try again in 5 minutes.",
                 "status": "limited"
             }), 200
             
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Scrape all result containers mapped to 'result__body' in the lite HTML
        for item in soup.find_all('div', class_='result__body'):
            title_el = item.find('a', class_='result__url')
            snippet_el = item.find('a', class_='result__snippet')
            
            if title_el and snippet_el:
                title = title_el.text.strip()
                href = title_el.get('href', '')
                snippet = snippet_el.text.strip()
                
                # Clean DuckDuckGo redirect URLs
                if 'uddg=' in href:
                    from urllib.parse import unquote
                    raw_url = href.split('uddg=')[-1].split('&')[0]
                    destination_url = unquote(raw_url)
                else:
                    destination_url = href
                    
                domain = destination_url.split("//")[-1].split("/")[0] if "//" in destination_url else "Web Link"

                results.append({
                    "title": title,
                    "description": snippet,
                    "url": destination_url,
                    "domain": domain
                })

        return jsonify(results), 200

    except Exception as e:
        print(f"DuckDuckGo API Error: {e}")
        # Always return 200 to keep Vercel logs green, but indicate failure in JSON
        return jsonify({
            "results": [],
            "error": "External Search Service Timeout",
            "details": str(e)
        }), 200

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
