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

    front_template = """<html>
 <body>
  <iframe frameborder="0" id="frame" scrolling="yes" src="{{ page }}&side=0" class="frameHide">
  </iframe>
  <div style="display:none">{{ page }}</div>
  <script>window.onresize=fit_win;document.getElementById('frame').onload=fit_win;</script>
 </body>
</html>"""

    back_template = """<html>
 <body>
  <iframe frameborder="0" id="frame" scrolling="yes" src="{{ page }}&side=1" class="frameHide">
  </iframe>
  <div style="display:none">{{ page }}</div>
  <script>window.onresize=fit_win;document.getElementById('frame').onload=fit_win;</script>
 </body>
</html>"""

    css = f"""
.card{{margin:0}}
#content{{margin:0}}
@keyframes cssAnimation{{from{{opacity:0}}to{{opacity:1}}}}
.frameHide{{opacity:0}}
.frameShow{{animation:cssAnimation 2s}}
.frameM{{margin-left:-15px;margin-top:-15px}}
.frameD{{position:fixed;margin-left:-20px;margin-top:-20px}}

<script>
function getViewport(){{
  let viewPortWidth,viewPortHeight;
  if(typeof window.innerWidth!='undefined'){{
    viewPortWidth=window.innerWidth;viewPortHeight=window.innerHeight;
  }}else if(typeof document.documentElement!='undefined'&&document.documentElement.clientWidth!==0){{
    viewPortWidth=document.documentElement.clientWidth;viewPortHeight=document.documentElement.clientHeight;
  }}else{{
    viewPortWidth=document.getElementsByTagName('body')[0].clientWidth;
    viewPortHeight=document.getElementsByTagName('body')[0].clientHeight;
  }}
  return[viewPortWidth,viewPortHeight];
}}
function isMobile(){{
  let check=false;
  (function(a){{if(/(android|ipad|playbook|silk|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-/i.test(a.substr(0,4)))check=true;}})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
}}
function fit_win(){{
  let frame=document.getElementById('frame');
  frame.width=getViewport()[0];frame.height=getViewport()[1];showFrame(1000);
}}
function updateIframeClass(){{
  let frame=document.getElementById("frame");
  if(!frame){{return;}}
  if(isMobile()){{frame.classList.add("frameM");}}else{{frame.classList.add("frameD");}}
}}
function showFrame(duration){{
  let frame=document.getElementById("frame");
  frame.classList.add("frameShow");frame.classList.remove("frameHide");
}}
function update_per_pref(){{
  function _update_config(rsp_obj){{
    let card=document.getElementsByClassName('card')[0];
    let content=document.getElementById("content");
    let dark_color="#303030";let white_color="#ffffff";
    let bg_color=rsp_obj['dark_mode']===true?dark_color:white_color;
    document.body.style.backgroundColor=bg_color;
    if(card){{card.style.backgroundColor=bg_color}}
    if(content){{content.style.backgroundColor=bg_color}}
  }}
  let xhr=new XMLHttpRequest();
  let api_pref="{base_url}/deck/prefer/default/";
  xhr.onreadystatechange=function(evt){{
    if(xhr.readyState===4&&xhr.status===200){{
      let rsp_json=JSON.parse(xhr.responseText);_update_config(rsp_json)
    }}
  }};
  xhr.open('GET',api_pref,false);xhr.send()
}}
function onload(){{update_per_pref();updateIframeClass();}}
onload();
</script>
""".format(base_url=base_url)

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
