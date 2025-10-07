# utils/parsing_utils.py

import json 
import os
from logging import Logger
import logging
import pandas as pd # type: ignore
from datetime import datetime
from typing import Dict, Any, Union, Tuple, List
from dotenv import load_dotenv
from google.cloud import secretmanager, storage
from google.api_core.exceptions import NotFound, PermissionDenied
# from yolo.yolo_utils import yolo_inference_filter
import subprocess 
from typing import Set
from google.cloud.exceptions import GoogleCloudError
from google.cloud import storage
from pathlib import Path

def configure_logging(id:str) -> Logger:
    """
    Configure logging for parser run.
    
    Args:
        id: Run job id for parser.
    """
    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Define log directory and file path
    log_dir = "./logging"
    os.makedirs(log_dir, exist_ok=True)  # Ensure the logging directory exists

    # Configure Logging
    LOG_FILE = f'''./logging/{id + "_" + timestamp + ".log"}''' # Change this to your preferred log file path
    logging.basicConfig(
        level=logging.DEBUG,  # Log all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode='a'),  # Append mode
            # logging.StreamHandler()
        ]
    )

    # get logger
    logger = logging.getLogger(__name__)

    # Only add handler if none exist
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE, mode='a')
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger



def read_text_file(file_path:str) -> str:
    """
    Reads a text file at a given filepath.

    Input:
        file_path (str): Filepath where the txt file is stored
    Output:
        output_string (str): String to be read.
    """

    with open(file_path,"r", encoding="utf-8") as f:
        output_string = f.read()

    return output_string


def retrieve_secret(secret_name: str, project_id: str) -> dict:
    """
    Retrieve a secret from GCP Secret Manager and parse it as a dictionary, loading it in as environment variables.

    Args:
        secret_name (str): The name of the secret.
        project_id (str): The GCP project ID.

    Returns:
        dict: A dictionary containing the secret's key-value pairs.
    """
    # Get logger
    logger = logging.getLogger(__name__)

    # Create a Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Fetch the secret
    response = client.access_secret_version(request={"name": secret_path})
    secret_json = response.payload.data.decode("UTF-8")  # Decode secret value

    # Parse the JSON secret
    secret_dict = json.loads(secret_json)

    # Set each secret as an environment variable
    for key, value in secret_dict.items():
        os.environ[key] = value  # Store in environment

    return secret_dict
    

def list_txt_filenames(folder_path: str, *, recursive: bool = False) -> List[str]:
    """
    Return a list of Txt filenames (not full paths) found in a folder.

    Parameters
    ----------
    folder_path : str
        Directory to search.
    recursive : bool, default False
        • False – look only at files directly inside `folder_path`.  
        • True  – walk sub-directories as well.

    Returns
    -------
    List[str]
        Filenames (e.g., ["file1.txt", "report_2024.txt"]).
        The list is sorted alphabetically.

    Raises
    ------
    FileNotFoundError
        If the folder does not exist.
    NotADirectoryError
        If `folder_path` is not a directory.
    """
    p = Path(folder_path)

    if not p.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    if not p.is_dir():
        raise NotADirectoryError(f"'{folder_path}' is not a directory.")

    pattern = "**/*.txt" if recursive else "*.txt"

    return sorted(f.name for f in p.glob(pattern) if f.is_file())

def load_config(file_path:str) -> dict:
    """
    Safely load a JSON config. 

    Args:
        file_path (str): A file path containing the config json file. 
        logger (Logger): Python logger to handle errors.
    Return
        config (dict): Dictionary containing the configuration information.
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        raise RuntimeError("Config file not found: './configs/config.json'")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON format in './configs/config.json'")
    return config


def validate_config(config:Dict[str,Any],logger:Logger):
    """
    Validates that all required properties in the config dictionary are filled out and have the correct data types.

    Args:
        config (Dict[str, Any]): The configuration dictionary.
        logger (logging.Logger): Logger instance for logging errors.

    Raises:
        ValueError: If any required field is missing, empty, or has an incorrect type.
    """

    # Define required keys with expected types
    required_keys_with_types = {
        "project_id": str,
        "secret_name": str,
        "max_chunk_size": int,
        "output_filepath": str,
        "input_type": str,
        "user_input_path": str,
        "dynamic_schema_prompt": str,
        "dynamic_schema_instructions": str,
        "system_prompt_path": str,
        "merge_system_prompt": str,
        "run_id": str,
        "max_llm_retries": int,
        "base_temperature": float,
        "llm-model-deployment-name": str
    }

    # Check for missing or empty values
    missing_keys = [key for key in required_keys_with_types if key not in config or config[key] in [None, "", []]]
    if missing_keys:
        logger.error(f"Config validation failed. Missing or empty fields: {missing_keys}")
        raise ValueError(f"Invalid config: Missing or empty fields: {missing_keys}")

    # Check for incorrect types
    type_mismatches = {
        key: expected_type for key, expected_type in required_keys_with_types.items()
        if key in config and not isinstance(config[key], expected_type)
    }
    if type_mismatches:
        logger.error(f"Config validation failed. Incorrect data types: {type_mismatches}")
        raise ValueError(f"Invalid config: Incorrect data types: {type_mismatches}")



def save_output_dataframe(output:dict, input_dict:dict) -> pd.DataFrame:
    """
    Save generated output dataframe from parsing output.

    Args: 
        output (dict): Output dictionary from parser.
        input_dict (dict): Input dictionary to parser
    Returns:
        df (pd.DataFrame): Dataframe of parser output.
    
    """
    # Check for output variable data type
    assert isinstance(output, dict), f"Expected a dictionary, but got {type(output).__name__}"

    # Define log directory and file path
    output_dir = "./outputs"
    os.makedirs(output_dir, exist_ok=True)  # Ensure the logging directory exists

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Conditionally handle chunking
    if "chunked_responses" not in output:
        # If output is a single dict, we can immediately cast to DataFrame
        df = pd.DataFrame([output])
        output_filepath = f'''{input_dict['output_filepath'].replace(".csv","_" + timestamp + ".csv")}'''
        df.to_csv(input_dict['output_filepath'], index=False)
    else:
        # This means we have multiple partial responses, flatten them
        partial_list = output["chunked_responses"]
        df = pd.DataFrame(partial_list)
        output_filepath = f'''{input_dict['output_filepath'].replace(".csv","_chunked_" + timestamp + ".csv")}'''

    if input_dict.get("timestamp_output_mode", True):
        # Export DF to CSV using output_filepath
        df.to_csv(output_filepath, index=False)
    
    # Export JSON to output filepath.
    with open(input_dict['output_filepath'].replace(".csv",".json"), 'w') as file:
        json.dump(output, file, indent=4)

    if input_dict.get('enable_cloud_logging',False):
        # Upload the CSV file to GCP bucket
        with open(input_dict['output_filepath'].replace(".csv",".json"), 'r') as file:
            output_list = json.load(file)

        # Error handling for empty output
        if output_list.get("chunked_responses") == []:
            pass
        elif output_list == []:
            pass
        else:
            upload_file_to_bucket(input_dict['output_filepath'].replace(".csv",".json"), 'data-extraction-services', f"{input_dict.get('gcp_upload_path')}/product_images/outputs/{input_dict.get('id')}_vision_parser_{input_dict.get('metadata_filter').get('url').replace('/','')}.json")


    return df

def initialize_environment_variables(secret_name: str, project_id: str, logger:Logger):
    """
    Retrieve GCP secret using google cloud secret manager, fallback to loading environment variables locally

    Args:
        secret_name (str): The name of the secret.
        project_id (str): The GCP project ID.
        logger (Logger): Logger instance from python's logging module

    Returns:
        dict: A dictionary containing the secret's key-value pairs.
    """
    try:
        # Attempt to retrieve secrets from GCP
        retrieve_secret(secret_name, project_id)
        logger.info(f"Successfully retrieved secrets from GCP Secret Manager: {secret_name}")

    except (secretmanager.exceptions.NotFound, secretmanager.exceptions.PermissionDenied) as gcp_error:
        logger.warning(f"Failed to retrieve secrets from GCP Secret Manager ({secret_name}): {gcp_error}")
        logger.info("Falling back to local .env file...")

        # Load from .env file as a fallback
        load_dotenv()

    except Exception as e:
        logger.error(f"Unexpected error while retrieving secrets: {e}", exc_info=True)
        raise RuntimeError("Failed to initialize environment variables.")


def safe_blob_download(
        blob: storage.Blob, 
        download_file_prefix: str,
        source_blob_name: str
    ) -> str:
    """
    Safely download a blob file from Google Cloud Storage.

    Args:
        blob: The blob object to download.
        download_file_prefix: The local directory to save the downloaded file.
        source_blob_name: The name of the source blob.  
    Returns:
        local_filename: The file path where the blob was downloaded.
    """
    try:
        # Download the file
        local_filename = os.path.join(download_file_prefix, os.path.basename(blob.name))
        blob.download_to_filename(local_filename)   

        # Handle and parse folder structure
        file_name = blob.name.split("/")[-1]
        file_suffix = file_name.split(".")[-1]
        metadata_path = download_file_prefix + "/" + file_name.replace(file_suffix,"json")

        # Download metadata of the file
        with open(metadata_path, 'w') as file:
            json.dump(blob.metadata, file, indent=4)

    except NotFound:
        logging.error(f"File not found in GCS: {source_blob_name}")
    except PermissionDenied:
        logging.error(f"Permission denied for file: {source_blob_name}")
    except Exception as e:
        logging.error(f"Unexpected error downloading {source_blob_name}: {e}")
    
    return local_filename


def upload_images_to_bucket(local_folder: str, bucket_name: str, destination_folder: str) -> None:
    """
    Upload all image files (e.g., .png, .jpg, .jpeg) from a local folder to a specified folder in a GCP bucket.

    Args:
        local_folder (str): Path to the local folder containing image files.
        bucket_name (str): Name of the GCP bucket to upload the images to.
        destination_folder (str): Destination folder path within the bucket where images will be uploaded.

    Raises:
        FileNotFoundError: If the provided local folder does not exist.
        GoogleCloudError: If an error occurs during the upload to GCP.
    """
    # Check if local folder exists
    if not os.path.exists(local_folder):
        raise FileNotFoundError(f"Local folder '{local_folder}' does not exist.")

    # Define image file extensions to look for
    image_extensions: Set[str] = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}

    # Initialize a GCP storage client and get the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Loop over files in the local folder
    for filename in os.listdir(local_folder):
        file_path = os.path.join(local_folder, filename)
        # Check if it's a file and has one of the desired extensions
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
            # Construct the destination blob name, ensuring proper folder structure
            blob_name = os.path.join(destination_folder, filename).replace("\\", "/")
            blob = bucket.blob(blob_name)
            try:
                blob.upload_from_filename(file_path)
                print(f"Uploaded '{file_path}' to 'gs://{bucket_name}/{blob_name}'")
            except GoogleCloudError as e:
                print(f"Failed to upload '{file_path}' to 'gs://{bucket_name}/{blob_name}': {e}")
                raise


def download_images_from_gcs(
    source_blob_name: str, 
    download_file_prefix: str = 'inputs/download_images', 
    bucket_name: str = 'data-extraction-services',
    image_suffix: Union[Tuple[str],str] = '.png',
    metadata_filter: Dict[str,str] = {},
    yolo_filter_mode: bool = False,
    enable_cloud_logging: bool = False,
    gcp_upload_path: str = ""
):
    """
    Downloads image(s) from a Google Cloud Storage bucket.

    Args:
        bucket_name: Name of the GCS bucket.
        source_blob_name: Path to the file inside the bucket.
        download_file_prefix: Local path to save the downloaded file.
        image_suffix: File extension of the image file(s) to download. 
                      When this variable is a Tuple (".png",".jpg") it captures multiple formats
                      When this variable is a string, it's just a single format ".png", etc.
        metadata_filter: Dictionary of metadata key-value pairs to filter the blobs by.
        enable_cloud_logging: Boolean flag to enable cloud logging.
        gcp_upload_path: Path to the GCP bucket for uploading logs.
    """
    # Initialize GCS client
    client = storage.Client()
    
    # Get the bucket
    bucket = client.bucket(bucket_name)
    
    try:
        # Solo-PNG mode: Download a single PNG file
        if source_blob_name.endswith(image_suffix):
            # Get the blob (file in bucket)
            blob = bucket.blob(source_blob_name)
            
            # Ensure the local directory exists
            os.makedirs(download_file_prefix, exist_ok=True)

            # Safe blob download of file
            local_filename = safe_blob_download(blob,download_file_prefix,source_blob_name)
            
            print(f"Downloaded {source_blob_name} from bucket {bucket_name} to {local_filename}")
        
        # Multi-PNG mode: Download all PNG files under a given prefix
        elif source_blob_name.endswith("/"):
            # List all blobs (files) that match the prefix
            blobs = bucket.list_blobs(prefix=source_blob_name)
            
            # Ensure the local directory exists
            os.makedirs(download_file_prefix, exist_ok=True)
            
            for blob in blobs:
                if blob.name.endswith(image_suffix):

                    # Metadata filter 
                    if metadata_filter != {}:
                        metadata = blob.metadata
                        if [metadata[key] for key in list(metadata_filter.keys())] != [metadata_filter[key] for key in list(metadata_filter.keys())]:
                            continue

                    # Safe blob download of file
                    local_filename = safe_blob_download(blob,download_file_prefix,source_blob_name)

                    # # YOLO filter mode conditional
                    # if yolo_filter_mode:
                    #     # Perform YOLO inference on the downloaded image
                    #     is_image_to_keep = yolo_inference_filter(local_filename)

                    #     if not(is_image_to_keep):
                    #         subprocess.run(["rm", "-f", f"{local_filename}"])
                    #         true_suffix = image_suffix.split(".")
                    #         subprocess.run(["rm", "-f", f"{local_filename.replace(true_suffix[-1],'json')}"])
                    #     else:
                    #         print(f"Downloaded {blob.name} from bucket {bucket_name} to {local_filename}")
                    #         if enable_cloud_logging:
                    #             upload_file_to_bucket(local_filename, 'data-extraction-services', f"{gcp_upload_path}/product_images/post-yolo-images/{blob.name.split('/')[-1]}")
                                
                    # else:
                    #     print(f"Downloaded {blob.name} from bucket {bucket_name} to {local_filename}")
    except FileNotFoundError as fnf_error:
        print(f"File not found error: {fnf_error}")
    except ValueError as val_error:
        print(f"Value error: {val_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_logger_filepath(logger: logging.Logger) -> str:
    """
    Retrieve the file path from the first FileHandler attached to the given logger.

    Args:
        logger (logging.Logger): The logger instance.

    Returns:
        str: The file path of the log file, or an empty string if no FileHandler is found.
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return ""




def upload_file_to_bucket(source: str, bucket_name: str, destination_blob_name: str, is_content: bool = False) -> None:
    """
    Upload an arbitrary file or string content to a specified Google Cloud Storage bucket.
    
    Args:
        source (str): If is_content is False, this is the local file path to be uploaded.
                      If is_content is True, this is the file content as a string.
        bucket_name (str): The name of the target GCS bucket.
        destination_blob_name (str): The destination path (including filename) in the GCS bucket.
        is_content (bool, optional): If True, treat 'source' as the file content to upload.
                                     If False, treat 'source' as a local file path. Defaults to False.
    
    Raises:
        FileNotFoundError: If is_content is False and the local file does not exist.
        GoogleCloudError: If an error occurs during the upload process.
    """
    logger = logging.getLogger(__name__)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    try:
        if is_content:
            # Upload the provided string as file content
            blob.upload_from_string(source)
            logger.info(f"Uploaded string content to 'gs://{bucket_name}/{destination_blob_name}'")
        else:
            # Check if the file exists
            if not os.path.exists(source):
                raise FileNotFoundError(f"File '{source}' does not exist.")
            blob.upload_from_filename(source)
            logger.info(f"Uploaded file '{source}' to 'gs://{bucket_name}/{destination_blob_name}'")
    except GoogleCloudError as e:
        logger.error(f"Error uploading to 'gs://{bucket_name}/{destination_blob_name}': {e}")
        raise


def add_timestamp_to_filepath(
    filepath: str,
    timestamp_format: str = "%Y%m%d_%H%M%S"
) -> str:
    """
    Append a timestamp to a filepath before its file extension.

    Args:
        filepath: Original file path (e.g., "output/report.xlsx").
        timestamp_format: Datetime format for the timestamp (default: "YYYYMMDD_HHMMSS").

    Returns:
        A new filepath string with the current timestamp inserted before the extension.
        E.g., "output/report_20250718_151234.xlsx".
    """
    path = Path(filepath)
    timestamp = datetime.now().strftime(timestamp_format)
    # Construct new filename
    new_name = f"{path.stem}_{timestamp}{path.suffix}"
    # Return full new path
    return str(path.with_name(new_name))


def normalize(name: str) -> str:
    """
    Normalize a vendor name by:
    - converting to lowercase
    - removing common legal suffixes (LLC, Inc, Corp, etc.)
    - stripping punctuation
    - collapsing multiple spaces
    
    Args:
        name: The original vendor name.
    
    Returns:
        A cleaned, normalized string used for fuzzy matching.
    """
    import re
    # lowercase
    name = name.lower()
    # remove legal suffixes
    name = re.sub(
        r'\b(llc|inc|incorporated|corp(oratio?n)?|co(mpany)?|ltd|dba)\b',
        '', name
    )
    # remove punctuation
    name = re.sub(r'[^a-z0-9 ]+', ' ', name)
    # collapse whitespace
    return re.sub(r'\s+', ' ', name).strip()