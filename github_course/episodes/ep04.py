from kit import browser, gh_top, repo_tabs, summary_scene, title_scene

NUM = 4
TITLE = "提交 Commit 与历史记录"

CSS = """
.cmcard { width:1100px; margin:10px auto 0; background:#fff; border-radius:24px; padding:36px 44px; box-shadow:0 14px 40px rgba(31,35,40,.10); }
.cmcard .top { display:flex; align-items:center; gap:22px; font-size:36px; font-weight:800; }
.cmcard .meta { display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:30px; }
.cmcard .meta div { background:#f6f8fa; border-radius:16px; padding:18px 24px; font-size:28px; }
.cmcard .meta b { display:block; font-size:24px; color:var(--muted); margin-bottom:6px; }
.sha { font-family:"JetBrains Mono"; background:#eef1f4; border-radius:8px; padding:2px 12px; }

.fileview .fhead { display:flex; align-items:center; gap:12px; padding:12px 18px; background:#f6f8fa; border:1px solid #d0d7de; border-radius:10px 10px 0 0; font-size:20px; }
.fileview .fhead .ic { margin-left:auto; display:flex; gap:10px; }
.fileview .fbody { border:1px solid #d0d7de; border-top:0; border-radius:0 0 10px 10px; padding:20px 26px; font-size:22px; line-height:1.6; min-height:220px; }
.icbtn { width:44px; height:38px; border:1px solid #d0d7de; border-radius:8px; display:grid; place-items:center; background:#fff; font-size:20px; }

.editor { border:1px solid #d0d7de; border-radius:10px; overflow:hidden; }
.editor .etabs { display:flex; background:#f6f8fa; border-bottom:1px solid #d0d7de; font-size:20px; }
.editor .etabs span { padding:10px 20px; } .editor .etabs span.act { background:#fff; font-weight:700; border-right:1px solid #d0d7de; }
.editor .code { font:22px/1.7 "JetBrains Mono","Source Han Sans SC"; padding:14px 0; }
.editor .code div { display:flex; } .editor .code i { width:60px; text-align:right; padding-right:18px; color:#8c959f; font-style:normal; }
.editor .code div.new { background:#dafbe1; }

.modal-bg { position:absolute; inset:0; background:rgba(31,35,40,.45); display:flex; align-items:center; justify-content:center; }
.modal { width:900px; background:#fff; border-radius:14px; box-shadow:0 20px 60px rgba(0,0,0,.3); font-size:21px; }
.modal .mh { padding:16px 24px; border-bottom:1px solid #d0d7de; font-size:24px; font-weight:700; }
.modal .mb { padding:20px 24px; }
.modal .mf { padding:14px 24px; border-top:1px solid #d0d7de; display:flex; justify-content:flex-end; gap:12px; }

.msgs { display:flex; gap:40px; }
.msgs .card { flex:1; }
.msgs .m { font:600 30px "JetBrains Mono","Source Han Sans SC"; padding:14px 20px; border-radius:12px; margin-top:14px; }
.msgs .bad .m { background:var(--red-soft); color:var(--red); text-decoration:line-through; }
.msgs .good .m { background:var(--green-soft); color:var(--green); }

.clist .day { font-size:20px; color:#59636e; padding:10px 0; }
.clist .ci { display:flex; align-items:center; gap:14px; border:1px solid #d0d7de; border-top:0; padding:14px 18px; font-size:21px; background:#fff; }
.clist .ci:first-of-type { border-top:1px solid #d0d7de; border-radius:10px 10px 0 0; }
.clist .ci:last-child { border-radius:0 0 10px 10px; }
.clist .ci .who { color:#59636e; font-size:18px; display:block; }
.clist .ci .r { margin-left:auto; display:flex; gap:10px; align-items:center; }
"""

S_CONCEPT = """
<h2 class="head" data-s="1">什么是一次“提交”？<small>Commit = 一次存档 + 一句说明</small></h2>
<div class="cmcard" data-s="1">
  <div class="top"><div class="gh-avatar" style="width:60px;height:60px"></div>添加注册账号的学习笔记</div>
  <div class="meta">
    <div data-s="2"><b>👤 谁改的</b>xiaoming-dev</div>
    <div data-s="2"><b>🕘 什么时候</b>2026 年 9 月 28 日 10:15</div>
    <div data-s="3"><b>📝 改了什么</b>README.md　<span style="color:var(--green)">+3</span> <span style="color:var(--red)">−0</span></div>
    <div data-s="4"><b>🔖 存档编号</b><span class="sha">a1b2c3d</span></div>
  </div>
</div>"""

REPO_BODY = """
<div class="gh-body">
  <div class="gh-title">my-notes <span class="gh-pill">Public</span></div>
  <div class="gh-toolbar"><span class="gh-btn">⑂ main ▾</span><span class="gh-btn" style="margin-left:auto" id="addfile">Add file ▾</span><span class="gh-btn green">&lt;&gt; Code ▾</span></div>
  <div class="gh-box">
    <div class="head"><div class="gh-avatar" style="width:30px;height:30px"></div><b>xiaoming-dev</b> Initial commit<span class="count" id="ccount">🕘 1 Commit</span></div>
    <div class="gh-row" id="readme-row"><i class="ico-file"></i>README.md<span class="msg">Initial commit</span><span class="when">now</span></div>
  </div>
</div>"""

S_OPEN = browser("https://github.com/xiaoming-dev/my-notes", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + REPO_BODY,
                 style="width:1600px;margin:-20px auto 0")

S_FILE = browser("https://github.com/xiaoming-dev/my-notes/blob/main/README.md", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + """
<div class="gh-body fileview">
  <div style="font-size:22px;margin-bottom:14px"><b>my-notes</b> / README.md</div>
  <div class="fhead"><span class="gh-btn" style="height:34px">Preview</span><span>Code</span><span style="color:#59636e">2 lines · 25 Bytes</span>
    <div class="ic"><span class="gh-btn" style="height:38px">Raw</span><span class="icbtn">⧉</span><span class="icbtn" id="pencil">✏️</span><span class="gh-btn" id="fhist" style="height:38px">🕘 History</span></div></div>
  <div class="fbody"><div style="font-size:34px;font-weight:700;border-bottom:1px solid #d0d7de;padding-bottom:8px;margin-bottom:10px">my-notes</div>我的学习笔记</div>
</div>""", style="width:1600px;margin:-20px auto 0")

EDITOR = """
<div class="gh-body">
  <div style="display:flex;align-items:center;gap:14px;font-size:22px;margin-bottom:14px"><b>my-notes</b> / <span class="inp" style="height:38px;width:220px">README.md</span> in <span class="gh-pill">main</span>
    <span style="margin-left:auto" class="gh-btn">Cancel changes</span><span class="gh-btn green" id="commit-btn">Commit changes...</span></div>
  <div class="editor"><div class="etabs"><span class="act">Edit</span><span>Preview</span></div>
    <div class="code">
      <div><i>1</i># my-notes</div>
      <div class="new"><i>2</i>我的学习笔记（每天更新）</div>
      <div><i>3</i></div>
      <div class="new" data-s="3"><i>4</i><span class="type" data-s="3" style="--n:9">## 今天学了什么</span></div>
      <div class="new" data-s="3"><i>5</i><span class="type" data-s="3" style="--n:11">- 注册了 GitHub 账号</span></div>
      <div class="new" data-s="3"><i>6</i><span class="type" data-s="3" style="--n:10">- 创建了第一个仓库</span></div>
    </div></div>
</div>"""

S_EDIT = browser("https://github.com/xiaoming-dev/my-notes/edit/main/README.md", gh_top("xiaoming-dev / <b>my-notes</b>") + EDITOR,
                 style="width:1600px;margin:-20px auto 0")

S_DIALOG = """<div style="position:relative;margin:-20px auto 0;width:1600px">""" + browser(
    "https://github.com/xiaoming-dev/my-notes/edit/main/README.md", gh_top("xiaoming-dev / <b>my-notes</b>") + EDITOR.replace(' class="type" data-s="3"', '').replace(' data-s="3"', '')) + """
<div class="modal-bg" data-s="1" style="border-radius:18px"><div class="modal">
  <div class="mh">Commit changes</div>
  <div class="mb">
    <div class="fld" id="d-msg"><label>Commit message</label><div class="inp focus"><span class="type" data-s="2" style="--n:12">记录今天的学习内容</span></div></div>
    <div class="fld" id="d-desc"><label>Extended description</label><div class="inp area ph">Add an optional extended description...</div></div>
    <div id="d-radio"><div class="opt"><div class="r on2"></div><div>Commit directly to the <span class="sha">main</span> branch</div></div>
    <div class="opt"><div class="r"></div><div>Create a <b>new branch</b> for this commit and start a pull request</div></div></div>
  </div>
  <div class="mf"><span class="gh-btn">Cancel</span><span class="gh-btn green" id="d-go">Commit changes</span></div>
</div></div></div>"""

S_MSG = """
<h2 class="head" data-s="1">怎样写好提交说明？<small>一句话，说清楚“改了什么”</small></h2>
<div class="msgs">
  <div class="card bad" data-s="2"><h3>❌ 不好的写法</h3>
    <div class="m">update</div><div class="m">改了一下</div><div class="m">111</div></div>
  <div class="card good" data-s="3"><h3>✅ 好的写法</h3>
    <div class="m">添加注册账号的学习笔记</div><div class="m">修正 README 中的错别字</div><div class="m">新增第二章：分支</div></div>
</div>
<div class="tip" data-s="4" style="margin-top:30px"><span class="emoji">💡</span><div>想象一个月后的自己：只看这句话，能不能知道当时改了什么？</div></div>"""

S_ADD = browser("https://github.com/xiaoming-dev/my-notes", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + REPO_BODY.replace(
    "Initial commit<span", "记录今天的学习内容<span").replace("1 Commit", "2 Commits") + """
<div class="menu" data-s="1" style="right:160px;top:318px"><div class="act" id="m-create">＋ Create new file</div><div id="m-upload">⤒ Upload files</div></div>""",
    style="width:1600px;margin:-20px auto 0;position:relative")

S_HIST = browser("https://github.com/xiaoming-dev/my-notes/commits/main", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + """
<div class="gh-body clist">
  <div style="font-size:30px;font-weight:700;margin-bottom:10px">Commits</div>
  <div class="day">⊙ Commits on Sep 28, 2026</div>
  <div class="ci" id="c-top"><div><b>添加第一天的笔记</b><span class="who">xiaoming-dev committed 2 minutes ago</span></div><div class="r"><span class="sha" id="c-sha">9f3e1ab</span><span class="icbtn">⧉</span><span class="icbtn" id="c-browse">&lt;&gt;</span></div></div>
  <div class="ci" id="c-2"><div><b>记录今天的学习内容</b><span class="who">xiaoming-dev committed 10 minutes ago</span></div><div class="r"><span class="sha">a1b2c3d</span><span class="icbtn">⧉</span><span class="icbtn">&lt;&gt;</span></div></div>
  <div class="ci"><div><b>Initial commit</b><span class="who">xiaoming-dev committed 1 hour ago</span></div><div class="r"><span class="sha">5c7d0e2</span><span class="icbtn">⧉</span><span class="icbtn">&lt;&gt;</span></div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_DIFF = browser("https://github.com/xiaoming-dev/my-notes/commit/a1b2c3d", gh_top("xiaoming-dev / <b>my-notes</b>") + """
<div class="gh-body">
  <div style="font-size:28px;font-weight:700">记录今天的学习内容</div>
  <div style="font-size:19px;color:#59636e;margin:6px 0 16px">xiaoming-dev committed 10 minutes ago · commit <span class="sha">a1b2c3d</span> · Showing 1 changed file with <b style="color:#1a7f37">3 additions</b> and <b style="color:#cf222e">1 deletion</b></div>
  <div class="gh-box diff">
    <div class="fh">README.md</div>
    <div class="l hunk"><i></i> @@ -1,2 +1,6 @@</div>
    <div class="l"><i>1</i> # my-notes</div>
    <div class="l del" id="dl"><i>2</i>-我的学习笔记</div>
    <div class="l add" id="al"><i>2</i>+我的学习笔记（每天更新）</div>
    <div class="l"><i>3</i> </div>
    <div class="l add"><i>4</i>+## 今天学了什么</div>
    <div class="l add"><i>5</i>+- 注册了 GitHub 账号</div>
  </div>
</div>""", style="width:1600px;margin:-20px auto 0")

SCENES = [
    title_scene(NUM, "在网页上完成你的第一次“存档”",
                ["欢迎回来！上一集我们创建了第一个仓库。"],
                ["这一集，我们在网页上修改文件，完成第一次提交，再学会查看历史记录。"]),
    dict(html=S_CONCEPT, steps=[
        dict(say=["先回顾一下：提交，英文叫 Commit，就是给文件存一次档，并且附上一句说明。"]),
        dict(say=["每一次提交，GitHub 都会记下是谁改的、什么时候改的；"]),
        dict(say=["还会记下具体改了哪些文件、哪几行；"]),
        dict(say=["每次提交还有一个独一无二的编号，就像存档的编号，以后可以凭它找到这一次的存档。"]),
    ]),
    dict(html=S_OPEN, steps=[
        dict(say=["我们来动手修改 README 文件。先在仓库首页，点击文件名 README 点 md。"],
             js="cursor('#readme-row', {fx:.06, click:true})"),
    ]),
    dict(html=S_FILE, steps=[
        dict(say=["现在打开了这个文件，可以看到它的内容。"]),
        dict(say=["文件右上方有一支铅笔图标，意思是编辑这个文件。点击它。"],
             js="hl('#pencil', {label:'编辑文件', side:'below', pad:6}); cursor('#pencil', {click:true, delay:600})"),
    ]),
    dict(html=S_EDIT, steps=[
        dict(say=["页面变成了编辑器，可以像写文档一样直接修改。"]),
        dict(say=["上方的 Edit 是编辑，Preview 是预览效果。"], js="hl('.etabs', {pad:2})"),
        dict(say=["我们把第二行改成：我的学习笔记，每天更新。", "再在最后加上几行：今天学了什么，注册了 GitHub 账号，创建了第一个仓库。"], js="hl(null)"),
        dict(say=["写完以后，点击右上角绿色的 Commit changes 按钮，准备提交。"],
             js="cursor('#commit-btn', {click:true})"),
    ]),
    dict(html=S_DIALOG, steps=[
        dict(say=["这时会弹出一个提交窗口。"]),
        dict(say=["第一栏 Commit message 是提交说明，我们写上：记录今天的学习内容。"], js="hl('#d-msg', {pad:6})"),
        dict(say=["第二栏是详细描述，可以不填。"], js="hl('#d-desc', {pad:6})"),
        dict(say=["下面有两个选项。第一个是直接提交到 main 主分支，第二个是新建一个分支。",
                  "分支我们后面再学，现在选第一个就好。"], js="hl('#d-radio', {pad:6})"),
        dict(say=["最后点击 Commit changes。这样，你的第一次提交就完成了！"],
             js="hl(null); cursor('#d-go', {click:true})"),
    ]),
    dict(html=S_MSG, steps=[
        dict(say=["说到提交说明，很多新手会随手写一个 update，或者改了一下。"]),
        dict(say=["这样的说明，过几天连自己都看不懂改了什么。"]),
        dict(say=["好的写法是：一句话说清楚改了什么。比如：添加注册账号的学习笔记，修正 README 中的错别字。"]),
        dict(say=["有个小窍门：想象一个月后的自己，只看这句话，能不能知道当时改了什么。"]),
    ]),
    dict(html=S_ADD, steps=[
        dict(say=["除了修改已有的文件，还可以新建和上传文件。",
                  "在仓库首页点击 Add file，会看到两个选项。"]),
        dict(say=["Create new file 是新建文件。文件名里加一个斜杠，比如 notes 斜杠 day1 点 md，就会自动创建一个 notes 文件夹。"],
             js="hl('#m-create', {pad:2})"),
        dict(say=["Upload files 是上传文件，把电脑里的文件直接拖进网页就行。",
                  "不管是新建还是上传，最后都要写一句说明，完成一次提交。"], js="hl('#m-upload', {pad:2})"),
    ]),
    dict(html=S_OPEN.replace("Initial commit<span", "添加第一天的笔记<span").replace("1 Commit", "3 Commits"), steps=[
        dict(say=["做了几次提交之后，怎么查看历史记录呢？",
                  "仓库首页文件列表的右上角，显示着提交的次数，点击它。"],
             js="hl('#ccount', {label:'点这里看历史', side:'above', pad:6}); cursor('#ccount', {click:true, delay:900})"),
    ]),
    dict(html=S_HIST, steps=[
        dict(say=["这里按时间顺序列出了所有的提交，最新的在最上面。"]),
        dict(say=["每一条都能看到提交说明、谁提交的、什么时候提交的。"], js="hl('#c-top', {pad:4})"),
        dict(say=["右边这串字母和数字，就是提交的编号。"], js="hl('#c-sha', {label:'提交编号', side:'below', pad:6})"),
        dict(say=["点最右边的尖括号按钮，还能看到仓库在那个时间点的完整样子，就像读取一个旧存档。"],
             js="hl('#c-browse', {label:'查看当时的样子', side:'below', pad:6})"),
        dict(say=["我们点开“记录今天的学习内容”这一条，看看具体改了什么。"],
             js="hl(null); cursor('#c-2', {fx:.1, click:true})"),
    ]),
    dict(html=S_DIFF, steps=[
        dict(say=["这个页面展示了这次提交的所有改动，叫做差异对比，英文是 diff。"]),
        dict(say=["红色、带减号的行，是删掉的内容；"], js="hl('#dl', {label:'删掉的行', side:'right', pad:2})"),
        dict(say=["绿色、带加号的行，是新加的内容。"], js="hl('#al', {label:'新加的行', side:'right', pad:2})"),
        dict(say=["修改一行，在这里就会显示成删掉旧的一行、再加上新的一行。",
                  "有了它，每一次改了什么，都一目了然。"], js="hl(null)"),
    ]),
    summary_scene(NUM, [
        "打开文件 → 点铅笔图标编辑",
        "Commit changes：写一句清楚的提交说明",
        "Add file：新建或上传文件",
        "点提交次数看历史，绿加红减看改动",
    ], [
        ["第一，打开文件，点击铅笔图标就能在网页上编辑。"],
        ["第二，点击 Commit changes 提交，并写一句清楚的说明。"],
        ["第三，用 Add file 可以新建或上传文件。"],
        ["第四，点击提交次数查看历史，绿色是新增，红色是删除。"],
    ], ["网页上的操作就学到这里。下一集，我们把仓库搬到自己的电脑上。我们下集见！"]),
]
