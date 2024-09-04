import os
import glob
import paramiko
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ssh_user = data.get('ssh_user')
ssh_password = data.get('ssh_password')
ssh_host = data.get('ssh_host')
ssh_port = data.get('ssh_port', 22)
backup_dir = data.get('backup_dir', 'backups/')  # Default backup directory
remote_backup_dir = data.get('remote_backup_dir', 'homeassistant-backup/')  # Default remote backup directory

def get_backup_file():
    os.chdir(backup_dir)  # Change directory to backup_dir
    backup_files = glob.glob('*')
    newest_file = max(backup_files, key=os.path.getmtime)
    logging.info(f"Newest backup file: {newest_file}")
    return newest_file

# Create a backup of Home Assistant
def create_backup():
    hass.services.call('backup', 'create')
    backup_file = get_backup_file()
    return backup_file
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
