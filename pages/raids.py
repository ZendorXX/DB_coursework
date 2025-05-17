import streamlit as st

from utils.db import fetch_query, fetch_with_cache

from database.queries import (
    GET_ALL_RAID_TEMPLATES_QUERY,
    GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY
)   
from database.redis_client import get_redis

def raids_page():
    conn = st.session_state.conn
    redis_client = get_redis()

    st.header("Рейды")

    if not st.session_state.player:
        st.warning("Пожалуйста, добавьте игровой аккаунт.")
        return

    # Кешируем список типов рейдов
    raid_templates = fetch_with_cache(
        conn,
        redis_client,
        'raids:templates',
        GET_ALL_RAID_TEMPLATES_QUERY
    )

    if not raid_templates:
        st.write("Рейды отсутствуют. Обратитесь к администратору.")
        return

    st.subheader("Выберите рейд для просмотра персонажей")
    raid_options = {raid['name']: raid['raid_template_id'] for raid in raid_templates}
    selected_raid_name = st.selectbox("Выберите рейд", list(raid_options.keys()))
    selected_raid_id = raid_options[selected_raid_name]

    st.subheader(f"Персонажи рейда: {selected_raid_name}")
    # Кешируем персонажей каждого шаблона рейда
    raid_characters = fetch_with_cache(
        conn,
        redis_client,
        f'raid:{selected_raid_id}:characters',
        GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY,
        (selected_raid_id,)
    )

    if raid_characters:
        for character in raid_characters:
            st.write(f"Юнит: {character['unit_name']}")
    else:
        st.write("Персонажи для этого рейда отсутствуют.")