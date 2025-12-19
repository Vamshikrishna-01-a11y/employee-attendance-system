create database eattendance;
use eattendance;
create table employee (
    emp_id int primary key auto_increment,
    emp_name varchar(50) not null
);
create table attendance (
    att_id int primary key auto_increment,
    emp_id int,
    att_date date,
    login_time time,
    logout_time time,
    work_hours float,
    foreign key (emp_id) references employee(emp_id),
    unique(emp_id, att_date)
);

select*from attendance;

insert into employee (emp_name) values ('Rahul');
insert into employee (emp_name) values ('Anita');
insert into employee (emp_name) values ('Anu');
insert into employee (emp_name) values ('Priya');

select * from employee;


