# Запросы для работы с пользователями
REGISTER_USER_QUERY = """
CALL register_user(%s, %s, %s);
"""

LOGIN_USER_QUERY = """
SELECT * FROM Users WHERE email = %s;
"""

# Запросы для работы с игровыми аккаунтами
GET_PLAYER_BY_USER_ID_QUERY = """
SELECT p.*, g.name AS guild_name
FROM Players p
LEFT JOIN Guilds g ON p.guild_id = g.guild_id
WHERE p.user_id = %s;
"""

ADD_PLAYER_QUERY = """
INSERT INTO Players (user_id, name, allycode, galactic_power, guild_id, guild_role)
VALUES (%s, %s, %s, 0, NULL, NULL);
"""

# Запросы для работы с гильдиями
GET_GUILD_BY_NAME_QUERY = """
SELECT * FROM Guilds WHERE name = %s;
"""

ADD_GUILD_QUERY = """
INSERT INTO Guilds (name, members_count, total_galactic_power)
VALUES (%s, 0, 0)
RETURNING guild_id;
"""

ADD_PLAYER_TO_GUILD_QUERY = """
UPDATE Players
SET guild_id = %s, guild_role = %s
WHERE user_id = %s;
"""

# Запросы для работы с юнитами
ADD_PLAYER_UNIT_QUERY = """
INSERT INTO Player_Units (player_id, unit_id, level, stars, gear_level, relic_level)
VALUES (%s, %s, %s, %s, %s, %s);
"""

GET_PLAYER_UNITS_QUERY = """
SELECT pu.*, u.name AS unit_name, u.type AS unit_type
FROM Player_Units pu
JOIN Units u ON pu.unit_id = u.unit_id
WHERE pu.player_id = %s;
"""

# Запросы для админ-панели
GET_ALL_USERS_QUERY = """
SELECT * FROM Users WHERE system_role != 'admin';
"""

DELETE_USER_QUERY = """
DELETE FROM Users WHERE user_id = %s;
"""

DELETE_PLAYER_QUERY = """
DELETE FROM Players WHERE player_id = %s;
"""

GET_ALL_GUILDS_QUERY = """
SELECT * FROM Guilds;
"""

DELETE_GUILD_QUERY = """
DELETE FROM Guilds WHERE guild_id = %s;
"""

GET_ALL_UNITS_QUERY = """
SELECT * FROM Units;
"""

DELETE_UNIT_QUERY = """
DELETE FROM Units WHERE unit_id = %s;
"""

INSERT_UNIT_QUERY = """
INSERT INTO Units (name, type) VALUES (%s, %s);
"""

GET_GUILD_MEMBERS_QUERY = """
SELECT * FROM Players WHERE guild_id = %s;
"""