CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    system_role VARCHAR(255) NOT NULL
);

CREATE TABLE Guilds (
    guild_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    members_count INT NOT NULL,
    total_galactic_power INT NOT NULL
);

CREATE TABLE Players (
    player_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    allycode VARCHAR(255) NOT NULL UNIQUE,
    galactic_power,
    guild_id INT,
    guild_role VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
);

CREATE TABLE Units (
    unit_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(255) NOT NULL
);

CREATE TABLE Player_Units (
    player_unit_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    unit_id INT NOT NULL,
    level INT NOT NULL,
    stars INT NOT NULL,
    gear_level INT,
    relic_level INT,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id)
);

CREATE TABLE Raid_Templates (
    raid_template_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Raids (
    raid_id SERIAL PRIMARY KEY,
    raid_template_id INT NOT NULL,
    guild_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    FOREIGN KEY (raid_template_id) REFERENCES Raid_Templates(raid_template_id),
    FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
);

CREATE TABLE Raid_Characters (
    raid_character_id SERIAL PRIMARY KEY,
    raid_template_id INT NOT NULL,
    unit_id INT NOT NULL,
    FOREIGN KEY (raid_template_id) REFERENCES Raid_Templates(raid_template_id),
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id)
);

CREATE TABLE Raid_Results (
    raid_result_id SERIAL PRIMARY KEY,
    raid_id INT NOT NULL,
    player_id INT NOT NULL,
    score INT NOT NULL,
    FOREIGN KEY (raid_id) REFERENCES Raids(raid_id),
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);

CREATE OR REPLACE PROCEDURE register_user(
    email VARCHAR(255),
    password_hash VARCHAR(255),
    name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Users (email, password_hash, name, system_role)
    VALUES (email, password_hash, name, 'user');
END;
$$;

CREATE OR REPLACE FUNCTION update_guild_members_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE Guilds
        SET members_count = members_count + 1
        WHERE guild_id = NEW.guild_id;

        IF (SELECT members_count FROM Guilds WHERE guild_id = NEW.guild_id) > 50 THEN
            RAISE EXCEPTION 'Гильдия не может содержать более 50 участников.';
        END IF;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE Guilds
        SET members_count = members_count - 1
        WHERE guild_id = OLD.guild_id;

        IF (SELECT members_count FROM Guilds WHERE guild_id = OLD.guild_id) < 1 THEN
            RAISE EXCEPTION 'Гильдия не может быть пустой.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_guild_members_count_trigger
AFTER INSERT OR DELETE ON Players
FOR EACH ROW
EXECUTE FUNCTION update_guild_members_count();

CREATE OR REPLACE FUNCTION delete_player_units_before_unit_delete()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM Player_Units WHERE unit_id = OLD.unit_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_unit_delete
BEFORE DELETE ON Units
FOR EACH ROW
EXECUTE FUNCTION delete_player_units_before_unit_delete();

CREATE OR REPLACE FUNCTION delete_player_before_user_delete()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM Players WHERE user_id = OLD.user_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_user_delete
BEFORE DELETE ON Users
FOR EACH ROW
EXECUTE FUNCTION delete_player_before_user_delete();

CREATE VIEW PlayerGuildView AS
SELECT p.player_id, p.name AS player_name, g.name AS guild_name, p.guild_role
FROM Players p
LEFT JOIN Guilds g ON p.guild_id = g.guild_id;

CREATE OR REPLACE FUNCTION get_guild_total_score(guild_id INT)
RETURNS INT AS $$
DECLARE
    total_score INT;
BEGIN
    SELECT SUM(rr.score) INTO total_score
    FROM RaidResults rr
    JOIN Raids r ON rr.raid_id = r.raid_id
    WHERE r.guild_id = $1;
    RETURN total_score;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE add_player(
    user_id INT,
    name VARCHAR(255),
    allycode VARCHAR(255),
    galactic_power INT,
    guild_id INT,
    guild_role VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Players (user_id, name, allycode, galactic_power, guild_id, guild_role)
    VALUES (user_id, name, allycode, galactic_power, guild_id, guild_role);
END;
$$;

CREATE TABLE Sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);