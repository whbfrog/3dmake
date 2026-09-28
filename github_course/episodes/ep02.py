from kit import browser, gh_top, summary_scene, title_scene

NUM = 2
TITLE = "注册账号与界面导览"

CSS = """
.prep { display:grid; grid-template-columns:repeat(3,1fr); gap:34px; }
.prep .card { text-align:center; padding:40px 30px; }
.prep .emoji { font-size:90px; display:block; margin-bottom:18px; }
.url-demo { margin-top:40px; text-align:center; font:700 44px "JetBrains Mono"; }
.url-demo b { color:var(--green); background:var(--green-soft); padding:4px 14px; border-radius:10px; }

.hero { height:560px; background:linear-gradient(160deg,#0d1117,#1b2a4a 60%,#3b2d6b); color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:30px; }
.hero h1 { font-size:60px; margin:0; text-align:center; line-height:1.25; }
.hero .cta { background:#1f883d; color:#fff; font-size:28px; font-weight:700; padding:16px 34px; border-radius:10px; }
.dark-top { height:72px; background:#0d1117; display:flex; align-items:center; gap:26px; padding:0 30px; color:#e6edf3; font-size:22px; }
.dark-top .sp { margin-left:auto; }
.dark-top .btn2 { border:1px solid #8b949e; border-radius:8px; padding:6px 16px; }

.signup { display:flex; height:740px; }
.signup .side { width:520px; background:linear-gradient(170deg,#0d1117,#1b2a4a); color:#fff; padding:60px 50px; font-size:36px; font-weight:800; line-height:1.4; }
.signup .side small { display:block; font-size:22px; font-weight:400; color:#9ea7b3; margin-top:18px; }
.signup .main { flex:1; padding:40px 70px; }
.signup h2 { font-size:34px; margin:0 0 24px; }

.code-boxes { display:flex; gap:14px; margin:30px 0; }
.code-boxes span { width:62px; height:76px; border:2px solid #d0d7de; border-radius:10px; display:grid; place-items:center; font:700 36px "JetBrains Mono"; }
.flow4 .fb { min-width:250px; }

.dash { display:flex; height:560px; }
.dash .lside { width:420px; padding:24px; border-right:1px solid #d0d7de; font-size:21px; }
.dash .lside h4 { font-size:21px; margin:0 0 14px; display:flex; align-items:center; }
.dash .lside .gh-btn { margin-left:auto; height:34px; }
.dash .feed { flex:1; padding:24px 34px; }
.dash .feed h3 { font-size:30px; margin:0 0 18px; }
.feed-card { border:1px solid #d0d7de; border-radius:12px; padding:18px 22px; margin-bottom:16px; font-size:21px; color:#57606a; }
.feed-card b { color:#1f2328; }

.panel { position:absolute; right:0; top:0; width:420px; height:100%; background:#fff; border-left:1px solid #d0d7de; box-shadow:-10px 0 30px rgba(31,35,40,.12); padding:24px; font-size:22px; }
.panel .who { display:flex; gap:14px; align-items:center; padding-bottom:16px; border-bottom:1px solid #d0d7de; margin-bottom:10px; }
.panel .it { padding:11px 10px; border-radius:8px; }
.panel .zh { color:var(--orange); font-weight:700; margin-left:10px; font-size:20px; }

.prof { display:flex; gap:44px; padding:30px 40px; }
.prof .pic { width:260px; height:260px; border-radius:50%; background:linear-gradient(135deg,#6cc4ff,#8250df); flex:none; }
.prof h3 { font-size:36px; margin:18px 0 0; } .prof .un { font-size:26px; color:#59636e; margin-bottom:16px; }
.grid-contrib { display:grid; grid-template-columns:repeat(40,16px); grid-auto-rows:16px; gap:4px; margin-top:20px; }
.grid-contrib i { border-radius:3px; background:#ebedf0; }
.grid-contrib i.g1 { background:#9be9a8; } .grid-contrib i.g2 { background:#40c463; } .grid-contrib i.g3 { background:#30a14e; } .grid-contrib i.g4 { background:#216e39; }

.set { display:flex; height:620px; }
.set .nav { width:380px; padding:24px; border-right:1px solid #d0d7de; font-size:21px; }
.set .nav div { padding:8px 12px; border-radius:8px; }
.set .nav div.act { background:#f6f8fa; font-weight:700; box-shadow:inset 3px 0 0 #fd8c73; }
.set .body { flex:1; padding:30px 40px; font-size:22px; }
.set h3 { font-size:30px; margin:0 0 16px; padding-bottom:10px; border-bottom:1px solid #d0d7de; }

.twofa { display:flex; gap:40px; }
.phone { width:300px; height:560px; border-radius:44px; background:#1f2328; padding:18px; flex:none; }
.phone .scr { background:#fff; height:100%; border-radius:30px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; font-size:24px; }
.phone .code6 { font:800 48px "JetBrains Mono"; color:var(--blue); letter-spacing:6px; }
.qr { width:200px; height:200px; background:
  conic-gradient(#1f2328 25%, #fff 0 50%, #1f2328 0 75%, #fff 0) 0 0/40px 40px; border:10px solid #fff; outline:3px solid #1f2328; }

.dict { display:grid; grid-template-columns:repeat(4,1fr); gap:22px; }
.dict div { background:#fff; border-radius:18px; padding:20px 24px; box-shadow:0 6px 18px rgba(31,35,40,.06); }
.dict b { display:block; font:700 32px "JetBrains Mono"; color:var(--blue); }
.dict span { font-size:30px; }
"""

S_PREP = """
<h2 class="head" data-s="1">注册前，准备好这三样</h2>
<div class="prep">
  <div class="card" data-s="2"><span class="emoji">📧</span><h3>一个常用邮箱</h3><p>QQ 邮箱、163、Outlook 都可以</p></div>
  <div class="card" data-s="3"><span class="emoji">🌐</span><h3>一个浏览器</h3><p>推荐 Chrome 或 Edge</p></div>
  <div class="card" data-s="4"><span class="emoji">🏷️</span><h3>想好用户名</h3><p>英文小写，简短好记</p></div>
</div>
<div class="url-demo" data-s="5">github.com/<b>xiaoming-dev</b></div>"""

S_HOME = browser("https://github.com", """
<div class="dark-top"><div class="gh-logo" style="background:#fff;color:#0d1117">G</div>Product　Solutions　Resources　Pricing
  <span class="sp"></span><span id="signin">Sign in</span><span class="btn2" id="signup">Sign up</span></div>
<div class="hero"><h1>Build and ship software on a<br>single, collaborative platform</h1>
  <div class="cta">Sign up for GitHub</div></div>""", style="width:1560px;margin:0 auto")

S_FORM = browser("https://github.com/signup", """
<div class="signup">
  <div class="side">Create your free account<small>Explore GitHub's core features for individuals and organizations.</small></div>
  <div class="main">
    <h2>Sign up to GitHub</h2>
    <div class="fld" id="f-email"><label>Email<em>*</em></label><div class="inp"><span class="type" data-s="2" style="--n:20">xiaoming@example.com</span></div></div>
    <div class="fld" id="f-pwd"><label>Password<em>*</em></label><div class="inp"><span class="type" data-s="3" style="--n:14">••••••••••••••••</span></div>
      <div class="hint">Password should be at least 15 characters OR at least 8 characters including a number and a lowercase letter.</div></div>
    <div class="fld" id="f-user"><label>Username<em>*</em></label><div class="inp"><span class="type" data-s="4" style="--n:12">xiaoming-dev</span></div>
      <div class="hint ok" data-s="4">✓ xiaoming-dev is available.</div></div>
    <div class="fld" id="f-country"><label>Your Country/Region<em>*</em></label><div class="inp">China ▾</div></div>
    <div class="gh-btn" id="f-go" style="width:100%;justify-content:center;background:#1f2328;color:#fff;height:50px">Continue ›</div>
  </div>
</div>""", style="width:1560px;margin:-30px auto 0")

S_VERIFY = """
<h2 class="head" data-s="1">接下来，完成两步验证</h2>
<div class="flow flow4" data-s="1">
  <div class="fb" data-s="1"><span class="emoji">📝</span><b>填写信息</b><span>邮箱 · 密码 · 用户名</span></div><div class="fa" data-s="2"></div>
  <div class="fb" data-s="2"><span class="emoji">🧩</span><b>人机验证</b><span>完成一个小谜题</span></div><div class="fa" data-s="3"></div>
  <div class="fb" data-s="3"><span class="emoji">📨</span><b>邮箱验证码</b><span>去邮箱查收</span></div><div class="fa" data-s="5"></div>
  <div class="fb" data-s="5" style="border-color:var(--green)"><span class="emoji">🎉</span><b>注册完成</b><span>可以登录啦</span></div>
</div>
<div class="row" style="margin-top:44px;gap:40px;align-items:center">
  <div class="card" data-s="3" style="flex:1">
    <h3 style="font-size:32px">You're almost done!</h3>
    <p style="font-size:24px">We sent a launch code to xiaoming@example.com</p>
    <div class="code-boxes"><span>3</span><span>8</span><span>1</span><span>5</span><span>0</span><span>2</span><span>7</span><span>4</span></div>
  </div>
  <div class="tip warn" data-s="4" style="flex:1"><span class="emoji">💡</span><div>收不到邮件？先看看<b>垃圾邮件</b>文件夹，或者等一两分钟再刷新。</div></div>
</div>"""

S_DASH = browser("https://github.com", gh_top("<b>Dashboard</b>") + """
<div class="dash">
  <div class="lside"><h4>Top repositories <span class="gh-btn green" id="d-new">▣ New</span></h4>
    <div class="inp ph" style="height:38px">Find a repository…</div>
    <p style="color:#59636e">还没有仓库，下一集我们就来创建第一个！</p></div>
  <div class="feed" id="d-feed"><h3>Home</h3>
    <div class="feed-card">👋 <b>Welcome to GitHub!</b> 从这里开始你的第一个项目。</div>
    <div class="feed-card">⭐ <b>Trending repositories</b> · 看看最近大家都在关注什么</div>
    <div class="feed-card">📘 <b>Learn Git and GitHub</b> · 官方入门教程</div></div>
</div>""", cls="dashwin", style="width:1600px;margin:-30px auto 0;position:relative")

S_MENU = browser("https://github.com", gh_top("<b>Dashboard</b>") + """
<div class="dash" style="position:relative">
  <div class="lside"><h4>Top repositories <span class="gh-btn green">▣ New</span></h4></div>
  <div class="feed"><h3>Home</h3><div class="feed-card">👋 <b>Welcome to GitHub!</b></div></div>
  <div class="panel" data-s="1">
    <div class="who"><div class="gh-avatar"></div><div><b>xiaoming-dev</b><br><span style="color:#59636e;font-size:19px">小明</span></div></div>
    <div class="it" id="m-prof">👤 Your profile <span class="zh" data-s="2">个人主页</span></div>
    <div class="it" id="m-repo">📦 Your repositories <span class="zh" data-s="2">我的仓库</span></div>
    <div class="it">⭐ Your stars <span class="zh" data-s="3">我收藏的项目</span></div>
    <div class="it" id="m-set">⚙️ Settings <span class="zh" data-s="3">设置</span></div>
    <div class="it" style="border-top:1px solid #d0d7de;margin-top:8px">↪ Sign out <span class="zh" data-s="4">退出登录</span></div>
  </div>
</div>""", style="width:1600px;margin:-30px auto 0")

def _contrib():
    import random
    rnd = random.Random(7)
    cells = []
    for i in range(280):
        v = rnd.random()
        g = "" if v < .55 else "g1" if v < .75 else "g2" if v < .88 else "g3" if v < .96 else "g4"
        cells.append(f'<i class="{g}"></i>')
    return "".join(cells)

S_PROFILE = browser("https://github.com/xiaoming-dev", gh_top("<b>xiaoming-dev</b>") + """
<div class="gh-tabs"><span class="act">Overview</span><span>Repositories</span><span>Projects</span><span>Packages</span><span>Stars</span></div>
<div class="prof">
  <div><div class="pic"></div><h3>小明</h3><div class="un">xiaoming-dev</div>
    <div class="gh-btn" id="p-edit" style="width:260px;justify-content:center">Edit profile</div></div>
  <div style="flex:1"><div style="font-size:24px;font-weight:700">128 contributions in the last year</div>
    <div class="grid-contrib" id="p-grid">""" + _contrib() + """</div>
    <div style="font-size:18px;color:#59636e;margin-top:10px">Less ▢▢▢▢ More</div></div>
</div>""", style="width:1600px;margin:-30px auto 0")

S_2FA = """
<h2 class="head" data-s="1">给账号加一把锁：双重验证 2FA</h2>
<div class="twofa">
  <div style="flex:1">
    <div class="steps">
      <div class="stp" data-s="2"><div class="num bg-blue">1</div><div>进入 Settings → Password and authentication<small>点 Enable two-factor authentication</small></div></div>
      <div class="stp" data-s="3"><div class="num bg-green">2</div><div>手机安装“身份验证器”App，扫描二维码<small>如 Microsoft Authenticator、Google Authenticator</small></div></div>
      <div class="stp" data-s="4"><div class="num bg-purple">3</div><div>输入 App 上显示的 6 位数字<small>数字每 30 秒变一次</small></div></div>
      <div class="stp" data-s="5"><div class="num bg-orange">4</div><div>下载“恢复码”，妥善保存<small>手机丢了，就靠它找回账号</small></div></div>
    </div>
  </div>
  <div class="phone" data-s="3"><div class="scr"><div class="qr"></div><div data-s="4" style="text-align:center">GitHub<br><span class="code6">482 913</span></div></div></div>
</div>"""

S_DICT = """
<h2 class="head" data-s="1">界面是英文的？别怕，常用的就这些<small>多用几次就熟了，也可以借助浏览器的翻译功能</small></h2>
<div class="dict">
  <div data-s="2"><b>Sign up</b><span>注册</span></div><div data-s="2"><b>Sign in</b><span>登录</span></div>
  <div data-s="2"><b>New</b><span>新建</span></div><div data-s="2"><b>Settings</b><span>设置</span></div>
  <div data-s="3"><b>Repository</b><span>仓库</span></div><div data-s="3"><b>Commit</b><span>提交</span></div>
  <div data-s="3"><b>Branch</b><span>分支</span></div><div data-s="3"><b>Pull request</b><span>拉取请求</span></div>
  <div data-s="4"><b>Save</b><span>保存</span></div><div data-s="4"><b>Cancel</b><span>取消</span></div>
  <div data-s="4"><b>Delete</b><span>删除</span></div><div data-s="4"><b>Public / Private</b><span>公开 / 私有</span></div>
</div>"""

SCENES = [
    title_scene(NUM, "拥有你的第一个 GitHub 账号",
                ["欢迎回来！上一集，我们搞懂了 GitHub 是什么。"],
                ["这一集，我们来动手注册一个账号，再带你认识一下 GitHub 的界面。"]),
    dict(html=S_PREP, steps=[
        dict(say=["注册之前，先准备好三样东西。"]),
        dict(say=["第一，一个常用的邮箱，QQ 邮箱、网易邮箱、Outlook 都可以。"]),
        dict(say=["第二，一个浏览器，推荐用 Chrome 或者 Edge。"]),
        dict(say=["第三，想好一个用户名。建议用英文小写，简短好记。"]),
        dict(say=["因为用户名会出现在你的主页网址里，比如 github.com 斜杠 xiaoming-dev。",
                  "以后分享给别人时，一看就知道是你。"]),
    ]),
    dict(html=S_HOME, steps=[
        dict(say=["打开浏览器，在地址栏输入 github.com，然后回车。",
                  "如果打开比较慢，可以多刷新几次，或者换个时间再试。"]),
        dict(say=["页面右上角有两个按钮：Sign in 是登录，Sign up 是注册。"],
             js="hl('#signin', {label:'登录', side:'below', pad:8}); "),
        dict(say=["我们还没有账号，所以点 Sign up。"],
             js="hl('#signup', {label:'注册', side:'below', pad:8}); cursor('#signup', {click:true})"),
    ]),
    dict(html=S_FORM, steps=[
        dict(say=["现在进入了注册页面，需要填写几项信息。"]),
        dict(say=["第一项 Email，填你的邮箱。"], js="hl('#f-email', {pad:8})"),
        dict(say=["第二项 Password，设置密码。",
                  "下面的提示是说：密码要么至少 15 位，要么至少 8 位，并且包含数字和小写字母。"],
             js="hl('#f-pwd', {pad:8})"),
        dict(say=["第三项 Username，也就是用户名。",
                  "如果下面出现绿色的提示，说明这个名字没人用过，可以注册；如果是红色，就换一个。"],
             js="hl('#f-user', {pad:8})"),
        dict(say=["国家或地区选 China，然后点击 Continue，继续。"],
             js="hl('#f-country', {pad:8}); cursor('#f-go', {click:true, delay:900})"),
    ]),
    dict(html=S_VERIFY, steps=[
        dict(say=["填完信息以后，还要完成两步验证。"]),
        dict(say=["第一步是人机验证，就是做一个简单的小谜题，证明你是真人。"]),
        dict(say=["第二步，GitHub 会往你的邮箱发一串验证码。打开邮箱，把验证码填进来就行。"]),
        dict(say=["如果收不到邮件，先看看垃圾邮件文件夹，或者等一两分钟再刷新。"]),
        dict(say=["验证通过，注册就完成了！",
                  "之后可能会问你几个问题，比如你打算用 GitHub 做什么，可以直接跳过。套餐选免费的 Free 就完全够用。"]),
    ]),
    dict(html=S_DASH, steps=[
        dict(say=["登录之后，首先看到的是首页，也叫 Dashboard，仪表盘。我们来认识一下它的布局。"]),
        dict(say=["左上角这个图标，随时点它都能回到首页。"], js="hl('.gh-logo', {label:'回到首页', side:'right', pad:6})"),
        dict(say=["中间上方是搜索框，可以搜索全世界的公开项目。"], js="hl('.gh-search', {label:'搜索', side:'below', pad:6})"),
        dict(say=["右上角的加号，用来新建仓库等内容；最右边的圆形头像，是你的个人菜单。"],
             js="hl('.gh-top .gh-btn', {label:'新建', side:'below', pad:6})"),
        dict(say=["左边这一栏会列出你的仓库，旁边的绿色 New 按钮也能新建仓库。"],
             js="hl('.lside', {label:'我的仓库', side:'right', pad:0})"),
        dict(say=["中间是动态信息，会显示你关注的人和项目的最新消息。"],
             js="hl('#d-feed', {label:'动态', side:'above', pad:0})"),
    ]),
    dict(html=S_MENU, steps=[
        dict(say=["点击右上角的头像，会弹出个人菜单。"]),
        dict(say=["Your profile 是你的个人主页；Your repositories 是你的所有仓库。"]),
        dict(say=["Your stars 是你收藏的项目；Settings 是设置，修改头像、密码、安全选项都在这里。"]),
        dict(say=["最下面的 Sign out，是退出登录。"]),
    ]),
    dict(html=S_PROFILE, steps=[
        dict(say=["点 Your profile，进入个人主页。这就是别人看到的你。"]),
        dict(say=["点击 Edit profile，可以设置头像、昵称和一句话介绍。"],
             js="hl('#p-edit', {label:'编辑资料', side:'below', pad:8})"),
        dict(say=["右边这一片小方格，叫做贡献图。",
                  "你每天在 GitHub 上提交内容，对应的格子就会变绿；颜色越深，说明那天做得越多。",
                  "很多人把它当作坚持学习的打卡记录。"],
             js="hl('#p-grid', {label:'贡献图：每天的“打卡”记录', side:'below', pad:10})"),
    ]),
    dict(html=S_2FA, steps=[
        dict(say=["注册完成后，强烈建议马上做一件事：开启双重验证，英文简称 2FA。",
                  "开启后，登录时除了密码，还要输入手机上的验证码，就算密码泄露，别人也登不进去。"]),
        dict(say=["操作方法是：打开 Settings，找到 Password and authentication，点击开启双重验证。"]),
        dict(say=["然后在手机上安装一个身份验证器 App，比如微软的 Authenticator，用它扫描页面上的二维码。"]),
        dict(say=["App 上会出现一个 6 位数字，每 30 秒变一次，把它填回网页。"]),
        dict(say=["最后一步很重要：下载恢复码，保存在安全的地方。万一手机丢了，就靠它找回账号。"]),
    ]),
    dict(html=S_DICT, steps=[
        dict(say=["你可能已经发现了，GitHub 的界面是英文的。别担心，常用的单词就这么几个。"]),
        dict(say=["Sign up 注册，Sign in 登录，New 新建，Settings 设置；"]),
        dict(say=["Repository 仓库，Commit 提交，Branch 分支，Pull request 拉取请求；"]),
        dict(say=["还有 Save 保存，Cancel 取消，Delete 删除，Public 和 Private，公开和私有。",
                  "多用几次就熟了，实在不懂，也可以用浏览器自带的翻译功能。"]),
    ]),
    summary_scene(NUM, [
        "准备邮箱，在 github.com 点 Sign up 注册",
        "认识首页：搜索、新建、头像菜单",
        "个人主页和绿色的贡献图",
        "一定要开启双重验证 2FA，保存好恢复码",
    ], [
        ["第一，准备好邮箱，在 github.com 点 Sign up，填写信息并完成验证。"],
        ["第二，首页上的搜索框、加号和头像菜单，是最常用的入口。"],
        ["第三，个人主页上的绿色格子，记录着你每天的贡献。"],
        ["第四，一定要开启双重验证，并保存好恢复码。"],
    ], ["下一集，我们来创建你的第一个仓库。我们下集见！"]),
]
