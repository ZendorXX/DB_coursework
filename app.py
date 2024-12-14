import streamlit as st
from database.db_config import get_connection
from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error
from database.queries import (
    REGISTER_USER_QUERY, LOGIN_USER_QUERY, GET_PLAYER_BY_USER_ID_QUERY, ADD_PLAYER_QUERY,
    GET_GUILD_BY_NAME_QUERY, ADD_GUILD_QUERY, ADD_PLAYER_TO_GUILD_QUERY
)
import bcrypt

# Инициализация состояния сессии
def initialize_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "player" not in st.session_state:
        st.session_state.player = None

# Хеширование пароля
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Проверка пароля
def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Получение информации об игровом аккаунте
def get_player_info(user_id):
    try:
        player = fetch_query(conn, GET_PLAYER_BY_USER_ID_QUERY, (user_id,))
        if player:
            st.session_state.player = player[0]
        else:
            st.session_state.player = None
    except Exception as e:
        handle_error(e)

def home_page():
    st.header("Добро пожаловать!")
    if st.session_state.user:
        st.write(f"Привет, {st.session_state.user['name']}!")

        # Получение информации об игровом аккаунте
        get_player_info(st.session_state.user['user_id'])

        if st.session_state.player:
            # Отображение информации об игровом аккаунте
            display_player_info()

            # Если игрок не состоит в гильдии, добавляем возможность вступления
            if not st.session_state.player['guild_id']:
                join_guild_form()
        else:
            # Если игровой аккаунт ещё не добавлен
            add_player_account_form()
    else:
        st.write("Пожалуйста, войдите или зарегистрируйтесь.")

# Функция для отображения информации об игровом аккаунте
def display_player_info():
    st.subheader("Ваш игровой аккаунт")
    st.write(f"Имя: {st.session_state.player['name']}")
    st.write(f"Allycode: {st.session_state.player['allycode']}")
    st.write(f"Галактическая мощь: {st.session_state.player['galactic_power']}")

    # Если игрок состоит в гильдии
    if st.session_state.player['guild_id']:
        st.write(f"Гильдия: {st.session_state.player['guild_name']}")
        st.write(f"Роль в гильдии: {st.session_state.player['guild_role']}")
    else:
        st.write("Вы не состоите в гильдии.")

# Функция для добавления игрового аккаунта
def add_player_account_form():
    st.subheader("Добавьте ваш игровой аккаунт")
    player_name = st.text_input("Игровое имя")
    allycode = st.text_input("Allycode")
    in_guild = st.checkbox("Я состою в гильдии")
    guild_name = None
    guild_role = None

    if in_guild:
        guild_name = st.text_input("Название гильдии")
        guild_role = st.selectbox("Роль в гильдии", ["Глава", "Офицер", "Участник"])

    if st.button("Добавить игровой аккаунт"):
        try:
            # Добавление игрового аккаунта
            execute_query(conn, ADD_PLAYER_QUERY, (st.session_state.user['user_id'], player_name, allycode))

            # Если игрок состоит в гильдии
            if in_guild and guild_name:
                add_player_to_guild(guild_name, guild_role)

            st.success("Игровой аккаунт успешно добавлен!")
            get_player_info(st.session_state.user['user_id'])  # Обновление информации об игровом аккаунте
        except Exception as e:
            handle_error(e)

# Функция для вступления в гильдию
def join_guild_form():
    st.subheader("Вступить в гильдию")
    guild_name = st.text_input("Название гильдии")
    guild_role = st.selectbox("Роль в гильдии", ["Глава", "Офицер", "Участник"])

    if st.button("Вступить в гильдию"):
        try:
            add_player_to_guild(guild_name, guild_role)
            st.success("Вы успешно вступили в гильдию!")
            get_player_info(st.session_state.user['user_id'])  # Обновление информации об игровом аккаунте
        except Exception as e:
            handle_error(e)

# Функция для добавления игрока в гильдию
def add_player_to_guild(guild_name, guild_role):
    # Проверка, существует ли гильдия
    guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))
    if not guild:
        # Создание новой гильдии
        execute_query(conn, ADD_GUILD_QUERY, (guild_name,))
        guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))

    # Добавление игрока в гильдию
    execute_query(conn, ADD_PLAYER_TO_GUILD_QUERY, (guild[0]['guild_id'], guild_role, st.session_state.user['user_id']))

# Страница "Регистрация"
def register_page():
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

# Страница "Вход"
def login_page():
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

# Страница "Выход"
def logout_page():
    st.session_state.user = None
    st.session_state.player = None
    st.success("Выход выполнен успешно!")

# Основная функция
def main():
    st.title("SWGOH Helper")
    initialize_session_state()

    if st.session_state.user:
        pages = {
            "Домашняя страница": home_page,
            "Выход": logout_page
        }
    else:
        pages = {
            "Домашняя страница": home_page,
            "Регистрация": register_page,
            "Вход": login_page
        }

    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

if __name__ == "__main__":
    conn = get_connection()
    main()