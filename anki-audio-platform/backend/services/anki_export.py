"""
genanki 封装：生成 Anki .apkg 牌组文件

核心设计：
- 卡片字段只有 `page`（指向云端渲染页面的 URL）
- 正面/背面模板使用 iframe 加载服务端页面（side=0/side=1）
- 样式 JS 实现 fit_win、isMobile、prefer API 等功能
"""
import os
import io
import random
import logging
import genanki

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def _get_model(base_url: str) -> genanki.Model:
    """创建 Anki 笔记类型（Note Type）"""
    # 固定的 model_id（同一个 Note Type 要保证 ID 一致）
    model_id = 1607392319

    # Anki 模板不需要完整 HTML 结构
    # {{page}} 是字段引用，会被替换成实际 URL
    # CSS 放在 Styling 区域，JS 放在模板中
    front_template = f"""<iframe frameborder="0" id="frame" scrolling="yes" src="{{{{page}}}}&side=0" style="width:100%;height:100vh;border:none;"></iframe>
<script>
(function(){{var f=document.getElementById('frame');var resize=function(){{f.style.height=window.innerHeight+'px';f.style.width=window.innerWidth+'px';}};resize();window.addEventListener('resize',resize);}})();
</script>"""

    back_template = f"""<iframe frameborder="0" id="frame" scrolling="yes" src="{{{{page}}}}&side=1" style="width:100%;height:100vh;border:none;"></iframe>
<script>
(function(){{var f=document.getElementById('frame');var resize=function(){{f.style.height=window.innerHeight+'px';f.style.width=window.innerWidth+'px';}};resize();window.addEventListener('resize',resize);}})();
</script>"""

    css = """
.card {
  margin: 0;
  padding: 0;
  background-color: #fff;
}
iframe {
  display: block;
}
"""

    return genanki.Model(
        model_id,
        "AnkiAudio Cloud",
        fields=[
            {"name": "page"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": front_template,
                "afmt": back_template,
            }
        ],
        css=css,
    )


def generate_apkg(
    deck_id: str,
    deck_title: str,
    segments: list[dict],
    base_url: str = None,
) -> bytes:
    """
    生成 Anki .apkg 文件。

    Args:
        deck_id: 牌组唯一 ID
        deck_title: 牌组名称（在 Anki 中显示）
        segments: 片段列表 [{id, seg_index, sentence, ...}, ...]
        base_url: 服务器基础 URL（覆盖环境变量）

    Returns:
        .apkg 文件的二进制内容
    """
    _base_url = base_url or BASE_URL
    model = _get_model(_base_url)

    # 固定 deck_id 对应固定的 genanki deck id（取 hash 的正整数部分）
    genanki_deck_id = abs(hash(deck_id)) % (10 ** 10)
    deck = genanki.Deck(genanki_deck_id, f"AnkiAudio::{deck_title}")

    for seg in segments:
        card_url = f"{_base_url}/card/{seg['id']}?type=ting&seg_index={seg['seg_index']}"
        note = genanki.Note(
            model=model,
            fields=[card_url],
        )
        deck.add_note(note)

    # 写入临时文件再读回
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        genanki.Package(deck).write_to_file(tmp_path)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass