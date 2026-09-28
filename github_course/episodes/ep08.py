from kit import browser, gh_top, repo_tabs, summary_scene, title_scene

NUM = 8
TITLE = "Pull Request 协作"

CSS = """
.flow .fb { min-width:260px; }
.banner-y { background:#fff8c5; border:1px solid #d4a72c; border-radius:10px; padding:14px 20px; display:flex; align-items:center; gap:14px; font-size:21px; margin-bottom:16px; }
.banner-y .gh-btn { margin-left:auto; }
.cmpbar { display:flex; gap:12px; align-items:center; border:1px solid #d0d7de; border-radius:10px; padding:12px 16px; font-size:20px; background:#f6f8fa; margin-bottom:18px; }
.cmpbar .ok { color:#1a7f37; margin-left:10px; }
.prform { display:flex; gap:26px; }
.prform .main { flex:1; }
.prform .sideb { width:330px; font-size:19px; color:#59636e; }
.prform .sideb div { border-bottom:1px solid #d0d7de; padding:12px 0; }
.prform .sideb b { color:#1f2328; display:block; }
.md-area { border:1px solid #d0d7de; border-radius:8px; min-height:170px; padding:12px 16px; font:20px/1.6 "JetBrains Mono","Source Han Sans SC"; white-space:pre-wrap; }
.prhead { font-size:34px; font-weight:400; margin-bottom:10px; } .prhead b { font-weight:700; }
.prmeta { display:flex; align-items:center; gap:14px; font-size:20px; color:#59636e; padding-bottom:16px; border-bottom:1px solid #d0d7de; }
.prtabs { display:flex; gap:6px; border-bottom:1px solid #d0d7de; margin:16px 0; font-size:20px; }
.prtabs span { padding:10px 16px; } .prtabs span.act { border:1px solid #d0d7de; border-bottom-color:#fff; border-radius:8px 8px 0 0; margin-bottom:-1px; background:#fff; font-weight:700; }
.prtabs i { font-style:normal; background:#eef1f4; border-radius:999px; padding:0 8px; margin-left:6px; font-size:16px; }
.tlc { border:1px solid #d0d7de; border-radius:10px; overflow:hidden; margin-bottom:14px; }
.tlc .th { background:#f6f8fa; padding:10px 16px; font-size:19px; border-bottom:1px solid #d0d7de; }
.tlc .tb { padding:14px 18px; font-size:21px; }
.mergebox { border:2px solid #1f883d; border-radius:12px; padding:18px 22px; display:flex; align-items:center; gap:16px; font-size:21px; }
.mergebox.bad { border-color:#9a6700; }
.mergebox .ic { width:48px; height:48px; border-radius:50%; background:#1f883d; color:#fff; display:grid; place-items:center; font-size:26px; flex:none; }
.mergebox.bad .ic { background:#9a6700; }
.mergebox.done { border-color:#8250df; } .mergebox.done .ic { background:#8250df; }
.rv { position:absolute; right:40px; top:120px; width:560px; background:#fff; border:1px solid #d0d7de; border-radius:12px; box-shadow:0 12px 32px rgba(31,35,40,.2); font-size:20px; z-index:5; }
.rv .h { padding:14px 18px; border-bottom:1px solid #d0d7de; font-weight:700; }
.rv .b { padding:14px 18px; }
.inl { margin:6px 0 6px 64px; border:1px solid #d0d7de; border-radius:10px; font-family:"Source Han Sans SC"; white-space:normal; background:#fff; }
.inl .th { background:#f6f8fa; padding:8px 14px; font-size:18px; border-bottom:1px solid #d0d7de; }
.inl .tb { padding:10px 14px; font-size:20px; }
.conf { font:23px/1.8 "JetBrains Mono","Source Han Sans SC"; }
.conf div { padding:0 18px; max-height:60px; overflow:hidden; transition:max-height .5s ease, opacity .4s; }
.conf div.off { max-height:0; }
.conf .mk { color:#cf222e; font-weight:700; background:#fff5f5; }
.conf .ours { background:#ddf4ff; } .conf .theirs { background:#fbefff; }
.conf-note { display:flex; flex-direction:column; gap:18px; width:520px; flex:none; }
.conf-note .tip { font-size:27px; padding:18px 24px; }
"""

S_WHAT = """
<h2 class="head" data-s="1">什么是 Pull Request？<small>“我在分支上改好了，请大家检查一下，再合并进 main”</small></h2>
<div class="flow" style="margin-top:40px">
  <div class="fb" data-s="2"><span class="emoji">⑂</span><b>分支上改好</b><span>提交并推送</span></div><div class="fa" data-s="3"></div>
  <div class="fb" data-s="3" style="border-color:var(--green)"><span class="emoji">📬</span><b>发起 PR</b><span>说明改了什么</span></div><div class="fa" data-s="4"></div>
  <div class="fb" data-s="4" style="border-color:var(--orange)"><span class="emoji">🔍</span><b>审查讨论</b><span>别人检查、提意见</span></div><div class="fa" data-s="5"></div>
  <div class="fb" data-s="5" style="border-color:var(--purple)"><span class="emoji">🔀</span><b>合并 Merge</b><span>进入 main 主线</span></div>
</div>"""

REPO = gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs()
REPO_PR = gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs("Pull requests", "1")
S_BANNER = browser("https://github.com/xiaoming-dev/my-notes", REPO + """
<div class="gh-body" style="height:470px">
  <div class="banner-y" id="yb">⑂ <b>add-chapter-3</b> had recent pushes 1 minute ago<span class="gh-btn green" id="cmp">Compare &amp; pull request</span></div>
  <div class="gh-title">my-notes <span class="gh-pill">Public</span></div>
  <div class="gh-box"><div class="head"><b>xiaoming-dev</b> 添加第二天的笔记<span class="count">🕘 5 Commits</span></div>
    <div class="gh-row"><i class="ico-dir"></i>notes</div><div class="gh-row"><i class="ico-file"></i>README.md</div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_OPEN = browser("https://github.com/xiaoming-dev/my-notes/compare/main...add-chapter-3", REPO + """
<div class="gh-body">
  <div style="font-size:30px;margin-bottom:12px">Open a pull request</div>
  <div class="cmpbar" id="cmpbar">⇆ <span class="gh-btn" style="height:34px">base: main ▾</span> ← <span class="gh-btn" style="height:34px">compare: add-chapter-3 ▾</span>
    <span class="ok">✓ <b>Able to merge.</b> These branches can be automatically merged.</span></div>
  <div class="prform"><div class="main">
    <div class="fld" id="pr-title"><label>Add a title</label><div class="inp focus"><span class="type" data-s="3" style="--n:9">添加第三章：分支</span></div></div>
    <div class="fld" id="pr-desc"><label>Add a description</label><div class="md-area"><span data-s="4" class="fade">## 改了什么
- 新增 notes/chapter3.md，介绍分支的用法

@xiaohong 帮忙看看有没有错别字，谢谢！</span></div></div>
    <div style="display:flex;justify-content:flex-end"><span class="gh-btn green" id="pr-go">Create pull request</span></div>
  </div>
  <div class="sideb" id="pr-side"><div><b>Reviewers ⚙</b>xiaohong</div><div><b>Assignees ⚙</b>xiaoming-dev</div><div><b>Labels ⚙</b>None yet</div></div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

PRHEAD = """<div class="prhead">添加第三章：分支 <span style="color:#59636e">#1</span></div>
  <div class="prmeta">{state}<span><b>xiaoming-dev</b> wants to merge 2 commits into <span class="sha">main</span> from <span class="sha">add-chapter-3</span></span></div>
  <div class="prtabs" id="prtabs"><span class="{c1}">💬 Conversation <i>1</i></span><span>Commits <i>2</i></span><span>Checks <i>0</i></span><span class="{c2}">± Files changed <i>1</i></span></div>"""
OPEN_STATE = '<span class="state open">⇄ Open</span>'
URL1 = "https://github.com/xiaoming-dev/my-notes/pull/1"

S_PR = browser(URL1, REPO_PR + """
<div class="gh-body">""" + PRHEAD.format(state=OPEN_STATE, c1="act", c2="") + """
  <div class="tlc"><div class="th"><b>xiaoming-dev</b> commented just now</div><div class="tb">## 改了什么<br>- 新增 notes/chapter3.md，介绍分支的用法</div></div>
  <div class="mergebox" id="mb"><div class="ic">✓</div><div><b>This branch has no conflicts with the base branch</b><br><span style="color:#59636e;font-size:19px">Merging can be performed automatically.</span></div>
    <span class="gh-btn green" style="margin-left:auto" id="mb-go">Merge pull request ▾</span></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_REVIEW = browser(URL1 + "/files", REPO_PR + """
<div class="gh-body" style="position:relative">""" + PRHEAD.format(state=OPEN_STATE, c1="", c2="act") + """
  <div class="gh-box diff"><div class="fh">notes/chapter3.md</div>
    <div class="l add"><i>1</i>+# 第三章：分支</div>
    <div class="l add" id="bad-line"><i>2</i>+分之就像一个平行世界。</div>
    <div class="inl" data-s="2"><div class="th"><b>xiaohong</b> · 审查意见</div><div class="tb">这里有个错别字：“分之”应该是“分支” 😄</div></div>
    <div class="l add"><i>3</i>+在支线上可以放心尝试。</div>
  </div>
  <div class="rv" data-s="3"><div class="h">Finish your review</div><div class="b">
    <div class="opt"><div class="r"></div><div><b>Comment</b><small>只是评论，不表态</small></div></div>
    <div class="opt"><div class="r on2"></div><div><b>Approve</b><small>同意合并</small></div></div>
    <div class="opt"><div class="r"></div><div><b>Request changes</b><small>需要修改后才能合并</small></div></div>
    <span class="gh-btn green">Submit review</span></div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

MERGED_STATE = '<span class="state merged">⇄ Merged</span>'
S_MERGED = browser(URL1, REPO_PR + """
<div class="gh-body">""" + PRHEAD.format(state=MERGED_STATE, c1="act", c2="").replace("wants to merge", "merged") + """
  <div class="tlc"><div class="th"><b>xiaohong</b> approved these changes</div><div class="tb">✅ 看过了，没问题！</div></div>
  <div class="mergebox done" id="mdone"><div class="ic">⇄</div><div><b>Pull request successfully merged and closed</b><br><span style="color:#59636e;font-size:19px">The add-chapter-3 branch can be safely deleted.</span></div>
    <span class="gh-btn" style="margin-left:auto" id="delbr">Delete branch</span></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_CONFLICT = """
<h2 class="head" data-s="1">遇到“冲突”怎么办？</h2>
<div class="row" style="gap:36px;align-items:flex-start">
""" + browser(URL1 + "/conflicts", """
<div style="display:flex;align-items:center;padding:12px 18px;border-bottom:1px solid #d0d7de;font-size:20px"><b>notes/chapter3.md</b><span style="margin-left:14px;color:#cf222e">1 conflict</span>
  <span class="gh-btn" style="margin-left:auto" id="resolved">✓ Mark as resolved</span></div>
<div class="conf">
  <div>2 # 第三章：分支</div>
  <div class="mk" data-hide="5">&lt;&lt;&lt;&lt;&lt;&lt;&lt; add-chapter-3</div>
  <div class="ours" id="ours">今天学习了分支</div>
  <div class="mk" data-hide="5">=======</div>
  <div class="theirs" id="theirs" data-hide="5">今天学习了 Branch</div>
  <div class="mk" data-hide="5">&gt;&gt;&gt;&gt;&gt;&gt;&gt; main</div>
</div>""", style="flex:1") + """
<div class="conf-note">
  <div class="tip warn" data-s="2"><span class="emoji">⚔️</span><div>两个人改了<b>同一处</b>，而且改得不一样，Git 不知道该听谁的。</div></div>
  <div class="tip" data-s="3"><span class="emoji">🔵</span><div>上面是你的分支，下面是 main 的内容。</div></div>
  <div class="tip good" data-s="5"><span class="emoji">✂️</span><div>删掉标记符号，只留下想要的内容，再点 Mark as resolved。</div></div>
</div></div>"""

SCENES = [
    title_scene(NUM, "请别人检查，再合并进主线",
                ["欢迎回来！上一集我们学会了分支，也在电脑上完成了合并。"],
                ["不过在团队里，合并之前通常要请别人先检查一下。这一集要讲的 Pull Request，就是做这件事的。"]),
    dict(html=S_WHAT, steps=[
        dict(say=["Pull Request，中文常叫拉取请求，大家也简称 PR。",
                  "它的意思是：我在分支上改好了，请大家检查一下，再合并进主线。"]),
        dict(say=["完整的流程是这样的：先在分支上修改、提交，并推送到 GitHub；"]),
        dict(say=["然后在 GitHub 上发起一个 PR，说明你改了什么；"]),
        dict(say=["其他人会审查你的修改，提出意见，大家一起讨论；"]),
        dict(say=["确认没问题后，再把它合并进 main。"]),
    ]),
    dict(html=S_BANNER, steps=[
        dict(say=["我们来实际操作。把 add-chapter-3 分支推送到 GitHub 以后，打开仓库页面，",
                  "顶部会出现一条黄色的提示，说这个分支刚刚有新的推送。"], js="hl('#yb', {pad:4})"),
        dict(say=["点击右边的 Compare and pull request 按钮，开始创建 PR。",
                  "在 GitHub Desktop 里推送以后，也会出现一个 Create Pull Request 的按钮，效果一样。"],
             js="hl(null); cursor('#cmp', {click:true})"),
    ]),
    dict(html=S_OPEN, steps=[
        dict(say=["这是创建 PR 的页面。"]),
        dict(say=["最上面这一行表示合并的方向：把 add-chapter-3 合并到 main，箭头从右指向左。",
                  "后面的绿色文字 Able to merge，表示可以自动合并，没有冲突。"], js="hl('#cmpbar', {pad:4})"),
        dict(say=["填写一个标题，说清楚这个 PR 做了什么，比如：添加第三章，分支。"], js="hl('#pr-title', {pad:6})"),
        dict(say=["在描述里，写上具体改了什么，还可以用 at 符号加用户名，请某个人来帮忙看看。"], js="hl('#pr-desc', {pad:6})"),
        dict(say=["右边的 Reviewers，可以指定审查的人。都填好后，点击 Create pull request。"],
             js="hl('#pr-side', {pad:6}); cursor('#pr-go', {click:true, delay:1500})"),
    ]),
    dict(html=S_PR, steps=[
        dict(say=["PR 创建好了！标题后面的井号 1，是它的编号。绿色的 Open，表示它正在进行中。"]),
        dict(say=["下面有几个标签：Conversation 是讨论区；Commits 是包含的提交；Files changed 是改动的文件。"],
             js="hl('#prtabs', {pad:2})"),
        dict(say=["页面最下方是合并区域，我们等审查通过了再来点它。"], js="hl('#mb', {pad:4})"),
    ]),
    dict(html=S_REVIEW, steps=[
        dict(say=["现在切换到审查者的角度。打开 Files changed，就能看到所有改动。"]),
        dict(say=["审查者发现第二行有个错别字，在这一行上点加号，写下一条意见。"], js="hl('#bad-line', {pad:2})"),
        dict(say=["看完以后，点击 Review changes 提交审查结果，有三个选项：",
                  "Comment 只是评论；Approve 是同意合并；Request changes 是要求修改后才能合并。"], js="hl(null)"),
        dict(say=["作为作者，收到意见后，只要在同一个分支上继续修改、提交、推送，PR 就会自动更新，不用重新创建。"]),
    ]),
    dict(html=S_PR, steps=[
        dict(say=["审查通过以后，回到 Conversation 页面，点击绿色的 Merge pull request，再点 Confirm merge 确认。"],
             js="hl('#mb', {pad:4}); cursor('#mb-go', {click:true, delay:1500})"),
    ]),
    dict(html=S_MERGED, steps=[
        dict(say=["合并成功！状态变成了紫色的 Merged，表示已经合并。"]),
        dict(say=["旁边会出现 Delete branch 按钮。分支的使命已经完成，可以放心删除。"],
             js="hl('#delbr', {pad:6})"),
        dict(say=["最后别忘了，在电脑上切换回 main 分支，拉取一下，把合并后的内容同步到本地。"], js="hl(null)"),
    ]),
    dict(html=S_CONFLICT, steps=[
        dict(say=["合并时，偶尔会遇到一种情况，叫做冲突。"]),
        dict(say=["冲突是指：两个分支修改了同一个文件的同一处地方，而且改得不一样，Git 不知道该听谁的。",
                  "这时 PR 页面会提示有冲突，并出现一个 Resolve conflicts 按钮，点击它。"]),
        dict(say=["冲突的地方会用特殊的符号标出来。小于号和等号之间，是你的分支的内容；"], js="hl('#ours', {pad:2})"),
        dict(say=["等号和大于号之间，是 main 上的内容。"], js="hl('#theirs', {pad:2})"),
        dict(say=["解决方法很简单：删掉这些标记符号，只留下你想要的内容。",
                  "然后点击 Mark as resolved，标记为已解决，再提交，就可以正常合并了。"],
             js="hl('#resolved', {pad:6})"),
    ]),
    summary_scene(NUM, [
        "PR = 请别人检查修改，再合并进 main",
        "推送分支 → Compare & pull request",
        "审查：Comment / Approve / Request changes",
        "冲突：删掉标记，保留想要的内容",
    ], [
        ["第一，Pull Request 就是请别人检查你的修改，同意后再合并进 main。"],
        ["第二，推送分支后，点击 Compare and pull request 就能创建。"],
        ["第三，审查时可以评论、同意，或者要求修改。"],
        ["第四，遇到冲突不要慌，删掉标记符号，保留想要的内容就行。",
         "另外，就算只有你一个人，也可以用 PR 来管理自己的修改，这是个很好的习惯。"],
    ], ["下一集，我们走出自己的仓库，去参与别人的开源项目。我们下集见！"]),
]
