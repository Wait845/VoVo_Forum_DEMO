create table register (
    email varchar(50) not null unique,
    password varchar(32) not null,
    veri_code int,
    session varchar(32) not null unique,
    session_at timestamp not null default now()
);


