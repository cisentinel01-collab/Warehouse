import os
import subprocess
from datetime import datetime

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)

        self.config = {
            'dbname': 'wms_erp',
            'user': 'wms_user',
            'password': 'wms_pass',
            'host': 'localhost'
        }

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.sql"
        filepath = os.path.join(self.backup_dir, filename)

        env = os.environ.copy()
        env['PGPASSWORD'] = self.config['password']

        try:
            cmd = [
                'pg_dump',
                '-h', self.config['host'],
                '-U', self.config['user'],
                '-d', self.config['dbname'],
                '-f', filepath
            ]
            subprocess.run(cmd, env=env, check=True)
            return filepath
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def restore_backup(self, filepath):
        env = os.environ.copy()
        env['PGPASSWORD'] = self.config['password']

        try:
            cmd = [
                'psql',
                '-h', self.config['host'],
                '-U', self.config['user'],
                '-d', self.config['dbname'],
                '-f', filepath
            ]
            subprocess.run(cmd, env=env, check=True)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
