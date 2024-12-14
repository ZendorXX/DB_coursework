import streamlit as st

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error
from utils.passwords import hash_password, check_password

from database.queries import REGISTER_USER_QUERY, LOGIN_USER_QUERY

def register_page():
    conn = st.session_state.conn

    st.header("Регистрация")
    name = st.text_input("Имя")
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    confirm_password = st.text_input("Подтвердите пароль", type="password")
    if st.button("Зарегистрироваться"):
        if password != confirm_password:
            st.error("Пароли не совпадают.")
        else:
            try:
                hashed_password = hash_password(password)
                execute_query(conn, REGISTER_USER_QUERY, (email, hashed_password, name))
                st.success("Регистрация прошла успешно!")
            except Exception as e:
                handle_error(e)

def login_page():
    conn = st.session_state.conn

    st.header("Вход")
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        try:
            user = fetch_query(conn, LOGIN_USER_QUERY, (email,))
            if user and check_password(password, user[0]['password_hash']):
                st.session_state.user = user[0]
                st.success("Вход выполнен успешно!")
            else:
                st.error("Неверный email или пароль.")
        except Exception as e:
            handle_error(e)

def logout_page():
    st.session_state.user = None
    st.session_state.player = None
    st.success("Выход выполнен успешно!")