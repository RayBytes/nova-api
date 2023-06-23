# Credit: @miss_articulate_python on Discord

import configparser
import os
import pathlib
import openai

# creating a config file, so we can store the api key and other settings
config_file = pathlib.Path(__file__).parent / 'config.ini'
config = configparser.ConfigParser()
config.read_dict({
    'openai': {
        'api_base': 'http://ENDPOINT',
        'api_key': '',
        'reset_ip_every_request': 'false'
    }
})

if config_file.exists():
    config.read(config_file)

with open(config_file, 'w', encoding='utf8') as configfile:
    config.write(configfile)

# the normal patch that you apply
openai.api_base = config['openai']['api_base']
openai.api_key = config['openai']['api_key']

# many modules lookup these environment variable, so we pre-emptively set them
os.environ['OPENAI_API_KEY'] = config['openai']['api_key']
os.environ['OPENAI_API_BASE'] = config['openai']['api_base']