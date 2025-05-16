import streamlit as st
from datetime import datetime

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

from database.queries import (
    GET_PLAYER_BY_USER_ID_QUERY, ADD_PLAYER_QUERY, GET_GUILD_BY_NAME_QUERY, ADD_GUILD_QUERY, ADD_PLAYER_TO_GUILD_QUERY,
    GET_ALL_RAID_TEMPLATES_QUERY, INSERT_RAID_QUERY, GET_RAIDS_BY_GUILD_ID_QUERY, INSERT_RAID_RESULT_QUERY
)

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
                if st.session_state.player['guild_role'] == "Глава":
                    add_raid_form()
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

def add_raid_form():
    conn = st.session_state.conn

    st.subheader("Добавить рейд")

    raid_templates = fetch_query(conn, GET_ALL_RAID_TEMPLATES_QUERY)
    if not raid_templates:
        st.write("Типы рейдов отсутствуют. Обратитесь к администратору.")
        return

    raid_options = {raid['name']: raid['raid_template_id'] for raid in raid_templates}
    selected_raid_name = st.selectbox("Выберите тип рейда", list(raid_options.keys()))
    selected_raid_id = raid_options[selected_raid_name]

    start_time = st.date_input("Дата начала рейда", datetime.now())
    end_time = st.date_input("Дата окончания рейда", datetime.now())

    if st.button("Добавить рейд"):
        try:
            execute_query(conn, INSERT_RAID_QUERY,
                          (selected_raid_id, st.session_state.player['guild_id'], start_time, end_time))
            st.success(f"Рейд '{selected_raid_name}' успешно добавлен!")
        except Exception as e:
            handle_error(e)

def add_raid_result_form():
    conn = st.session_state.conn

    st.subheader("Добавить результаты рейда")

    raids = fetch_query(conn, GET_RAIDS_BY_GUILD_ID_QUERY, (st.session_state.player['guild_id'],))
    if not raids:
        st.write("В данный момент нет активных рейдов.")
        return

    raid_options = {raid['name']: raid['raid_id'] for raid in raids}
    selected_raid_name = st.selectbox("Выберите рейд", list(raid_options.keys()))
    selected_raid_id = raid_options[selected_raid_name]

    score = st.number_input("Введите ваши очки", min_value=0, step=1)

    if st.button("Добавить результат"):
        try:
            execute_query(conn, INSERT_RAID_RESULT_QUERY,
                          (selected_raid_id, st.session_state.player['player_id'], score))
            st.success(f"Результаты рейда '{selected_raid_name}' успешно добавлены!")
        except Exception as e:
            handle_error(e)