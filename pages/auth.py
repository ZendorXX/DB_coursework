import streamlit as st
import secrets

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error
from utils.passwords import hash_password, check_password

from database.queries import REGISTER_USER_QUERY, LOGIN_USER_QUERY

from database.redis_client import get_redis, TOKEN_TTL, SESSION_TTL

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
                token = secrets.token_hex(16)
                redis_client = get_redis()

                redis_client.setex(f"auth:{token}", TOKEN_TTL, user[0]['user_id'])

                session_data = {
                    'user_id': user[0]['user_id'],
                    'user_name': user[0]['name'],
                    'system_role': user[0]['system_role']
                }
                redis_client.hset(f"session:{token}", mapping=session_data)
                redis_client.expire(f"session:{token}", SESSION_TTL)

                st.session_state.auth_token = token
                st.session_state.logged_in = True
                st.session_state.user_name = user[0]['name']
                st.session_state.user_id = user[0]['user_id']
                st.session_state.system_role = user[0]['system_role']
                st.session_state.user = user[0]
                st.success("Вход выполнен успешно!")
            else:
                st.error("Неверный email или пароль.")
        except Exception as e:
            handle_error(e)

def logout_page():
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        redis_client = get_redis()
        token = st.session_state.auth_token
        redis_client.delete(f"auth:{token}")
        redis_client.delete(f"session:{token}")
    
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_id = None
    st.session_state.system_role = ""
    st.session_state.auth_token = None
    st.session_state.user = None
    st.session_state.player = None
    st.success("Выход выполнен успешно!")