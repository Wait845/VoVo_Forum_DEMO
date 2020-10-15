create table reply (
    id int primary key auto_increment unique,
    post_id int not null REFERENCES post,
    id_inside int not null,
    replyer int not null REFERENCES user,
    content text not null ,
    reply_at timestamp not null default now(),
    is_locked boolean not null default 0
);

# INSERT INTO reply (post_id, id_inside, replyer, content) VALUES (10610, 1, 10070, 'hello');
#INSERT INTO reply (post_id, id_inside, replyer, content) VALUES (10005, (SELECT COUNT(id) FROM (SELECT id FROM reply WHERE post_id = 10005) AS temp)+1, 10008, 'hello');

