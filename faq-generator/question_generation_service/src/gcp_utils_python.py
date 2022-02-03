import os
import sys
from configparser import ConfigParser, BasicInterpolation
import logging
from google.cloud import storage

from src.utils import get_named_logger


# Initiating logger
logger = get_named_logger(__name__)


def get_gcp_config():
    """
    Function to read GCP Config stored in Properties file
    Assumes gcp.properties exists and is in same dir.

    :return: config_variables
    :rtype: dict
    """

    logger.debug("Reading GCP config")

    config_file = "gcp.properties"
    config_file_path = os.path.join(os.path.dirname(__file__), config_file)

    lifecycle_env = os.getenv("lifecycle_env", "dev")
    if lifecycle_env not in ["dev", "stg", "prod"]:
        print(
            f"Undefined lifecycle environment: {lifecycle_env}."
            + "Environment variable 'lifecycle_env' must be set and must have a value of 'dev', 'stg' or 'prod' "
        )
        return None
    else:
        gcp_config = ConfigParser(interpolation=BasicInterpolation())
        if os.path.exists(config_file_path):
            gcp_config.read(config_file_path)
            config_variables = gcp_config[lifecycle_env]
            return config_variables
        else:
            print(f"Error while reading GCP config: {config_file_path}")
            return None


def save_data(file_path, file_name):
    """
    Save data to a GCS bucket

    :param file_path: Local path to the file
    :type file_path: sting
    :param file_name: Name of the file
    :type file_name: sting
    """

    logger.debug("Saving file to GCS")

    config_variables = get_gcp_config()
    print(str(type(config_variables)))
    client = storage.Client(project=config_variables.get("project_id"))
    bucket = client.get_bucket(config_variables.get("bucket"))

    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path)


def get_data(file_path, file_name):
    """
    Get data from a GCS bucket

    :param file_path: Local path to the file
    :type file_path: sting
    :param file_name: Name of the file
    :type file_name: sting
    """

    logger.debug("Getting file from GCS")

    config_variables = get_gcp_config()
    client = storage.Client(project=config_variables.get("project_id"))
    bucket = client.get_bucket(config_variables.get("bucket"))

    blob = bucket.blob(file_name)
    blob.download_to_filename(file_path)
