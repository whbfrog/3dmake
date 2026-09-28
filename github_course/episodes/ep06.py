from kit import PS, summary_scene, term, title_scene, win

NUM = 6
TITLE = "本地修改与同步"

CSS = """
.sync { position:relative; height:600px; }
.sync .box { position:absolute; top:150px; width:420px; height:300px; border-radius:30px; background:#fff; box-shadow:0 12px 36px rgba(31,35,40,.10);
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; border:4px solid #e1e6eb; }
.sync .box .emoji { font-size:100px; } .sync .box b { font-size:40px; } .sync .box span { font-size:28px; color:var(--muted); }
.sync .arr { position:absolute; left:560px; width:500px; text-align:center; font-size:34px; font-weight:800; }
.sync .arr::after { content:""; display:block; height:10px; margin-top:10px; background:currentColor;
  clip-path:polygon(0 30%, 94% 30%, 94% 0, 100% 50%, 94% 100%, 94% 70%, 0 70%); }
.sync .arr.l::after { transform:scaleX(-1); }
.sync .cm { position:absolute; left:40px; top:470px; width:420px; text-align:center; font-size:30px; font-weight:800; color:var(--purple); }

.vsc { background:#1e1e1e; color:#d4d4d4; }
.vsc .side { width:320px; background:#252526; padding:16px; font-size:20px; }
.vsc .side div { padding:6px 10px; }
.vsc .side div.act { background:#37373d; }
.vsc .ed { flex:1; font:23px/1.75 "JetBrains Mono","Source Han Sans SC"; padding:20px 0; }
.vsc .ed div { display:flex; } .vsc .ed i { width:60px; text-align:right; padding-right:22px; color:#6e7681; font-style:normal; }
.vsc .tab { background:#1e1e1e; padding:10px 20px; font-size:19px; border-top:2px solid #0078d4; display:inline-block; }

.hbar { padding:14px 16px; font-size:19px; border-bottom:1px solid #eef1f4; }
.hbar b { display:block; font-size:20px; }
.hbar span { color:#57606a; }
.hbar.sel { background:#ddf4ff; }

.daily { display:flex; gap:24px; align-items:center; justify-content:center; margin-top:10px; }
.daily .d { width:330px; background:#fff; border-radius:24px; padding:30px 26px; text-align:center; box-shadow:0 10px 30px rgba(31,35,40,.08); }
.daily .d .emoji { font-size:74px; } .daily .d b { display:block; font-size:38px; margin:12px 0 6px; } .daily .d span { font-size:26px; color:var(--muted); }
.daily .ar { font-size:48px; color:var(--muted); }
"""

S_BIG = """
<h2 class="head" data-s="1">同步的三个动作</h2>
<div class="sync">
  <div class="box" data-s="1" style="left:40px;border-color:var(--blue)"><div class="emoji">💻</div><b>本地仓库</b><span>你的电脑</span></div>
  <div class="box" data-s="1" style="left:1100px;border-color:var(--green)"><div class="emoji">☁️</div><b>远程仓库</b><span>GitHub</span></div>
  <div class="cm" data-s="2">① Commit 提交：在本地存档</div>
  <div class="arr" data-s="3" style="top:200px;color:var(--green)">② Push 推送：上传 ↑</div>
  <div class="arr l" data-s="4" style="top:330px;color:var(--blue)">③ Pull 拉取：下载 ↓</div>
</div>"""

S_EDIT = win("day2.md - my-notes - Visual Studio Code", """
<div style="display:flex;height:560px" class="vsc">
  <div class="side"><div style="color:#bbb;font-size:17px">EXPLORER › MY-NOTES</div><div>› .git</div><div>⌄ notes</div>
    <div style="padding-left:30px">day1.md</div><div class="act" style="padding-left:30px" data-s="2">day2.md <span style="color:#73c991">U</span></div><div>README.md <span style="color:#e2c08d" data-s="3">M</span></div></div>
  <div style="flex:1;display:flex;flex-direction:column"><div style="background:#252526"><span class="tab">day2.md</span></div>
    <div class="ed">
      <div data-s="2"><i>1</i><span class="type" data-s="2" style="--n:10;color:#569cd6"># 第二天：本地同步</span></div>
      <div data-s="2"><i>2</i></div>
      <div data-s="2"><i>3</i><span class="type" data-s="2" style="--n:12">- 安装了 GitHub Desktop</span></div>
      <div data-s="2"><i>4</i><span class="type" data-s="2" style="--n:12">- 把仓库克隆到了电脑上</span></div>
    </div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

def desktop(branch_btn, files, right, commit_box, extra=""):
    return win("GitHub Desktop", f"""
<div class="ghd-bar"><div class="sec"><small>Current repository</small><b>my-notes ▾</b></div><div class="sec"><small>Current branch</small><b>⑂ main ▾</b></div>
  <div class="sec wide" id="syncbtn">{branch_btn}</div></div>
<div class="ghd-main"><div class="ghd-left">{files}{commit_box}</div><div class="ghd-right">{right}</div></div>{extra}""",
               style="width:1600px;margin:-20px auto 0;position:relative")

FILES = """<div class="ghd-tabs"><span class="act">Changes 2</span><span>History</span></div>
  <div style="padding:8px 16px;font-size:19px;color:#57606a;border-bottom:1px solid #eef1f4">2 changed files</div>
  <div class="ghd-file sel" id="f-new"><span class="cb">✓</span>notes\\day2.md<span class="st add">+</span></div>
  <div class="ghd-file" id="f-mod"><span class="cb">✓</span>README.md<span class="st">•</span></div>"""

DIFF = """<div class="diff"><div class="fh">notes\\day2.md</div>
  <div class="l add"><i>1</i>+# 第二天：本地同步</div><div class="l add"><i>2</i>+</div>
  <div class="l add"><i>3</i>+- 安装了 GitHub Desktop</div><div class="l add"><i>4</i>+- 把仓库克隆到了电脑上</div></div>"""

def cbox(msg="", typed=False):
    inner = f'<span class="type" data-s="2" style="--n:9">{msg}</span>' if typed else (msg or "Summary (required)")
    cls = "inp filled" if msg else "inp"
    return f"""<div class="ghd-commit" id="cbox"><div class="{cls}" id="c-sum">{inner}</div><div class="inp area" id="c-desc">Description</div>
    <div class="btn" id="c-go">Commit 2 files to <b>main</b></div></div>"""

FETCH = "<small>Fetch origin</small><b>⟳ Last fetched 5 minutes ago</b>"
PUSH = "<small>Push origin</small><b>↑ Push origin <span class='pill' style='background:#0969da;color:#fff'>1</span></b>"
PULL = "<small>Pull origin</small><b>↓ Pull origin <span class='pill' style='background:#0969da;color:#fff'>1</span></b>"

S_CHANGES = desktop(FETCH, FILES, DIFF, cbox())
S_COMMIT = desktop(FETCH, FILES, DIFF, cbox("添加第二天的笔记", typed=True))
EMPTY_FILES = """<div class="ghd-tabs"><span class="act">Changes</span><span>History</span></div>
  <div style="padding:20px;color:#57606a;font-size:20px">0 changed files</div>"""
UNDO = """<div class="ghd-commit" id="undo" data-s="3" style="display:flex;align-items:center;gap:12px;font-size:19px">
  <div style="flex:1">Committed just now<br><b>添加第二天的笔记</b></div><span class="gh-btn">Undo</span></div>"""
PUSH_RIGHT = """<div class="ghd-empty"><div style="font-size:30px;font-weight:700;color:#1f2328">No local changes</div>
  <div class="ghd-card" id="push-card">You have 1 local commit waiting to be pushed to GitHub.<span class="gh-btn blue">Push origin</span></div></div>"""
S_PUSH = desktop(PUSH, EMPTY_FILES, PUSH_RIGHT, UNDO)
PULL_RIGHT = """<div class="ghd-empty"><div style="font-size:30px;font-weight:700;color:#1f2328">No local changes</div>
  <div class="ghd-card">The current branch has 1 commit on GitHub that is not on your computer.<span class="gh-btn blue">Pull origin</span></div></div>"""
S_PULL = desktop(FETCH, EMPTY_FILES, PULL_RIGHT, "")

HIST_FILES = """<div class="ghd-tabs"><span>Changes</span><span class="act">History</span></div>
  <div class="hbar"><b>在网页上修改了 README</b><span>xiaoming-dev · 1 分钟前</span></div>
  <div class="hbar sel" id="h-sel"><b>添加第二天的笔记</b><span>xiaoming-dev · 10 分钟前</span></div>
  <div class="hbar"><b>添加第一天的笔记</b><span>xiaoming-dev · 1 小时前</span></div>
  <div class="hbar"><b>记录今天的学习内容</b><span>xiaoming-dev · 1 小时前</span></div>
  <div class="hbar"><b>Initial commit</b><span>xiaoming-dev · 2 小时前</span></div>"""
S_HIST = desktop(FETCH, HIST_FILES, DIFF, "")

S_CLI = """
<h2 class="head" data-s="1">对应的命令<small>在仓库文件夹里打开 PowerShell 输入</small></h2>
""" + term(
    '<div data-s="2">' + PS.replace("xiaoming&gt;", "xiaoming\\my-notes&gt;") + '<span class="hi">git status</span>　<span class="cm"># 看看改了哪些文件</span>\n'
    '<span class="o">modified:   README.md\nUntracked files:  notes/day2.md</span></div>'
    '<div data-s="3">' + PS.replace("xiaoming&gt;", "xiaoming\\my-notes&gt;") + '<span class="hi">git add .</span>　<span class="cm"># 选中所有改动</span></div>'
    '<div data-s="4">' + PS.replace("xiaoming&gt;", "xiaoming\\my-notes&gt;") + '<span class="hi">git commit -m "添加第二天的笔记"</span>　<span class="cm"># 提交</span></div>'
    '<div data-s="5">' + PS.replace("xiaoming&gt;", "xiaoming\\my-notes&gt;") + '<span class="hi">git push</span>　<span class="cm"># 推送到 GitHub</span>\n'
    + PS.replace("xiaoming&gt;", "xiaoming\\my-notes&gt;") + '<span class="hi">git pull</span>　<span class="cm"># 拉取最新内容</span></div>',
    style="margin-top:-10px")

S_DAILY = """
<h2 class="head" data-s="1">养成每天的好习惯</h2>
<div class="daily">
  <div class="d" data-s="2"><div class="emoji">⬇️</div><b>Pull</b><span>开工前，先拉取最新内容</span></div><div class="ar" data-s="3">›</div>
  <div class="d" data-s="3"><div class="emoji">✏️</div><b>修改</b><span>编辑你的文件</span></div><div class="ar" data-s="4">›</div>
  <div class="d" data-s="4"><div class="emoji">💾</div><b>Commit</b><span>完成一件事，就提交一次</span></div><div class="ar" data-s="5">›</div>
  <div class="d" data-s="5"><div class="emoji">⬆️</div><b>Push</b><span>收工前，推送到 GitHub</span></div>
</div>"""

SCENES = [
    title_scene(NUM, "修改 → 提交 → 推送，学会同步",
                ["欢迎回来！上一集，我们把仓库克隆到了电脑上。"],
                ["这一集，我们在电脑上修改文件，再把修改同步回 GitHub。这是日常使用中最核心的操作。"]),
    dict(html=S_BIG, steps=[
        dict(say=["先看一张图。左边是你电脑上的本地仓库，右边是 GitHub 上的远程仓库。"]),
        dict(say=["第一个动作是提交，Commit。在本地修改完文件后，先在自己电脑上存个档。"]),
        dict(say=["第二个动作是推送，Push。把本地的存档上传到 GitHub。"]),
        dict(say=["第三个动作是拉取，Pull。把 GitHub 上的新内容下载到电脑上。",
                  "记住这三个词：提交是存档，推送是上传，拉取是下载。"]),
    ]),
    dict(html=S_EDIT, steps=[
        dict(say=["我们先在电脑上修改文件。用什么软件都可以，这里用的是免费的代码编辑器 Visual Studio Code。"]),
        dict(say=["我们在 notes 文件夹里，新建一个文件 day2.md，写上第二天的笔记。"]),
        dict(say=["再顺手改一下 README 文件。改完记得按 Ctrl 加 S 保存。"]),
    ]),
    dict(html=S_CHANGES, steps=[
        dict(say=["切换到 GitHub Desktop，它会自动发现你的修改。"]),
        dict(say=["左边的 Changes 列表里，列出了改动过的文件。",
                  "绿色加号表示新增的文件，黄色圆点表示修改过的文件。"], js="hl('#f-new', {pad:2})"),
        dict(say=["点击一个文件，右边就会显示具体的改动，和网页上一样，绿色是新增的内容。"], js="hl('.ghd-right', {pad:0})"),
        dict(say=["每个文件前面的勾选框，决定这次提交要包含哪些文件，默认全部勾选。"], js="hl('#f-mod .cb', {pad:6})"),
    ]),
    dict(html=S_COMMIT, steps=[
        dict(say=["接下来提交。左下角是提交区域。"], js="hl('#cbox', {pad:0})"),
        dict(say=["在 Summary 里写一句提交说明：添加第二天的笔记。下面的 Description 可以不填。"], js="hl('#c-sum', {pad:4})"),
        dict(say=["然后点击蓝色的 Commit to main 按钮。"], js="hl(null); cursor('#c-go', {click:true})"),
    ]),
    dict(html=S_PUSH, steps=[
        dict(say=["提交完成！不过要注意，这次提交只存在你的电脑上，GitHub 网页上还看不到。"]),
        dict(say=["看右上角，按钮变成了 Push origin，旁边的数字 1，表示有一个提交等待上传。",
                  "点击它，就会把提交推送到 GitHub。"], js="hl('#syncbtn', {pad:0}); cursor('#syncbtn', {fx:.2, click:true, delay:1500})"),
        dict(say=["另外，提交之后左下角会出现一个 Undo 按钮。如果发现提交错了，在推送之前点它，就能撤销这次提交。"],
             js="hl('#undo', {pad:0})"),
        dict(say=["推送完成后，刷新 GitHub 网页，就能看到刚才的提交了。"], js="hl(null)"),
    ]),
    dict(html=S_PULL, steps=[
        dict(say=["反过来，如果你在网页上改了文件，或者在另一台电脑上推送了新提交，",
                  "本地的仓库就落后了，这时要用拉取。"]),
        dict(say=["点击右上角的 Fetch origin，它会检查 GitHub 上有没有新内容。"],
             js="hl('#syncbtn', {pad:0})"),
        dict(say=["如果有，按钮就会变成 Pull origin，点击它，新内容就下载到你的电脑上了。"],
             js="document.querySelector('.scene:not(.leave) #syncbtn').innerHTML = \"" + PULL.replace('"', '\\"') + "\"; cursor('#syncbtn', {fx:.2, click:true, delay:600})"),
    ]),
    dict(html=S_HIST, steps=[
        dict(say=["点击左边的 History 标签，可以查看所有的提交历史。"]),
        dict(say=["选中一个提交，右边就会显示这次提交改了什么。和网页上的历史记录是一样的。"], js="hl('#h-sel', {pad:0})"),
    ]),
    dict(html=S_CLI, steps=[
        dict(say=["同样的操作，用命令行也能完成。"]),
        dict(say=["git status，查看有哪些文件改动了。"]),
        dict(say=["git add 空格 点，把所有改动都选中，相当于在 Desktop 里打勾。"]),
        dict(say=["git commit 杠 m，后面跟上引号括起来的提交说明，完成提交。"]),
        dict(say=["最后，git push 推送，git pull 拉取。"]),
    ]),
    dict(html=S_DAILY, steps=[
        dict(say=["最后，给你一个每天使用的好习惯。"]),
        dict(say=["开始工作前，先 Pull，拉取最新的内容；"]),
        dict(say=["然后修改文件；"]),
        dict(say=["每完成一件小事，就 Commit 提交一次；"]),
        dict(say=["结束工作前，Push 推送到 GitHub。这样云端永远有一份最新的备份。"]),
    ]),
    summary_scene(NUM, [
        "Commit 提交：在本地存档",
        "Push 推送：上传到 GitHub",
        "Pull 拉取：从 GitHub 下载更新",
        "每天：先 Pull，再修改、Commit，最后 Push",
    ], [
        ["第一，Commit 提交，是在自己电脑上存档。"],
        ["第二，Push 推送，是把存档上传到 GitHub。"],
        ["第三，Pull 拉取，是把 GitHub 上的更新下载下来。"],
        ["第四，每天开工先拉取，收工前推送。"],
    ], ["下一集，我们来学习 Git 里一个非常强大的功能：分支。我们下集见！"]),
]
