
# Personal Expense Tracker API
 This is a django based web api designed to be used to track a user's expenses

## Setting up the project

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/dunfred/expense-tracker-api.git
$ cd expense-tracker-api
```

Create a python virtual environment to install dependencies in and activate it:

```sh
$ virtualenv2 --no-site-packages expense-tracker-env
$ source expense-tracker-env/bin/activate
```

Then install the dependencies:

```sh
(expense-tracker-env)$ pip install -r requirements.txt
```
Note the `(expense-tracker-env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies, make sure you're in the directory containing `manage.py` then run:
```sh
(expense-tracker-env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`

### Author
- [Fred Dunyo](https://github.com/dunfred)
