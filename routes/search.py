import requests
import re
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify

search_bp = Blueprint('search', __name__)

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
