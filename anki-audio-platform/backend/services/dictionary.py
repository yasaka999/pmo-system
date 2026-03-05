"""
单词解释服务
支持中英双语释义，优先中文释义
Updated: 2026-03-05 12:22
"""
import aiohttp
import logging
import json
import re
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# 免费词典API
DICT_APIS = {
    "free_dictionary": "https://api.dictionaryapi.dev/api/v2/entries/en/",
}


async def lookup_word_youdao(word: str) -> Optional[Dict]:
    """
    使用有道词典API查询单词（中英双语）
    
    Returns:
        {
            "word": "example",
            "phonetic": "/ɪɡˈzæmpəl/",
            "pos": "n.",
            "definition_cn": "例子；榜样",
            "definition_en": "a thing characteristic of its kind",
            "example": "This is an example."
        }
    """
    # 有道词典API（免费版）
    url = f"https://dict.youdao.com/jsonapi?q={word.lower()}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                logger.info(f"有道词典API响应状态: {resp.status}")
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                logger.info(f"有道词典返回keys: {list(data.keys())[:5]}")
                if not data:
                    return None
                
                result = {
                    "word": word.lower(),
                    "phonetic": "",
                    "pos": "",
                    "definition_cn": "",
                    "definition_en": "",
                    "example": ""
                }
                
                # 解析有道词典返回的数据
                # 结构: { "ec": { "word": [{ "ukphone": "...", "trs": [...] }] } }
                if "ec" in data:
                    ec = data["ec"]
                    if "word" in ec and ec["word"]:
                        word_info = ec["word"][0]
                        
                        # 音标（优先美音）
                        result["phonetic"] = word_info.get("usphone", "") or word_info.get("ukphone", "")
                        if result["phonetic"]:
                            result["phonetic"] = f"/{result['phonetic']}/"
                        
                        # 词性和释义
                        if "trs" in word_info:
                            trs = word_info["trs"]
                            definitions = []
                            
                            for tr in trs[:4]:  # 最多取4个释义
                                if isinstance(tr, dict) and "tr" in tr:
                                    for t in tr["tr"]:
                                        if isinstance(t, dict) and "l" in t:
                                            i_data = t["l"].get("i", [])
                                            # i 可能是列表或字符串
                                            if isinstance(i_data, list):
                                                for item in i_data:
                                                    if isinstance(item, str):
                                                        # 去掉HTML标签
                                                        clean = re.sub(r'<[^>]+>', '', item)
                                                        if clean:
                                                            definitions.append(clean)
                                            elif isinstance(i_data, str):
                                                clean = re.sub(r'<[^>]+>', '', i_data)
                                                if clean:
                                                    definitions.append(clean)
                            
                            if definitions:
                                result["definition_cn"] = "；".join(definitions[:4])
                
                # 尝试获取英文释义
                if "ee" in data:
                    ee = data["ee"]
                    word_info = None
                    # ee["word"] 可能是列表或字典
                    if isinstance(ee.get("word"), list) and ee["word"]:
                        word_info = ee["word"][0]
                    elif isinstance(ee.get("word"), dict):
                        word_info = ee["word"]
                    
                    if word_info and "trs" in word_info:
                        trs = word_info["trs"]
                        en_defs = []
                        for tr in trs[:2]:
                            if isinstance(tr, dict) and "tr" in tr:
                                for t in tr["tr"]:
                                    if isinstance(t, dict) and "l" in t:
                                        i_data = t["l"].get("i", [])
                                        if isinstance(i_data, list):
                                            for item in i_data:
                                                if isinstance(item, str):
                                                    clean = re.sub(r'<[^>]+>', '', item)
                                                    if clean:
                                                        en_defs.append(clean)
                                        elif isinstance(i_data, str):
                                            clean = re.sub(r'<[^>]+>', '', i_data)
                                            if clean:
                                                en_defs.append(clean)
                        result["definition_en"] = "; ".join(en_defs[:2])
                
                # 如果有中文释义就返回
                logger.info(f"有道词典结果: definition_cn={result['definition_cn'][:50] if result['definition_cn'] else 'empty'}")
                if result["definition_cn"]:
                    return result
                    
    except Exception as e:
        logger.warning(f"有道词典查询失败 [{word}]: {e}")
        import traceback
        logger.warning(traceback.format_exc())
    
    return None


async def lookup_word_free(word: str) -> Optional[Dict]:
    """
    使用 Free Dictionary API 查询单词（纯英文）
    
    Returns:
        {
            "word": "example",
            "phonetic": "/ɪɡˈzæmpəl/",
            "pos": "noun",
            "definition_en": "a thing characteristic of its kind",
            "example": "This is an example."
        }
    """
    url = f"{DICT_APIS['free_dictionary']}{word.lower()}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                if not data or not isinstance(data, list):
                    return None
                
                entry = data[0]
                result = {
                    "word": entry.get("word", word),
                    "phonetic": "",
                    "pos": "",
                    "definition_en": "",
                    "example": ""
                }
                
                # 获取音标
                if entry.get("phonetic"):
                    result["phonetic"] = entry["phonetic"]
                elif entry.get("phonetics"):
                    for p in entry["phonetics"]:
                        if p.get("text"):
                            result["phonetic"] = p["text"]
                            break
                
                # 获取词性和定义
                if entry.get("meanings"):
                    meaning = entry["meanings"][0]
                    result["pos"] = meaning.get("partOfSpeech", "")
                    
                    if meaning.get("definitions"):
                        defn = meaning["definitions"][0]
                        result["definition_en"] = defn.get("definition", "")
                        result["example"] = defn.get("example", "")
                
                return result
                
    except Exception as e:
        logger.warning(f"Free Dictionary查询失败 [{word}]: {e}")
        return None


async def lookup_word(word: str, lang: str = "en") -> Optional[Dict]:
    """
    查询单词解释（优先中文释义）
    
    1. 先尝试有道词典（中英双语）
    2. 失败则用 Free Dictionary（纯英文）
    """
    if lang != "en":
        return None
    
    # 优先使用有道词典（有中文释义）
    result = await lookup_word_youdao(word)
    if result and result.get("definition_cn"):
        return result
    
    # 备用：Free Dictionary（纯英文）
    result = await lookup_word_free(word)
    if result:
        return result
    
    return None


def extract_difficult_words(sentence: str, lang: str = "en") -> List[str]:
    """
    从句子中提取可能的难点单词
    
    策略：
    1. 长词（>8字符）
    2. 低频词（可扩展为词频表）
    3. 专业术语（可扩展为术语库）
    """
    words = []
    
    if lang == "en":
        # 提取英文单词
        raw_words = re.findall(r'\b[a-zA-Z]+\b', sentence)
        
        # 简单策略：长词可能是难点
        for w in raw_words:
            if len(w) > 7 and w.lower() not in COMMON_WORDS:
                words.append(w.lower())
    
    return list(set(words))[:5]  # 最多5个难点词


# 常见词列表（用于过滤）
COMMON_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
    "something", "because", "through", "between", "different", "important", "another",
    "however", "although", "therefore", "together", "anything", "everything",
    "everyone", "someone", "nothing", "something", "anything"
}


async def annotate_sentence(sentence: str, lang: str = "en") -> Dict:
    """
    标注句子中的难点单词
    
    Returns:
        {
            "sentence": "original sentence",
            "words": [
                {
                    "word": "example",
                    "start": 10,
                    "end": 17,
                    "data": {
                        "phonetic": "/ɪɡˈzæmpəl/",
                        "pos": "noun",
                        "definition": "a thing characteristic of its kind",
                        "example": "This is an example."
                    }
                }
            ]
        }
    """
    result = {
        "sentence": sentence,
        "words": []
    }
    
    if lang != "en":
        return result
    
    # 提取难点词
    difficult_words = extract_difficult_words(sentence, lang)
    
    for word in difficult_words:
        # 查找单词在句子中的位置
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        match = pattern.search(sentence)
        
        if match:
            # 查询单词解释
            word_data = await lookup_word(word, lang)
            
            if word_data and (word_data.get("definition_cn") or word_data.get("definition_en")):
                result["words"].append({
                    "word": word,
                    "start": match.start(),
                    "end": match.end(),
                    "data": word_data
                })
    
    return result


def render_annotated_sentence(sentence: str, words_data: List[Dict]) -> str:
    """
    渲染带标注的句子HTML
    
    将难点单词包装成可点击的span标签
    """
    if not words_data:
        return sentence
    
    # 按位置排序，从后往前替换
    sorted_words = sorted(words_data, key=lambda x: x["start"], reverse=True)
    
    result = sentence
    for w in sorted_words:
        word = w["word"]
        data = w.get("data", {})
        
        # 构建tooltip数据
        tooltip = {
            "word": data.get("word", word),
            "phonetic": data.get("phonetic", ""),
            "pos": data.get("pos", ""),
            "definition_cn": data.get("definition_cn", ""),
            "definition_en": data.get("definition_en", ""),
            "example": data.get("example", "")
        }
        
        # 创建带标注的span
        span = f'<span class="word-tip" data-tip="{json.dumps(tooltip, ensure_ascii=False)}">{word}</span>'
        
        # 替换（保持原大小写）
        original = sentence[w["start"]:w["end"]]
        result = result[:w["start"]] + span + result[w["end"]:]
    
    return result