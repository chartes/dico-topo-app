1) Install the server dependencies
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2) Start the server in debug mode:
```
gunicorn flask_app:flask_app -c gunicorn.conf.py
```
3) Then visit http://127.0.0.1:5003/dico-topo

Eventually builds the frontend to the latest version:
```
cd app/dicotopo_client
npm install
npm run build
```
