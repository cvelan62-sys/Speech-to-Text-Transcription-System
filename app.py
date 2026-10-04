"""AI-Based Speech-to-Text Transcription System - Streamlit front end.
Run:  streamlit run app.py
"""
import json
import logging
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import audio_utils as au
from config import APP_TITLE, LANGUAGES, MAX_FILE_MB, SUPPORTED_FORMATS
from exporter import to_docx, to_txt
from styles import CSS, cards, pipeline
from transcriber import TranscriptionError, format_text, transcribe_segments

log = logging.getLogger("stt")
st.set_page_config(page_title="AI Speech-to-Text", page_icon="🎙️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

S = st.session_state
S.setdefault("history", [])
S.setdefault("editor", "")
S.setdefault("source", "—")
S.setdefault("lang_used", "English")


def clear_text():
    S.editor = ""


def load_record(i):
    S.editor = S.history[i]["Transcription"]
    S.source, S.lang_used = S.history[i]["Audio File"], S.history[i]["Language"]


def fmt_time(sec):
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"


@st.cache_resource(show_spinner=False, max_entries=3)
def cached_load(data: bytes, ext: str):
    return au.load_audio(data, ext)


def copy_button(text):
    safe = json.dumps(text).replace("</", "<\\/")
    components.html(f"""
    <button id="b" style="width:100%;height:38px;border:1px solid #cfd8d5;border-radius:6px;background:#fff;
      font:600 14px sans-serif;color:#14212B;cursor:pointer">📋 Copy transcription</button>
    <script>
    const t = {safe}, b = document.getElementById('b');
    b.onclick = async () => {{
      try {{ await navigator.clipboard.writeText(t); }}
      catch (e) {{ const a = document.createElement('textarea'); a.value = t; document.body.appendChild(a);
                  a.select(); document.execCommand('copy'); a.remove(); }}
      b.innerText = '✅ Copied!'; setTimeout(() => b.innerText = '📋 Copy transcription', 1800);
    }};
    </script>""", height=44)


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("Spoken language", list(LANGUAGES))
    denoise = st.checkbox("Noise reduction", value=True,
                          help="Normalises volume and removes low-frequency rumble before recognition.")
    st.caption(f"FFmpeg: {'✅ found' if au.ffmpeg_available() else '⚠️ not found (only WAV will work)'}")
    st.divider()
    st.caption("Engine: Google Web Speech API via SpeechRecognition. An internet connection is required.")

# ---------------- Header + placeholders ----------------
st.markdown(f'<div class="hero"><h1>🎙️ {APP_TITLE}</h1>'
            '<p>Turn speech into editable text: upload a recording or speak into your microphone.</p></div>',
            unsafe_allow_html=True)
flow_ph = st.empty()
dash_ph = st.empty()

# ---------------- 1. Audio input ----------------
st.subheader("1 · Audio input")
mode = st.radio("Input source", ["📁 Upload audio file", "🎙️ Record from microphone"],
                horizontal=True, label_visibility="collapsed")
data, name, ext = None, None, None

if mode.startswith("📁"):
    f = st.file_uploader(f"Upload {', '.join(x.upper() for x in SUPPORTED_FORMATS)} (max {MAX_FILE_MB} MB)",
                         accept_multiple_files=False)
    if f:
        ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if ext not in SUPPORTED_FORMATS:
            st.error(f"Unsupported format “.{ext or 'unknown'}”. Please upload one of: "
                     f"{', '.join(x.upper() for x in SUPPORTED_FORMATS)}.")
        elif f.size > MAX_FILE_MB * 1024 * 1024:
            st.error(f"File is larger than {MAX_FILE_MB} MB. Please upload a smaller file.")
        else:
            data, name = f.getvalue(), f.name
else:
    if not hasattr(st, "audio_input"):
        st.error("Microphone recording needs Streamlit 1.40 or newer. Run: pip install -U streamlit")
    else:
        st.caption("Press 🎙️ to **start recording**, press ⏹️ to **stop**. Your browser will ask for microphone "
                   "permission the first time. If it is blocked, allow the microphone for this site.")
        rec = st.audio_input("Record speech")
        if rec:
            data, name, ext = rec.getvalue(), f"recording_{datetime.now():%H%M%S}.wav", "wav"

seg, duration = None, 0.0
if data:
    try:
        seg = cached_load(data, ext)
        duration = seg.duration_seconds
        st.audio(data)
        c = st.columns(4)
        c[0].metric("File name", name if len(name) < 22 else name[:19] + "…")
        c[1].metric("Type", ext.upper())
        c[2].metric("Duration", fmt_time(duration))
        c[3].metric("Size", f"{len(data) / 1024 / 1024:.2f} MB")
    except au.AudioError as e:
        st.error(str(e))

# ---------------- 2. Transcribe ----------------
st.subheader("2 · Transcribe")
if st.button("TRANSCRIBE AUDIO", type="primary", use_container_width=True, disabled=seg is None):
    with st.status("Transcribing…", expanded=True) as status:
        try:
            st.write("🔧 Processing audio…")
            chunks = au.split(au.prepare(seg, denoise))
            bar = st.progress(0.0)
            parts, unclear = transcribe_segments(
                chunks, LANGUAGES[language],
                lambda i, n: bar.progress(i / n, text=f"🧠 Recognising speech… part {i} of {n}"))
            if not parts:
                raise TranscriptionError("No clear speech was detected. Try a closer microphone, less background "
                                         "noise, or check that the selected language matches the speech.")
            text = format_text(parts)
            bar.progress(1.0, text="✅ Done")
            S.editor, S.source, S.lang_used = text, name, language
            S.history.append({"Date/Time": f"{datetime.now():%Y-%m-%d %H:%M:%S}", "Audio File": name,
                              "Language": language, "Word Count": len(text.split()), "Transcription": text})
            status.update(label="Transcription complete", state="complete")
            if unclear:
                st.warning(f"{unclear} part(s) of the audio were unclear and were skipped.")
        except (au.AudioError, TranscriptionError) as e:
            status.update(label="Transcription failed", state="error")
            st.error(str(e))
        except Exception:
            log.exception("Unexpected transcription error")
            status.update(label="Transcription failed", state="error")
            st.error("Something went wrong while transcribing. Please try again or use a different file.")

# ---------------- 3. Result ----------------
st.subheader("3 · Transcription")
st.text_area("Transcription", key="editor", height=300, label_visibility="collapsed",
             placeholder="Your transcription will appear here. You can edit it freely.")
text = S.editor
m = st.columns(3)
m[0].metric("Words", len(text.split()))
m[1].metric("Characters", len(text))
m[2].metric("Paragraphs", len([p for p in text.split("\n\n") if p.strip()]))

b = st.columns(4)
with b[0]:
    copy_button(text)
b[1].download_button("⬇️ Download TXT", to_txt(text), "transcription.txt", "text/plain",
                     disabled=not text.strip(), use_container_width=True)
b[2].download_button("⬇️ Download DOCX", to_docx(text, S.source, S.lang_used) if text.strip() else b"",
                     "transcription.docx",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     disabled=not text.strip(), use_container_width=True)
b[3].button("🗑️ Clear transcription", on_click=clear_text, disabled=not text, use_container_width=True)

# ---------------- 4. History ----------------
st.subheader("4 · Session history")
if not S.history:
    st.info("No transcriptions yet. Your results from this session will be listed here.")
else:
    df = pd.DataFrame(S.history)
    st.dataframe(df.drop(columns="Transcription"), use_container_width=True, hide_index=True)
    for i in reversed(range(len(S.history))):
        r = S.history[i]
        with st.expander(f"{r['Date/Time']} · {r['Audio File']} · {r['Language']} · {r['Word Count']} words"):
            st.write(r["Transcription"])
            st.button("Load into editor", key=f"load{i}", on_click=load_record, args=(i,))
    h = st.columns([1, 1, 2])
    h[0].download_button("⬇️ History (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                         "transcription_history.csv", "text/csv", use_container_width=True)
    h[1].button("Clear history", on_click=lambda: S.history.clear(), use_container_width=True)

# ---------------- Dashboard + workflow (filled last so it reflects this run) ----------------
dash_ph.markdown(cards([
    ("Total transcriptions", len(S.history)),
    ("Total words", f"{sum(r['Word Count'] for r in S.history):,}"),
    ("Current audio duration", fmt_time(duration) if seg else "—"),
    ("Selected language", language),
]), unsafe_allow_html=True)
flow_ph.markdown(pipeline(5 if text.strip() else (1 if seg else 0)), unsafe_allow_html=True)
