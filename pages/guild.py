import streamlit as st
import json

from utils.db import execute_query, fetch_with_cache, fetch_query
from utils.error_handling import handle_error
from database.queries import (
    GET_GUILD_MEMBERS_QUERY,
    ADD_GUILD_MEMBER_QUERY,
    REMOVE_GUILD_MEMBER_QUERY,
    UPDATE_GUILD_MEMBER_ROLE_QUERY
)
from database.redis_client import get_redis


def guild_page():
    if 'player' not in st.session_state or not st.session_state.player:
        st.warning("Пожалуйста, войдите как игрок и выберите гильдию.")
        return

    player = st.session_state.player
    guild_id = player.get('guild_id')
    if not guild_id:
        st.info("Вы не состоите в гильдии.")
        return

    conn = st.session_state.conn
    redis_client = get_redis()
    cache_key = f"guild:{guild_id}:members"

    st.header(f"Гильдия игрока: {player.get('guild_name', guild_id)}")

    # Кешируем состав гильдии
    members = fetch_with_cache(
        conn,
        redis_client,
        cache_key,
        GET_GUILD_MEMBERS_QUERY,
        (guild_id,)
    )

    # Отображение состава
    st.subheader("Состав гильдии")
    for m in members:
        st.write(f"{m['name']} (Allycode: {m['allycode']}) — Роль: {m['guild_role']}")

    # Проверка прав: только глава (role='leader')
    leader = next((m for m in members if m['allycode'] == player['allycode'] and m['guild_role']=='Глава'), None)
    if not leader:
        return  # только просмотр

    st.markdown("---")
    st.subheader("Управление гильдией")

    # Добавление участника
    with st.form("add_member_form"):
        new_allycode = st.text_input("Allycode нового участника")
        new_role = st.selectbox("Роль", ["Участник", "Офицер", "Глава"], index=0)
        submitted_add = st.form_submit_button("Добавить участника")
    if submitted_add and new_allycode:
        try:
            execute_query(conn, ADD_GUILD_MEMBER_QUERY, (guild_id, new_allycode, new_role))
            redis_client.delete(cache_key)
            redis_client.publish(
                "guild",
                json.dumps({"type":"member_add","guild_id":guild_id,"allycode":new_allycode,"role":new_role})
            )
            st.success(f"Участник {new_allycode} добавлен с ролью {new_role}.")
        except Exception as e:
            handle_error(e)

    # Удаление или изменение роли существующего
    with st.form("manage_member_form"):
        options = {f"{m['name']} ({m['allycode']}) — {m['guild_role']}": m for m in members}
        sel_label = st.selectbox("Выберите участника", list(options.keys()))
        sel = options[sel_label]
        action = st.radio("Действие", ["Удалить", "Изменить роль"], index=0)
        new_role2 = None
        if action == "Изменить роль":
            new_role2 = st.selectbox("Новая роль", ["Участник", "Офицер", "Глава"], index=0)
        submitted_manage = st.form_submit_button("Применить")
    if submitted_manage:
        try:
            if action == "Удалить":
                execute_query(conn, REMOVE_GUILD_MEMBER_QUERY, (guild_id, sel['allycode']))
                redis_client.publish(
                    "guild",
                    json.dumps({"type":"member_remove","guild_id":guild_id,"allycode":sel['allycode']})
                )
                st.success(f"Участник {sel['allycode']} удалён.")
            else:
                execute_query(conn, UPDATE_GUILD_MEMBER_ROLE_QUERY, (new_role2, guild_id, sel['allycode']))
                redis_client.publish(
                    "guild",
                    json.dumps({"type":"member_role_change","guild_id":guild_id,"allycode":sel['allycode'],"new_role":new_role2})
                )
                st.success(f"Роль участника {sel['allycode']} изменена на {new_role2}.")
            redis_client.delete(cache_key)
        except Exception as e:
            handle_error(e)