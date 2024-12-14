import streamlit as st

from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

from database.queries import GET_PLAYER_UNITS_QUERY, GET_ALL_UNITS_QUERY, ADD_PLAYER_UNIT_QUERY

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