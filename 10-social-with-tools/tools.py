from dotenv import load_dotenv
from crewai.tools import tool 
from firecrawl import FirecrawlApp
import os
import re

@tool("web_search_tool")
def web_search_tool(query: str):
    """
    웹 검색 도구(Firecrawl)를 사용하여 최신 뉴스를 검색하고 수집합니다.
    Args:
        query: str
            검색할 쿼리를 입력합니다.
    Returns
        웹 검색 결과를 Markdown 형식으로 반환합니다.
    """

    load_dotenv()
    cleaned_chunks = []

    try:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return "Error: API KEY NOT FOUND"
        firecrawl = FirecrawlApp(api_key=api_key)
        response = firecrawl.search(
            query=query,
            limit=2,
            scrape_options={
                "formats": ["markdown"],
            },
            sources=["news"]
        )

        if response.news:
            for news_item in response.news:
                try:
                    title = news_item.metadata.title
                    url = news_item.metadata.url
                    markdown = news_item.markdown
                    cleaned = re.sub(r"\\+|\n+", " ", markdown).strip() # 문자열 줄바꿈 제거
                    cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned) # 링크 제거
                    cleaned_result = {
                        "title": title,
                        "url": url,
                        "markdown": cleaned,
                    }
                    cleaned_chunks.append(cleaned_result)

                except Exception as e:
                    print(f"Error: {e}")
                    continue
        else:
            print("No response found")
    except Exception as e:
        print(f"Error: {e}")

    
    return cleaned_chunks
