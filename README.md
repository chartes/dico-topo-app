
<h1>The <a target="_blank" href="https://dicotopo.cths.fr/">DicoTopo</a> application API<image height="45" align="right" src="https://github.com/user-attachments/assets/f65ff1c0-ac0f-410d-8fe8-1bc0d6a3f2fe"/></h1>

![Static Badge](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&label=PYTHON&color=blue)
![Static Badge](https://img.shields.io/badge/sqlite-3-blue?style=for-the-badge&logo=sqlite)

![Static Badge](https://img.shields.io/badge/Flask-3.1.0-blue?logo=flask)
![Static Badge](https://img.shields.io/badge/SQLAlchemy-1.4.18-blue?logo=Sqlalchemy)
![Static Badge](https://img.shields.io/badge/elasticsearch-8.12-blue?logo=elasticsearch)

## Description

This repository contains the API service code for [https://dicotopo.cths.fr](https://dicotopo.cths.fr).

## Prerequisite - Install Elasticsearch

### Install Elasticsearch _and_ its ICU plugin
  
:warning: Use an ES version compatible with [requirements.txt](./requirements.txt)  
:information_source: Below commands are run independently/outside virtual environments (`deactivate`)  
  - Elasticsearch: refer to your organisation instructions or [Elasticsearch guidelines](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html#elasticsearch-install-packages)  
  - [ICU plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html): check if ICU is installed with `uconv -V`, otherwise:  
    <pre><code><b><i>path/to/elasticsearch_folder</i></b>/bin/elasticsearch-plugin install analysis-icu</code></pre>

- With docker (security disabled)
    <pre><code>
      docker run --name <b><i>es-dico-topo</i></b> -d -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "xpack.security.http.ssl.enabled=false" elasticsearch:8.12.1
      docker exec <b><i>es-dico-topo</i></b> bash -c "bin/elasticsearch-plugin install analysis-icu"
      docker restart <b><i>es-dico-topo</i></b>
    </code></pre>

## Install

- Clone the GitHub repository in your projects' folder:
  ```bash
  cd path/to/projects_folder/
  git clone https://github.com/chartes/dico-topo-app.git
  ```

- Ensure you are running Python 3.12, for example with pyenv:
  ```bash
  pyenv shell 3.12
  ```

- Set up the virtual environment:
  <pre><code>
  cd <b><i>path/to/projects_folder</i></b>/dico-topo-app
  python -m venv <b><i>your_venv_name</i></b>
  source <b><i>your_venv_name</i></b>/bin/activate
  pip install -e .
  </code></pre>
  
- For servers requiring uWSGI to run Python apps (remote Nginx servers):
  - check if uWSGI is installed `pip list --local`
  - install it in your virtual *__your_venv_name__* if it's not: `pip install uwsgi`.  
  The WSGI application is located at `dico_topo.flask_app:flask_app`  
  *NB : this command may require wheel:*  
    - to check whether wheel is installed: `pip show wheel`  
    - to install it if required: `pip install wheel`

## Indexing

- Install Elasticsearch and create indices _if they are not available_:    

- Follow the ES installation & initial indexing instructions [above](#prerequisite-install-elasticsearch)  

> :warning: Below (re)indexing commands are run within the app virtual environment:  
> reactivate the virtual environment if needed (<code>source <b><i>your_venv_name</i></b>/bin/activate</code>)  
> 
> In below commands, options are indicated within brackets <em>(option)</em>. Remove them as required.
> 
> With ES security enabled, the <em>ES_PASSWORD</em> option is required in commands below.

### Initial indexing:

<pre><code>
(ES_PASSWORD=<b><i>ELASTIC_PASSWORD</i></b>) python dico_topo/manage.py (--config=<b><i>local/staging/prod/test</i></b>) db-reindex --host=http://localhost
</code></pre>

### Reindex (updating index configuration changes):
<pre><code>
(ES_PASSWORD=<b><i>ELASTIC_PASSWORD</i></b>) python dico_topo/manage.py (--config=<b><i>local/staging/prod/test</i></b>) db-reindex --indexes=<b><i>places/old-labels</i></b> --host=http://localhost --delete=1
</code></pre>

The above command updates the indexes according to the project ES [configuration files](./elasticsearch/).  

### Reindex (without index configuration changes):
<pre><code>
(ES_PASSWORD=<b><i>ELASTIC_PASSWORD</i></b>) python dico_topo/manage.py (--config=<b><i>local/staging/prod/test</i></b>) db-reindex --indexes=<b><i>places/old-labels</i></b> --host=http://localhost
</code></pre>

### Check created indexes:

- with ES security disabled:
<pre><code>
curl -X POST "http://localhost:9200/dicotopo__development__places/_refresh?pretty"
curl http://localhost:9200/_cat/indices?v
</code></pre>

- with ES security enabled: 
<pre><code>
curl -X POST "http://elastic:<b><i>ELASTIC_PASSWORD</i></b>@localhost:9200/dicotopo__<b><i>development/production</i></b>__places/_refresh?pretty"
curl http://elastic:<b><i>ELASTIC_PASSWORD</i></b>@localhost:9200/_cat/indices?v
</code></pre>

## Launch the app:
> :warning: Below commands are mainly for local launch.  
> For servers, apps may be started via processes management tools, refer to the servers documentation
  - Reactivate the virtual environment if needed (<code>source <b><i>your_venv_name</i></b>/bin/activate</code>)
  - Launch:  
  from the subfolder containing flask_app.py (`cd path/to/dico-topo-app`)
    <code>(ES_PASSWORD=<b><i>ELASTIC_PASSWORD</i></b>) python dico_topo/flask_app.py</code>
  - Then visit http://localhost:5003/dico-topo/api/1.0?capabilities to get infos about the API capabilities


## Launch the front-end:
- [Front-end's Readme](https://github.com/chartes/dico-topo-vue)

---
Additional details for offline commands:

```bash
python dico_topo/manage.py --help

Usage: dico_topo/manage.py [OPTIONS] COMMAND [ARGS]...

  Generates the client

Options:
  --config TEXT  --config=local/staging/prod/test to select appropriate .env
                 file to use, default= staging
  --help         Show this message and exit.

Commands:
  db-create    Creates a local database
  db-recreate  Recreates a local database.
  db-reindex   Rebuild the elasticsearch indexes from the current database
  db-validate
  id-register
```

