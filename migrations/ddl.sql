CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    system_role VARCHAR(255) NOT NULL
);

CREATE TABLE Players (
    player_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    allycode VARCHAR(255) NOT NULL UNIQUE,
    galactic_power INT NOT NULL,
    guild_id INT,
    guild_role VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
);

CREATE TABLE Guilds (
    guild_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    members_count INT NOT NULL,
    total_galactic_power INT NOT NULL
);

CREATE TABLE Units (
    unit_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level INT NOT NULL,
    stars INT NOT NULL,
    type VARCHAR(255) NOT NULL
);

CREATE TABLE CharacterDetails (
    unit_id INT PRIMARY KEY,
    gear_level INT NOT NULL,
    relic_level INT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id)
);

CREATE TABLE PlayerUnits (
    player_unit_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    unit_id INT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id)
);

CREATE TABLE RaidTemplates (
    raid_template_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Raids (
    raid_id SERIAL PRIMARY KEY,
    raid_template_id INT NOT NULL,
    guild_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    FOREIGN KEY (raid_template_id) REFERENCES RaidTemplates(raid_template_id),
    FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
);

CREATE TABLE RaidCharacters (
    raid_character_id SERIAL PRIMARY KEY,
    raid_template_id INT NOT NULL,
    unit_id INT NOT NULL,
    FOREIGN KEY (raid_template_id) REFERENCES RaidTemplates(raid_template_id),
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id)
);

CREATE TABLE RaidResults (
    raid_result_id SERIAL PRIMARY KEY,
    raid_id INT NOT NULL,
    player_id INT NOT NULL,
    score INT NOT NULL,
    FOREIGN KEY (raid_id) REFERENCES Raids(raid_id),
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);








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