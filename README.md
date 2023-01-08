Activate the virtual environment venv
If using the Git Bash, type:

```sh
source ./Scripts/activate
```
Then, type:
```sh
python app.py # for development mode
# or
waitress-serve --port=5000 app:app # for production mode
```