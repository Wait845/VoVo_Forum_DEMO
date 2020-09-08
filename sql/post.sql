create table post (
    id int primary key auto_increment unique,
    poster_id int not null REFERENCES user,
    title varchar(120) not null,
    content text,
    posted_at timestamp not null default now(),
    click_num int not null default 0,
    last_replyer int not null REFERENCES user,
    last_reply_at timestamp not null default now() on update now(),
    reply_num int not null default 0,
    is_locked boolean not null default 0,
    top boolean not null default 0
);

alter table post auto_increment = 10000;

# INSERT INTO post (poster_id, title, content, last_replyer) VALUES ()

# SELECT post.id, posted_at, click_num, title, content, poster_id, user.name FROM post INNER JOIN user ON poster_id = user.id WHERE post.id = 10613;
# 查找某帖子附带发/回帖人名
SELECT post.id, post.poster_id, s1.name, post.title, post.last_replyer, s2.name, post.last_reply_at, post.reply_num, top FROM post
    INNER JOIN user AS s1 ON poster_id = s1.id
    INNER JOIN user AS s2 ON last_replyer = s2.id
    ORDER BY last_reply_at DESC LIMIT 10;