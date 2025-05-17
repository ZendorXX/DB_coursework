import streamlit as st
import json
import csv
import io

from utils.db import execute_query, fetch_query, fetch_with_cache
from utils.error_handling import handle_error

from database.queries import (
    GET_PLAYER_UNITS_QUERY, GET_ALL_UNITS_QUERY, ADD_PLAYER_UNIT_QUERY,
    UPDATE_PLAYER_UNIT_QUERY
)
from database.redis_client import get_redis

def import_units_from_file():
    conn = st.session_state.conn

    st.subheader("Импорт юнитов из CSV-файла")
    st.write("Загрузите файл CSV с колонками 'name', 'level', 'stars', 'gear_level', 'relic_level'.")

    uploaded_file = st.file_uploader("Выберите файл", type=["csv"])
    if uploaded_file is not None:
        try:
            file_content = io.TextIOWrapper(uploaded_file, encoding='utf-8')

            reader = csv.DictReader(file_content)
            for row in reader:
                try:
                    level = int(row['level'])
                    stars = int(row['stars'])
                    gear_level = int(row['gear_level']) if row['gear_level'] else None
                    relic_level = int(row['relic_level']) if row['relic_level'] else None
                except ValueError:
                    st.warning(f"Неверный формат чисел в строке: {row}")
                    continue

                unit_name = row['name']
                unit = fetch_query(conn, "SELECT unit_id FROM Units WHERE name = %s", (unit_name,))
                if not unit:
                    st.warning(f"Юнит с именем '{unit_name}' не найден в базе данных.")
                    continue

                unit_id = unit[0]['unit_id']

                execute_query(conn, ADD_PLAYER_UNIT_QUERY,
                              (st.session_state.player['player_id'], unit_id, level, stars, gear_level, relic_level))
                
            redis_client = get_redis()
            # Pub/Sub
            redis_client.publish(
                "units",
                json.dumps({
                    "type": "import_csv",
                    "action": "loaded",
                    "player_id": st.session_state.player['player_id'],
                    "player_name": st.session_state.player['name'],
                    "user_id": st.session_state.user['user_id'],
                    "user_name": st.session_state.user['name']
                })
            )

            st.success("Юниты успешно импортированы!")
        except Exception as e:
            handle_error(e)

def view_player_units():
    """
    Отображает, кеширует и позволяет редактировать юниты игрока.
    """
    conn = st.session_state.conn
    player_id = st.session_state.player['player_id']
    redis_client = get_redis()

    cache_key = f"player:{player_id}:units"
    # Кешируем список юнитов игрока
    units = fetch_with_cache(
        conn,
        redis_client,
        cache_key,
        GET_PLAYER_UNITS_QUERY,
        (player_id,)
    )

    st.subheader("Ваши юниты")
    if units:
        st.subheader("Ваши юниты")
        for unit in units:
            st.write(f"Имя: {unit['unit_name']}, \
                    Уровень: {unit['level']}, \
                    Звёзды: {unit['stars']}, \
                    Снаряжение: {unit['gear_level']}, \
                    Реликвии: {unit['relic_level']}")
    else:
        st.write("У вас пока нет юнитов.")
    
    st.subheader("Редактировать юниты")
    if units:
        # Формируем опции для selectbox
        unit_options = {
            f"{u['unit_name']} (Уровень: {u['level']}, Звёзд: {u['stars']})": u
            for u in units
        }
        selected_label = st.selectbox(
            "Выберите юнит для редактирования",
            list(unit_options.keys())
        )
        selected = unit_options[selected_label]

        st.write(f"Юнит: {selected['unit_name']} (Тип: {selected['unit_type']})")

        # Поля для редактирования
        new_level = st.number_input(
            "Уровень",
            min_value=1,
            max_value=85,
            value=selected['level'],
            key="edit_unit_level"
        )
        new_stars = st.number_input(
            "Количество звёзд",
            min_value=1,
            max_value=7,
            value=selected['stars'],
            key="edit_unit_stars"
        )
        new_gear_level = None
        new_relic_level = None
        if selected['unit_type'] == 'character':
            new_gear_level = st.number_input(
                "Уровень снаряжения",
                min_value=1,
                max_value=12,
                value=selected['gear_level'],
                key="edit_unit_gear_level"
            )
            new_relic_level = st.number_input(
                "Уровень реликвий",
                min_value=0,
                max_value=8,
                value=selected['relic_level'],
                key="edit_unit_relic_level"
            )

        if st.button("Сохранить изменения"):
            try:
                # Обновляем в БД
                execute_query(
                    conn,
                    UPDATE_PLAYER_UNIT_QUERY,
                    (new_level, new_stars, new_gear_level, new_relic_level, selected['player_unit_id'])
                )
                # Инвалидируем кеш юнитов игрока
                redis_client.delete(cache_key)
                # Публикуем событие об изменении
                redis_client.publish(
                    "units",
                    json.dumps({
                        "type": "unit_edit",
                        "action": "updated",
                        "player_id": st.session_state.player['player_id'],
                        "player_name": st.session_state.player['name'],
                        "user_id": st.session_state.user['user_id'],
                        "user_name": st.session_state.user['name'],
                        "unit_id": selected['player_unit_id']
                    })
                )
                st.success(f"Юнит {selected['unit_name']} успешно обновлён!")
            except Exception as e:
                handle_error(e)
    else:
        st.write("У вас пока нет юнитов.")

def import_units_manually():
    conn = st.session_state.conn
    st.subheader("Импорт юнитов вручную")
    st.write("Введите данные юнитов в формате: name,level,stars,gear_level,relic_level (по одному юниту на строку).")
    manual_input = st.text_area("Введите юнитов", height=200)
    if st.button("Импортировать юнитов"):
        try:
            for line in manual_input.split("\n"):
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) == 5:
                        unit_name, level, stars, gear_level, relic_level = parts
                        unit = fetch_query(conn, "SELECT unit_id FROM Units WHERE name = %s", (unit_name,))
                        if not unit:
                            st.warning(f"Юнит с именем '{unit_name}' не найден в базе данных.")
                            continue

                        unit_id = unit[0]['unit_id']
                        execute_query(conn, ADD_PLAYER_UNIT_QUERY,
                                      (st.session_state.player['player_id'], unit_id, level, stars, gear_level, relic_level))
                    else:
                        st.warning(f"Неверный формат строки: {line}")
            redis_client = get_redis()
            # Pub/Sub
            redis_client.publish(
                "units",
                json.dumps({
                    "type": "import_by_hand",
                    "action": "loaded",
                    "player_id": st.session_state.player['player_id'],
                    "player_name": st.session_state.player['name'],
                    "user_id": st.session_state.user['user_id'],
                    "user_name": st.session_state.user['name']
                })
            )
            st.success("Юниты успешно импортированы!")
        except Exception as e:
            handle_error(e)

def add_new_unit():
    conn = st.session_state.conn
    st.subheader("Добавить юнит")

    units = fetch_query(conn, GET_ALL_UNITS_QUERY)
    if not units:
        st.write("Юниты отсутствуют. Обратитесь к администратору.")
        return
    
    unit_options = {unit['name']: unit['unit_id'] for unit in units}
    selected_unit_name = st.selectbox("Выберите юнит для добавления", list(unit_options.keys()))
    selected_unit_id = unit_options[selected_unit_name]

    level = st.number_input("Уровень", min_value=1, max_value=85, value=1, key="add_unit_level")
    stars = st.number_input("Количество звёзд", min_value=1, max_value=7, value=1, key="add_unit_stars")
    gear_level = st.number_input("Уровень снаряжения", min_value=1, max_value=12, value=1, key="add_unit_gear_level") if units[selected_unit_id - 1]['type'] == 'character' else None
    relic_level = st.number_input("Уровень реликвий", min_value=0, max_value=8, value=0, key="add_unit_relic_level") if units[selected_unit_id - 1]['type'] == 'character' else None

    if st.button("Добавить юнит"):
        try:
            execute_query(conn, ADD_PLAYER_UNIT_QUERY,
                          (st.session_state.player['player_id'], selected_unit_id, level, stars, gear_level, relic_level))
            redis_client = get_redis()
            # Pub/Sub
            redis_client.publish(
                "units",
                json.dumps({
                    "type": "import_one_unit",
                    "action": "loaded",
                    "player_id": st.session_state.player['player_id'],
                    "player_name": st.session_state.player['name'],
                    "user_id": st.session_state.user['user_id'],
                    "user_name": st.session_state.user['name']
                })
            )
            st.success(f"Юнит {selected_unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)
    

def units_page():
    conn = st.session_state.conn

    st.header("Ваши юниты")

    if not st.session_state.player:
        st.warning("Пожалуйста, добавьте игровой аккаунт.")
        return

    st.header("Управление юнитами")

    unit_pages = {
        "Просмотр юнитов": view_player_units,
        "Добавить новый юнит": add_new_unit,
        "Импорт юнитов из файла": import_units_from_file,
        "Импорт юнитов вручную": import_units_manually
    }
    selected_page = st.sidebar.selectbox("Управление юнитами", list(unit_pages.keys()))
    unit_pages[selected_page]()

    

    