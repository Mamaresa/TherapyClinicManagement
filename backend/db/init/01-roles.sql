-- Database roles (issue N1). Run once per PostgreSQL cluster as a superuser.
-- docker-compose runs this automatically on first start. In any other
-- environment, change both passwords before running it.
--
-- clinic_owner: owns the database and every table; used only for migrations.
--               CREATEDB is needed only to create the test database.
-- clinic_app:   the Django runtime role. Owns nothing, so it cannot ALTER,
--               DROP, TRUNCATE or disable triggers. Table privileges are
--               granted by the migrations (apps/core/migrations/0001_*).

CREATE ROLE clinic_owner LOGIN PASSWORD 'owner_dev_password' CREATEDB;
CREATE ROLE clinic_app LOGIN PASSWORD 'app_dev_password'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;

CREATE DATABASE clinic OWNER clinic_owner;
