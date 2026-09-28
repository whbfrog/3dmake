from kit import browser, gh_top, repo_tabs, summary_scene, title_scene

NUM = 3
TITLE = "创建第一个仓库"

CSS = """
.newform { padding:30px 60px; font-size:22px; }
.newform h2 { font-size:34px; margin:0 0 6px; }
.newform .sub { color:#59636e; margin-bottom:22px; font-size:20px; }
.own { display:flex; align-items:flex-end; gap:14px; }
.own .slash { font-size:34px; padding-bottom:4px; }
.side-tips { display:flex; flex-direction:column; gap:22px; width:560px; flex:none; }
.side-tips .tip { font-size:28px; padding:20px 26px; }
.cfg { border:1px solid #d0d7de; border-radius:10px; }
.cfg .rowc { display:flex; align-items:center; gap:16px; padding:18px 22px; border-top:1px solid #d0d7de; }
.cfg .rowc:first-child { border-top:0; }
.cfg .rowc .t b { display:block; font-size:22px; } .cfg .rowc .t small { color:#59636e; font-size:18px; }
.cfg .ctrl { margin-left:auto; }
.toggle { width:64px; height:34px; border-radius:17px; background:#d0d7de; position:relative; }
.toggle::after { content:""; position:absolute; left:4px; top:4px; width:26px; height:26px; border-radius:50%; background:#fff; transition:left .4s; }
.toggle.onx { background:#1f883d; } .toggle.onx::after { left:34px; }
.vis { display:flex; gap:40px; }
.vis .card { flex:1; }
.vis .emoji { font-size:80px; }
.vis h3 { font-size:44px; margin:14px 0; }
.vis ul { margin:0; padding-left:30px; font-size:30px; line-height:1.8; color:var(--muted); }
.three { display:grid; grid-template-columns:repeat(3,1fr); gap:30px; }
.three .card h3 { font-size:36px; } .three .card { padding:32px 34px; }
.three .card .tag { margin:14px 0 16px; }
.three .card p { font-size:27px; }
.menu-wrap { position:relative; }
.tabinfo { display:grid; grid-template-columns:repeat(4,1fr); gap:26px; margin-top:30px; }
.tabinfo .card { padding:26px 28px; }
.tabinfo h3 { font-family:"JetBrains Mono"; font-size:30px; color:var(--blue); margin:0 0 10px; }
.tabinfo p { font-size:27px; }
.danger { border:2px solid #cf222e; border-radius:12px; }
.danger .rowc { display:flex; align-items:center; padding:18px 24px; border-top:1px solid #ffcecb; font-size:22px; }
.danger .rowc:first-child { border-top:0; }
.danger .rowc .gh-btn { margin-left:auto; color:#cf222e; }
"""

S_ENTRY = browser("https://github.com", gh_top("<b>Dashboard</b>") + """
<div class="dash" style="display:flex;height:520px;position:relative">
  <div style="width:420px;padding:24px;border-right:1px solid #d0d7de;font-size:21px">
    <div style="display:flex;align-items:center;font-weight:700">Top repositories <span class="gh-btn green" id="e-new" style="margin-left:auto;height:34px">▣ New</span></div></div>
  <div style="flex:1;padding:24px 34px;font-size:30px;font-weight:700">Home</div>
  <div class="menu" data-s="2" style="right:70px;top:6px">
    <div class="act" id="e-newrepo">New repository</div><div>Import repository</div><div>New codespace</div><div>New gist</div><hr><div>New organization</div>
  </div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_FORM1 = """
<div class="row" style="gap:40px;align-items:flex-start;margin-top:-20px">
""" + browser("https://github.com/new", gh_top("<b>New repository</b>") + """
<div class="newform">
  <h2>Create a new repository</h2>
  <div class="sub">A repository contains all project files, including the revision history.</div>
  <div class="own">
    <div class="fld"><label>Owner <em>*</em></label><div class="inp" style="width:250px">🟣 xiaoming-dev ▾</div></div>
    <div class="slash">/</div>
    <div class="fld" id="n-name" style="flex:1"><label>Repository name <em>*</em></label><div class="inp focus"><span class="type" data-s="2" style="--n:8">my-notes</span></div>
      <div class="hint ok" data-s="2">✓ my-notes is available.</div></div>
  </div>
  <div class="fld" id="n-desc"><label>Description <span style="font-weight:400;color:#59636e">(optional)</span></label><div class="inp"><span class="type" data-s="4" style="--n:6">我的学习笔记</span></div></div>
</div>""", style="flex:1") + """
<div class="side-tips">
  <div class="tip" data-s="3"><span class="emoji">✅</span><div>名字用<b>英文小写</b>，单词之间用<b>短横线</b>连接，如 <code>my-notes</code></div></div>
  <div class="tip bad" data-s="3"><span class="emoji">🚫</span><div>尽量不用中文和空格，网址里会很难看</div></div>
  <div class="tip good" data-s="4"><span class="emoji">✍️</span><div>描述可以用中文，一句话说明项目是做什么的</div></div>
</div></div>"""

S_VIS = """
<h2 class="head" data-s="1">公开 Public 还是私有 Private？</h2>
<div class="vis">
  <div class="card" data-s="2"><div class="emoji">🌍</div><h3>Public 公开</h3>
    <ul><li>所有人都能看到</li><li>只有你（和你邀请的人）能修改</li><li>适合开源项目、作品集</li></ul></div>
  <div class="card" data-s="3"><div class="emoji">🔒</div><h3>Private 私有</h3>
    <ul><li>只有你和你邀请的人能看到</li><li>免费账号也能无限创建</li><li>适合个人资料、未完成的作品</li></ul></div>
</div>
<div class="tip warn" data-s="4" style="margin-top:30px"><span class="emoji">⚠️</span><div>不管公开还是私有，都<b>不要</b>把密码、身份证号这类敏感信息放进仓库。</div></div>"""

S_CFG = browser("https://github.com/new", gh_top("<b>New repository</b>") + """
<div class="newform" style="padding-top:24px">
  <div style="font-size:26px;font-weight:700;margin-bottom:14px">Configuration</div>
  <div class="cfg">
    <div class="rowc" id="c-vis"><div class="t"><b>Choose visibility</b><small>Choose who can see and commit to this repository</small></div><div class="ctrl gh-btn">🌍 Public ▾</div></div>
    <div class="rowc" id="c-readme"><div class="t"><b>Add README</b><small>READMEs can be used as longer descriptions.</small></div><div class="ctrl"><div class="toggle" id="tg"></div></div></div>
    <div class="rowc" id="c-ignore"><div class="t"><b>Add .gitignore</b><small>.gitignore tells git which files not to track.</small></div><div class="ctrl gh-btn">No .gitignore ▾</div></div>
    <div class="rowc" id="c-lic"><div class="t"><b>Add license</b><small>Licenses explain how others can use your code.</small></div><div class="ctrl gh-btn">No license ▾</div></div>
  </div>
  <div style="display:flex;justify-content:flex-end;margin-top:24px"><span class="gh-btn green" id="c-create" style="height:48px;font-size:22px">Create repository</span></div>
</div>""", style="width:1560px;margin:-20px auto 0")

S_THREE = """
<h2 class="head" data-s="1">这三个选项分别是什么意思？</h2>
<div class="three">
  <div class="card" data-s="2"><h3>📖 README</h3><span class="tag t-green">建议打开</span><p>项目的说明书。打开后，仓库一创建就会自带这个文件，首页会直接显示它的内容。</p></div>
  <div class="card" data-s="3"><h3>🙈 .gitignore</h3><span class="tag t-blue">按需选择</span><p>一份“忽略清单”，告诉 Git 哪些文件不用管，比如临时文件。写代码时按语言选模板，写笔记可以不选。</p></div>
  <div class="card" data-s="4"><h3>📜 License</h3><span class="tag t-purple">开源时再选</span><p>许可证，说明别人可以怎样使用你的代码。练习项目可以不选，开源项目常用 MIT。</p></div>
</div>"""

S_REPO = browser("https://github.com/xiaoming-dev/my-notes", gh_top("xiaoming-dev / <b>my-notes</b>") + repo_tabs() + """
<div class="gh-body">
  <div class="gh-title" id="r-title">my-notes <span class="gh-pill">Public</span></div>
  <div class="gh-toolbar"><span class="gh-btn">⑂ main ▾</span><span class="gh-btn" style="margin-left:auto">Add file ▾</span><span class="gh-btn green" id="r-code">&lt;&gt; Code ▾</span></div>
  <div class="gh-box">
    <div class="head"><div class="gh-avatar" style="width:30px;height:30px"></div><b>xiaoming-dev</b> Initial commit<span class="count">🕘 1 Commit</span></div>
    <div class="gh-row" id="r-file"><i class="ico-file"></i>README.md<span class="msg">Initial commit</span><span class="when">now</span></div>
  </div>
  <div class="gh-box gh-readme" id="r-readme"><div class="head">📖 README</div>
    <div class="md"><h4>my-notes</h4><p>我的学习笔记</p></div></div>
</div>""", style="width:1600px;margin:-20px auto 0")

S_TABS = """
<h2 class="head" data-s="1">仓库页面上方的几个标签</h2>
""" + browser("https://github.com/xiaoming-dev/my-notes", repo_tabs(), style="width:1200px") + """
<div class="tabinfo">
  <div class="card" data-s="2"><h3>Code</h3><p>仓库里的文件，默认打开这里</p></div>
  <div class="card" data-s="3"><h3>Issues</h3><p>问题反馈和待办事项</p></div>
  <div class="card" data-s="4"><h3>Pull requests</h3><p>别人提交的修改请求，第 8 集细讲</p></div>
  <div class="card" data-s="5"><h3>Settings</h3><p>仓库设置：改名、改公开私有、删除</p></div>
</div>"""

S_DANGER = """
<h2 class="head" data-s="1">建错了也不怕<small>Settings 页面最下方的 Danger Zone（危险区域）</small></h2>
<div class="danger" data-s="2" style="background:#fff">
  <div class="rowc"><div><b>Change repository visibility</b><br><span style="color:#59636e">修改公开 / 私有</span></div><span class="gh-btn">Change visibility</span></div>
  <div class="rowc"><div><b>Transfer ownership</b><br><span style="color:#59636e">转让给别人</span></div><span class="gh-btn">Transfer</span></div>
  <div class="rowc" id="dz-del"><div><b>Delete this repository</b><br><span style="color:#59636e">删除仓库（无法恢复！）</span></div><span class="gh-btn">Delete this repository</span></div>
</div>
<div class="tip" data-s="3" style="margin-top:26px"><span class="emoji">✏️</span><div>仓库改名在 Settings 页面<b>最上方</b>的 Repository name，改完点 Rename 即可。</div></div>"""

SCENES = [
    title_scene(NUM, "在网页上新建一个属于你的仓库",
                ["欢迎回来！账号注册好了，这一集，我们来创建你的第一个仓库。"],
                ["仓库就是存放项目的文件夹。整个过程都在网页上完成，只要两三分钟。"]),
    dict(html=S_ENTRY, steps=[
        dict(say=["登录 GitHub 以后，有两个地方可以新建仓库。",
                  "一个是首页左边的绿色 New 按钮。"], js="hl('#e-new', {label:'方法一', side:'below', pad:8})"),
        dict(say=["另一个是右上角的加号，点开后选择 New repository，也就是新建仓库。"],
             js="hl(null); cursor('#e-newrepo', {click:true})"),
    ]),
    dict(html=S_FORM1, steps=[
        dict(say=["现在来到了创建仓库的页面。第一项 Owner 是仓库的主人，默认就是你自己，不用改。"]),
        dict(say=["第二项 Repository name，填仓库的名字。我们填 my-notes，意思是我的笔记。",
                  "出现绿色的对勾，说明名字可以用。"], js="hl('#n-name', {pad:8})"),
        dict(say=["起名字有个小习惯：用英文小写，单词之间用短横线连接。",
                  "尽量不要用中文和空格，因为仓库名会出现在网址里。"]),
        dict(say=["第三项 Description 是描述，可以不填。填的话用中文也没问题，一句话说明这个仓库是做什么的。"],
             js="hl('#n-desc', {pad:8})"),
    ]),
    dict(html=S_VIS, steps=[
        dict(say=["往下是一个重要的选择：公开，还是私有？"]),
        dict(say=["Public 公开：所有人都能看到你的仓库，但只有你和你邀请的人才能修改。适合开源项目和作品集。"]),
        dict(say=["Private 私有：只有你和你邀请的人能看到。免费账号也能创建私有仓库，适合放个人资料。"]),
        dict(say=["要提醒一句：不管公开还是私有，都不要把密码、身份证号这类敏感信息放进仓库。"]),
    ]),
    dict(html=S_CFG, steps=[
        dict(say=["再往下是几个配置选项。"]),
        dict(say=["Choose visibility，就是刚才说的公开和私有，我们选 Public。"], js="hl('#c-vis', {pad:4})"),
        dict(say=["Add README，把它打开，仓库就会自带一个说明文件。"],
             js="hl('#c-readme', {pad:4}); document.getElementById('tg').classList.add('onx')"),
        dict(say=["Add .gitignore 和 Add license，这次先保持默认，不用选。"], js="hl('#c-ignore', {pad:4})"),
    ]),
    dict(html=S_THREE, steps=[
        dict(say=["这三个选项是什么意思呢？我们简单解释一下。"]),
        dict(say=["README，是项目的说明书。打开后，仓库首页会直接显示它的内容，建议每次都打开。"]),
        dict(say=["点 gitignore，是一份忽略清单，告诉 Git 哪些文件不用管，比如电脑自动生成的临时文件。",
                  "写代码时按编程语言选模板就行，写笔记可以不选。"]),
        dict(say=["License，是许可证，说明别人可以怎样使用你的代码。练习项目可以不选，开源项目常用的是 MIT 许可证。"]),
    ]),
    dict(html=S_CFG.replace('class="toggle"', 'class="toggle onx"'), steps=[
        dict(say=["一切设置好以后，点击右下角绿色的 Create repository 按钮。"],
             js="cursor('#c-create', {click:true})"),
    ]),
    dict(html=S_REPO, steps=[
        dict(say=["恭喜你，第一个仓库创建成功了！"]),
        dict(say=["左上方是仓库的名字，前面是你的用户名。",
                  "浏览器地址栏里的网址，就是这个仓库的地址，可以直接分享给别人。"],
             js="hl('#r-title', {label:'仓库名', side:'right', pad:8})"),
        dict(say=["下面的文件列表里，已经有了一个 README 点 md 文件，这就是刚才勾选生成的说明书。"],
             js="hl('#r-file', {label:'自动生成的说明文件', side:'above', pad:4})"),
        dict(say=["页面下方会直接显示 README 的内容。以后我们修改这个文件，这里也会跟着变。"],
             js="hl('#r-readme', {label:'README 的内容', side:'above', pad:6})"),
    ]),
    dict(html=S_TABS, steps=[
        dict(say=["仓库页面上方有一排标签，我们认识一下最常用的几个。"]),
        dict(say=["Code，是仓库里的文件，默认打开的就是它。"]),
        dict(say=["Issues，用来记录问题反馈和待办事项。"]),
        dict(say=["Pull requests，是别人提交的修改请求，我们在第八集详细讲。"]),
        dict(say=["Settings，是仓库的设置，可以改名字、改公开私有，也可以删除仓库。"]),
    ]),
    dict(html=S_DANGER, steps=[
        dict(say=["万一仓库名字起错了，或者想删掉重来，也不用担心。"]),
        dict(say=["打开 Settings，页面最下方有一块红色的 Danger Zone，也就是危险区域。",
                  "在这里可以修改公开私有，也可以删除仓库。删除以后无法恢复，操作前一定要想清楚。"],
             js="hl('#dz-del', {pad:2})"),
        dict(say=["如果只是想改名字，在 Settings 页面最上方修改 Repository name，再点 Rename 就可以了。"], js="hl(null)"),
    ]),
    summary_scene(NUM, [
        "右上角 ＋ → New repository 新建仓库",
        "仓库名：英文小写 + 短横线",
        "Public 所有人可见，Private 仅自己可见",
        "打开 Add README，自动生成说明书",
    ], [
        ["第一，点击右上角的加号，选择 New repository，就能新建仓库。"],
        ["第二，仓库名用英文小写，单词之间用短横线连接。"],
        ["第三，Public 公开，所有人可见；Private 私有，只有自己可见。"],
        ["第四，记得打开 Add README，自动生成一份说明书。"],
    ], ["下一集，我们在网页上修改文件，完成你的第一次提交，并学会查看历史记录。我们下集见！"]),
]
