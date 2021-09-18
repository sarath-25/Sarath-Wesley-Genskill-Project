drop table if exists tasks;
drop table if exists users;


create table users (
      id varchar(100) primary key,
      name text unique not null,
      mail text unique not null,
      pwd text unique not null
);


create table tasks (
    id serial primary key,
    task_name text unique not null,
    task_description text unique not null,
    due_date date not null,
    due_time time not null,
    date_time text,
    status text,
    _user varchar(100),
    foreign key(_user) references users(id) on delete cascade
);
