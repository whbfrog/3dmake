from kit import PS, browser, gh_top, repo_tabs, summary_scene, term, title_scene, win

NUM = 5
TITLE = "把仓库搬到电脑上"

CSS = """
.twin { display:flex; gap:40px; }
.twin .card { flex:1; }
.twin .emoji { font-size:84px; }
.twin h3 { font-size:44px; margin:10px 0; }
.twin ul { margin:16px 0 0; padding-left:30px; font-size:30px; line-height:1.8; color:var(--muted); }

.dl-hero { height:520px; background:linear-gradient(160deg,#6e40c9,#1f6feb); color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:26px; text-align:center; }
.dl-hero h1 { font-size:58px; margin:0; } .dl-hero p { font-size:26px; margin:0; opacity:.85; }
.dl-hero .b { background:#fff; color:#1f2328; font-size:26px; font-weight:700; padding:14px 30px; border-radius:10px; }

.welcome { display:flex; height:560px; }
.welcome .l { flex:1; padding:50px 60px; }
.welcome h2 { font-size:40px; margin:0 0 16px; }
.welcome p { font-size:22px; color:#57606a; margin:0 0 30px; }
.welcome .b { display:block; width:420px; text-align:center; padding:14px; border-radius:8px; font-size:22px; margin-bottom:16px; border:1px solid #d0d7de; }
.welcome .b.p { background:#0969da; color:#fff; border-color:#0969da; }
.welcome .r { width:520px; background:linear-gradient(160deg,#ddf4ff,#fbefff); display:grid; place-items:center; font-size:170px; }

.dlg { width:980px; margin:0 auto; }
.dlg .dtabs { display:flex; border-bottom:1px solid #d0d7de; font-size:21px; }
.dlg .dtabs span { padding:12px 22px; } .dlg .dtabs span.act { border-bottom:3px solid #0969da; font-weight:700; }
.dlg .db { padding:22px 28px; }
.dlg .rl .it { padding:10px 14px; font-size:21px; border-radius:6px; }
.dlg .rl .it.act { background:#0969da; color:#fff; }
.dlg .df { display:flex; justify-content:flex-end; gap:12px; padding:16px 28px; border-top:1px solid #d0d7de; }
.btnb { background:#0969da; color:#fff; border-radius:6px; padding:9px 26px; font-size:21px; font-weight:600; }

.codemenu { position:absolute; right:40px; top:300px; width:560px; background:#fff; border:1px solid #d0d7de; border-radius:12px; box-shadow:0 12px 32px rgba(31,35,40,.18); font-size:20px; }
.codemenu .h { padding:14px 18px; border-bottom:1px solid #d0d7de; font-weight:700; }
.codemenu .u { margin:14px 18px; display:flex; gap:10px; align-items:center; }
.codemenu .u .inp { flex:1; font-family:"JetBrains Mono"; font-size:17px; height:40px; }
.codemenu .o { padding:12px 18px; border-top:1px solid #d0d7de; }

.explorer .path { padding:10px 18px; border-bottom:1px solid #e1e1e1; font-size:20px; color:#333; background:#fafafa; }
.explorer .fl { padding:10px 18px; }
.explorer .fi { display:flex; gap:14px; align-items:center; padding:9px 12px; font-size:22px; border-radius:6px; }
.explorer .fi.ghost { opacity:.55; }
.explorer .fi .emoji { font-size:28px; }
.explorer .fi .ty { margin-left:auto; color:#666; font-size:19px; width:200px; }
"""

S_WHY = """
<h2 class="head" data-s="1">为什么要把仓库搬到电脑上？</h2>
<div class="flow" style="margin-top:30px">
  <div class="fb" data-s="2" style="border-color:var(--green)"><span class="emoji">☁️</span><b>远程仓库</b><span>在 GitHub 上</span></div>
  <div class="fa" data-s="3" style="min-width:280px">clone 克隆</div>
  <div class="fb" data-s="3" style="border-color:var(--blue)"><span class="emoji">💻</span><b>本地仓库</b><span>在你的电脑上</span></div>
</div>
<div class="tip" data-s="4" style="margin-top:50px"><span class="emoji">💡</span><div><b>克隆</b>：把云端的仓库完整复制一份到电脑上，<b>连同所有的历史记录</b>一起。</div></div>"""

S_TOOLS = """
<h2 class="head" data-s="1">需要安装什么工具？</h2>
<div class="twin">
  <div class="card" data-s="2" style="border:4px solid var(--blue)"><div class="emoji">🖱️</div><h3>GitHub Desktop</h3>
    <span class="tag t-blue">推荐新手先用</span>
    <ul><li>图形界面，点按钮就能操作</li><li>GitHub 官方出品，免费</li><li>本系列主要用它演示</li></ul></div>
  <div class="card" data-s="3"><div class="emoji">⌨️</div><h3>Git 命令行</h3>
    <span class="tag t-purple">进阶可选</span>
    <ul><li>在黑色窗口里输入命令</li><li>更灵活，程序员常用</li><li>每一步都会附上对应命令</li></ul></div>
</div>"""

S_DL = browser("https://desktop.github.com", """
<div class="dl-hero"><div style="font-size:90px" class="emoji">🖥️</div><h1>GitHub Desktop</h1>
  <p>Focus on what matters instead of fighting with Git.</p><div class="b" id="dl-btn">⬇ Download for Windows</div></div>""",
                 style="width:1500px;margin:-10px auto 0")

S_WELCOME = win("GitHub Desktop", """
<div class="welcome"><div class="l"><h2>Welcome to GitHub Desktop</h2>
  <p>GitHub Desktop is a seamless way to contribute to projects on GitHub.</p>
  <span class="b p" id="w-signin">Sign in to GitHub.com</span><span class="b">Sign in to GitHub Enterprise</span>
  <span style="font-size:20px;color:#0969da">Skip this step</span></div>
  <div class="r emoji">🐙</div></div>""", style="width:1500px;margin:-10px auto 0")

S_CONFIG = win("GitHub Desktop", """
<div style="padding:44px 60px;font-size:22px;height:560px">
  <h2 style="font-size:36px;margin:0 0 10px">Configure Git</h2>
  <p style="color:#57606a;margin:0 0 26px">This is used to identify the commits you create. Anyone will be able to see this information if you publish commits.</p>
  <div id="cfg-opt"><div class="opt"><div class="r on2"></div><div>Use my GitHub account name and email address</div></div>
  <div class="opt"><div class="r"></div><div>Configure manually</div></div></div>
  <div style="margin-top:40px;display:flex;gap:14px"><span class="btnb" id="cfg-fin">Finish</span><span class="gh-btn">Cancel</span></div>
</div>""", style="width:1500px;margin:-10px auto 0")

S_CLONE = win("Clone a repository", """
<div class="dlg" style="width:auto">
  <div class="dtabs"><span class="act">GitHub.com</span><span>GitHub Enterprise</span><span>URL</span></div>
  <div class="db">
    <div class="inp ph" style="margin-bottom:12px">Filter your repositories</div>
    <div class="rl" id="cl-list"><div style="font-size:19px;color:#57606a;padding:6px 0">Your repositories</div>
      <div class="it act" id="cl-repo">📦 xiaoming-dev/my-notes</div><div class="it">📦 xiaoming-dev/hello-world</div></div>
    <div class="fld" id="cl-path" style="margin-top:22px"><label>Local path</label>
      <div style="display:flex;gap:10px"><div class="inp" style="flex:1;font-family:'JetBrains Mono';font-size:19px">C:\\Users\\xiaoming\\Documents\\GitHub\\my-notes</div><span class="gh-btn">Choose...</span></div></div>
  </div>
  <div class="df"><span class="gh-btn">Cancel</span><span class="btnb" id="cl-go">Clone</span></div>
</div>""", style="width:1100px;margin:-10px auto 0")

S_CODE = browser("https://github.com/xiaoming-dev/my-notes", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + """
<div class="gh-body" style="height:520px">
  <div class="gh-title">my-notes <span class="gh-pill">Public</span></div>
  <div class="gh-toolbar"><span class="gh-btn">⑂ main ▾</span><span class="gh-btn" style="margin-left:auto">Add file ▾</span><span class="gh-btn green" id="codebtn">&lt;&gt; Code ▾</span></div>
  <div class="gh-box"><div class="head"><b>xiaoming-dev</b> 添加第一天的笔记<span class="count">🕘 3 Commits</span></div>
    <div class="gh-row"><i class="ico-dir"></i>notes</div><div class="gh-row"><i class="ico-file"></i>README.md</div></div>
</div>
<div class="codemenu" data-s="2"><div class="h">Clone</div>
  <div style="padding:10px 18px 0;font-size:18px"><b>HTTPS</b>　SSH　GitHub CLI</div>
  <div class="u" id="cm-url"><div class="inp">https://github.com/xiaoming-dev/my-notes.git</div><span class="icbtn" style="width:44px;height:40px;border:1px solid #d0d7de;border-radius:8px;display:grid;place-items:center">⧉</span></div>
  <div class="o" id="cm-desk">🖥️ Open with GitHub Desktop</div>
  <div class="o" id="cm-zip">🗜️ Download ZIP</div>
</div>""", style="width:1600px;margin:-20px auto 0;position:relative")

S_DONE = win("GitHub Desktop", """
<div class="ghd-bar"><div class="sec"><small>Current repository</small><b>my-notes ▾</b></div><div class="sec"><small>Current branch</small><b>⑂ main ▾</b></div><div class="sec wide"><small>Fetch origin</small><b>⟳ Last fetched just now</b></div></div>
<div class="ghd-main"><div class="ghd-left"><div class="ghd-tabs"><span class="act">Changes</span><span>History</span></div>
  <div style="padding:20px;color:#57606a;font-size:20px">0 changed files</div></div>
  <div class="ghd-right"><div class="ghd-empty"><div style="font-size:30px;font-weight:700;color:#1f2328">No local changes</div>
    <div class="ghd-card" id="dn-vs">Open the repository in your external editor<span class="gh-btn">Open in Visual Studio Code</span></div>
    <div class="ghd-card" id="dn-ex">View the files of your repository in Explorer<span class="gh-btn">Show in Explorer</span></div>
    <div class="ghd-card">Open the repository page on GitHub in your browser<span class="gh-btn">View on GitHub</span></div></div></div></div>""",
          style="width:1600px;margin:-20px auto 0")

S_EXPLORER = win("📁 my-notes", """
<div class="explorer"><div class="path">此电脑 › 文档 › GitHub › my-notes</div>
<div class="fl">
  <div class="fi ghost" data-s="3" id="ex-git"><span class="emoji">📁</span>.git<span class="ty">隐藏的文件夹</span></div>
  <div class="fi"><span class="emoji">📁</span>notes<span class="ty">文件夹</span></div>
  <div class="fi"><span class="emoji">📄</span>README.md<span class="ty">Markdown 文件</span></div>
</div></div>""", cls="explorer-win", style="width:1100px;margin:0 auto")

S_EXPLORER_FULL = """<h2 class="head" data-s="1">克隆下来的文件夹里有什么？</h2>
<div class="row" style="gap:40px;align-items:flex-start">""" + S_EXPLORER.replace('style="width:1100px;margin:0 auto"', 'style="flex:1"') + """
<div style="width:560px;display:flex;flex-direction:column;gap:22px">
  <div class="tip good" data-s="2"><span class="emoji">📄</span><div>和网页上一模一样的文件，可以用任何软件打开、编辑</div></div>
  <div class="tip warn" data-s="4"><span class="emoji">⚠️</span><div><b>.git</b> 是 Git 的“存档库”，保存着全部历史。<b>不要删除，也不要手动修改</b></div></div>
</div></div>"""

S_CLI = """
<h2 class="head" data-s="1">用命令行也能做到<small>先到 git-scm.com 下载安装 Git for Windows，一路点 Next 即可</small></h2>
""" + term(
    '<div data-s="2">' + PS + '<span class="hi">git --version</span>\n<span class="o">git version 2.51.0.windows.1</span></div>'
    '<div data-s="3">' + PS + '<span class="hi">git config --global user.name "xiaoming"</span>\n'
    + PS + '<span class="hi">git config --global user.email "xiaoming@example.com"</span></div>'
    '<div data-s="4">' + PS + '<span class="hi">git clone https://github.com/xiaoming-dev/my-notes.git</span>\n'
    '<span class="o">Cloning into \'my-notes\'...\nReceiving objects: 100% (9/9), done.</span></div>'
    '<div data-s="5">' + PS + '<span class="hi">cd my-notes</span></div>', style="margin-top:-10px")

SCENES = [
    title_scene(NUM, "安装工具，把仓库“克隆”到你的电脑",
                ["欢迎回来！前面几集，我们都是在网页上操作的。"],
                ["这一集，我们安装工具，把仓库搬到自己的电脑上。"]),
    dict(html=S_WHY, steps=[
        dict(say=["网页上改文件很方便，但只适合小改动。",
                  "真正做项目时，我们需要在电脑上用各种软件来编辑，比如写代码、改文档、处理图片。"]),
        dict(say=["放在 GitHub 上的仓库，叫做远程仓库。"]),
        dict(say=["把它复制到电脑上，就有了一个本地仓库。这个复制的动作，叫做克隆，英文是 clone。"]),
        dict(say=["注意，克隆不是简单的下载文件，而是把整个仓库，连同所有的历史记录，都完整地复制下来。"]),
    ]),
    dict(html=S_TOOLS, steps=[
        dict(say=["要在电脑上使用 Git，有两种工具可以选。"]),
        dict(say=["第一种是 GitHub Desktop，GitHub 官方出品的免费软件。",
                  "它是图形界面，点点按钮就能完成操作，非常适合新手，我们这套课程主要用它来演示。"]),
        dict(say=["第二种是命令行，在一个黑色的窗口里输入命令。它更灵活，程序员用得最多。",
                  "每讲一个操作，我也会顺便告诉你对应的命令，感兴趣的话可以试试。"]),
    ]),
    dict(html=S_DL, steps=[
        dict(say=["先来安装 GitHub Desktop。在浏览器里打开 desktop.github.com。"]),
        dict(say=["点击 Download for Windows，下载安装包。"],
             js="hl('#dl-btn', {pad:8}); cursor('#dl-btn', {click:true, delay:600})"),
        dict(say=["下载完成后，双击运行。它会自动安装，不需要做任何选择，装好后会自动打开。"], js="hl(null)"),
    ]),
    dict(html=S_WELCOME, steps=[
        dict(say=["第一次打开时，会看到欢迎页面。"]),
        dict(say=["点击 Sign in to GitHub.com。这时会跳转到浏览器，确认授权以后，就登录好了。"],
             js="hl('#w-signin', {pad:6}); cursor('#w-signin', {click:true, delay:900})"),
    ]),
    dict(html=S_CONFIG, steps=[
        dict(say=["接着是配置 Git。这里的名字和邮箱，会记录在你以后的每一次提交里。"]),
        dict(say=["选择第一项，使用 GitHub 账号的名字和邮箱，然后点 Finish，完成。"],
             js="hl('#cfg-opt', {pad:6}); cursor('#cfg-fin', {click:true, delay:1200})"),
    ]),
    dict(html=S_CLONE, steps=[
        dict(say=["现在来克隆仓库。点击菜单 File，选择 Clone repository，会打开克隆窗口。"]),
        dict(say=["在 GitHub.com 这一页，会列出你所有的仓库。选中 my-notes。"],
             js="hl('#cl-repo', {pad:4})"),
        dict(say=["下面的 Local path，是仓库保存在电脑上的位置，默认在文档下的 GitHub 文件夹里，一般不用改。"],
             js="hl('#cl-path', {pad:6})"),
        dict(say=["最后点击 Clone。稍等几秒钟，仓库就下载到电脑上了。"],
             js="hl(null); cursor('#cl-go', {click:true})"),
    ]),
    dict(html=S_CODE, steps=[
        dict(say=["另外，在网页上也能发起克隆。仓库首页有个绿色的 Code 按钮，点开它。"],
             js="cursor('#codebtn', {click:true})"),
        dict(say=["这里的网址，是仓库的克隆地址，命令行会用到它。"], js="hl('#cm-url', {pad:4})"),
        dict(say=["点 Open with GitHub Desktop，会直接跳到 GitHub Desktop 里克隆。"], js="hl('#cm-desk', {pad:0})"),
        dict(say=["最下面的 Download ZIP 只是下载一个压缩包，里面只有文件，没有历史记录，也没法同步。",
                  "所以要用 Git 管理项目，一定要用克隆，而不是下载压缩包。"], js="hl('#cm-zip', {pad:0})"),
    ]),
    dict(html=S_DONE, steps=[
        dict(say=["克隆完成后，GitHub Desktop 的界面是这样的。"]),
        dict(say=["左上角显示当前的仓库 my-notes，旁边是当前分支 main。"], js="hl('.ghd-bar .sec', {pad:0})"),
        dict(say=["中间有几个快捷按钮：用代码编辑器打开，或者在文件资源管理器里打开。我们点 Show in Explorer 看一看。"],
             js="hl('#dn-ex', {pad:4}); cursor('#dn-ex .gh-btn', {click:true, delay:900})"),
    ]),
    dict(html=S_EXPLORER_FULL, steps=[
        dict(say=["这就是本地仓库的文件夹。"]),
        dict(say=["里面的文件和网页上一模一样，你可以用任何软件打开、编辑它们。"]),
        dict(say=["如果打开了显示隐藏文件，还会看到一个叫 点 git 的文件夹。"]),
        dict(say=["它是 Git 的存档库，保存着全部的历史记录。千万不要删除，也不要手动修改它。"]),
    ]),
    dict(html=S_CLI, steps=[
        dict(say=["最后看看命令行的做法。先到 git-scm.com 下载安装 Git for Windows，安装时一路点 Next 就行。",
                  "装好后，在开始菜单打开 PowerShell。"]),
        dict(say=["输入 git 空格 杠杠 version，能显示版本号，就说明安装成功了。"]),
        dict(say=["然后用这两条命令，设置你的名字和邮箱。只需要设置一次。"]),
        dict(say=["接着输入 git clone，后面加上仓库的克隆地址，回车，仓库就克隆下来了。",
                  "如果是私有仓库，第一次会弹出浏览器，让你登录 GitHub。"]),
        dict(say=["最后用 cd 命令，进入仓库的文件夹。"]),
    ]),
    summary_scene(NUM, [
        "GitHub 上是远程仓库，电脑上是本地仓库",
        "安装 GitHub Desktop，登录并配置 Git",
        "File → Clone repository 克隆到电脑",
        ".git 文件夹是存档库，不要删",
    ], [
        ["第一，GitHub 上的是远程仓库，电脑上的是本地仓库。"],
        ["第二，安装 GitHub Desktop，登录账号，配置名字和邮箱。"],
        ["第三，用 Clone repository 把仓库克隆到电脑上，不要用下载压缩包代替。"],
        ["第四，点 git 文件夹保存着全部历史，千万不要删。"],
    ], ["下一集，我们在电脑上修改文件，再把修改同步回 GitHub。我们下集见！"]),
]
