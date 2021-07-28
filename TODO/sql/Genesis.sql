drop table if exists tasks;
drop table if exists users;


create table users (
      id serial primary key,
      name text unique not null,
      mail text unique not null,
      pwd text unique not null
);


create table tasks (
    id serial primary key,
    task_name text unique not null,
    task_description text unique not null,
    due_date date,
    due_time time,
    _user integer,
    foreign key(_user) references users(id) on delete cascade
);
