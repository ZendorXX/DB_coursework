import streamlit as st
import csv
import io
import os
import subprocess

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
        "Рейды": manage_raids,
        "Резервное копирование": backup_database, 
        "Восстановление базы данных": restore_database 
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

    unit_pages = {
        "Добавить новый юнит": add_new_unit,
        "Импорт юнитов из файла": import_units_from_file,
        "Импорт юнитов вручную": import_units_manually,
        "Просмотр и удаление юнитов": view_and_delete_units 
    }
    selected_page = st.sidebar.selectbox("Управление юнитами", list(unit_pages.keys()))
    unit_pages[selected_page]()

def view_and_delete_units():
    conn = st.session_state.conn
    st.subheader("Просмотр и удаление юнитов")

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if units:
        st.write("Список юнитов:")
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

def add_new_unit():
    conn = st.session_state.conn
    st.subheader("Добавить новый юнит")
    unit_name = st.text_input("Имя юнита")
    unit_type = st.selectbox("Тип юнита", ["character", "ship"])

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, INSERT_UNIT_QUERY, (unit_name, unit_type))
            st.success(f"Юнит {unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

def import_units_from_file():
    conn = st.session_state.conn
    st.subheader("Импорт юнитов из файла")
    st.write("Загрузите файл CSV с колонками 'name' и 'type' (например, 'character' или 'ship').")

    uploaded_file = st.file_uploader("Выберите файл", type=["csv"])
    if uploaded_file is not None:
        try:
            file_content = io.TextIOWrapper(uploaded_file, encoding='utf-8')

            units = []
            reader = csv.DictReader(file_content)
            for row in reader:
                units.append((row['Name'], row['Type']))

            for unit in units:
                execute_query(conn, INSERT_UNIT_QUERY, unit)

            st.success(f"Успешно добавлено {len(units)} юнитов!")
        except Exception as e:
            handle_error(e)

def import_units_manually():
    conn = st.session_state.conn
    st.subheader("Импорт юнитов вручную")
    st.write("Введите имена юнитов, разделенные переносом строки. Укажите тип юнита (character или ship) в конце строки через запятую.")

    units_text = st.text_area("Введите юнитов", height=300)
    if st.button("Добавить юнитов"):
        try:
            units = []
            for line in units_text.split("\n"):
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        name, unit_type = parts
                        units.append((name.strip(), unit_type.strip()))
                    else:
                        st.warning(f"Неверный формат строки: {line}")

            for unit in units:
                execute_query(conn, INSERT_UNIT_QUERY, unit)

            st.success(f"Успешно добавлено {len(units)} юнитов!")
        except Exception as e:
            handle_error(e)

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

    st.subheader("Добавить персонажа в рейд")

    raid_options = {raid['name']: raid['raid_template_id'] for raid in raid_templates}
    selected_raid_name = st.selectbox("Выберите рейд", list(raid_options.keys()))
    selected_raid_id = raid_options[selected_raid_name]

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return

    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    if st.button("Добавить персонажа"):
        try:
            execute_query(conn, INSERT_RAID_CHARACTER_QUERY, (selected_raid_id, selected_unit_id))
            st.success(f"Персонаж {selected_unit_name} успешно добавлен в рейд {selected_raid_name}!")
        except Exception as e:
            handle_error(e)

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

def backup_database():
    conn = st.session_state.conn

    st.subheader("Резервное копирование базы данных")

    db_name = "postgres"
    db_user = "postgres"
    db_password = "1234"
    db_host = "localhost"
    db_port = "5432"

    backup_path = st.text_input("Укажите путь для сохранения резервной копии", value="backup.dump")

    if st.button("Создать резервную копию"):
        try:
            command = f"pg_dump -U {db_user} -h {db_host} -p {db_port} -F c -b -v -f {backup_path} {db_name}"
            os.environ['PGPASSWORD'] = db_password
            subprocess.run(command, shell=True, check=True)
            st.success(f"Резервная копия успешно создана: {backup_path}")
        except Exception as e:
            st.error(f"Ошибка при создании резервной копии: {e}")
        finally:
            del os.environ['PGPASSWORD']

def restore_database():
    conn = st.session_state.conn

    st.subheader("Восстановление базы данных")

    db_name = "postgres"
    db_user = "postgres"
    db_password = "1234"
    db_host = "localhost"
    db_port = "5432"

    backup_path = st.text_input("Укажите путь к файлу резервной копии", value="backup.dump")

    if st.button("Восстановить базу данных"):
        try:
            command = f"pg_restore -U {db_user} -h {db_host} -p {db_port} -d {db_name} -v --clean {backup_path}"
            os.environ['PGPASSWORD'] = db_password
            subprocess.run(command, shell=True, check=True)
            st.success(f"База данных успешно восстановлена из: {backup_path}")
        except Exception as e:
            st.error(f"Ошибка при восстановлении базы данных: {e}")
        finally:
            del os.environ['PGPASSWORD']