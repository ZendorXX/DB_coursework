import streamlit as st

from database.db_config import get_connection
from redis_client import get_redis, TOKEN_TTL, SESSION_TTL

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
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "system_role" not in st.session_state:
        st.session_state.system_role = ""
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

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

    # Подключение к Redis и загрузка сессии
    redis_client = get_redis()
    token = st.session_state.auth_token
    if token:
        session_key = f"session:{token}"
        session_data = redis_client.hgetall(session_key)
        if session_data:
            st.session_state.user_id = int(session_data.get('user_id'))
            st.session_state.user_name = session_data.get('user_name')
            st.session_state.system_role = session_data.get('system_role')
            st.session_state.logged_in = True
            redis_client.expire(session_key, SESSION_TTL)
            redis_client.expire(f"auth:{token}" , TOKEN_TTL)
        else:
            for key in ['auth_token','logged_in','user_name','user_id','system_role']:
                st.session_state.pop(key, None)

    if st.session_state.user:
        if st.session_state.user['system_role'] == 'admin':
            admin_navigation()
        else:
            user_navigation()
    else:
        guest_navigation()

if __name__ == "__main__":
    main()