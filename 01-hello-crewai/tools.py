from crewai.tools import tool

@tool("count_words")
def count_words(sentence: str) -> int:
    """문장에서 단어의 개수를 셉니다.
    Args:
        sentence (str): 단어를 셀 문장.
    Returns:
        int: 문장에 포함된 단어의 개수.
    """
    return len(sentence.split())