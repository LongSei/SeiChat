import yaml
from typing import Type
from discord.ext import commands

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data