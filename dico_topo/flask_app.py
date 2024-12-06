import os, argparse
from dico_topo.app import create_app


POSSIBLE_ENV_VALUES = [ "local", "staging", "prod", "test" ]


#################################################################
# Selecting the .env file to use for deployment (default = staging) #
#################################################################


# Creating a dictionary of flask_app.py options (--config=staging) and their matching environment variables files aliases (staging)
# Creating a flask_app.py --help listing these options
parser = argparse.ArgumentParser(
    description='Flask app for dico-topo'
)
parser.add_argument('--config', type=str, choices=POSSIBLE_ENV_VALUES ,default='staging', help="/".join(POSSIBLE_ENV_VALUES) + ' to select the appropriate .env file to use, default=staging', metavar='')
args = parser.parse_args()
# Checking on the .env to be selected for deployment
# For server deployments, the .env name can be provided from the server configuration
server_env_config_env_var = os.environ.get('SERVER_ENV_CONFIG')
if server_env_config_env_var:
    print("Server provided an .env file : ", server_env_config_env_var)
    env = server_env_config_env_var
# Otherwise, check if .env file to use is provided in command line (with '--config=' option)
else:
    env = args.config
print("selected_env_file : ", env)

###############################################
# Launching app with the selected environment #
###############################################

flask_app = create_app(config_name=env)

if __name__ == "__main__":
    flask_app.run(debug=True, port=5003, host='localhost')
