import streamlit as st

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

from database.queries import (
    GET_ALL_USERS_QUERY, DELETE_USER_QUERY, DELETE_PLAYER_QUERY, GET_PLAYER_BY_USER_ID_QUERY,
    GET_ALL_GUILDS_QUERY, DELETE_GUILD_QUERY, DELETE_UNIT_QUERY,  INSERT_UNIT_QUERY, 
    GET_GUILD_MEMBERS_QUERY, INSERT_RAID_TEMPLATE_QUERY, DELETE_RAID_TEMPLATE_QUERY,DELETE_RAID_CHARACTER_QUERY,
    INSERT_RAID_CHARACTER_QUERY, GET_ALL_UNITS_QUERY, GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY,
    GET_ALL_RAID_TEMPLATES_QUERY
)

def admin_panel():
    st.title("Админ-панель")

    admin_pages = {
        "Пользователи": manage_users,
        "Гильдии": manage_guilds,
        "Юниты": manage_units,
        "Рейды": manage_raids
    }
    selected_page = st.sidebar.selectbox("Админ-панель", list(admin_pages.keys()))
    admin_pages[selected_page]()

def manage_users():
    conn = st.session_state.conn

    st.header("Управление пользователями")

    users = fetch_query(conn, GET_ALL_USERS_QUERY)

    if users:
        st.subheader("Список пользователей")
        for user in users:
            st.write(f"ID: {user['user_id']}, Имя: {user['name']}, Email: {user['email']}")

            player = fetch_query(conn, GET_PLAYER_BY_USER_ID_QUERY, (user['user_id'],))
            if player:
                st.write(f"Игровой аккаунт: {player[0]['name']}, Allycode: {player[0]['allycode']}")

                if st.button(f"Удалить игровой аккаунт {player[0]['name']}"):
                    try:
                        execute_query(conn, DELETE_PLAYER_QUERY, (player[0]['player_id'],))
                        st.success(f"Игровой аккаунт {player[0]['name']} удалён!")
                        st.experimental_rerun()  
                    except Exception as e:
                        handle_error(e)

            if st.button(f"Удалить пользователя {user['name']}"):
                try:
                    execute_query(conn, DELETE_USER_QUERY, (user['user_id'],))
                    st.success(f"Пользователь {user['name']} удалён!")
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Пользователи отсутствуют.")

def manage_units():
    conn = st.session_state.conn

    st.header("Управление юнитами")

    st.subheader("Добавить новый юнит")
    unit_name = st.text_input("Имя юнита")
    unit_type = st.selectbox("Тип юнита", ["character", "ship"])

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, INSERT_UNIT_QUERY,
                          (unit_name, unit_type))
            st.success(f"Юнит {unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

    st.subheader("Список юнитов")
    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if units:
        for unit in units:
            st.write(f"ID: {unit['unit_id']}, Имя: {unit['name']}, Тип: {unit['type']}")

            if st.button(f"Удалить юнит {unit['name']}"):
                try:
                    execute_query(conn, DELETE_UNIT_QUERY, (unit['unit_id'],))
                    st.success(f"Юнит {unit['name']} удалён!")
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Юниты отсутствуют.")

def manage_guilds():
    conn = st.session_state.conn 

    st.header("Управление гильдиями")

    guilds = fetch_query(conn, GET_ALL_GUILDS_QUERY)

    if guilds:
        st.subheader("Список гильдий")
        for guild in guilds:
            st.write(f"ID: {guild['guild_id']}, Название: {guild['name']}, Участников: {guild['members_count']}")

            if st.button(f"Просмотреть состав гильдии {guild['name']}"):
                view_guild_members(guild['guild_id'])

            if st.button(f"Удалить гильдию {guild['name']}"):
                try:
                    execute_query(conn, DELETE_GUILD_QUERY, (guild['guild_id'],))
                    st.success(f"Гильдия {guild['name']} удалена!")
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Гильдии отсутствуют.")

def view_guild_members(guild_id):
    conn = st.session_state.conn 

    st.subheader("Состав гильдии")

    players = fetch_query(conn, GET_GUILD_MEMBERS_QUERY, (guild_id,))

    if players:
        for player in players:
            st.write(f"Имя: {player['name']}, Allycode: {player['allycode']}, Роль: {player['guild_role']}")
    else:
        st.write("В гильдии нет участников.")

def manage_raids():
    conn = st.session_state.conn 

    st.header("Управление рейдами")

    st.subheader("Добавить новый тип рейда")
    raid_name = st.text_input("Название рейда")

    if st.button("Добавить рейд"):
        try:
            execute_query(conn, INSERT_RAID_TEMPLATE_QUERY, (raid_name,))
            st.success(f"Рейд {raid_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

    st.subheader("Список рейдов")
    raid_templates = fetch_query(conn, GET_ALL_RAID_TEMPLATES_QUERY)
    if raid_templates:
        for raid in raid_templates:
            st.write(f"ID: {raid['raid_template_id']}, Название: {raid['name']}")

            if st.button(f"Просмотреть персонажей рейда {raid['name']}"):
                view_raid_characters(raid['raid_template_id'])

            if st.button(f"Удалить рейд {raid['name']}"):
                try:
                    execute_query(conn, DELETE_RAID_TEMPLATE_QUERY, (raid['raid_template_id'],))
                    st.success(f"Рейд {raid['name']} удалён!")
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Рейды отсутствуют.")

def view_raid_characters(raid_template_id):
    conn = st.session_state.conn
     
    st.subheader("Персонажи рейда")

    raid_characters = fetch_query(conn, GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY, (raid_template_id,))

    if raid_characters:
        for character in raid_characters:
            st.write(f"ID: {character['raid_character_id']}, Юнит: {character['unit_name']}")

            if st.button(f"Удалить персонажа {character['unit_name']}"):
                try:
                    execute_query(conn, DELETE_RAID_CHARACTER_QUERY, (character['raid_character_id'],))
                    st.success(f"Персонаж {character['unit_name']} удалён из рейда!")
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Персонажи отсутствуют.")

    st.subheader("Добавить персонажа в рейд")

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return

    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    if st.button("Добавить персонажа"):
        try:
            execute_query(conn, INSERT_RAID_CHARACTER_QUERY, (raid_template_id, selected_unit_id))
            st.success(f"Персонаж {selected_unit_name} успешно добавлен в рейд!")
        except Exception as e:
            handle_error(e)