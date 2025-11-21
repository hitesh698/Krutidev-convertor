# streamlit_app.py
import streamlit as st
import base64
import importlib
import inspect

st.set_page_config(page_title="Mangal ⇄ Krutidev Converter", layout="centered")

st.title("Mangal ⇄ Krutidev Converter")
st.write("Text paste karo, convert karo — Krutidev font preview bhi milega.")

def load_font_css(ttf_path="krutidev010.ttf", font_family="KrutidevCustom"):
    try:
        with open(ttf_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        css = f"""
        <style>
        @font-face {{
          font-family: '{font_family}';
          src: url(data:font/ttf;base64,{data}) format('truetype');
        }}
        .krut {{
          font-family: '{font_family}';
          font-size: 18px;
          white-space: pre-wrap;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Font load failed: {e}")

load_font_css()

def import_converter_module(module_name="ab"):
    try:
        mod = importlib.import_module(module_name)
        return mod
    except Exception as e:
        st.error(f"Could not import `{module_name}.py`. Upload it to repo. Error: {e}")
        return None

ab = import_converter_module("ab")

def find_converter_callable(mod):
    if not mod:
        return None
    candidates = []
    for name, obj in inspect.getmembers(mod):
        if inspect.isfunction(obj):
            if name.lower() in ("convert","convert_text","to_krutidev","mangal_to_krutidev","unicode_to_krutidev","main"):
                return obj
            candidates.append(obj)
    for fn in candidates:
        try:
            sig = inspect.signature(fn)
            if len(sig.parameters) == 1:
                return fn
        except Exception:
            continue
    return None

converter_fn = find_converter_callable(ab)

st.subheader("Input")
text_in = st.text_area("Yahan Mangal/Unicode text ya Krutidev text paste karo:", height=180)

col1, col2 = st.columns(2)
with col1:
    direction = st.selectbox("Conversion direction (auto):", ["Auto — try converter", "Force → Krutidev", "Force → Unicode"])
    convert_btn = st.button("Convert")

with col2:
    copy_btn = st.button("Copy output")

output = ""

if convert_btn:
    if not ab:
        st.error("Converter module not available. Ensure ab.py is uploaded and has a conversion function.")
    elif not text_in.strip():
        st.warning("Kuch text to daalo pehle.")
    else:
        if converter_fn:
            try:
                output = converter_fn(text_in)
            except Exception as e:
                st.error(f"Converter function raised error: {e}")
                if hasattr(ab, "main"):
                    try:
                        output = ab.main(text_in)
                    except Exception:
                        output = ""
        else:
            if hasattr(ab, "main"):
                try:
                    output = ab.main(text_in)
                except Exception as e:
                    st.error(f"No simple converter function found. ab.main raised: {e}")
            else:
                st.error("No suitable function found in ab.py. Please ensure ab.py exposes a function like `convert(text)` or `main(text)` that returns converted text.")

if output:
    st.subheader("Output")
    st.code(output, language=None)
    st.markdown("<div class='krut'>Preview (Krutidev font)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='krut'>{output}</div>", unsafe_allow_html=True)
    st.download_button("Download output as .txt", data=output, file_name="converted.txt", mime="text/plain")
    if copy_btn:
        st.write(
            """
            <script>
            navigator.clipboard.writeText(`%s`);
            </script>
            """ % output.replace("`","\\`"),
            unsafe_allow_html=True,
        )
