import streamlit as st

from database.db_config import get_connection

from pages.home import home_page
from pages.auth import register_page, login_page, logout_page
from pages.admin import admin_panel
from pages.raids import raids_page
from pages.units import units_page


def initialize_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "player" not in st.session_state:
        st.session_state.player = None
    if "conn" not in st.session_state:
        st.session_state.conn = get_connection()

def admin_navigation():
    pages = {
        "Админ-панель": admin_panel,
        "Выход": logout_page
    }
    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

def user_navigation():
    pages = {
        "Домашняя страница": home_page,
        "Юниты": units_page,
        "Рейды": raids_page,
        "Выход": logout_page
    }
    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

def guest_navigation():
    pages = {
        "Домашняя страница": home_page,
        "Регистрация": register_page,
        "Вход": login_page
    }
    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

def main():
    st.title("SWGOH Helper")
    initialize_session_state()

    if st.session_state.user:
        if st.session_state.user['system_role'] == 'admin':
            admin_navigation()
        else:
            user_navigation()
    else:
        guest_navigation()

if __name__ == "__main__":
    main()