## Setup migrations:

```bash
flask db init
flask db migrate
flask db upgrade
```

Create a new db
> createdb ``newdb``

Bootstrap flask migration to auto generate migrations subfolder in the project using 
> flask db init

Call Migrate in app.py 
> migrate = Migrate(app, newdb)

Set up migration on the new db using 
> flask db migrate

Upgrade the db with any new changes in app.py db models using 
> flask db upgrade

For every updates to db models in app.py run previous two commands


It’s always helpful to read the docs!
https://alembic.sqlalchemy.org/en/latest/
https://flask-migrate.readthedocs.io/en/latest/