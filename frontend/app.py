import streamlit as st
import os

pages = [
    st.Page(os.path.join("pages", "intro.py"), title="Intro", icon="🏠", default=True),
    st.Page(os.path.join("pages", "chat.py"), title="Chat", icon="🗨️", default=False)
]

pg = st.navigation(pages)
pg.run()