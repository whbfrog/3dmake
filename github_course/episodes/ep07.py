from kit import PS, summary_scene, term, title_scene, win

NUM = 7
TITLE = "分支 Branch"

CSS = """
.graph { width:1620px; height:560px; overflow:visible; }
.graph .ln { fill:none; stroke-width:12; stroke-linecap:round; stroke-dasharray:1600; stroke-dashoffset:1600; transition:stroke-dashoffset 1.2s ease, opacity .3s; }
.graph .ln.on { stroke-dashoffset:0; transform:none; }
.graph circle { stroke:#fff; stroke-width:6; }
.graph text { font:700 30px "Source Han Sans SC"; }
.graph .lbl { font:800 34px "JetBrains Mono"; }

.why { display:flex; gap:40px; align-items:stretch; }
.why .card { flex:1; }
.why .emoji { font-size:80px; }
.why h3 { font-size:40px; margin:14px 0; }
.why p { font-size:30px; }

.bmenu { position:absolute; left:250px; top:122px; width:520px; background:#fff; border:1px solid #d0d7de; border-radius:10px; box-shadow:0 12px 32px rgba(31,35,40,.2); font-size:21px; z-index:5; }
.bmenu .h { display:flex; gap:10px; padding:14px; border-bottom:1px solid #d0d7de; }
.bmenu .h .inp { flex:1; height:40px; }
.bmenu .it { padding:12px 18px; } .bmenu .it.act { background:#ddf4ff; }
.bmenu .sec2 { font-size:17px; color:#57606a; padding:10px 18px 4px; }

.cdlg { position:absolute; left:50%; top:130px; transform:translateX(-50%); width:760px; background:#fff; border:1px solid #d0d7de; border-radius:12px; box-shadow:0 20px 60px rgba(0,0,0,.3); z-index:6; font-size:21px; }
.cdlg .dh { padding:16px 24px; border-bottom:1px solid #d0d7de; font-weight:700; font-size:24px; }
.cdlg .dbody { padding:22px 24px; }
.cdlg .df { display:flex; justify-content:flex-end; gap:12px; padding:14px 24px; border-top:1px solid #d0d7de; }
.btnb { background:#0969da; color:#fff; border-radius:6px; padding:9px 24px; font-size:21px; font-weight:600; }

.twoexp { display:flex; gap:40px; }
.twoexp > div { flex:1; }
.twoexp .cap { font-size:32px; font-weight:800; margin-bottom:16px; }
.explorer .path { padding:10px 18px; border-bottom:1px solid #e1e1e1; font-size:20px; color:#333; background:#fafafa; }
.explorer .fl { padding:10px 18px; }
.explorer .fi { display:flex; gap:14px; align-items:center; padding:9px 12px; font-size:24px; }
.explorer .fi .emoji { font-size:30px; }
.explorer .fi.new { background:#dafbe1; border-radius:8px; }
"""

def graph(merge_step=5):
    return f"""
<svg class="graph" viewBox="0 0 1620 560">
  <path class="ln" data-s="2" d="M60 380 L1560 380" stroke="#0969da" />
  <path class="ln" data-s="3" d="M430 380 C 530 380, 530 170, 640 170 L 1080 170" stroke="#8250df" />
  <path class="ln" data-s="{merge_step}" d="M1080 170 C 1190 170, 1190 380, 1290 380" stroke="#8250df" />
  <g data-s="2"><circle cx="130" cy="380" r="30" fill="#0969da"/><circle cx="280" cy="380" r="30" fill="#0969da"/><circle cx="430" cy="380" r="30" fill="#0969da"/>
    <text class="lbl" x="60" y="475" fill="#0969da">main 主线</text><text x="60" y="520" fill="#57606a" style="font-size:24px">稳定可用</text></g>
  <g data-s="3"><text class="lbl" x="640" y="110" fill="#8250df">new-idea 支线</text></g>
  <g data-s="4"><circle cx="740" cy="170" r="30" fill="#8250df"/><circle cx="900" cy="170" r="30" fill="#8250df"/><circle cx="1060" cy="170" r="30" fill="#8250df"/>
    <text x="900" y="250" text-anchor="middle" fill="#8250df">放心尝试，不影响主线</text></g>
  <g data-s="4"><circle cx="700" cy="380" r="30" fill="#0969da"/><text x="700" y="450" text-anchor="middle" fill="#57606a" style="font-size:24px">主线照常更新</text></g>
  <g data-s="{merge_step}"><circle cx="1290" cy="380" r="38" fill="#1f883d"/><text x="1290" y="470" text-anchor="middle" fill="#1f883d">合并 merge</text></g>
</svg>"""

S_WHY = """
<h2 class="head" data-s="1">为什么需要分支？</h2>
<div class="why">
  <div class="card" data-s="2"><div class="emoji">😰</div><h3>没有分支时</h3><p>想试一个大改动，改到一半，原来能用的版本也被改乱了。</p></div>
  <div class="card" data-s="3"><div class="emoji">🌌</div><h3>有了分支</h3><p>另开一个“平行世界”随便尝试。满意了就合并回来，不满意直接丢掉。</p></div>
</div>"""

S_GRAPH = """<h2 class="head" data-s="1">分支长什么样？</h2>""" + graph()

def desk(branch, right="", extra="", sync="<small>Fetch origin</small><b>⟳ Last fetched just now</b>"):
    return win("GitHub Desktop", f"""
<div class="ghd-bar"><div class="sec"><small>Current repository</small><b>my-notes ▾</b></div>
  <div class="sec" id="curbr"><small>Current branch</small><b>⑂ {branch} ▾</b></div><div class="sec wide" id="syncbtn">{sync}</div></div>
<div class="ghd-main"><div class="ghd-left"><div class="ghd-tabs"><span class="act">Changes</span><span>History</span></div>
  <div style="padding:20px;color:#57606a;font-size:20px">0 changed files</div></div><div class="ghd-right">{right}</div></div>{extra}""",
               style="width:1600px;margin:-20px auto 0;position:relative")

S_NEW = desk("main", extra="""
<div class="bmenu" data-s="1"><div class="h"><div class="inp ph">Filter</div><span class="gh-btn" id="nb">New branch</span></div>
  <div class="sec2">Default branch</div><div class="it act">✓ ⑂ main</div></div>
<div class="cdlg" data-s="3"><div class="dh">Create a branch</div><div class="dbody">
  <div class="fld" id="nb-name"><label>Name</label><div class="inp focus"><span class="type" data-s="3" style="--n:13">add-chapter-3</span></div></div>
  <div style="font-size:19px;color:#57606a">Your new branch will be based on your currently checked out branch (main).</div></div>
  <div class="df"><span class="gh-btn">Cancel</span><span class="btnb" id="nb-go">Create branch</span></div></div>""")

PUB = """<div class="ghd-empty"><div style="font-size:30px;font-weight:700;color:#1f2328">No local changes</div>
  <div class="ghd-card" id="pubcard">Publish your branch to GitHub so others can see it.<span class="gh-btn blue">Publish branch</span></div></div>"""
S_ON = desk("add-chapter-3", PUB, sync="<small>Publish branch</small><b>⤒ Publish this branch to GitHub</b>")

EXPL = """<div class="win explorer"><div class="wbar">📁 my-notes<div class="ctl"><span>—</span><span>☐</span><span>✕</span></div></div>
<div class="path">此电脑 › 文档 › GitHub › my-notes › notes</div><div class="fl">
  <div class="fi"><span class="emoji">📄</span>day1.md</div><div class="fi"><span class="emoji">📄</span>day2.md</div>{extra}</div></div>"""
S_SWITCH = """
<h2 class="head" data-s="1">切换分支，文件夹里的内容会跟着变</h2>
<div class="twoexp">
  <div data-s="2"><div class="cap" style="color:var(--purple)">⑂ 在 add-chapter-3 分支</div>""" + EXPL.format(extra='<div class="fi new"><span class="emoji">📄</span>chapter3.md　<span style="color:#1a7f37;font-size:20px">新写的</span></div>') + """</div>
  <div data-s="3"><div class="cap" style="color:var(--blue)">⑂ 切换回 main 分支</div>""" + EXPL.format(extra='<div class="fi" style="color:#8c959f;font-size:22px">（chapter3.md 暂时“消失”了）</div>') + """</div>
</div>
<div class="tip warn" data-s="5" style="margin-top:30px"><span class="emoji">💡</span><div>切换分支之前，<b>先把手头的修改提交</b>，这样最不容易出乱子。</div></div>"""

MERGE_DLG = """<div class="cdlg" data-s="2"><div class="dh">Merge into <span class="sha" style="font-family:'JetBrains Mono'">main</span></div><div class="dbody">
  <div class="inp ph" style="margin-bottom:12px">Filter</div>
  <div style="padding:10px 14px;background:#ddf4ff;border-radius:6px" id="mg-br">⑂ add-chapter-3</div>
  <div style="font-size:19px;color:#1a7f37;margin-top:16px">✓ This will merge 2 commits from add-chapter-3 into main.</div></div>
  <div class="df"><span class="btnb" id="mg-go" style="width:100%;text-align:center">Create a merge commit</span></div></div>"""
S_MERGE = desk("main", extra="""<div class="menu" data-s="1" style="left:250px;top:40px"><div>New branch…</div><div>Rename…</div><div>Delete…</div><hr>
  <div>Update from main</div><div class="act" id="mg-item">Merge into current branch…</div><div>Rebase current branch…</div></div>""" + MERGE_DLG)

S_CLI = """
<h2 class="head" data-s="1">对应的命令</h2>
""" + term(
    '<div data-s="2">' + PS + '<span class="hi">git switch -c add-chapter-3</span>　<span class="cm"># 新建并切换到分支</span>\n'
    + PS + '<span class="hi">git push -u origin add-chapter-3</span>　<span class="cm"># 发布分支</span></div>'
    '<div data-s="3">' + PS + '<span class="hi">git branch</span>　<span class="cm"># 查看所有分支</span>\n<span class="o">* add-chapter-3\n  main</span></div>'
    '<div data-s="4">' + PS + '<span class="hi">git switch main</span>　<span class="cm"># 切换回 main</span>\n'
    + PS + '<span class="hi">git merge add-chapter-3</span>　<span class="cm"># 把支线合并进来</span></div>'
    '<div data-s="5">' + PS + '<span class="hi">git branch -d add-chapter-3</span>　<span class="cm"># 删除用完的分支</span></div>',
    style="margin-top:-10px")

SCENES = [
    title_scene(NUM, "开一个平行世界，放心大胆地尝试",
                ["欢迎回来！前面我们学会了提交和同步。"],
                ["这一集，我们学习 Git 里最强大的功能之一：分支。学会它，你就能放心大胆地做各种尝试。"]),
    dict(html=S_WHY, steps=[
        dict(say=["为什么需要分支呢？设想一下：你的项目现在运行得好好的，但你想试一个大改动。"]),
        dict(say=["如果直接在原来的版本上改，改到一半，原本能用的版本也被改乱了，想撤回都麻烦。"]),
        dict(say=["分支就像开了一个平行世界。你在平行世界里随便尝试，主世界完全不受影响。",
                  "满意了，就把它合并回来；不满意，直接丢掉就好。"]),
    ]),
    dict(html=S_GRAPH, steps=[
        dict(say=["我们用一张图来看看分支长什么样。"]),
        dict(say=["蓝色的这条是主线，叫做 main 分支。仓库创建时自动就有，它应该一直保持稳定、可用。",
                  "每个圆点，代表一次提交。"]),
        dict(say=["从主线的某一次提交开始，我们分出一条紫色的支线，起名叫 new-idea。"]),
        dict(say=["在支线上，你可以提交很多次，放心尝试；同时，主线也可以照常更新，互不干扰。"]),
        dict(say=["等支线上的工作完成了，再把它合并回主线。这个动作，叫做合并，英文是 merge。"]),
    ]),
    dict(html=S_NEW, steps=[
        dict(say=["我们在 GitHub Desktop 里实际操作一下。点击顶部的 Current branch，会列出所有分支，现在只有 main。"]),
        dict(say=["点击 New branch，新建分支。"], js="cursor('#nb', {click:true})"),
        dict(say=["给分支起个名字，比如 add-chapter-3，意思是添加第三章。",
                  "分支名和仓库名一样，用英文小写和短横线，最好能看出要做什么。"], js="hl('#nb-name', {pad:6})"),
        dict(say=["点击 Create branch，分支就创建好了，并且自动切换了过去。"], js="hl(null); cursor('#nb-go', {click:true})"),
    ]),
    dict(html=S_ON, steps=[
        dict(say=["看顶部，当前分支已经变成了 add-chapter-3。"], js="hl('#curbr', {pad:0})"),
        dict(say=["右边多了一个 Publish branch 按钮，意思是发布分支，也就是把这个分支上传到 GitHub。"],
             js="hl('#syncbtn', {pad:0})"),
        dict(say=["接下来，在这个分支上修改文件、提交、推送，和上一集的操作完全一样。"], js="hl(null)"),
    ]),
    dict(html=S_SWITCH, steps=[
        dict(say=["分支有一个神奇的地方。"]),
        dict(say=["假设我们在 add-chapter-3 分支上，新写了一个 chapter3.md 文件，并且提交了。"]),
        dict(say=["现在切换回 main 分支，再看文件夹，chapter3.md 不见了！"]),
        dict(say=["别慌，文件没有丢，它只是保存在另一个分支里。切换回 add-chapter-3，它又会回来。",
                  "Git 会根据你所在的分支，自动把文件夹变成那个分支的样子。"]),
        dict(say=["提醒一下：切换分支之前，最好先把手头的修改提交，这样最不容易出乱子。"]),
    ]),
    dict(html=S_MERGE, steps=[
        dict(say=["第三章写完了，怎么合并回主线呢？",
                  "先切换到 main 分支，然后点击菜单 Branch，选择 Merge into current branch，合并到当前分支。"],
             js="hl('#mg-item', {pad:0})"),
        dict(say=["在弹出的窗口里，选择要合并进来的分支 add-chapter-3。"], js="hl('#mg-br', {pad:4})"),
        dict(say=["点击 Create a merge commit，合并就完成了。最后别忘了 Push，推送到 GitHub。"],
             js="hl(null); cursor('#mg-go', {click:true})"),
        dict(say=["用完的分支，可以在 Branch 菜单里点 Delete 删除。",
                  "不过，在团队合作中，更常用的合并方式是 Pull Request，我们下一集就讲。"]),
    ]),
    dict(html=S_CLI, steps=[
        dict(say=["最后看一下命令行的写法。"]),
        dict(say=["git switch 杠 c 加分支名，新建并切换到这个分支；再用 git push 发布它。"]),
        dict(say=["git branch，查看所有分支，前面带星号的，是你当前所在的分支。"]),
        dict(say=["git switch main 切换回主线，再用 git merge 把支线合并进来。"]),
        dict(say=["最后，git branch 杠 d，删除用完的分支。"]),
    ]),
    summary_scene(NUM, [
        "分支 = 平行世界，放心尝试不影响主线",
        "main 是主线，要保持稳定可用",
        "Current branch → New branch 新建分支",
        "Branch → Merge into current branch 合并",
    ], [
        ["第一，分支就像平行世界，可以放心尝试，不影响主线。"],
        ["第二，main 是主线分支，要一直保持稳定可用。"],
        ["第三，在 Current branch 里点 New branch，就能新建分支。"],
        ["第四，切换到 main，用 Merge into current branch 把支线合并回来。"],
    ], ["下一集，我们学习团队协作的核心：Pull Request。我们下集见！"]),
]
