create table notification (
    id int primary key auto_increment unique,
    to_user int not null REFERENCES user,
    from_user int not null REFERENCES user,
    post_id int not null REFERENCES post(id),
    created_at timestamp not null default now(),
    seen boolean not null default 0,
    is_locked boolean not null default 0
);

# INSERT INTO notification (to_user, from_user, post_id) VALUES (10000, 10001, 100300);