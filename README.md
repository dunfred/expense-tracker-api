
# Personal Expense Tracker API
[![codecov](https://codecov.io/gh/dunfred/expense-tracker-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/dunfred/expense-tracker-api)

This is a web api designed to be used to track a user's income and expenses.

For this project the following were used;
```
- python-3.9.16 (https://www.python.org/downloads/release/python-3916/)
- virtualenv-20.21.0
```
## Setting up the project

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/dunfred/expense-tracker-api.git
$ cd expense-tracker-api
```

Create a python virtual environment to install dependencies in and activate it:

```sh
$ virtualenv --python=python3.9  expense-tracker-env

# On Linux or macOS
$ source expense-tracker-env/bin/activate

# On Windows
$ expense-tracker-env\Scripts\activate
```

Make sure you create a **.env** file in the root directory of the project with the following variables (same directory **manage.py** file is located)

```env
SECRET_KEY=your_secret
DEBUG=1
CORS_ORIGIN_WHITELIST=http://localhost:8000
```

Then install the dependencies:

```sh
(expense-tracker-env)$ pip install -r requirements.txt
```
Note the `(expense-tracker-env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

Once `pip` has finished downloading the dependencies, make sure you're in the directory containing `manage.py` then run:
```sh
# To create a new sqlite3 db file with all migrations
(expense-tracker-env)$ python manage.py migrate

# To create your superuser account
(expense-tracker-env)$ python manage.py createsuperuser

# And finally, start project server
(expense-tracker-env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`

### Author
- [Fred Dunyo](https://github.com/dunfred)
