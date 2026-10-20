"""Gera o SQLite para entrega usando a biblioteca padrao (sem Django).

A estrutura segue as tabelas criadas pelas migracoes convencionais de Django 5.2
(auth/admin/contenttypes/sessions) e migracoes do app blog. Destina-se a
ambientes offline; quando houver Django instalado, usar `manage.py migrate`
e `manage.py seed_demo` para verificacao adicional.
"""
import base64
import hashlib
import importlib.util
import os
import secrets
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db.sqlite3"
DATA = ROOT / "blog" / "demo_data.py"


def demo_data():
    spec = importlib.util.spec_from_file_location("demo_data", DATA)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def datetime_sql(dt):
    return dt.astimezone(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f")


def hash_password(password):
    rounds = 600000
    salt = secrets.token_urlsafe(15)[:22]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), rounds)
    return f"pbkdf2_sha256${rounds}${salt}${base64.b64encode(digest).decode()}"


SCHEMA = """
CREATE TABLE django_migrations (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, app varchar(255) NOT NULL, name varchar(255) NOT NULL, applied datetime NOT NULL);
CREATE TABLE django_content_type (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, app_label varchar(100) NOT NULL, model varchar(100) NOT NULL, UNIQUE(app_label,model));
CREATE TABLE auth_permission (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(255) NOT NULL, content_type_id integer NOT NULL REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED, codename varchar(100) NOT NULL, UNIQUE(content_type_id,codename));
CREATE TABLE auth_group (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(150) NOT NULL UNIQUE);
CREATE TABLE auth_group_permissions (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, group_id integer NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED, permission_id integer NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED, UNIQUE(group_id,permission_id));
CREATE TABLE auth_user (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, password varchar(128) NOT NULL, last_login datetime NULL, is_superuser bool NOT NULL, username varchar(150) NOT NULL UNIQUE, first_name varchar(150) NOT NULL, last_name varchar(150) NOT NULL, email varchar(254) NOT NULL, is_staff bool NOT NULL, is_active bool NOT NULL, date_joined datetime NOT NULL);
CREATE TABLE auth_user_groups (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED, group_id integer NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED, UNIQUE(user_id,group_id));
CREATE TABLE auth_user_user_permissions (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED, permission_id integer NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED, UNIQUE(user_id,permission_id));
CREATE TABLE django_admin_log (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, action_time datetime NOT NULL, object_id text NULL, object_repr varchar(200) NOT NULL, action_flag smallint unsigned NOT NULL CHECK(action_flag>=0), change_message text NOT NULL, content_type_id integer NULL REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED, user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE django_session (session_key varchar(40) NOT NULL PRIMARY KEY, session_data text NOT NULL, expire_date datetime NOT NULL);
CREATE TABLE blog_post (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, title varchar(200) NOT NULL, content text NOT NULL, published_at datetime NOT NULL);
CREATE TABLE blog_comment (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, text text NOT NULL, published_at datetime NOT NULL, author_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED, post_id bigint NOT NULL REFERENCES blog_post(id) DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE blog_category (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(100) NOT NULL UNIQUE, description text NOT NULL);
CREATE TABLE blog_post_categories (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, post_id bigint NOT NULL REFERENCES blog_post(id) DEFERRABLE INITIALLY DEFERRED, category_id bigint NOT NULL REFERENCES blog_category(id) DEFERRABLE INITIALLY DEFERRED, UNIQUE(post_id,category_id));
CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission (content_type_id);
CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions (group_id);
CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions (permission_id);
CREATE INDEX auth_user_groups_user_id_6a12ed8b ON auth_user_groups (user_id);
CREATE INDEX auth_user_groups_group_id_97559544 ON auth_user_groups (group_id);
CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON auth_user_user_permissions (user_id);
CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON auth_user_user_permissions (permission_id);
CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log (content_type_id);
CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log (user_id);
CREATE INDEX django_session_expire_date_a5c62663 ON django_session (expire_date);
CREATE INDEX blog_comment_author_id_59c0c6e0 ON blog_comment (author_id);
CREATE INDEX blog_comment_post_id_580e96ef ON blog_comment (post_id);
CREATE INDEX blog_post_categories_post_id_9435e4de ON blog_post_categories (post_id);
CREATE INDEX blog_post_categories_category_id_6d43f4ff ON blog_post_categories (category_id);
"""
MIGRATIONS = {
    "contenttypes": ["0001_initial", "0002_remove_content_type_name"],
    "auth": ["0001_initial", "0002_alter_permission_name_max_length", "0003_alter_user_email_max_length", "0004_alter_user_username_opts", "0005_alter_user_last_login_null", "0006_require_contenttypes_0002", "0007_alter_validators_add_error_messages", "0008_alter_user_username_max_length", "0009_alter_user_last_name_max_length", "0010_alter_group_name_max_length", "0011_update_proxy_permissions", "0012_alter_user_first_name_max_length"],
    "admin": ["0001_initial", "0002_logentry_remove_auto_add", "0003_logentry_add_action_flag_choices"],
    "sessions": ["0001_initial"],
    "blog": ["0001_initial", "0002_comment", "0003_categories"],
}


def build():
    if DB.exists() and "--force" not in sys.argv:
        raise SystemExit(f"Banco ja existe: {DB}. Use --force para recriar.")
    if DB.exists():
        DB.unlink()
    contents = demo_data()
    admin_name = "admin_local"
    admin_password = secrets.token_urlsafe(22)
    con = sqlite3.connect(DB)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(SCHEMA)
        now = "2026-10-20 17:00:00.000000"
        for app, migrations in MIGRATIONS.items():
            for migration in migrations:
                con.execute("INSERT INTO django_migrations (app,name,applied) VALUES (?,?,?)", (app, migration, now))
        types = [("admin", "logentry"), ("auth", "permission"), ("auth", "group"), ("auth", "user"), ("contenttypes", "contenttype"), ("sessions", "session"), ("blog", "post"), ("blog", "comment"), ("blog", "category")]
        for app, model in types:
            cur = con.execute("INSERT INTO django_content_type (app_label,model) VALUES (?,?)", (app,model))
            name = model.replace("contenttype", "content type")
            for action in ["add", "change", "delete", "view"]:
                con.execute("INSERT INTO auth_permission (name,content_type_id,codename) VALUES (?,?,?)", (f"Can {action} {name}",cur.lastrowid, f"{action}_{model}"))
        for username, email in [("ana_demo", "ana@example.invalid"), ("bruno_demo", "bruno@example.invalid")]:
            con.execute("INSERT INTO auth_user (password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES (?,?,?,?,?,?,?,?,?,?)", ("!senha-nao-habilitada",None,0,username,"","",email,0,1,now))
        con.execute("INSERT INTO auth_user (password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES (?,?,?,?,?,?,?,?,?,?)", (hash_password(admin_password),None,1,admin_name,"","","",1,1,now))
        categories={}
        for name, description in contents.CATEGORIES:
            cur=con.execute("INSERT INTO blog_category (name, description) VALUES (?,?)",(name,description))
            categories[name]=cur.lastrowid
        posts={}
        for title,content,date,cat_names in contents.POSTS:
            cur=con.execute("INSERT INTO blog_post (title,content,published_at) VALUES (?,?,?)",(title,content,datetime_sql(date)))
            posts[title]=cur.lastrowid
            for name in cat_names:
                con.execute("INSERT INTO blog_post_categories (post_id,category_id) VALUES (?,?)",(cur.lastrowid,categories[name]))
        for title, username, text, date in contents.COMMENTS:
            user_id=con.execute("SELECT id FROM auth_user WHERE username=?",(username,)).fetchone()[0]
            con.execute("INSERT INTO blog_comment (text,published_at,author_id,post_id) VALUES (?,?,?,?)",(text,datetime_sql(date),user_id,posts[title]))
        con.commit()
        assert con.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        assert con.execute("SELECT count(*) FROM blog_post").fetchone()[0]==3
        assert con.execute("SELECT count(*) FROM blog_comment").fetchone()[0]==4
        assert con.execute("SELECT count(*) FROM blog_category").fetchone()[0]==3
        creds = ROOT.parent / "acesso_admin_local.txt"
        creds.write_text("ACESSO AO ADMINISTRADOR NO AMBIENTE LOCAL (nao publicar)\n\n" f"Login: {admin_name}\nSenha: {admin_password}\nURL: http://127.0.0.1:8000/admin/\n\n" "IMPORTANTE: a senha e somente para o banco SQLite local recebido.\n" "Ela nao se aplica ao PostgreSQL do Render. Nao publique este arquivo no GitHub.\n",encoding="utf-8")
        os.chmod(creds,0o600)
        print(f"Banco criado: {DB}. Banco com 3 posts, 3 categorias, 4 comentarios, 1 superusuario.")
        print(f"Credenciais locais em: {creds}")
    finally:
        con.close()


if __name__ == "__main__":
    build()
