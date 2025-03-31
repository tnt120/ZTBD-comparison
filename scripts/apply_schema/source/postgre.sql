create table users
(
    id            uuid default gen_random_uuid() not null
        constraint id
            primary key,
    email         text                           not null,
    name          text                           not null,
    surname       text                           not null,
    password      text                           not null,
    birth_date    date                           not null,
    creation_date timestamp                      not null,
    sex           text                           not null
);

alter table users
    owner to postgres;

create table drugs
(
    id                       integer not null
        primary key,
    atc_codes                varchar(255),
    characteristic           varchar(1024),
    company                  varchar(512),
    info                     varchar(1024),
    name                     varchar(512),
    permit_expiration        varchar(512),
    permit_number            varchar(512),
    pharmaceutical_form_name varchar(512),
    power                    varchar(2048),
    procedure_type           varchar(512)
);

alter table drugs
    owner to postgres;

create table drug_packs
(
    id                     uuid default gen_random_uuid() not null
        primary key,
    accessibility_category varchar(255),
    gtin_code              varchar(255),
    pack_size              varchar(255),
    pack_type              varchar(255),
    pack_unit              varchar(255),
    packages_quantity      varchar(255),
    drug_id                integer
        constraint fkm2otv1x00ka652rwow6ne5tkq
            references drugs
);

alter table drug_packs
    owner to postgres;

create table user_drugs
(
    id         uuid default gen_random_uuid() not null
        primary key,
    amount     integer,
    dose_size  integer                        not null,
    end_date   date,
    priority   varchar(255)                   not null
        constraint user_drugs_priority_check
            check ((priority)::text = ANY
                   (ARRAY [('LOW'::character varying)::text, ('HIGH'::character varying)::text])),
    start_date date                           not null,
    drug_id    integer                        not null
        constraint fkddhawvhf3nwehwikswlbiy144
            references drugs,
    user_id    uuid                           not null
        constraint fk814sgkd0gh27wkawu2vaov12t
            references users
);

alter table user_drugs
    owner to postgres;

create table drug_dose_day
(
    id           uuid default gen_random_uuid() not null
        primary key,
    day          varchar(255)                   not null
        constraint drug_dose_day_day_check
            check ((day)::text = ANY
                   (ARRAY [('SUNDAY'::character varying)::text, ('MONDAY'::character varying)::text, ('TUESDAY'::character varying)::text, ('WEDNESDAY'::character varying)::text, ('THURSDAY'::character varying)::text, ('FRIDAY'::character varying)::text, ('SATURDAY'::character varying)::text])),
    user_drug_id uuid                           not null
        constraint fkdoh6jgefqiluwtex9dxln4uru
            references user_drugs
);

alter table drug_dose_day
    owner to postgres;

create table drug_dose_time
(
    id           uuid default gen_random_uuid() not null
        primary key,
    dose_time    time(6)                        not null,
    user_drug_id uuid                           not null
        constraint fk1o1um5u1rla9ys2kqmn35yacx
            references user_drugs
);

alter table drug_dose_time
    owner to postgres;

create table units
(
    id     uuid default gen_random_uuid() not null
        primary key,
    name   varchar(255)                   not null
        constraint uketw07nfppovq9p7ov8hcb38wy
            unique,
    symbol varchar(255)                   not null
        constraint ukmicsja0upstxrxx390w10oorb
            unique
);

alter table units
    owner to postgres;

create table parameters
(
    id                 uuid default gen_random_uuid() not null
        primary key,
    hint               varchar(255)                   not null,
    max_standard_value double precision               not null,
    max_value          double precision               not null,
    min_standard_value double precision               not null,
    min_value          double precision               not null,
    name               varchar(255)                   not null
        constraint uk103wr298mpbr2vhx5tr7ila1o
            unique,
    unit_id            uuid
        constraint fkleaodv34nl7jvw3n72q8c73nr
            references units
);

alter table parameters
    owner to postgres;

create table drugs_logs
(
    id         uuid default gen_random_uuid() not null
        primary key,
    created_at timestamp(6),
    day        varchar(255)                   not null
        constraint drugs_logs_day_check
            check ((day)::text = ANY
                   (ARRAY [('SUNDAY'::character varying)::text, ('MONDAY'::character varying)::text, ('TUESDAY'::character varying)::text, ('WEDNESDAY'::character varying)::text, ('THURSDAY'::character varying)::text, ('FRIDAY'::character varying)::text, ('SATURDAY'::character varying)::text])),
    taken_time time(6)                        not null,
    time       time(6)                        not null,
    drug_id    integer                        not null
        constraint fkk2n02ea121di9jb44q0p46bqp
            references drugs,
    user_id    uuid                           not null
        constraint fk701q8cq4xumxvvfw903iu59bm
            references users
);

alter table drugs_logs
    owner to postgres;

create table parameters_logs
(
    id           uuid default gen_random_uuid() not null
        primary key,
    created_at   timestamp(6),
    value        double precision,
    parameter_id uuid
        constraint fk8e9nwqd4vrk2hhjecuo52ch5o
            references parameters,
    user_id      uuid
        constraint fkb4viy83pn6kq04os5o130sf9s
            references users
);

alter table parameters_logs
    owner to postgres;