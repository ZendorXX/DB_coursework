REGISTER_USER_QUERY = """
CALL register_user(%s, %s, %s);
"""

LOGIN_USER_QUERY = """
SELECT * FROM Users WHERE email = %s;
"""

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