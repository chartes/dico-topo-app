1) Install the server dependencies
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2) Start the server in debug mode:
```
python flask_app.py
```
3) Then visit http://127.0.0.1:5003/dico-topo/api/1.0?capabilities to get infos about the API capabilities


more info about the configuration of ES:  https://jolicode.com/blog/construire-un-bon-analyzer-francais-pour-elasticsearch


How to reindex all indexable data, referencing a localhost api:
```
python manage.py db-reindex --host=http://localhost --delete=1  
```
