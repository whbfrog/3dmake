"""Scene helpers shared by episodes 2-10."""

EPISODES = [
    "GitHub 到底是什么？", "注册账号与界面导览", "创建第一个仓库", "提交 Commit 与历史记录",
    "把仓库搬到电脑上", "本地修改与同步", "分支 Branch", "Pull Request 协作",
    "参与开源", "实用技巧与总结",
]


def title_scene(num, tagline, say1, say2):
    html = f"""
<div class="center">
  <div class="tag t-green" data-s="1" style="font-size:34px;padding:10px 30px">GitHub 零基础入门 · 第 {num} 集</div>
  <h1 class="title" data-s="1" style="font-size:112px;margin:40px 0 30px">{EPISODES[num - 1]}</h1>
  <div data-s="2" style="font-size:48px;font-weight:600;color:var(--muted)">{tagline}</div>
</div>"""
    return dict(html=html, steps=[dict(say=say1), dict(say=say2)])


def summary_scene(num, points, say_points, say_next, next_text=None):
    """points: 3-4 short lines; say_points: one narration list per point."""
    colors = ["bg-blue", "bg-green", "bg-purple", "bg-orange"]
    lis = "".join(f'<div class="li" data-s="{i + 2}"><div class="num {colors[i]}">{i + 1}</div>{p}</div>'
                  for i, p in enumerate(points))
    if next_text is None:
        next_text = f"第 {num + 1} 集 · {EPISODES[num]}"
    k = len(points) + 2
    html = f"""
<h2 class="head" data-s="1">本集小结</h2>
<div class="sum"><div class="card">{lis}</div>
<div class="next" data-s="{k}"><span class="tag t-green">{'下集预告' if num < 10 else '课程结束'}</span>{next_text}</div></div>"""
    steps = [dict(say=["好，我们来总结一下这一集。"])]
    steps += [dict(say=s) for s in say_points]
    steps.append(dict(say=say_next, min=4.0))
    return dict(html=html, steps=steps)


def browser(url, body, cls="", style=""):
    return f"""<div class="browser {cls}" style="{style}">
  <div class="bar"><i></i><i></i><i></i><div class="url">{url}</div></div>{body}</div>"""


def gh_top(crumb="", extra=""):
    return f"""<div class="gh-top"><div class="gh-logo">G</div><div class="gh-crumb">{crumb}</div>
  <div class="gh-search">Type / to search</div>{extra}<div class="gh-btn" style="height:36px;padding:0 10px">＋ ▾</div><div class="gh-avatar"></div></div>"""


def repo_tabs(active="Code", prs="0"):
    tabs = ["&lt;&gt; Code", "Issues", f"Pull requests {prs}" if prs != "0" else "Pull requests", "Actions", "Settings"]
    keys = ["Code", "Issues", "Pull requests", "Actions", "Settings"]
    return '<div class="gh-tabs">' + "".join(
        f'<span class="{"act" if k == active else ""}">{t}</span>' for k, t in zip(keys, tabs)) + "</div>"


def win(title, body, cls="", style=""):
    return f"""<div class="win {cls}" style="{style}"><div class="wbar">{title}<div class="ctl"><span>—</span><span>☐</span><span>✕</span></div></div>{body}</div>"""


def term(lines, title="Windows PowerShell", cls="", style=""):
    return f"""<div class="term {cls}" style="{style}"><div class="tbar">▶ {title}</div><div class="tbody">{lines}</div></div>"""


PS = '<span class="ps">PS C:\\Users\\xiaoming&gt;</span> '
