from database.db_config import get_connection

def main(target_user_id):
    update_query = """
    UPDATE Users
    SET system_role = 'admin'
    WHERE user_id = %s;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(update_query, (target_user_id,))
            conn.commit()

            if cur.rowcount == 0:
                print(f"Пользователь с user_id = {target_user_id} не найден.")
            else:
                print(f"Роль пользователя с user_id = {target_user_id} успешно обновлена на 'admin'.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    conn = get_connection()
    main(6)