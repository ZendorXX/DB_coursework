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

            # Добавление информации о юнитах
            add_player_units()
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

def add_player_units():
    st.subheader("Добавить информацию о своих юнитах")

    # Получение списка всех юнитов
    units = fetch_query(conn, "SELECT * FROM Units")
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return

    # Выбор юнита
    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    # Ввод игровой информации
    level = st.number_input("Уровень", min_value=1, max_value=85, value=1)
    stars = st.number_input("Количество звёзд", min_value=1, max_value=7, value=1)
    gear_level = st.number_input("Уровень снаряжения", min_value=1, max_value=12, value=1) if units[selected_unit_id - 1]['type'] == 'character' else None
    relic_level = st.number_input("Уровень реликвий", min_value=0, max_value=9, value=0) if units[selected_unit_id - 1]['type'] == 'character' else None

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, "INSERT INTO PlayerUnits (player_id, unit_id, level, stars, gear_level, relic_level) VALUES (%s, %s, %s, %s, %s, %s)",
                          (st.session_state.player['player_id'], selected_unit_id, level, stars, gear_level, relic_level))
            st.success(f"Юнит {selected_unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e) 

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

def admin_panel():
    st.title("Админ-панель")

    # Навигация по разделам админ-панели
    admin_pages = {
        "Пользователи": manage_users,
        "Гильдии": manage_guilds,
        "Юниты": manage_units,
    }
    selected_page = st.sidebar.selectbox("Админ-панель", list(admin_pages.keys()))
    admin_pages[selected_page]()

def manage_users():
    st.header("Управление пользователями")

    # Получение списка всех пользователей (кроме админов)
    users = fetch_query(conn, "SELECT * FROM Users WHERE system_role != 'admin'")

    if users:
        st.subheader("Список пользователей")
        for user in users:
            st.write(f"ID: {user['user_id']}, Имя: {user['name']}, Email: {user['email']}")

            # Получение игрового аккаунта пользователя
            player = fetch_query(conn, GET_PLAYER_BY_USER_ID_QUERY, (user['user_id'],))
            if player:
                st.write(f"Игровой аккаунт: {player[0]['name']}, Allycode: {player[0]['allycode']}")

                # Кнопка для удаления игрового аккаунта
                if st.button(f"Удалить игровой аккаунт {player[0]['name']}"):
                    try:
                        execute_query(conn, "DELETE FROM Players WHERE player_id = %s", (player[0]['player_id'],))
                        st.success(f"Игровой аккаунт {player[0]['name']} удалён!")
                        st.experimental_rerun()  # Перезагрузка страницы
                    except Exception as e:
                        handle_error(e)

            # Кнопка для удаления пользователя
            if st.button(f"Удалить пользователя {user['name']}"):
                try:
                    execute_query(conn, "DELETE FROM Users WHERE user_id = %s", (user['user_id'],))
                    st.success(f"Пользователь {user['name']} удалён!")
                    st.experimental_rerun()  # Перезагрузка страницы
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Пользователи отсутствуют.")

def manage_units():
    st.header("Управление юнитами")

    # Форма для добавления нового юнита
    st.subheader("Добавить новый юнит")
    unit_name = st.text_input("Имя юнита")
    unit_type = st.selectbox("Тип юнита", ["character", "ship"])
    is_character = unit_type == "character"

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, "INSERT INTO Units (name, type) VALUES (%s, %s)",
                          (unit_name, unit_type))
            st.success(f"Юнит {unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

    # Отображение списка всех юнитов
    st.subheader("Список юнитов")
    units = fetch_query(conn, "SELECT * FROM Units")
    if units:
        for unit in units:
            st.write(f"ID: {unit['unit_id']}, Имя: {unit['name']}, Тип: {unit['type']}")
    else:
        st.write("Юниты отсутствуют.")

def manage_guilds():
    st.header("Управление гильдиями")

    # Получение списка всех гильдий
    guilds = fetch_query(conn, "SELECT * FROM Guilds")

    if guilds:
        st.subheader("Список гильдий")
        for guild in guilds:
            st.write(f"ID: {guild['guild_id']}, Название: {guild['name']}, Участников: {guild['members_count']}")

            # Кнопка для просмотра состава гильдии
            if st.button(f"Просмотреть состав гильдии {guild['name']}"):
                view_guild_members(guild['guild_id'])

            # Кнопка для удаления гильдии
            if st.button(f"Удалить гильдию {guild['name']}"):
                try:
                    execute_query(conn, "DELETE FROM Guilds WHERE guild_id = %s", (guild['guild_id'],))
                    st.success(f"Гильдия {guild['name']} удалена!")
                    st.experimental_rerun()  # Перезагрузка страницы
                except Exception as e:
                    handle_error(e)
    else:
        st.write("Гильдии отсутствуют.")

def view_guild_members(guild_id):
    st.subheader("Состав гильдии")

    # Получение списка игроков в гильдии
    players = fetch_query(conn, "SELECT * FROM Players WHERE guild_id = %s", (guild_id,))

    if players:
        for player in players:
            st.write(f"Имя: {player['name']}, Allycode: {player['allycode']}, Роль: {player['guild_role']}")
    else:
        st.write("В гильдии нет участников.")

def main():
    st.title("SWGOH Helper")
    initialize_session_state()

    if st.session_state.user:
        # Если пользователь авторизован
        if st.session_state.user['system_role'] == 'admin':
            # Если пользователь - администратор
            admin_navigation()
        else:
            # Если пользователь - обычный пользователь
            user_navigation()
    else:
        # Если пользователь не авторизован
        guest_navigation()

# Навигация для администратора
def admin_navigation():
    pages = {
        "Админ-панель": admin_panel,
        "Выход": logout_page
    }
    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

# Навигация для обычного пользователя
def user_navigation():
    pages = {
        "Домашняя страница": home_page,
        "Выход": logout_page
    }
    selected_page = st.sidebar.selectbox("Навигация", list(pages.keys()))
    pages[selected_page]()

# Навигация для гостя (неавторизованного пользователя)
def guest_navigation():
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