#!/usr/bin/env python3
import os
import sys
sys.path.append('..')
import yaml
import json
import shutil
import openai
import logging

from datetime import datetime
from pathlib import Path

import my_logger

logger = logging.getLogger('apiLogger')

from prompt_generation import generate_code_prompt

def get_summary(prompts: list[str], GPT_settings: dict[str, any]) -> dict[str, any]:
    """Call the OpenAI API with the prompts given.

    Args:
        prompts (list[str]): The prompts to send to the API.
        GPT_settings (dict[str, any]): The setting for the API.

    Returns:
        dict[str, any]: The response object.
    """
    API_KEY = os.getenv("OPENAI_API_KEY")
    logger.info(f'using apikey: {API_KEY}')
    openai.api_key = API_KEY

    response = openai.Completion.create(
        prompt=prompts,
        **GPT_settings
    )
    
    return response

def create_experiment_dir() -> str:
    """Create a experiment dir to save results.

    Returns:
        str: The path to the new dir.
    """
    root = '../../data/experiments'
    fname = datetime.now().strftime('%m-%d-%Y/%H_%M')
    dir_path = Path(root).joinpath(fname)
    dir_path.mkdir(parents=True, exist_ok=False)
    return dir_path

def save_json(dir_name: str, obj_to_save: any, fname: str, indent: int = 4) -> None:
    """Save a json object to a file

    Args:
        dir_name (str): The directory to save to.
        obj_to_save (any): The object to save.
        fname (str): The file name to save as.
        indent (int, optional): Indent of the json file. Defaults to 4.
    """
    dir_name = os.path.join(dir_name, fname)
    with open(dir_name, 'w') as f:
        json.dump(obj_to_save, f, indent=indent)

if __name__ == "__main__":
    generation_config = 'config.yaml'
    prompts, output_dirs = generate_code_prompt(config=generation_config)

    api_config = 'api_settings.yaml'
    with open(api_config) as file:
        GPT_settings = yaml.safe_load(file)

    if len(sys.argv) > 1:
        model = sys.argv[1]
        logger.info(f'Using fine tuned model: {model}')
        # Use our model instead of the pretrained ones
        GPT_settings.pop('engine')
        GPT_settings['model'] = model
        response = get_summary(prompts, GPT_settings)
    else:
        logger.info(f'Using pretrained model: {GPT_settings["engine"]}')
        response = get_summary(prompts, GPT_settings)

    dirname = create_experiment_dir()
    codes = {str(k): v for k, v in enumerate([val["text"] for val in response["choices"]])}

    logger.info(f'Created dir {dirname} for saving results.')
    save_json(dirname, output_dirs, 'test.json')    # List of problems
    save_json(dirname, response, 'response.json')   # Full GPT response
    save_json(dirname, codes, 'all_codes.json')   # Code dict 

    shutil.copy(api_config, dirname)
    shutil.copy(generation_config, dirname)
