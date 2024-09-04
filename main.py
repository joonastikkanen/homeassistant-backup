import os
import glob
import paramiko
import yaml
import requests
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# LOAD CONFIG FILE
def load_config():
    with open('./scripts/homeassistant-backup/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

# Set variables from config file
config = load_config()
ssh_user = config['ssh_user']
ssh_password = config['ssh_password']
ssh_host = config['ssh_host']
ssh_port = config['ssh_port']
homeassistant_url = config['homeassistant_url']
homeassistant_token = config['homeassistant_token']
backup_dir = config.get('backup_dir', 'backups/')  # Default backup directory
remote_backup_dir = config.get('remote_backup_dir', 'homeassistant-backup/')  # Default remote backup directory

def get_backup_file():
    os.chdir(backup_dir)  # Change directory to backup_dir
    backup_files = glob.glob('*')
    newest_file = max(backup_files, key=os.path.getmtime)
    logging.info(f"Newest backup file: {newest_file}")
    return newest_file

# Create a backup of Home Assistant
def create_backup():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % homeassistant_token
    }
    data = {}
    response = requests.post(f"%s/api/services/backup/create" % homeassistant_url, headers=headers, json=data)
    if response.status_code == 200:
        logging.info("Backup created successfully.")
        backup_file = get_backup_file()
        return backup_file
    else:
        logging.error("Failed to create backup.")
        logging.error(f"Response status code: {response.status_code}")
        return None
# Upload the backup file to the server
def upload_backup(backup_file):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
    
    sftp = ssh.open_sftp()
    
    # Create a new folder with month and year
    now = datetime.datetime.now()
    folder_name = now.strftime("%Y-%m")
    remote_folder_path = os.path.join(remote_backup_dir, folder_name)
    sftp.mkdir(remote_folder_path)
    
    local_path = os.path.join(backup_file)
    remote_path = os.path.join(remote_folder_path, os.path.basename(backup_file))
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    logging.info("Backup uploaded successfully.")

# Main function
def main():
    try:
        backup_file = create_backup()
        upload_backup(backup_file)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
