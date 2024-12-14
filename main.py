import streamlit as st
from db_config import get_connection
from utils.db import execute_query, fetch_query
from utils.error_handling import handle_error

st.title("SWGOH Helper")

conn = get_connection()

def get_players():
    query = "SELECT * FROM PlayerGuildView;"
    return fetch_query(conn, query)

if st.button("Показать игроков"):
    try:
        players = get_players()
        st.write(players)
    except Exception as e:
        handle_error(e)

def add_player(user_id, name, allycode, galactic_power, guild_id, guild_role):
    query = """
    CALL add_player(%s, %s, %s, %s, %s, %s);
    """
    execute_query(conn, query, (user_id, name, allycode, galactic_power, guild_id, guild_role))

with st.form("add_player_form"):
    st.write("Добавить игрока")
    user_id = st.number_input("User ID", value=1)
    name = st.text_input("Имя игрока")
    allycode = st.text_input("Код союзника")
    galactic_power = st.number_input("Галактическая мощь", value=0)
    guild_id = st.number_input("Guild ID", value=1)
    guild_role = st.selectbox("Роль в гильдии", ["Leader", "Officer", "Member"])
    submit = st.form_submit_button("Добавить")

if submit:
    try:
        add_player(user_id, name, allycode, galactic_power, guild_id, guild_role)
        st.success("Игрок добавлен!")
    except Exception as e:
        handle_error(e)