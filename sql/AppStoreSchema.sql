/*******************

  Create the schema

********************/
DROP SEQUENCE IF EXISTS job_id_seq;
CREATE SEQUENCE job_id_seq;

DROP TABLE IF EXISTS applications;
CREATE TABLE IF NOT EXISTS applications (
	email VARCHAR(64) NOT NULL ,
	job_id SERIAL NOT NULL ,
	PRIMARY KEY (email, job_id)
	);

DROP TABLE IF EXISTS skills;
CREATE TABLE IF NOT EXISTS skills(
	email VARCHAR(64),
	skill VARCHAR(64) NOT NULL,
	PRIMARY KEY (email, skill)
	);
	
DROP TABLE IF EXISTS past_exp;
CREATE TABLE IF NOT EXISTS past_exp(
	email VARCHAR(64),
	company_name VARCHAR(64) NOT NULL,
	dept VARCHAR(64) NOT NULL,
	job_title VARCHAR(64) NOT NULL,
	years INT NOT NULL CHECK ((years) >= 1),
	PRIMARY KEY (email,company_name, dept, job_title)
	);

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
	full_name VARCHAR(64) NOT NULL,
	email VARCHAR(64) PRIMARY KEY,
	phone_num CHAR(8) NOT NULL UNIQUE CHECK (LENGTH(phone_num) >= 8),
	location VARCHAR(9)
	CONSTRAINT location CHECK (LOWER(location) IN ('north', 'south', 'east', 'west', 'northeast', 'northwest', 'southwest', 'southeast'))
	);

DROP TABLE IF EXISTS jobs;
CREATE TABLE IF NOT EXISTS jobs(
	name VARCHAR(64),
	email VARCHAR(64),
	job_id SERIAL unique NOT NULL, --unique?
	job_title VARCHAR(64) NOT NULL,
	descript VARCHAR(512) NOT NULL,
	dept VARCHAR(64) NOT NULL,
	est_pay INT CHECK (est_pay >= 1),
	location VARCHAR(9)
	CONSTRAINT location CHECK (LOWER(location) IN ('north', 'south', 'east', 'west', 'northeast', 'northwest', 'southwest', 'southeast')),
	expiry DATE CHECK ((expiry) > NOW()),
	primary key (email, job_title, dept)
	);

DROP TABLE IF EXISTS company;
CREATE TABLE IF NOT EXISTS company(
	name VARCHAR(64) NOT NULL,
	industry VARCHAR(64) NOT NULL,
	email VARCHAR(64) PRIMARY KEY
	);


------------------------------------------
ALTER TABLE skills
	ADD CONSTRAINT fk_email FOREIGN KEY (email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE past_exp
	ADD CONSTRAINT fk_email FOREIGN KEY (email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
	
ALTER TABLE jobs
	ADD CONSTRAINT fk_email FOREIGN KEY (email) REFERENCES company(email) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE applications
	ADD CONSTRAINT fk_email FOREIGN KEY (email) references users(email) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
	ADD CONSTRAINT fk_job_id FOREIGN KEY (job_id) references jobs(job_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
	
