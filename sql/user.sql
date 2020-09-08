create table user (
    id int primary key auto_increment unique,
    name varchar(10) not null unique,
    password varchar(32) not null,
    email varchar(50) not null unique,
    join_at timestamp not null default now(),
    session varchar(32) unique,
    session_at timestamp not null default now() on update now(),
    is_locked boolean not null default 0,
    level int not null default 0
);

alter table user auto_increment = 10000;

# INSERT INTO user (name, password, email, session) VALUES ('vogel2', 'baoshizhu', '6118444@au.edu', 'BMcGVPp3bYKJyBAJ');
SELECT session FROM user WHERE id = 10000 AND TIMESTAMPDIFF(MINUTE, session_at, NOW());