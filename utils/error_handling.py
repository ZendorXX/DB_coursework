import streamlit as st

def handle_error(e):
    """
    Обрабатывает ошибки и выводит сообщение пользователю.
    """
    st.error(f"Произошла ошибка: {e}")