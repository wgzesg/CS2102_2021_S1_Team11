DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE categories (
    category VARCHAR PRIMARY KEY NOT NULL
);
INSERT INTO categories VALUES ('bird');
INSERT INTO categories VALUES ('cat');
INSERT INTO categories VALUES ('dog');
INSERT INTO categories VALUES ('hamster');
INSERT INTO categories VALUES ('shark');
INSERT INTO categories VALUES ('fish');
INSERT INTO categories VALUES ('rabbit');
INSERT INTO categories VALUES ('spider');
INSERT INTO categories VALUES ('turtle');
INSERT INTO categories VALUES ('insect');
INSERT INTO categories VALUES ('horse');
INSERT INTO categories VALUES ('duck');
INSERT INTO categories VALUES ('hedgehog');
INSERT INTO categories VALUES ('snake');
INSERT INTO categories VALUES ('guinea pig');

CREATE TABLE users (
    username VARCHAR NOT NULL,
    contact BIGINT PRIMARY KEY NOT NULL,
    card VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    usertype VARCHAR NOT NULL,
    postalcode BIGINT NOT NULL
);

CREATE TABLE role (
    name VARCHAR NOT NULL UNIQUE
);
INSERT INTO role VALUES ('admin');
INSERT INTO role VALUES ('petowner');
INSERT INTO role VALUES ('caretaker');

CREATE TABLE user_roles (
    contact BIGINT PRIMARY KEY NOT NULL REFERENCES public.users(contact),
    usertype VARCHAR NOT NULL REFERENCES public.role(name)
);

CREATE TABLE canparttime (
    ccontact BIGINT PRIMARY KEY NOT NULL REFERENCES public.users(contact),
    isparttime BOOLEAN NOT NULL,
    avgrating FLOAT NOT NULL,
    petday INT NOT NULL,
    salary INTEGER NOT NULL
);

CREATE TABLE dailyprice (
    category VARCHAR NOT NULL REFERENCES public.categories(category),
    rating INTEGER NOT NULL,
    price INTEGER NOT NULL,
    PRIMARY KEY (category, rating)
);

INSERT INTO dailyprice VALUES ('dog', 1, 10);
INSERT INTO dailyprice VALUES ('dog', 2, 20);
INSERT INTO dailyprice VALUES ('dog', 3, 30);
INSERT INTO dailyprice VALUES ('dog', 4, 40);
INSERT INTO dailyprice VALUES ('dog', 5, 50);
INSERT INTO dailyprice VALUES ('cat', 1, 11);
INSERT INTO dailyprice VALUES ('cat', 2, 22);
INSERT INTO dailyprice VALUES ('cat', 3, 33);
INSERT INTO dailyprice VALUES ('cat', 4, 44);
INSERT INTO dailyprice VALUES ('cat', 5, 55);
INSERT INTO dailyprice VALUES ('bird', 1, 12);
INSERT INTO dailyprice VALUES ('bird', 2, 24);
INSERT INTO dailyprice VALUES ('bird', 3, 36);
INSERT INTO dailyprice VALUES ('bird', 4, 48);
INSERT INTO dailyprice VALUES ('bird', 5, 60);
INSERT INTO dailyprice VALUES ('shark', 1, 10);
INSERT INTO dailyprice VALUES ('shark', 2, 20);
INSERT INTO dailyprice VALUES ('shark', 3, 30);
INSERT INTO dailyprice VALUES ('shark', 4, 40);
INSERT INTO dailyprice VALUES ('shark', 5, 50);
INSERT INTO dailyprice VALUES ('hamster', 1, 10);
INSERT INTO dailyprice VALUES ('hamster', 2, 20);
INSERT INTO dailyprice VALUES ('hamster', 3, 30);
INSERT INTO dailyprice VALUES ('hamster', 4, 40);
INSERT INTO dailyprice VALUES ('hamster', 5, 50);
INSERT INTO dailyprice VALUES ('fish', 1, 10);
INSERT INTO dailyprice VALUES ('fish', 2, 20);
INSERT INTO dailyprice VALUES ('fish', 3, 30);
INSERT INTO dailyprice VALUES ('fish', 4, 40);
INSERT INTO dailyprice VALUES ('fish', 5, 50);
INSERT INTO dailyprice VALUES ('rabbit', 1, 10);
INSERT INTO dailyprice VALUES ('rabbit', 2, 20);
INSERT INTO dailyprice VALUES ('rabbit', 3, 30);
INSERT INTO dailyprice VALUES ('rabbit', 4, 40);
INSERT INTO dailyprice VALUES ('rabbit', 5, 50);
INSERT INTO dailyprice VALUES ('spider', 1, 10);
INSERT INTO dailyprice VALUES ('spider', 2, 20);
INSERT INTO dailyprice VALUES ('spider', 3, 30);
INSERT INTO dailyprice VALUES ('spider', 4, 40);
INSERT INTO dailyprice VALUES ('spider', 5, 50);
INSERT INTO dailyprice VALUES ('turtle', 1, 10);
INSERT INTO dailyprice VALUES ('turtle', 2, 20);
INSERT INTO dailyprice VALUES ('turtle', 3, 30);
INSERT INTO dailyprice VALUES ('turtle', 4, 40);
INSERT INTO dailyprice VALUES ('turtle', 5, 50);
INSERT INTO dailyprice VALUES ('insect', 1, 10);
INSERT INTO dailyprice VALUES ('insect', 2, 20);
INSERT INTO dailyprice VALUES ('insect', 3, 30);
INSERT INTO dailyprice VALUES ('insect', 4, 40);
INSERT INTO dailyprice VALUES ('insect', 5, 50);
INSERT INTO dailyprice VALUES ('horse', 1, 10);
INSERT INTO dailyprice VALUES ('horse', 2, 20);
INSERT INTO dailyprice VALUES ('horse', 3, 30);
INSERT INTO dailyprice VALUES ('horse', 4, 40);
INSERT INTO dailyprice VALUES ('horse', 5, 50);
INSERT INTO dailyprice VALUES ('duck', 1, 10);
INSERT INTO dailyprice VALUES ('duck', 2, 20);
INSERT INTO dailyprice VALUES ('duck', 3, 30);
INSERT INTO dailyprice VALUES ('duck', 4, 40);
INSERT INTO dailyprice VALUES ('duck', 5, 50);
INSERT INTO dailyprice VALUES ('hedgehog', 1, 10);
INSERT INTO dailyprice VALUES ('hedgehog', 2, 20);
INSERT INTO dailyprice VALUES ('hedgehog', 3, 30);
INSERT INTO dailyprice VALUES ('hedgehog', 4, 40);
INSERT INTO dailyprice VALUES ('hedgehog', 5, 50);
INSERT INTO dailyprice VALUES ('snake', 1, 10);
INSERT INTO dailyprice VALUES ('snake', 2, 20);
INSERT INTO dailyprice VALUES ('snake', 3, 30);
INSERT INTO dailyprice VALUES ('snake', 4, 40);
INSERT INTO dailyprice VALUES ('snake', 5, 50);
INSERT INTO dailyprice VALUES ('guinea pig', 1, 10);
INSERT INTO dailyprice VALUES ('guinea pig', 2, 20);
INSERT INTO dailyprice VALUES ('guinea pig', 3, 30);
INSERT INTO dailyprice VALUES ('guinea pig', 4, 40);
INSERT INTO dailyprice VALUES ('guinea pig', 5, 50);

CREATE TABLE pets(
    petname VARCHAR NOT NULL,
    pcontact BIGINT NOT NULL REFERENCES public.users(contact),
    category VARCHAR NOT NULL REFERENCES public.categories(category),
    age INTEGER NOT NULL,
    PRIMARY KEY (petName, pcontact)
);

CREATE TABLE available (
    startday DATE NOT NULL,
    endday DATE NOT NULL CHECK(endday - startday >= 0),
    ccontact BIGINT NOT NULL REFERENCES public.users(contact),
    PRIMARY KEY (ccontact, startday, endday)
);

CREATE TABLE cantakecare (
    ccontact BIGINT NOT NULL REFERENCES public.users(contact),
    category VARCHAR REFERENCES public.categories(category), 
    PRIMARY KEY (ccontact, category)
);

CREATE TABLE biddings(
  pcontact BIGINT NOT NULL,
  ccontact BIGINT NOT NULL REFERENCES public.users(contact),
  petname VARCHAR NOT NULL,

  startday DATE NOT NULL,
  endday DATE NOT NULL CHECK(endday - startday >= 0),

  /* paymentmode is either 'creditcard' or 'cash' */
  paymentmode VARCHAR NOT NULL,
  /* delivermode is either 'pet owner deliver' or 'pick up' or 'transfer through PCS' */
  deliverymode VARCHAR NOT NULL,

  /* status can be pending, success, fail or end */
  status VARCHAR NOT NULL,

  PRIMARY KEY (pcontact, ccontact, petname, startday, endday),
  FOREIGN KEY (pcontact, petname) REFERENCES public.pets(pcontact, petname)
);

CREATE TABLE reviews(
    pcontact BIGINT NOT NULL,
    ccontact BIGINT NOT NULL,
    petname VARCHAR NOT NULL,
    startday DATE NOT NULL,
    endday DATE NOT NULL CHECK(endday - startday >= 0),
    rating INTEGER NOT NULL CHECK(rating <= 5 AND rating >= 0),
    review VARCHAR NOT NULL,
    PRIMARY KEY (pcontact, ccontact, petname, startday, endday)
);
 
