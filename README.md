Install the server dependencies
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Starting the server in debug mode:
```
gunicorn flask_app:flask_app -c gunicorn.conf.py
```
Building the front end:

```
cd app/client
npm install
npm run build
```
