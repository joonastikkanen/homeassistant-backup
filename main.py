import os
import subprocess
import paramiko
import yaml
import requests

# LOAD CONFIG FILE
def load_config():
    with open('./config.yaml', 'r') as file:
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
backup_dir = config.get('backup_dir', '/backup')  # Default backup directory
remote_backup_dir = config.get('remote_backup_dir', '/remote/backup/path')  # Default remote backup directory
# Create a backup of Home Assistant
def create_backup():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % homeassistant_token
    }
    data = {}
    response = requests.post(f"http://%s/api/services/backup/create" % homeassistant_url, headers=headers, json=data)
    if response.status_code == 200:
        print("Backup created successfully.")
        return True
    else:
        print("Failed to create backup.")
        return None

def get_backup_file():
    backup_files = os.listdir(backup_dir)
    newest_file = max(backup_files, key=os.path.getctime)
    print(f"Newest backup file: {newest_file}")
    return newest_file

# Upload the backup file to the server
def upload_backup(backup_file):
    backup_file = get_backup_file()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
    
    sftp = ssh.open_sftp()
    local_path = os.path.join(backup_dir, backup_file)
    remote_path = os.path.join(remote_backup_dir, backup_file)
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print("Backup uploaded successfully.")

# Main function
def main():
    try:
        backup_file = create_backup()
        upload_backup(backup_file)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    
api/services/backup/create