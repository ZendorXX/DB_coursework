import streamlit as st

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

from database.queries import GET_PLAYER_BY_USER_ID_QUERY, ADD_PLAYER_QUERY, GET_GUILD_BY_NAME_QUERY, ADD_GUILD_QUERY, ADD_PLAYER_TO_GUILD_QUERY

def home_page():
    st.header("Добро пожаловать!")
    if st.session_state.user:
        st.write(f"Привет, {st.session_state.user['name']}!")

        get_player_info(st.session_state.user['user_id'])

        if st.session_state.player:
            display_player_info()

            if not st.session_state.player['guild_id']:
                join_guild_form()
                
        else:
            add_player_account_form()
    else:
        st.write("Пожалуйста, войдите или зарегистрируйтесь.")

def get_player_info(user_id):
    conn = st.session_state.conn

    try:
        player = fetch_query(conn, GET_PLAYER_BY_USER_ID_QUERY, (user_id,))
        if player:
            st.session_state.player = player[0]
        else:
            st.session_state.player = None
    except Exception as e:
        handle_error(e)

def display_player_info():
    st.subheader("Ваш игровой аккаунт")
    st.write(f"Имя: {st.session_state.player['name']}")
    st.write(f"Allycode: {st.session_state.player['allycode']}")
    st.write(f"Галактическая мощь: {st.session_state.player['galactic_power']}")

    if st.session_state.player['guild_id']:
        st.write(f"Гильдия: {st.session_state.player['guild_name']}")
        st.write(f"Роль в гильдии: {st.session_state.player['guild_role']}")
    else:
        st.write("Вы не состоите в гильдии.")

def add_player_account_form():
    conn = st.session_state.conn

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
            execute_query(conn, ADD_PLAYER_QUERY, (st.session_state.user['user_id'], player_name, allycode))

            if in_guild and guild_name:
                add_player_to_guild(guild_name, guild_role)

            st.success("Игровой аккаунт успешно добавлен!")
            get_player_info(st.session_state.user['user_id']) 
        except Exception as e:
            handle_error(e)

def join_guild_form():
    st.subheader("Вступить в гильдию")
    guild_name = st.text_input("Название гильдии")
    guild_role = st.selectbox("Роль в гильдии", ["Глава", "Офицер", "Участник"])

    if st.button("Вступить в гильдию"):
        try:
            add_player_to_guild(guild_name, guild_role)
            st.success("Вы успешно вступили в гильдию!")
            get_player_info(st.session_state.user['user_id']) 
        except Exception as e:
            handle_error(e)

def add_player_to_guild(guild_name, guild_role):
    conn = st.session_state.conn

    guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))
    if not guild:
        execute_query(conn, ADD_GUILD_QUERY, (guild_name,))
        guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))

    execute_query(conn, ADD_PLAYER_TO_GUILD_QUERY, (guild[0]['guild_id'], guild_role, st.session_state.user['user_id']))