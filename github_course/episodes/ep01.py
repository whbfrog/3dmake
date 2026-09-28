NUM = 1
TITLE = "GitHub 到底是什么？"

CSS = """
.folder { width: 1040px; background:#fff; border-radius:22px; border:1px solid #e1e6eb; box-shadow:0 14px 40px rgba(31,35,40,.10); overflow:hidden; }
.folder .fbar { height:64px; background:#f0f3f6; display:flex; align-items:center; padding:0 28px; font-size:28px; color:var(--muted); border-bottom:1px solid #e1e6eb; }
.files { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; padding:44px 30px 50px; }
.file { display:flex; flex-direction:column; align-items:center; gap:18px; font-size:24px; text-align:center; }
.doc { width:110px; height:136px; border-radius:10px; background:linear-gradient(#fff,#f4f7fb); border:3px solid #9fb3c8; position:relative;
  display:grid; place-items:center; font:900 48px "Source Han Sans SC"; color:#fff; }
.doc::before { content:""; position:absolute; left:14px; right:14px; top:44px; height:48px; background:#2b579a; border-radius:8px; z-index:0; }
.doc b { position:relative; z-index:1; }
.qs { display:flex; flex-direction:column; gap:28px; }
.q { font-size:38px; font-weight:700; background:#fff; border-radius:18px; padding:22px 32px; border-left:10px solid var(--red); box-shadow:0 8px 24px rgba(31,35,40,.08); }

.tl { position:relative; height:420px; margin-top:30px; }
.tl .line { position:absolute; left:40px; right:40px; top:150px; height:10px; border-radius:5px; background:#cfd8e3; }
.save { position:absolute; top:88px; width:240px; margin-left:-120px; display:flex; flex-direction:column; align-items:center; gap:14px; }
.save .dot { width:128px; height:128px; border-radius:28px; background:#fff; border:5px solid var(--blue); display:grid; place-items:center; font-size:62px; box-shadow:0 8px 20px rgba(9,105,218,.18); }
.save .name { font-size:32px; font-weight:800; }
.save .cap { font-size:28px; color:var(--muted); }
.save.now .dot { border-color:var(--green); background:var(--green-soft); }
.back { position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible; }
.back path { fill:none; stroke:var(--orange); stroke-width:8; stroke-linecap:round; stroke-dasharray:1100; stroke-dashoffset:1100; transition:stroke-dashoffset 1.1s ease, opacity .3s; }
.back path.on { stroke-dashoffset:0; transform:none; }
.back text { font:700 34px "Source Han Sans SC"; fill:var(--orange); }
.banner { margin:10px auto 0; width:fit-content; font-size:50px; font-weight:900; padding:22px 60px; border-radius:22px; background:var(--dark); color:#fff; }
.banner em { font-style:normal; color:#7ee787; }

.vs .card { flex:1; padding:44px 50px; }
.vs .big { font-size:96px; }
.vs h3 { font-size:64px; margin:0 0 18px; }
.vs ul { margin:22px 0 0; padding:0; list-style:none; font-size:34px; line-height:1.8; }
.vs li::before { content:"✓ "; color:var(--green); font-weight:900; }
.formula { margin-top:34px; text-align:center; font-size:44px; font-weight:800; }
.formula span { padding:10px 26px; border-radius:14px; }

.collab { position:relative; width:900px; height:580px; margin-top:-20px; }
.hub { position:absolute; left:290px; top:10px; width:320px; height:190px; border-radius:30px; background:var(--dark); color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; }
.hub .emoji { font-size:70px; } .hub b { font-size:34px; }
.person { position:absolute; top:370px; width:220px; display:flex; flex-direction:column; align-items:center; gap:10px; font-size:30px; font-weight:700; }
.person .emoji { font-size:96px; width:150px; height:150px; border-radius:50%; background:#fff; display:grid; place-items:center; box-shadow:0 8px 20px rgba(31,35,40,.10); }
.arrows { position:absolute; inset:0; overflow:visible; }
.arrows path { fill:none; stroke:var(--green); stroke-width:7; stroke-linecap:round; stroke-dasharray:500; stroke-dashoffset:500; transition:stroke-dashoffset 1s ease, opacity .3s; }
.arrows path.on { stroke-dashoffset:0; transform:none; }
.log { flex:1; align-self:center; }
.log .item { display:flex; gap:18px; align-items:center; padding:20px 0; border-top:1px solid #e6eaef; font-size:30px; }
.log .item:first-of-type { border-top:0; }
.log .who { font-weight:800; width:90px; } .log .what { flex:1; color:var(--muted); } .log .t { font-family:"JetBrains Mono"; color:var(--muted); font-size:26px; }

.grid4 { display:grid; grid-template-columns:1fr 1fr; gap:30px 36px; }
.grid4 .card { display:flex; gap:30px; align-items:center; padding:30px 38px; }
.grid4 .emoji { font-size:74px; }
.grid4 h3 { font-size:40px; margin:0 0 8px; }
.grid4 p { font-size:29px; }
.foot { margin-top:34px; text-align:center; font-size:36px; font-weight:700; color:var(--purple); }

.repo { width:1620px; margin:-20px auto 0; }
.gloss .row2 { display:flex; align-items:center; gap:34px; background:#fff; border-radius:20px; padding:14px 36px; margin-bottom:16px; box-shadow:0 6px 18px rgba(31,35,40,.06); }
.gloss .term { width:420px; font-size:46px; font-weight:900; }
.gloss .term small { display:block; font-size:28px; font-weight:600; font-family:"JetBrains Mono"; margin-top:2px; }
.gloss .def { font-size:34px; color:var(--muted); }

.road { display:grid; grid-template-columns:repeat(5,1fr); gap:28px; margin-top:20px; }
.node { background:#fff; border-radius:20px; padding:26px 24px; height:200px; border:3px solid #e1e6eb; transition:background .6s, border-color .6s, color .6s, transform .6s; }
.node .n { font-size:28px; font-weight:800; color:var(--muted); transition:color .6s; }
.node .nt { font-size:33px; font-weight:800; margin-top:10px; line-height:1.35; }
.node.me { border-color:var(--dark); background:var(--dark); color:#fff; }
.node.me .n { color:#7ee787; }
.node.hot { border-color:var(--green); background:var(--green-soft); transform:translateY(-8px); }
.node.hot .n { color:var(--green); }

.sum .card { padding:40px 56px; }
.sum .li { display:flex; gap:28px; align-items:center; font-size:40px; font-weight:600; padding:18px 0; }
.next { margin-top:40px; display:flex; align-items:center; gap:30px; background:var(--dark); color:#fff; border-radius:24px; padding:30px 48px; font-size:42px; font-weight:800; }
.next .tag { font-size:30px; }
"""

S_TITLE = """
<div class="center">
  <div class="tag t-green" data-s="1" style="font-size:34px;padding:10px 30px">零基础 · 共 10 集</div>
  <h1 class="title" data-s="1" style="font-size:124px;margin:40px 0 30px">GitHub 零基础入门</h1>
  <div data-s="2" style="font-size:58px;font-weight:700;color:var(--muted)">第 1 集 · GitHub 到底是什么？</div>
</div>"""

S_FILES = """
<h2 class="head">你是不是也这样管理文件？</h2>
<div class="row" style="gap:60px;align-items:center">
  <div class="folder" data-s="1">
    <div class="fbar"><span class="emoji" style="margin-right:12px">📁</span>我的文档 &gt; 毕业论文</div>
    <div class="files">
      <div class="file pop" data-s="2"><div class="doc"><b>W</b></div>论文_最终版.docx</div>
      <div class="file pop" data-s="3"><div class="doc"><b>W</b></div>论文_最终版2.docx</div>
      <div class="file pop" data-s="4"><div class="doc"><b>W</b></div>论文_真的最终版.docx</div>
      <div class="file pop" data-s="4"><div class="doc"><b>W</b></div>论文_打死不改版.docx</div>
    </div>
  </div>
  <div class="qs">
    <div class="q" data-s="5">❓ 哪个才是最新的？</div>
    <div class="q" data-s="5">❓ 每一版改了什么？</div>
    <div class="q" data-s="5">❓ 怎么退回上周的版本？</div>
  </div>
</div>"""

S_SAVE = """
<h2 class="head" data-s="1">打个比方：游戏存档</h2>
<div class="tl">
  <div class="line" data-s="1"></div>
  <div class="save pop" data-s="2" style="left:12%"><div class="dot emoji">💾</div><div class="name">存档 1</div><div class="cap" data-s="4">写完第一章</div></div>
  <div class="save pop" data-s="2" style="left:37%"><div class="dot emoji">💾</div><div class="name">存档 2</div><div class="cap" data-s="4">加入实验数据</div></div>
  <div class="save pop" data-s="2" style="left:62%"><div class="dot emoji">💾</div><div class="name">存档 3</div><div class="cap" data-s="4">修改结论</div></div>
  <div class="save now pop" data-s="2" style="left:87%"><div class="dot emoji">🎮</div><div class="name">现在</div><div class="cap" data-s="4">改坏了？</div></div>
  <svg class="back" viewBox="0 0 1620 420">
    <path data-s="3" d="M1380 80 C 1300 -40, 700 -40, 610 70" />
    <path data-s="3" d="M610 70 l -8 -34 M610 70 l 34 -10" />
    <text data-s="3" x="995" y="52" text-anchor="middle">读档，回到过去</text>
  </svg>
</div>
<div class="banner" data-s="5">这种做法就叫 <em>版本控制</em></div>"""

S_VS = """
<h2 class="head" data-s="1">Git 和 GitHub，不是一回事</h2>
<div class="row vs">
  <div class="card" data-s="2">
    <h3><span class="emoji">💻</span> Git</h3>
    <span class="tag t-blue">装在电脑上的软件</span>
    <ul><li>给文件“存档”</li><li>记录每一次修改</li><li>不联网也能用</li></ul>
  </div>
  <div class="card" data-s="3">
    <h3><span class="emoji">☁️</span> GitHub</h3>
    <span class="tag t-green">一个网站 · github.com</span>
    <ul><li>把存档放到云端</li><li>分享给别人看</li><li>和别人一起修改</li></ul>
  </div>
</div>
<div class="formula" data-s="4"><span class="t-blue">Git = 存档工具</span>　　<span class="t-green">GitHub = 云端仓库 + 协作社区</span></div>"""

S_COLLAB = """
<h2 class="head" data-s="1">最厉害的地方：多人协作</h2>
<div class="row" style="gap:70px">
  <div class="collab">
    <svg class="arrows" viewBox="0 0 900 580">
      <path data-s="3" d="M150 370 C 160 280, 250 200, 320 190" />
      <path data-s="3" d="M450 370 L 450 215" />
      <path data-s="3" d="M750 370 C 740 280, 650 200, 580 190" />
    </svg>
    <div class="hub pop" data-s="3"><div class="emoji">📦</div><b>GitHub 上的仓库</b></div>
    <div class="person pop" data-s="2" style="left:40px"><div class="emoji">👨‍💻</div>小明</div>
    <div class="person pop" data-s="2" style="left:340px"><div class="emoji">👩‍💻</div>小红</div>
    <div class="person pop" data-s="2" style="left:640px"><div class="emoji">🧑‍💻</div>小刚</div>
  </div>
  <div class="card log" data-s="4">
    <h3 style="font-size:36px">📜 修改记录</h3>
    <div class="item"><span class="who">小明</span><span class="what">修改了首页标题</span><span class="t">10:02</span></div>
    <div class="item"><span class="who">小红</span><span class="what">新增了登录页面</span><span class="t">10:15</span></div>
    <div class="item"><span class="who">小刚</span><span class="what">修正了一个错别字</span><span class="t">10:31</span></div>
    <div class="item" data-s="5" style="color:var(--green);font-weight:700;border-top:2px dashed #cfd8e3">✅ 不会互相覆盖 · 改坏了也能找回</div>
  </div>
</div>"""

S_USES = """
<h2 class="head" data-s="1">GitHub 能用来做什么？</h2>
<div class="grid4">
  <div class="card" data-s="2"><div class="emoji">🗂️</div><div><h3>保存与找回</h3><p>代码和文档的每个历史版本，都能随时找回</p></div></div>
  <div class="card" data-s="3"><div class="emoji">🤝</div><div><h3>团队协作</h3><p>分工修改、互相检查，再合并到一起</p></div></div>
  <div class="card" data-s="4"><div class="emoji">📚</div><div><h3>学习开源</h3><p>上亿个公开项目，许多知名软件的源代码都能直接看</p></div></div>
  <div class="card" data-s="5"><div class="emoji">🌐</div><div><h3>展示自己</h3><p>放上作品集，还能免费发布个人网站</p></div></div>
</div>
<div class="foot" data-s="6">✍️ 不只是程序员：写文章、记笔记、整理资料，一样用得上</div>"""

S_REPO = """
<div class="browser repo" data-s="1">
  <div class="bar"><i></i><i></i><i></i><div class="url">https://github.com/xiaoming/my-notes</div></div>
  <div class="gh-top"><div class="gh-logo">G</div><div class="gh-crumb">xiaoming / <b>my-notes</b></div><div class="gh-search">Type / to search</div><div class="gh-avatar"></div></div>
  <div class="gh-tabs"><span class="act">&lt;&gt; Code</span><span>Issues 2</span><span>Pull requests 1</span><span>Actions</span><span>Settings</span></div>
  <div class="gh-body">
    <div class="gh-title">my-notes <span class="gh-pill">Public</span></div>
    <div class="gh-toolbar"><span class="gh-btn">⑂ main ▾</span><span class="gh-btn">3 Branches</span><span class="gh-btn" style="margin-left:auto">☆ Star 8</span><span class="gh-btn green">&lt;&gt; Code ▾</span></div>
    <div class="gh-box repo-files">
      <div class="head"><div class="gh-avatar" style="width:30px;height:30px"></div><b>xiaoming</b> 更新了学习笔记<span class="count" id="commits">🕘 12 Commits</span></div>
      <div class="gh-row"><i class="ico-dir"></i>images<span class="msg">添加截图</span><span class="when">2 days ago</span></div>
      <div class="gh-row"><i class="ico-dir"></i>notes<span class="msg">更新了学习笔记</span><span class="when">1 hour ago</span></div>
      <div class="gh-row"><i class="ico-file"></i>.gitignore<span class="msg">初始化项目</span><span class="when">last week</span></div>
      <div class="gh-row"><i class="ico-file"></i>README.md<span class="msg">完善项目说明</span><span class="when">3 days ago</span></div>
    </div>
    <div class="gh-box gh-readme">
      <div class="head">📖 README</div>
      <div class="md"><h4>我的学习笔记</h4><p>这里记录我学习编程的点点滴滴，欢迎一起交流！</p></div>
    </div>
  </div>
</div>"""

S_GLOSS = """
<h2 class="head" data-s="1" style="margin-bottom:30px">先混个脸熟：四个核心词<small>后面每一集都会详细讲，现在记住名字就行</small></h2>
<div class="gloss">
  <div class="row2" data-s="2"><div class="term" style="color:var(--blue)">仓库<small>Repository</small></div><div class="def">存放项目的地方，像一个文件夹</div></div>
  <div class="row2" data-s="3"><div class="term" style="color:var(--green)">提交<small>Commit</small></div><div class="def">一次“存档”，附带一句说明</div></div>
  <div class="row2" data-s="4"><div class="term" style="color:var(--purple)">分支<small>Branch</small></div><div class="def">不影响主线，开一条支线试新想法</div></div>
  <div class="row2" data-s="5"><div class="term" style="color:var(--orange)">拉取请求<small>Pull Request</small></div><div class="def">请别人检查你的修改，同意后再合并</div></div>
</div>"""

S_ROAD = """
<h2 class="head" data-s="1">课程路线图</h2>
<div class="road" data-s="1">
  <div class="node me"><div class="n">第 1 集</div><div class="nt">GitHub 是什么</div></div>
  <div class="node g2"><div class="n">第 2 集</div><div class="nt">注册账号与界面导览</div></div>
  <div class="node g2"><div class="n">第 3 集</div><div class="nt">创建第一个仓库</div></div>
  <div class="node g2"><div class="n">第 4 集</div><div class="nt">提交与历史记录</div></div>
  <div class="node g3"><div class="n">第 5 集</div><div class="nt">把仓库搬到电脑上</div></div>
  <div class="node g3"><div class="n">第 6 集</div><div class="nt">本地修改与同步</div></div>
  <div class="node g4"><div class="n">第 7 集</div><div class="nt">分支 Branch</div></div>
  <div class="node g4"><div class="n">第 8 集</div><div class="nt">Pull Request 协作</div></div>
  <div class="node g4"><div class="n">第 9 集</div><div class="nt">参与开源</div></div>
  <div class="node g4"><div class="n">第 10 集</div><div class="nt">实用技巧与总结</div></div>
</div>"""

S_SUM = """
<h2 class="head" data-s="1">本集小结</h2>
<div class="sum">
  <div class="card">
    <div class="li" data-s="2"><div class="num bg-blue">1</div>版本控制 ≈ 游戏存档，随时回到过去</div>
    <div class="li" data-s="3"><div class="num bg-green">2</div>Git 是存档工具，GitHub 是云端仓库 + 协作社区</div>
    <div class="li" data-s="4"><div class="num bg-purple">3</div>四个核心词：仓库 · 提交 · 分支 · Pull Request</div>
  </div>
  <div class="next" data-s="5"><span class="tag t-green">下集预告</span>第 2 集 · 注册 GitHub 账号，熟悉界面</div>
</div>"""


def hot(group):
    return f"document.querySelectorAll('.node.{group}').forEach(e => e.classList.add('hot'))"


SCENES = [
    dict(html=S_TITLE, steps=[
        dict(say=["大家好，欢迎来到《GitHub 零基础入门》。",
                  "这套课程一共十集，专门为第一次接触 GitHub 的朋友准备，不需要任何编程基础。"]),
        dict(say=["这一集，我们先不急着动手，而是先搞清楚一个问题：GitHub 到底是什么？"]),
    ]),
    dict(html=S_FILES, steps=[
        dict(say=["先来看一个你可能很熟悉的场景。"]),
        dict(say=["写论文的时候，改完一版，存一个“最终版”；"]),
        dict(say=[("老师提了意见，又存一个“最终版2”；", "老师提了意见，又存一个“最终版二”；")]),
        dict(say=["后来又改了好几次，就有了“真的最终版”，还有“打死不改版”。"]),
        dict(say=["时间一长，问题就来了：哪个才是最新的？每一版到底改了什么？",
                  "想退回上周的版本，又该怎么办？"]),
        dict(say=["这些麻烦，正是 Git 和 GitHub 要帮我们解决的。"]),
    ]),
    dict(html=S_SAVE, steps=[
        dict(say=["打个比方，你一定玩过可以存档的游戏。"]),
        dict(say=["打到关键的地方，就存一个档；"]),
        dict(say=["万一打输了，读档就能回到之前的状态，一点也不慌。"]),
        dict(say=["管理文件也可以这样：每改好一处，就存一个档，并且写清楚这次改了什么。",
                  "以后想看哪一版、想回到哪一版，都很方便。"]),
        dict(say=["这种做法，有个专门的名字，叫做“版本控制”。"]),
    ]),
    dict(html=S_VS, steps=[
        dict(say=["说到版本控制，就绕不开两个名字：Git 和 GitHub。", "它们长得很像，但并不是一回事。"]),
        dict(say=["Git 是一个装在你电脑上的软件，专门负责给文件存档，记录每一次修改。",
                  "它不需要联网，在自己电脑上就能用。"]),
        dict(say=["GitHub 则是一个网站。它可以把你电脑上的存档放到云端保存，",
                  "还能分享给别人，和别人一起修改。"]),
        dict(say=["简单记一句话：Git 是存档工具；", "GitHub 是放存档的云端仓库，外加一个大家交流合作的社区。"]),
    ]),
    dict(html=S_COLLAB, steps=[
        dict(say=["GitHub 最厉害的地方，在于多人协作。"]),
        dict(say=["比如三个人一起做一个项目，每个人都在自己的电脑上修改；"]),
        dict(say=["改好之后，都交到 GitHub 上的同一个仓库里。"]),
        dict(say=["谁在什么时间、改了哪些内容，都记录得清清楚楚。"]),
        dict(say=["大家的修改不会互相覆盖，就算改坏了，也能找回原来的版本。"]),
    ]),
    dict(html=S_USES, steps=[
        dict(say=["那 GitHub 能用来做什么呢？主要有这么几件事。"]),
        dict(say=["第一，保存与找回。代码和文档的每一个历史版本，都能随时找回来。"]),
        dict(say=["第二，团队协作。大家分工修改、互相检查，再合并到一起。"]),
        dict(say=["第三，学习开源。GitHub 上有上亿个公开项目，许多知名软件的源代码都能直接看到。"]),
        dict(say=["第四，展示自己。你可以把作品放上去当作品集，甚至免费发布一个个人网站。"]),
        dict(say=["而且它不只是程序员的工具，写文章、记笔记、整理资料，也一样用得上。"]),
    ]),
    dict(html=S_REPO, steps=[
        dict(say=["我们来看看，GitHub 上的一个项目长什么样。"]),
        dict(say=["这样一个项目，叫做“仓库”，英文是 Repository。", "它就像一个文件夹，存放着这个项目的所有文件。"],
             js="hl('.repo-files', {label:'仓库里的文件', side:'above', delay:200})"),
        dict(say=["右上角这里，显示的是提交的次数。",
                  "在 GitHub 里，每一次“存档”都叫做一次“提交”，英文是 Commit。",
                  "这里的十二次提交，就相当于存了十二次档。"],
             js="hl('#commits', {label:'12 次提交 = 存了 12 次档', side:'above', pad:8})"),
        dict(say=["下面这段说明文字，来自一个叫 README 的文件，相当于这个项目的说明书。"],
             js="hl('.gh-readme', {label:'README：项目说明书', side:'above'})"),
        dict(say=["现在看不懂也没关系，后面每一集，都会带你亲手操作一遍。"], js="hl(null)"),
    ]),
    dict(html=S_GLOSS, steps=[
        dict(say=["最后，我们先认识四个最常用的词，混个脸熟就行。"]),
        dict(say=["仓库，Repository，就是存放项目的地方；"]),
        dict(say=["提交，Commit，就是一次存档，还会附带一句说明；"]),
        dict(say=["分支，Branch，可以在不影响主线的情况下，开一条支线去尝试新想法；"]),
        dict(say=["拉取请求，Pull Request，就是请别人检查你的修改，同意之后再合并进去。"]),
    ]),
    dict(html=S_ROAD, steps=[
        dict(say=["整套课程的学习路线是这样的。"]),
        dict(say=["先注册账号、创建仓库，在网页上完成你的第一次提交；"], js=hot("g2")),
        dict(say=["然后把仓库搬到自己的电脑上，学会上传和同步；"], js=hot("g3")),
        dict(say=["接着学习分支和 Pull Request，最后动手参与开源，", "还会发布一个属于你自己的网页。"], js=hot("g4")),
    ]),
    dict(html=S_SUM, steps=[
        dict(say=["好，我们来总结一下这一集。"]),
        dict(say=["第一，版本控制就像游戏存档，随时可以回到过去。"]),
        dict(say=["第二，Git 是存档工具，GitHub 是云端仓库加上协作社区。"]),
        dict(say=["第三，仓库、提交、分支和 Pull Request，是接下来要学的四个核心概念。"]),
        dict(say=["下一集，我们一起注册一个 GitHub 账号，并熟悉它的界面。", "我们下集见！"], min=4.0),
    ]),
]
