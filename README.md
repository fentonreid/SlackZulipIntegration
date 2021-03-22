# SlackZulipIntegration

## Prerequisites

* Git 
* Python 3.7.7+
* Pip 


## Git Clone

Clone from this repo using the following command.

```text
git clone https://github.com/fentonreid/SlackZulipIntegration.git
```

## Installing Python Dependencies

From the root directory of this project "slackZulipIntegration/" run the following command in console. 

```text
pip install -r requirements.txt
```

## Start the Integration Setup Website with default port

```bash
cd flaskFiles/

python flask_app.py
```

## Start the Integration Setup Website with a specific port
```bash
cd flaskFiles/

python flask_app.py PORT
```

To load the website simply navigate to http://localhost:PORT/


## Running Tests

### Altering the .env file

To run tests the .env file found at "tests/.env" needs to be modified. 

This .env is 5 lines long and mimics the 5 integration details required for the integration to begin. 


### Run flaskSite, integration and markdown tests

To run these files simply navigate to the "tests/runAllTests/" directory, and open a new console in this directory. 

The following commands will run three of four test files.

```bash
python runFlaskSite.py
python runIntegration.py
python runMarkdown.py
```

### Run the Jasmine tests

The Jasmine tests are run in a different way. Similar to above we start by opening a console in the "tests/runAllTests/" directory.

```bash
python runJavascript.py
```

This will run a Jasmine server on port 5000 that can be accessed through the following URL, http://localhost:5000/?random=false. 


## Maintenance

### Updating the Emoji List 

To update the emoji list run the "/integration/markdown/emojis/updateEmojiList.py" file through a console using the following commands. 

```bash
cd integration/markdown/emojis/
python updateEmojiList.py
```

### Altering the Database URI

Flask-SQLAlchemy is used in this project and the ORM is determined by the config option found in "flaskFiles/__init__.py. The following code found on line 22 of the __init__.py file is currently used to map to a Sqlite database termed userDetails.db.

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userDetails.db'
```

Using the documentation found [here](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format) the relevant database engine can be altered.

