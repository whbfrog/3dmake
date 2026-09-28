from kit import browser, gh_top, summary_scene, title_scene

NUM = 9
TITLE = "参与开源"

CSS = """
.os { display:grid; grid-template-columns:repeat(3,1fr); gap:30px; }
.os .card { text-align:center; padding:36px 30px; }
.os .emoji { font-size:84px; display:block; margin-bottom:12px; }
.srch { display:flex; gap:26px; padding:24px 28px; }
.srch .fl { width:300px; font-size:20px; }
.srch .fl div { padding:8px 12px; border-radius:8px; }
.srch .fl div.act { background:#f6f8fa; font-weight:700; box-shadow:inset 3px 0 0 #fd8c73; }
.srch .res { flex:1; }
.res .r { border-bottom:1px solid #d0d7de; padding:16px 0; font-size:20px; }
.res .r b { color:#0969da; font-size:23px; }
.res .r p { margin:6px 0; color:#1f2328; }
.res .r .m { color:#59636e; font-size:18px; display:flex; gap:22px; }
.lbl { display:inline-block; border-radius:999px; padding:1px 12px; font-size:17px; font-weight:600; margin-left:8px; }
.lbl.gfi { background:#7057ff; color:#fff; } .lbl.bug { background:#d73a4a; color:#fff; } .lbl.q { background:#d876e3; color:#fff; } .lbl.doc { background:#0075ca; color:#fff; }
.rbtns { display:flex; gap:10px; margin-left:auto; }
.rbtns .gh-btn b { background:#eef1f4; border-radius:999px; padding:0 8px; font-size:17px; margin-left:4px; }
.meaning { display:grid; grid-template-columns:repeat(3,1fr); gap:26px; margin-top:30px; }
.meaning .card { padding:26px 30px; }
.meaning h3 { font-size:34px; }
.meaning p { font-size:27px; }
.issues .it { display:flex; align-items:center; gap:14px; padding:14px 18px; border-top:1px solid #d0d7de; font-size:21px; }
.issues .it:first-child { border-top:0; }
.issues .it .o { color:#1a7f37; font-size:22px; }
.issues .it small { display:block; color:#59636e; font-size:17px; }
.newissue { display:flex; gap:30px; }
.md-area { border:1px solid #d0d7de; border-radius:8px; min-height:220px; padding:12px 16px; font:20px/1.6 "JetBrains Mono","Source Han Sans SC"; white-space:pre-wrap; }
.fork-map { position:relative; height:620px; }
.fork-map .nd { position:absolute; width:440px; background:#fff; border-radius:24px; padding:24px 28px; box-shadow:0 10px 30px rgba(31,35,40,.10); border:4px solid #e1e6eb; text-align:center; }
.fork-map .nd .emoji { font-size:60px; } .fork-map .nd b { display:block; font-size:32px; margin:6px 0; } .fork-map .nd span { font:20px "JetBrains Mono"; color:var(--muted); }
.fork-map svg { position:absolute; inset:0; overflow:visible; }
.fork-map svg path { fill:none; stroke-width:8; stroke-linecap:round; stroke-dasharray:900; stroke-dashoffset:900; transition:stroke-dashoffset 1s ease, opacity .3s; }
.fork-map svg path.on { stroke-dashoffset:0; transform:none; }
.fork-map svg text { font:800 30px "Source Han Sans SC"; }
.etq { display:flex; flex-direction:column; gap:18px; }
.etq .tip { font-size:31px; padding:18px 30px; }
"""

S_OS = """
<h2 class="head" data-s="1">什么是开源？<small>源代码公开，任何人都可以查看、学习，甚至参与改进</small></h2>
<div class="os">
  <div class="card" data-s="2"><span class="emoji">👀</span><h3>看</h3><p>学习高手是怎么写代码的</p></div>
  <div class="card" data-s="3"><span class="emoji">🛠️</span><h3>用</h3><p>免费使用现成的工具和代码</p></div>
  <div class="card" data-s="4"><span class="emoji">🤝</span><h3>改</h3><p>发现问题、提出建议、贡献代码</p></div>
</div>"""

S_SEARCH = browser("https://github.com/search?q=markdown+editor", gh_top("<b>Search</b>") + """
<div class="srch">
  <div class="fl" id="s-filter"><div class="act">📦 Repositories</div><div>🔣 Code</div><div>⊙ Issues</div><div>👤 Users</div>
    <div style="margin-top:14px;font-weight:700">Languages</div><div>● JavaScript</div><div>● Python</div><div>● TypeScript</div></div>
  <div class="res"><div style="font-size:22px;font-weight:700;margin-bottom:6px">2.1k results</div>
    <div class="r" id="s-first"><b>open-org / awesome-editor</b><p>一个简单好用的 Markdown 编辑器</p><div class="m"><span>● TypeScript</span><span id="s-star">☆ 8.5k</span><span>Updated 2 hours ago</span></div></div>
    <div class="r"><b>writer-lab / md-notes</b><p>Take notes in Markdown, sync with Git.</p><div class="m"><span>● JavaScript</span><span>☆ 2.3k</span><span>Updated yesterday</span></div></div>
    <div class="r"><b>py-tools / mdview</b><p>Preview Markdown files in your terminal.</p><div class="m"><span>● Python</span><span>☆ 960</span><span>Updated 3 days ago</span></div></div>
  </div></div>""", style="width:1600px;margin:-20px auto 0")

REPO_HEAD = """<div class="gh-body" style="padding-bottom:10px"><div class="gh-title" style="margin-bottom:0">📦 open-org / awesome-editor <span class="gh-pill">Public</span>
  <div class="rbtns"><span class="gh-btn" id="b-watch">👁 Watch <b>120</b></span><span class="gh-btn" id="b-fork">⑂ Fork <b>1.2k</b></span><span class="gh-btn" id="b-star">☆ Star <b>8.5k</b></span></div></div></div>"""
TABS = """<div class="gh-tabs"><span class="{a}">&lt;&gt; Code</span><span class="{b}">⊙ Issues 42</span><span>Pull requests 7</span><span>Actions</span></div>"""

S_BTNS = browser("https://github.com/open-org/awesome-editor", gh_top("open-org / <b>awesome-editor</b>") + REPO_HEAD + TABS.format(a="act", b=""),
                 style="width:1600px;margin:-20px auto 0") + """
<div class="meaning">
  <div class="card" data-s="2"><h3>☆ Star 收藏</h3><p>相当于点赞 + 收藏。以后在 Your stars 里能找到它。</p></div>
  <div class="card" data-s="3"><h3>👁 Watch 关注</h3><p>项目有新动态时通知你。一般不用开，消息会很多。</p></div>
  <div class="card" data-s="4"><h3>⑂ Fork 复刻</h3><p>把整个仓库复制一份到你自己名下，随便改。</p></div>
</div>"""

S_ISSUES = browser("https://github.com/open-org/awesome-editor/issues", gh_top("open-org / <b>awesome-editor</b>") + REPO_HEAD + TABS.format(a="", b="act") + """
<div class="gh-body" style="padding-top:14px">
  <div class="gh-toolbar"><div class="inp ph" style="flex:1;height:40px">is:issue is:open</div><span class="gh-btn">Labels</span><span class="gh-btn green" id="i-new">New issue</span></div>
  <div class="gh-box issues">
    <div class="it"><span class="o">⊙</span><div>导出 PDF 时中文显示为方框 <span class="lbl bug">bug</span><small>#128 opened 2 days ago by lin-dev</small></div></div>
    <div class="it" id="i-gfi"><span class="o">⊙</span><div>README 里有几处错别字 <span class="lbl gfi">good first issue</span> <span class="lbl doc">documentation</span><small>#125 opened 5 days ago by open-org-bot</small></div></div>
    <div class="it"><span class="o">⊙</span><div>如何修改默认字体大小？ <span class="lbl q">question</span><small>#121 opened last week by xiaohong</small></div></div>
  </div></div>""", style="width:1600px;margin:-20px auto 0")

S_NEWISSUE = """
<h2 class="head" data-s="1">怎样提一个好的 Issue？</h2>
<div class="newissue">""" + browser("https://github.com/open-org/awesome-editor/issues/new", """
<div class="gh-body">
  <div class="fld"><label>Add a title</label><div class="inp">导出 PDF 时中文显示为方框</div></div>
  <div class="fld"><label>Add a description</label><div class="md-area">**问题描述**
导出 PDF 后，所有中文都变成了方框。

**复现步骤**
1. 新建一个文档，输入中文
2. 点击“导出 PDF”

**我的环境**：Windows 11，版本 2.3.0
（附截图）</div></div>
  <div style="display:flex;justify-content:flex-end"><span class="gh-btn green">Create</span></div></div>""", style="flex:1") + """
<div style="width:540px;display:flex;flex-direction:column;gap:18px">
  <div class="tip" data-s="2" style="font-size:28px"><span class="emoji">🔍</span><div>先搜索，看看是不是已经有人提过</div></div>
  <div class="tip" data-s="3" style="font-size:28px"><span class="emoji">📝</span><div>写清楚：发生了什么、怎样复现、你的环境</div></div>
  <div class="tip" data-s="4" style="font-size:28px"><span class="emoji">🖼️</span><div>附上截图，一图胜千言</div></div>
  <div class="tip good" data-s="5" style="font-size:28px"><span class="emoji">🙏</span><div>语气礼貌，维护者多是业余时间在帮忙</div></div>
</div></div>"""

S_FLOW = """
<h2 class="head" data-s="1">给别人的项目贡献代码：Fork 工作流</h2>
<div class="fork-map">
  <svg viewBox="0 0 1620 620">
    <path data-s="2" d="M440 110 L 1170 110" stroke="#8250df"/><text data-s="2" x="805" y="90" text-anchor="middle" fill="#8250df">① Fork 复刻</text>
    <path data-s="3" d="M1390 190 L 1390 390" stroke="#0969da"/><text data-s="3" x="1410" y="300" fill="#0969da">② Clone 克隆</text>
    <path data-s="5" d="M1320 390 L 1320 190" stroke="#1f883d"/><text data-s="5" x="1300" y="300" text-anchor="end" fill="#1f883d">④ Push 推送</text>
    <path data-s="6" d="M1170 150 L 440 150" stroke="#d4700a"/><text data-s="6" x="805" y="200" text-anchor="middle" fill="#d4700a">⑤ Pull Request</text>
  </svg>
  <div class="nd" data-s="1" style="left:0;top:40px;border-color:var(--orange)"><div class="emoji">🏛️</div><b>原项目</b><span>open-org/awesome-editor</span></div>
  <div class="nd" data-s="2" style="left:1170px;top:40px;border-color:var(--purple)"><div class="emoji">⑂</div><b>你的 Fork</b><span>xiaoming-dev/awesome-editor</span></div>
  <div class="nd" data-s="3" style="left:1170px;top:400px;border-color:var(--blue)"><div class="emoji">💻</div><b>你的电脑</b><span>③ 新建分支，修改提交</span></div>
</div>"""

S_FORK = browser("https://github.com/open-org/awesome-editor/fork", gh_top("open-org / <b>awesome-editor</b>") + """
<div class="gh-body" style="padding:30px 60px">
  <div style="font-size:32px;font-weight:700">Create a new fork</div>
  <div style="font-size:20px;color:#59636e;margin:6px 0 24px">A fork is a copy of a repository. Forking a repository allows you to freely experiment with changes without affecting the original project.</div>
  <div class="own" style="display:flex;gap:14px;align-items:flex-end">
    <div class="fld"><label>Owner <em>*</em></label><div class="inp" style="width:260px">🟣 xiaoming-dev ▾</div></div><div style="font-size:34px;padding-bottom:4px">/</div>
    <div class="fld" style="flex:1"><label>Repository name <em>*</em></label><div class="inp">awesome-editor</div><div class="hint ok">✓ awesome-editor is available.</div></div></div>
  <div class="opt"><div class="c on2"></div><div>Copy the <span class="sha">main</span> branch only</div></div>
  <div style="display:flex;justify-content:flex-end;margin-top:14px"><span class="gh-btn green" id="f-go">Create fork</span></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_XPR = browser("https://github.com/open-org/awesome-editor/compare/main...xiaoming-dev:awesome-editor:fix-typo", gh_top("open-org / <b>awesome-editor</b>") + """
<div class="gh-body">
  <div style="font-size:30px;margin-bottom:12px">Comparing changes</div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;border:1px solid #d0d7de;border-radius:10px;padding:14px 16px;font-size:19px;background:#f6f8fa" id="xbar">
    <span id="x-base" style="display:flex;gap:10px"><span class="gh-btn" style="height:34px">base repository: open-org/awesome-editor ▾</span><span class="gh-btn" style="height:34px">base: main ▾</span></span> ←
    <span id="x-head" style="display:flex;gap:10px"><span class="gh-btn" style="height:34px">head repository: xiaoming-dev/awesome-editor ▾</span><span class="gh-btn" style="height:34px">compare: fix-typo ▾</span></span></div>
  <div style="color:#1a7f37;font-size:20px;margin:14px 0">✓ <b>Able to merge.</b> These branches can be automatically merged.</div>
  <div class="gh-box diff"><div class="fh">README.md</div>
    <div class="l del"><i>12</i>-支持实时预栏</div><div class="l add"><i>12</i>+支持实时预览</div></div>
  <div style="display:flex;justify-content:flex-end;margin-top:16px"><span class="gh-btn green">Create pull request</span></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_ETQ = """
<h2 class="head" data-s="1">参与开源的几条礼仪</h2>
<div class="etq">
  <div class="tip" data-s="2"><span class="emoji">📖</span><div>先读 <b>README</b> 和 <b>CONTRIBUTING.md</b>，了解项目的规矩</div></div>
  <div class="tip" data-s="3"><span class="emoji">🌱</span><div>从小事做起：修错别字、完善文档，找 <b>good first issue</b></div></div>
  <div class="tip" data-s="4"><span class="emoji">🎯</span><div>一个 PR 只做一件事，写清楚改了什么、为什么改</div></div>
  <div class="tip good" data-s="5"><span class="emoji">🙏</span><div>保持礼貌和耐心，维护者可能过几天才回复</div></div>
</div>"""

SCENES = [
    title_scene(NUM, "Star、Fork、Issue，给别人的项目做贡献",
                ["欢迎回来！前面八集，我们一直在管理自己的仓库。"],
                ["这一集，我们走出去，看看怎样参与别人的开源项目。"]),
    dict(html=S_OS, steps=[
        dict(say=["先说说什么是开源。开源就是把源代码公开，任何人都可以查看、学习，甚至参与改进。",
                  "GitHub 上有数不清的开源项目，很多我们每天在用的软件，都是开源的。"]),
        dict(say=["对初学者来说，开源项目首先是最好的学习资料，可以看看高手是怎么写代码的；"]),
        dict(say=["其次，你可以免费使用这些现成的工具；"]),
        dict(say=["等你熟练了，还可以发现问题、提出建议，甚至贡献自己的代码。"]),
    ]),
    dict(html=S_SEARCH, steps=[
        dict(say=["怎么找到感兴趣的项目呢？最简单的办法是用顶部的搜索框，输入关键词，比如 markdown editor。"]),
        dict(say=["左边可以筛选类型和编程语言。"], js="hl('#s-filter', {pad:4})"),
        dict(say=["每个结果下面都显示了星星的数量，星星越多，说明越受欢迎。"],
             js="hl('#s-star', {label:'星星数', side:'below', pad:6})"),
        dict(say=["我们点开第一个项目看看。"], js="hl(null); cursor('#s-first b', {click:true})"),
    ]),
    dict(html=S_BTNS, steps=[
        dict(say=["在项目页面的右上角，有三个按钮，我们来认识一下。"], js="hl('.rbtns', {pad:6})"),
        dict(say=["Star，就是点一颗星，相当于点赞加收藏。以后在个人菜单的 Your stars 里，就能找到它。"], js="hl('#b-star', {pad:6})"),
        dict(say=["Watch，是关注。项目有新动态时会通知你，不过消息会很多，一般不用开。"], js="hl('#b-watch', {pad:6})"),
        dict(say=["Fork，是复刻，把整个仓库复制一份到你自己的名下，你可以随便修改，不会影响原项目。"], js="hl('#b-fork', {pad:6})"),
    ]),
    dict(html=S_ISSUES, steps=[
        dict(say=["再来看 Issues 标签。Issue 可以理解为问题反馈，用户在这里报告错误、提出建议、提问。"]),
        dict(say=["每个 Issue 可以打上标签，比如 bug 表示程序错误，question 表示提问。"]),
        dict(say=["特别留意这个紫色的标签：good first issue，意思是适合新手的第一个任务。",
                  "想参与开源，从这类 Issue 开始最合适。"], js="hl('#i-gfi', {pad:2})"),
        dict(say=["如果你在使用中遇到问题，可以点击 New issue，提交一个新的反馈。"],
             js="hl('#i-new', {pad:6})"),
    ]),
    dict(html=S_NEWISSUE, steps=[
        dict(say=["怎样提一个好的 Issue 呢？"]),
        dict(say=["第一，先搜索一下，看看是不是已经有人提过同样的问题。"]),
        dict(say=["第二，写清楚发生了什么、怎样才能复现，以及你用的是什么系统和版本。"]),
        dict(say=["第三，最好附上截图，一图胜千言。"]),
        dict(say=["第四，语气要礼貌。开源项目的维护者，大多是用业余时间在帮忙。"]),
    ]),
    dict(html=S_FLOW, steps=[
        dict(say=["如果你想直接修改别人的项目，比如修一个错别字，该怎么做呢？",
                  "你没有原项目的修改权限，所以要用一种叫 Fork 工作流的方法。"]),
        dict(say=["第一步，Fork，把原项目复刻到自己名下。"]),
        dict(say=["第二步，把你的 Fork 克隆到电脑上。第三步，新建一个分支，修改并提交。"]),
        dict(say=["这几步，我们在前面几集都练过了。"]),
        dict(say=["第四步，把分支推送到你自己的 Fork。"]),
        dict(say=["第五步，从你的 Fork 向原项目发起一个 Pull Request，请原作者审查并合并。"]),
    ]),
    dict(html=S_FORK, steps=[
        dict(say=["点击 Fork 按钮后，会来到这个页面。Owner 是你自己，仓库名保持不变就好。"]),
        dict(say=["点击 Create fork，几秒钟后，你的名下就有了一份一模一样的仓库。"], js="cursor('#f-go', {click:true})"),
    ]),
    dict(html=S_XPR, steps=[
        dict(say=["修改完并推送以后，在原项目页面发起 Pull Request。这时的合并方向，有点不一样。"]),
        dict(say=["左边的 base repository 是原项目，也就是要合并进去的地方；"], js="hl('#x-base', {pad:4})"),
        dict(say=["右边的 head repository 是你的 Fork，后面是你修改用的分支。"], js="hl('#x-head', {pad:4})"),
        dict(say=["下面能看到这次的改动：把“预栏”改成了“预览”。确认无误后，点击 Create pull request，等待原作者回复就可以了。"],
             js="hl(null)"),
    ]),
    dict(html=S_ETQ, steps=[
        dict(say=["最后，说说参与开源的几条礼仪。"]),
        dict(say=["第一，动手之前，先读项目的 README 和 CONTRIBUTING 文件，了解这个项目的规矩。"]),
        dict(say=["第二，从小事做起，比如修改错别字、完善文档，或者找标着 good first issue 的任务。"]),
        dict(say=["第三，一个 PR 只做一件事，并写清楚改了什么、为什么改。"]),
        dict(say=["第四，保持礼貌和耐心，维护者可能要过几天才会回复你。"]),
    ]),
    summary_scene(NUM, [
        "Star 收藏，Watch 关注，Fork 复刻",
        "Issue：问题反馈，从 good first issue 起步",
        "Fork → Clone → 分支修改 → Push → PR",
        "先读规矩，从小事做起，保持礼貌",
    ], [
        ["第一，Star 是收藏，Watch 是关注，Fork 是复刻到自己名下。"],
        ["第二，Issue 用来反馈问题，新手可以从 good first issue 开始。"],
        ["第三，贡献代码的流程是：Fork、克隆、在分支上修改、推送，最后发起 PR。"],
        ["第四，先读项目的规矩，从小事做起，保持礼貌。"],
    ], ["下一集是最后一集，我们学习几个实用技巧，并总结整套课程。我们下集见！"]),
]
