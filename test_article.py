import requests
import json

# Your DeepSeek API Key
DEEPSEEK_API_KEY = "sk-2d594d1ee9d44f5d89ba5e49427097db"  # Replace with your actual key

def generate_article(topic):
    """Generate an article using DeepSeek API"""
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Write a short, engaging article about {topic} for a "Today in History" mobile app.

The article should:
- Be 100-150 words long
- Include key historical facts
- Be written in a clear, engaging style
- End with a interesting fact

Write the article in English:"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful historian writing engaging articles for a mobile app."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if response.status_code == 200:
        article = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return article
    else:
        return f"Error: {result}"

# ===== TEST IT =====
if __name__ == "__main__":
    print("🧪 Testing DeepSeek Article Generation\n")
    print("=" * 50)
    
    # Test 1: Nikola Tesla
    print("\n📖 Test 1: Nikola Tesla")
    print("-" * 30)
    article1 = generate_article("Nikola Tesla")
    print(article1)
    
    print("\n" + "=" * 50)
    
    # Test 2: World War I
    print("\n📖 Test 2: World War I")
    print("-" * 30)
    article2 = generate_article("World War I")
    print(article2)
    
    print("\n" + "=" * 50)
    
    # Test 3: Moon Landing
    print("\n📖 Test 3: Moon Landing")
    print("-" * 30)
    article3 = generate_article("Moon Landing 1969")
    print(article3)
    
    print("\n✅ Test complete!")
