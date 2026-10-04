"""Custom CSS and small HTML components."""

CSS = """
<style>
#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
.block-container {padding-top: 1.6rem; max-width: 1180px;}
.hero {background: #123B3A; color: #F2F7F5; padding: 1.6rem 1.9rem; border-radius: 6px;
       border-left: 8px solid #2DD4BF; margin-bottom: 1rem;}
.hero h1 {font-size: 1.75rem; margin: 0 0 .3rem 0; color: #fff; letter-spacing: -.01em;}
.hero p {margin: 0; color: #B7D4CE; font-size: .98rem;}
.flow {display: flex; flex-wrap: wrap; gap: .4rem; margin: .2rem 0 1.1rem 0;}
.flow span {padding: .3rem .75rem; border-radius: 99px; font-size: .82rem; background: #E4EBE8; color: #55676A;}
.flow span.done {background: #CDEBE4; color: #0F5B53;}
.flow span.now {background: #0F766E; color: #fff; font-weight: 600;}
.cards {display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .8rem; margin-bottom: 1.2rem;}
.card {background: #fff; border: 1px solid #DDE5E2; border-top: 3px solid #0F766E; border-radius: 6px; padding: .85rem 1rem;}
.card .v {font-size: 1.7rem; font-weight: 700; color: #123B3A; line-height: 1.15;}
.card .l {font-size: .85rem; color: #5B6B6E;}
div.stButton > button[kind="primary"] {font-weight: 700; letter-spacing: .03em; padding: .7rem 1rem;}
textarea {font-size: 1.02rem !important; line-height: 1.6 !important;}
</style>
"""

STEPS = ["Audio Input", "Audio Processing", "Speech Recognition", "Text Processing",
         "Transcription", "Editing", "Export"]


def cards(items):
    body = "".join(f'<div class="card"><div class="v">{v}</div><div class="l">{l}</div></div>' for l, v in items)
    return f'<div class="cards">{body}</div>'


def pipeline(active: int):
    spans = []
    for i, s in enumerate(STEPS):
        cls = "done" if i < active else ("now" if i == active else "")
        spans.append(f'<span class="{cls}">{s}</span>')
    return f'<div class="flow">{"".join(spans)}</div>'
