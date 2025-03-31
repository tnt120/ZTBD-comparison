create table drugs
(
    id                       int auto_increment
        primary key,
    atc_codes                varchar(255)  null,
    characteristic           varchar(1024) null,
    company                  varchar(512)  null,
    info                     varchar(1024) null,
    name                     varchar(512)  null,
    permit_expiration        varchar(512)  null,
    permit_number            varchar(512)  null,
    pharmaceutical_form_name varchar(512)  null,
    power                    varchar(2048) null,
    procedure_type           varchar(512)  null
);

create table drug_packs
(
    id                     char(36) not null  default(UUID()) primary key,
    accessibility_category varchar(255) null,
    gtin_code              varchar(255) null,
    pack_size              varchar(255) null,
    pack_type              varchar(255) null,
    pack_unit              varchar(255) null,
    packages_quantity      varchar(255) null,
    drug_id                int          not null,
    constraint drug_packs_ibfk_1
        foreign key (drug_id) references drugs (id)
            on delete cascade
);

create index drug_id
    on drug_packs (drug_id);

create table units
(
    id     char(36)     not null
        primary key,
    name   varchar(255) not null,
    symbol varchar(255) not null,
    constraint name
        unique (name),
    constraint symbol
        unique (symbol)
);

create table parameters
(
    id                 char(36)     not null
        primary key,
    hint               varchar(255) not null,
    max_standard_value double       not null,
    max_value          double       not null,
    min_standard_value double       not null,
    min_value          double       not null,
    name               varchar(255) not null,
    unit_id            char(36)     null,
    constraint name
        unique (name),
    constraint parameters_ibfk_1
        foreign key (unit_id) references units (id)
            on delete set null
);

create index unit_id
    on parameters (unit_id);

create table users
(
    id            char(36)                         not null
        primary key,
    email         varchar(255)                     not null,
    name          varchar(255)                     not null,
    surname       varchar(255)                     not null,
    password      varchar(255)                     not null,
    birth_date    date                             not null,
    creation_date datetime(6)                      not null,
    sex           enum ('MALE', 'FEMALE', 'OTHER') not null
);

create table drugs_logs
(
    id         char(36)                                                                            not null
        primary key,
    created_at datetime(6)                                                                         null,
    day        enum ('SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY') not null,
    taken_time time(6)                                                                             not null,
    time       time(6)                                                                             not null,
    drug_id    int                                                                                 not null,
    user_id    char(36)                                                                            not null,
    constraint drugs_logs_ibfk_1
        foreign key (drug_id) references drugs (id)
            on delete cascade,
    constraint drugs_logs_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
);

create index drug_id
    on drugs_logs (drug_id);

create index user_id
    on drugs_logs (user_id);

create table parameters_logs
(
    id           char(36)    not null
        primary key,
    created_at   datetime(6) null,
    value        double      null,
    parameter_id char(36)    null,
    user_id      char(36)    null,
    constraint parameters_logs_ibfk_1
        foreign key (parameter_id) references parameters (id)
            on delete cascade,
    constraint parameters_logs_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
);

create index parameter_id
    on parameters_logs (parameter_id);

create index user_id
    on parameters_logs (user_id);

create table user_drugs
(
    id         char(36)             not null
        primary key,
    amount     int                  null,
    dose_size  int                  not null,
    end_date   date                 null,
    priority   enum ('LOW', 'HIGH') not null,
    start_date date                 not null,
    drug_id    int                  not null,
    user_id    char(36)             not null,
    constraint user_drugs_ibfk_1
        foreign key (drug_id) references drugs (id)
            on delete cascade,
    constraint user_drugs_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
);

create table drug_dose_day
(
    id           char(36)                                                                            not null
        primary key,
    day          enum ('SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY') not null,
    user_drug_id char(36)                                                                            not null,
    constraint drug_dose_day_ibfk_1
        foreign key (user_drug_id) references user_drugs (id)
            on delete cascade
);

create index user_drug_id
    on drug_dose_day (user_drug_id);

create table drug_dose_time
(
    id           char(36) not null
        primary key,
    dose_time    time(6)  not null,
    user_drug_id char(36) not null,
    constraint drug_dose_time_ibfk_1
        foreign key (user_drug_id) references user_drugs (id)
            on delete cascade
);

create index user_drug_id
    on drug_dose_time (user_drug_id);

create index drug_id
    on user_drugs (drug_id);

create index user_id
    on user_drugs (user_id);

