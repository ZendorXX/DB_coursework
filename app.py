import streamlit as st
from database.db_config import get_connection
from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error
from database.queries import (
    REGISTER_USER_QUERY, LOGIN_USER_QUERY, GET_PLAYER_BY_USER_ID_QUERY, ADD_PLAYER_QUERY,
    GET_GUILD_BY_NAME_QUERY, ADD_GUILD_QUERY, ADD_PLAYER_TO_GUILD_QUERY, ADD_PLAYER_UNIT_QUERY,
    GET_PLAYER_UNITS_QUERY, GET_ALL_USERS_QUERY, DELETE_USER_QUERY, DELETE_PLAYER_QUERY,
    GET_ALL_GUILDS_QUERY, DELETE_GUILD_QUERY, GET_ALL_UNITS_QUERY, DELETE_UNIT_QUERY,
    INSERT_UNIT_QUERY, GET_GUILD_MEMBERS_QUERY, INSERT_RAID_TEMPLATE_QUERY, GET_ALL_RAID_TEMPLATES_QUERY,
    DELETE_RAID_TEMPLATE_QUERY, GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY, DELETE_RAID_CHARACTER_QUERY,
    INSERT_RAID_CHARACTER_QUERY
)

import bcrypt

def initialize_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "player" not in st.session_state:
        st.session_state.player = None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

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

        get_player_info(st.session_state.user['user_id'])

        if st.session_state.player:
            display_player_info()

            if not st.session_state.player['guild_id']:
                join_guild_form()
                
        else:
            add_player_account_form()
    else:
        st.write("Пожалуйста, войдите или зарегистрируйтесь.")

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
    guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))
    if not guild:
        execute_query(conn, ADD_GUILD_QUERY, (guild_name,))
        guild = fetch_query(conn, GET_GUILD_BY_NAME_QUERY, (guild_name,))

    execute_query(conn, ADD_PLAYER_TO_GUILD_QUERY, (guild[0]['guild_id'], guild_role, st.session_state.user['user_id']))

def add_player_units():
    st.subheader("Добавить информацию о своих юнитах")

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return

    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    level = st.number_input("Уровень", min_value=1, max_value=85, value=1)
    stars = st.number_input("Количество звёзд", min_value=1, max_value=7, value=1)
    gear_level = st.number_input("Уровень снаряжения", min_value=1, max_value=12, value=1) if units[selected_unit_id - 1]['type'] == 'character' else None
    relic_level = st.number_input("Уровень реликвий", min_value=0, max_value=9, value=0) if units[selected_unit_id - 1]['type'] == 'character' else None

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, ADD_PLAYER_UNIT_QUERY,
                          (st.session_state.player['player_id'], selected_unit_id, level, stars, gear_level, relic_level))
            st.success(f"Юнит {selected_unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e) 

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

def logout_page():
    st.session_state.user = None
    st.session_state.player = None
    st.success("Выход выполнен успешно!")

def units_page():
    st.header("Ваши юниты")

    if not st.session_state.player:
        st.warning("Пожалуйста, добавьте игровой аккаунт.")
        return

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return

    st.subheader("Добавить юнит")
    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    level = st.number_input("Уровень", min_value=1, max_value=85, value=1)
    stars = st.number_input("Количество звёзд", min_value=1, max_value=7, value=1)
    gear_level = st.number_input("Уровень снаряжения", min_value=1, max_value=12, value=1) if units[selected_unit_id - 1]['type'] == 'character' else None
    relic_level = st.number_input("Уровень реликвий", min_value=0, max_value=8, value=0) if units[selected_unit_id - 1]['type'] == 'character' else None

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, ADD_PLAYER_UNIT_QUERY,
                          (st.session_state.player['player_id'], selected_unit_id, level, stars, gear_level, relic_level))
            st.success(f"Юнит {selected_unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

    st.subheader("Ваши юниты")
    player_units = fetch_query(conn, GET_PLAYER_UNITS_QUERY, (st.session_state.player['player_id'],))
    if player_units:
        for unit in player_units:
            st.write(f"Юнит: {unit['unit_name']} (Тип: {unit['unit_type']})")
            if unit['unit_type'] == 'character':
                st.write(f"Уровень: {unit['level']}, Звёзд: {unit['stars']} Снаряжение: {unit['gear_level']}, Реликвии: {unit['relic_level']}")
            else:
                st.write(f"Уровень: {unit['level']}, Звёзд: {unit['stars']}")
    else:
        st.write("У вас пока нет юнитов.")

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
    st.subheader("Состав гильдии")

    players = fetch_query(conn, GET_GUILD_MEMBERS_QUERY, (guild_id,))

    if players:
        for player in players:
            st.write(f"Имя: {player['name']}, Allycode: {player['allycode']}, Роль: {player['guild_role']}")
    else:
        st.write("В гильдии нет участников.")

def manage_raids():
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

def raids_page():
    st.header("Рейды")

    if not st.session_state.player:
        st.warning("Пожалуйста, добавьте игровой аккаунт.")
        return

    raid_templates = fetch_query(conn, GET_ALL_RAID_TEMPLATES_QUERY)
    if not raid_templates:
        st.write("Рейды отсутствуют. Обратитесь к администратору.")
        return

    st.subheader("Выберите рейд для просмотра персонажей")
    raid_options = {raid['name']: raid['raid_template_id'] for raid in raid_templates}
    selected_raid_name = st.selectbox("Выберите рейд", list(raid_options.keys()))
    selected_raid_id = raid_options[selected_raid_name]

    st.subheader(f"Персонажи рейда: {selected_raid_name}")
    raid_characters = fetch_query(conn, GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY, (selected_raid_id,))

    if raid_characters:
        for character in raid_characters:
            st.write(f"Юнит: {character['unit_name']}")
    else:
        st.write("Персонажи для этого рейда отсутствуют.")

if __name__ == "__main__":
    conn = get_connection()
    main()