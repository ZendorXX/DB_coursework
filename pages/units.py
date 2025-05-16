import streamlit as st
import csv
import io

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

from database.queries import (
    GET_PLAYER_UNITS_QUERY, GET_ALL_UNITS_QUERY, ADD_PLAYER_UNIT_QUERY,
    UPDATE_PLAYER_UNIT_QUERY
)

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

            st.success("Юниты успешно импортированы!")
        except Exception as e:
            handle_error(e)


def units_page():
    conn = st.session_state.conn

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
            st.success(f"Юнит {selected_unit_name} успешно добавлен!")
        except Exception as e:
            handle_error(e)

    import_units_from_file()

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
            st.success("Юниты успешно импортированы!")
        except Exception as e:
            handle_error(e)

    st.subheader("Ваши юниты")
    player_units = fetch_query(conn, GET_PLAYER_UNITS_QUERY, (st.session_state.player['player_id'],))
    if player_units:
        unit_options = {f"{unit['unit_name']} (Уровень: {unit['level']}, Звёзд: {unit['stars']})": unit for unit in player_units}
        selected_unit = st.selectbox("Выберите юнит для редактирования", list(unit_options.keys()))
        selected_unit_data = unit_options[selected_unit]

        st.write(f"Юнит: {selected_unit_data['unit_name']} (Тип: {selected_unit_data['unit_type']})")

        new_level = st.number_input("Уровень", min_value=1, max_value=85, value=selected_unit_data['level'], key="edit_unit_level")
        new_stars = st.number_input("Количество звёзд", min_value=1, max_value=7, value=selected_unit_data['stars'], key="edit_unit_stars")
        new_gear_level = st.number_input("Уровень снаряжения", min_value=1, max_value=12, value=selected_unit_data['gear_level'], key="edit_unit_gear_level") if selected_unit_data['unit_type'] == 'character' else None
        new_relic_level = st.number_input("Уровень реликвий", min_value=0, max_value=8, value=selected_unit_data['relic_level'], key="edit_unit_relic_level") if selected_unit_data['unit_type'] == 'character' else None

        if st.button("Сохранить изменения"):
            try:
                execute_query(conn, UPDATE_PLAYER_UNIT_QUERY,
                              (new_level, new_stars, new_gear_level, new_relic_level, selected_unit_data['player_unit_id']))
                st.success(f"Юнит {selected_unit_data['unit_name']} успешно обновлён!")
            except Exception as e:
                handle_error(e)
    else:
        st.write("У вас пока нет юнитов.")