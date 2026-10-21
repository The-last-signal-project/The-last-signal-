CREATE TABLE IF NOT EXISTS skill_saves (
    skillsave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,

    account_id INTEGER NOT NULL UNIQUE,
    skill_level INTEGER NOT NULL,


    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,
FOREIGN KEY (skill_id )
        REFERENCES skill(skill_id)
        ON DELETE RESTRICT,
FOREIGN KEY (skill_level)
        REFERENCES skills_level(skill_level)
        ON DELETE RESTRICT


);




CREATE TABLE IF NOT EXISTS skill (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
     

    skill_name TEXT NOT NULL UNIQUE,
    level_max INTEGER NOT NULL UNIQUE DEFAULT 1
);



CREATE TABLE IF NOT EXISTS skills_level (
    skill_level INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    level INTERGER NOT NULL DEFAULT 1,
    level_max INTEGER NOT NULL DEFAULT 1,
    bonus INTEGER NOT NULL,
    categorie TEXT  NOT NULL,
    CHECK ( level <= level_max),

    FOREIGN KEY (skill_id)
        REFERENCES skill(skill_id)
        ON DELETE RESTRICT,

  FOREIGN KEY (level_max)
        REFERENCES skill(level_max)
        ON DELETE RESTRICT
);


