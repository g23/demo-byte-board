DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE users (
    id integer primary key autoincrement,
    username text unique not null,
    pass text not null,
    email text, -- not required
    power_level integer not null,
    joined_on datetime default current_timestamp
);

CREATE TABLE posts (
    id integer primary key autoincrement,
    user_id integer references users,
    title text not null,
    content text not null,
    is_topic integer default 0,
    topic_id integer references posts,
    min_power_level integer, -- maybe access restriction if time permits
    created_at datetime default current_timestamp
);