@app.route('/api/article')
def get_article():
    """Get full Wikipedia article content"""
    title = request.args.get('title', '')
    if not title:
        return jsonify({'error': 'No title provided'}), 400
    
    try:
        # Clean the search query - remove special characters and extra spaces
        clean_title = re.sub(r'[^\w\s]', '', title)
        clean_title = ' '.join(clean_title.split())
        
        # Try multiple search strategies
        search_terms = [
            clean_title,
            title,
            title.split(' ')[0] + ' ' + title.split(' ')[1] if len(title.split(' ')) > 1 else title
        ]
        
        page_title = None
        for search_term in search_terms[:2]:  # Try first 2 search terms
            if not search_term or len(search_term) < 3:
                continue
                
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_term}&format=json"
            search_resp = requests.get(search_url, timeout=5)
            
            if search_resp.status_code == 200:
                search_data = search_resp.json()
                if search_data.get('query', {}).get('search'):
                    page_title = search_data['query']['search'][0]['title']
                    break
        
        if not page_title:
            # Fallback: try searching by year only
            year_match = re.search(r'\b(\d{4})\b', title)
            if year_match:
                year = year_match.group(1)
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={year}&format=json"
                search_resp = requests.get(search_url, timeout=5)
                if search_resp.status_code == 200:
                    search_data = search_resp.json()
                    if search_data.get('query', {}).get('search'):
                        page_title = search_data['query']['search'][0]['title']
        
        if not page_title:
            return jsonify({'error': 'No Wikipedia article found for this event'}), 404
        
        # Get the page summary
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        summary_resp = requests.get(summary_url, timeout=5)
        summary_data = summary_resp.json() if summary_resp.status_code == 200 else {}
        
        # Get the full content
        content_url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page_title}&format=json&prop=text"
        content_resp = requests.get(content_url, timeout=5)
        content_data = content_resp.json() if content_resp.status_code == 200 else {}
        
        # Extract text from HTML content
        raw_html = content_data.get('parse', {}).get('text', {}).get('*', '')
        clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Get the first 1500 characters as preview
        preview = clean_text[:1500] + '...' if len(clean_text) > 1500 else clean_text
        
        # If no extract from summary, use preview
        extract = summary_data.get('extract', preview)
        if not extract or len(extract) < 50:
            extract = preview
        
        return jsonify({
            'title': page_title,
            'extract': extract,
            'full_text': preview,
            'url': f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
            'thumbnail': summary_data.get('thumbnail', {}).get('source', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
