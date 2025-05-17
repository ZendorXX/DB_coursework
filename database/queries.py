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

ADD_GUILD_MEMBER_QUERY = """
INSERT INTO Players (user_id, name, allycode, galactic_power, guild_id, guild_role)
VALUES (
    (SELECT user_id FROM Players WHERE allycode = %s),
    (SELECT name FROM Players WHERE allycode = %s),
    %s,
    0,
    %s,
    %s
);
"""

REMOVE_GUILD_MEMBER_QUERY = """
DELETE FROM Players
WHERE guild_id = %s AND allycode = %s;
"""

UPDATE_GUILD_MEMBER_ROLE_QUERY = """
UPDATE Players
SET guild_role = %s
WHERE guild_id = %s AND allycode = %s;
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

UPDATE_PLAYER_UNIT_QUERY = """
UPDATE Player_Units
SET level = %s, stars = %s, gear_level = %s, relic_level = %s
WHERE player_unit_id = %s;
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

# Запросы для работы с рейдами
INSERT_RAID_TEMPLATE_QUERY = """
INSERT INTO Raid_Templates (name) VALUES (%s) RETURNING raid_template_id;
"""

GET_ALL_RAID_TEMPLATES_QUERY = """
SELECT * FROM Raid_Templates;
"""

DELETE_RAID_TEMPLATE_QUERY = """
DELETE FROM Raid_Templates WHERE raid_template_id = %s;
"""

# Запросы для работы с персонажами рейдов
INSERT_RAID_CHARACTER_QUERY = """
INSERT INTO Raid_Characters (raid_template_id, unit_id) VALUES (%s, %s);
"""

GET_RAID_CHARACTERS_BY_TEMPLATE_QUERY = """
SELECT rc.*, u.name AS unit_name
FROM Raid_Characters rc
JOIN Units u ON rc.unit_id = u.unit_id
WHERE rc.raid_template_id = %s;
"""

DELETE_RAID_CHARACTER_QUERY = """
DELETE FROM Raid_Characters WHERE raid_character_id = %s;
"""

INSERT_RAID_QUERY = """
INSERT INTO Raids (raid_template_id, guild_id, start_time, end_time)
VALUES (%s, %s, %s, %s);
"""

GET_RAIDS_BY_GUILD_ID_QUERY = """
SELECT r.raid_id as raid_id, rt.name as name
FROM Raids r
JOIN Raid_Templates rt ON r.raid_template_id = rt.raid_template_id
WHERE r.guild_id = %s
"""

INSERT_RAID_RESULT_QUERY = """
INSERT INTO Raid_Results (raid_id, player_id, score)
VALUES (%s, %s, %s)
"""