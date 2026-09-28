from kit import EPISODES, browser, gh_top, repo_tabs, summary_scene, title_scene

NUM = 10
TITLE = "实用技巧与总结"

CSS = """
.mdgrid { display:grid; grid-template-columns:1fr 1fr; gap:0; background:#fff; border-radius:22px; overflow:hidden; box-shadow:0 12px 36px rgba(31,35,40,.10); }
.mdgrid .hd { padding:14px 28px; font-size:26px; font-weight:800; background:#f6f8fa; border-bottom:1px solid #d0d7de; }
.mdgrid .src, .mdgrid .out { padding:12px 28px; border-bottom:1px solid #eef1f4; min-height:70px; display:flex; align-items:center; }
.mdgrid .src { font:27px "JetBrains Mono","Source Han Sans SC"; color:#57606a; border-right:1px solid #d0d7de; }
.mdgrid .src b { color:#cf222e; font-weight:700; }
.mdgrid .out { font-size:28px; }
.mdgrid .out a { color:#0969da; text-decoration:underline; }
.mdgrid .out code { background:#eef1f4; padding:2px 10px; border-radius:6px; font-size:24px; }

.pages { display:flex; height:560px; }
.pages .nav { width:340px; padding:22px; border-right:1px solid #d0d7de; font-size:20px; }
.pages .nav div { padding:7px 12px; border-radius:8px; }
.pages .nav div.act { background:#f6f8fa; font-weight:700; box-shadow:inset 3px 0 0 #fd8c73; }
.pages .body { flex:1; padding:26px 36px; font-size:21px; }
.pages h3 { font-size:30px; margin:0 0 16px; padding-bottom:10px; border-bottom:1px solid #d0d7de; }
.live { background:#dafbe1; border:1px solid #4ac26b; border-radius:10px; padding:14px 18px; margin-bottom:20px; }
.live a { color:#0969da; font-family:"JetBrains Mono"; }

.special { display:flex; gap:36px; }
.special .card { flex:1; }
.special h3 { font-size:34px; }
.special .u { font:700 28px "JetBrains Mono"; color:var(--green); background:var(--green-soft); padding:8px 16px; border-radius:10px; display:inline-block; margin:10px 0 14px; }
.special p { font-size:28px; }

.safe { display:flex; gap:36px; align-items:flex-start; }
.safe .lcol { flex:1; display:flex; flex-direction:column; gap:18px; }
.safe .tip { font-size:29px; padding:18px 26px; }
.gi { width:520px; flex:none; }

.review { display:grid; grid-template-columns:repeat(5,1fr); gap:20px; }
.review .n { background:#fff; border-radius:18px; padding:20px; border:3px solid #e1e6eb; min-height:150px; transition:opacity .5s, transform .65s cubic-bezier(.2,.8,.2,1), background .6s, border-color .6s; }
.review .n.done { border-color:var(--green); background:var(--green-soft); }
.review .n small { color:var(--green); font-weight:800; font-size:24px; }
.review .n div { font-size:28px; font-weight:800; margin-top:6px; line-height:1.35; }

.next3 { display:grid; grid-template-columns:repeat(3,1fr); gap:30px; }
.next3 .card { padding:34px; }
.next3 .emoji { font-size:74px; }
.next3 h3 { font-size:36px; margin:14px 0; }
.next3 .u { font:600 24px "JetBrains Mono"; color:var(--blue); margin-bottom:12px; }
.next3 p { font-size:27px; }
"""

S_MD = """
<h2 class="head" data-s="1">Markdown：用简单的符号排版<small>README.md 的 .md，就是 Markdown 格式</small></h2>
<div class="mdgrid">
  <div class="hd">你写的</div><div class="hd">显示的效果</div>
  <div class="src" data-s="2"><b>#</b>&nbsp;我的学习笔记</div><div class="out" data-s="2" style="font-size:40px;font-weight:800">我的学习笔记</div>
  <div class="src" data-s="3"><b>**</b>重点<b>**</b>&nbsp;内容</div><div class="out" data-s="3"><b>重点</b>&nbsp;内容</div>
  <div class="src" data-s="4"><b>-</b>&nbsp;第一项</div><div class="out" data-s="4">• 第一项</div>
  <div class="src" data-s="5"><b>[</b>GitHub<b>](</b>https://github.com<b>)</b></div><div class="out" data-s="5"><a>GitHub</a></div>
  <div class="src" data-s="6"><b>`</b>git push<b>`</b></div><div class="out" data-s="6"><code>git push</code></div>
</div>"""

S_PAGES = browser("https://github.com/xiaoming-dev/my-notes/settings/pages", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs("Settings") + """
<div class="pages">
  <div class="nav"><div>General</div><div>Collaborators</div><div>Branches</div><div>Actions</div><div class="act" id="pg-nav">Pages</div><div>Secrets and variables</div></div>
  <div class="body"><h3>GitHub Pages</h3>
    <div class="live" data-s="5">✅ Your site is live at <a>https://xiaoming-dev.github.io/my-notes/</a></div>
    <div class="fld" id="pg-src"><label>Source</label><span class="gh-btn">Deploy from a branch ▾</span></div>
    <div class="fld" id="pg-br"><label>Branch</label><div style="display:flex;gap:12px"><span class="gh-btn">⑂ main ▾</span><span class="gh-btn">📁 / (root) ▾</span><span class="gh-btn" id="pg-save">Save</span></div></div>
  </div></div>""", style="width:1600px;margin:-20px auto 0")

S_SPECIAL = """
<h2 class="head" data-s="1">两个特殊的仓库名</h2>
<div class="special">
  <div class="card" data-s="2"><h3>🌐 个人网站</h3><div class="u">xiaoming-dev.github.io</div>
    <p>仓库名写成“<b>用户名.github.io</b>”，开启 Pages 后，网址就是 https://用户名.github.io，非常适合做个人主页。</p></div>
  <div class="card" data-s="3"><h3>👤 个人主页介绍</h3><div class="u">xiaoming-dev</div>
    <p>仓库名和<b>用户名一模一样</b>，它的 README 会显示在你的 GitHub 个人主页最上方，可以写一段自我介绍。</p></div>
</div>"""

S_SAFE = """
<h2 class="head" data-s="1">安全第一：这些东西千万别上传</h2>
<div class="safe">
  <div class="lcol">
    <div class="tip bad" data-s="2"><span class="emoji">🔑</span><div>密码、API 密钥、令牌，以及存放它们的配置文件（如 <b>.env</b>）</div></div>
    <div class="tip bad" data-s="2"><span class="emoji">🪪</span><div>身份证、手机号、住址等个人隐私</div></div>
    <div class="tip" data-s="3"><span class="emoji">🙈</span><div>把不想上传的文件写进 <b>.gitignore</b>，Git 就会自动忽略它们</div></div>
    <div class="tip warn" data-s="4"><span class="emoji">🚨</span><div>不小心传上去了？删文件不够，历史里还有！<b>马上去对应网站作废并更换密钥</b></div></div>
  </div>
  <div class="gi" data-s="3">""" + browser(".gitignore", """<div class="diff" style="padding:10px 0;font-size:26px">
    <div class="l"><i>1</i> .env</div><div class="l"><i>2</i> *.log</div><div class="l"><i>3</i> node_modules/</div><div class="l"><i>4</i> 我的私人笔记/</div></div>""") + """</div>
</div>"""

def _review():
    cells = "".join(f'<div class="n" data-s="{2 if i < 4 else 3 if i < 6 else 4}"><small>第 {i + 1} 集</small><div>{t}</div></div>'
                    for i, t in enumerate(EPISODES))
    return f"""<h2 class="head" data-s="1">回顾：这十集我们学了什么</h2><div class="review">{cells}</div>"""

S_REVIEW = _review()

S_NEXT = """
<h2 class="head" data-s="1">接下来，可以这样继续学</h2>
<div class="next3">
  <div class="card" data-s="2"><div class="emoji">📘</div><h3>官方文档</h3><div class="u">docs.github.com</div><p>有简体中文版，遇到问题随时查</p></div>
  <div class="card" data-s="3"><div class="emoji">🎮</div><h3>互动练习</h3><div class="u">skills.github.com</div><p>GitHub 官方的动手课程，边做边学</p></div>
  <div class="card" data-s="4"><div class="emoji">🔁</div><h3>坚持使用</h3><div class="u">每天一次提交</div><p>用仓库记笔记、放作品，慢慢就熟练了</p></div>
</div>"""

SCENES = [
    title_scene(NUM, "Markdown、GitHub Pages 和安全习惯",
                ["欢迎来到最后一集！"],
                ["这一集，我们学习几个非常实用的技巧，最后一起回顾整套课程，并聊聊接下来可以怎么继续学。"]),
    dict(html=S_MD, steps=[
        dict(say=["你一定注意到了，README 文件的后缀是点 md。md 是 Markdown 的缩写，",
                  "它是一种用简单符号来排版的写法，GitHub 上到处都在用。我们来看几个最常用的。"]),
        dict(say=["一个井号加空格，表示标题。井号越多，标题越小。"]),
        dict(say=["两个星号包住文字，表示加粗。"]),
        dict(say=["减号加空格，表示列表的一项。"]),
        dict(say=["方括号里写文字，后面圆括号里写网址，就变成了一个链接。"]),
        dict(say=["用反引号包住的内容，会显示成代码的样子。",
                  "学会这几个，就足够写出一份漂亮的 README 了。"]),
    ]),
    dict(html=S_PAGES, steps=[
        dict(say=["第二个技巧：GitHub Pages。它能免费把你的仓库变成一个网站，任何人都能通过网址访问。"]),
        dict(say=["打开仓库的 Settings，在左边找到 Pages。"], js="hl('#pg-nav', {pad:2})"),
        dict(say=["Source 选择 Deploy from a branch，也就是从分支发布。"], js="hl('#pg-src', {pad:6})"),
        dict(say=["Branch 选择 main，文件夹选根目录，然后点击 Save 保存。"],
             js="hl('#pg-br', {pad:6}); cursor('#pg-save', {click:true, delay:1500})"),
        dict(say=["等上一两分钟，刷新页面，上方就会出现你的网址。",
                  "如果仓库里有 index 点 html 网页文件，就会显示这个网页；没有的话，会显示 README 的内容。"],
             js="hl('.live', {pad:4})"),
    ]),
    dict(html=S_SPECIAL, steps=[
        dict(say=["再告诉你两个特殊的仓库名。"]),
        dict(say=["第一个：把仓库命名为你的用户名，加上点 github 点 io。",
                  "开启 Pages 后，网址就是用户名点 github 点 io，非常适合做个人网站。"]),
        dict(say=["第二个：创建一个和你用户名一模一样的仓库。",
                  "它的 README 会显示在你的个人主页最上方，你可以在里面写一段自我介绍。"]),
    ]),
    dict(html=S_SAFE, steps=[
        dict(say=["第三个技巧，其实是一条安全提醒，非常重要。"]),
        dict(say=["密码、各种网站的密钥，还有身份证号、手机号这类个人隐私，千万不要上传到仓库里，尤其是公开仓库。"]),
        dict(say=["不想上传的文件，可以写进点 gitignore 文件里，Git 就会自动忽略它们，提交时不会带上。"]),
        dict(say=["万一不小心传上去了，只删掉文件是不够的，因为历史记录里还保留着。",
                  "正确的做法是：马上去对应的网站，把这个密钥作废，换一个新的。"]),
    ]),
    dict(html=S_REVIEW, steps=[
        dict(say=["好，最后我们一起回顾一下这十集的内容。"]),
        dict(say=["我们先认识了 GitHub，注册了账号，创建了仓库，在网页上完成了提交；"],
             js="document.querySelectorAll('.review .n').forEach((e,i)=>{ if(i<4) e.classList.add('done') })"),
        dict(say=["然后把仓库搬到电脑上，学会了提交、推送和拉取；"],
             js="document.querySelectorAll('.review .n').forEach((e,i)=>{ if(i<6) e.classList.add('done') })"),
        dict(say=["又学习了分支和 Pull Request，参与了开源，最后掌握了几个实用技巧。",
                  "恭喜你，已经走完了 GitHub 入门的全部路程！"],
             js="document.querySelectorAll('.review .n').forEach(e=>e.classList.add('done'))"),
    ]),
    dict(html=S_NEXT, steps=[
        dict(say=["接下来可以怎么继续学呢？给你三个建议。"]),
        dict(say=["第一，GitHub 官方文档，有简体中文版，遇到问题随时可以查。"]),
        dict(say=["第二，GitHub Skills，是官方的互动练习课程，跟着提示一步步动手，很适合巩固。"]),
        dict(say=["第三，也是最重要的：坚持使用。用仓库记笔记、放作品，每天提交一次，慢慢就熟练了。"]),
    ]),
    summary_scene(NUM, [
        "Markdown：用 # ** - 等符号排版",
        "GitHub Pages：免费把仓库变成网站",
        "密码密钥不上传，用 .gitignore 忽略",
        "坚持使用，从每天一次提交开始",
    ], [
        ["第一，Markdown 用井号、星号、减号这些简单符号来排版。"],
        ["第二，GitHub Pages 能免费把仓库变成一个网站。"],
        ["第三，密码和密钥千万不要上传，可以用 gitignore 来忽略。"],
        ["第四，坚持使用，从每天一次提交开始。"],
    ], ["《GitHub 零基础入门》到这里就全部结束了。感谢你的观看，祝你在 GitHub 上玩得开心，我们后会有期！"],
        next_text="感谢观看 · 祝你在 GitHub 上玩得开心！"),
]
