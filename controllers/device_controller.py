class DeviceController:
    def __init__(self, db=None):
        self.db = db

    def get_all_devices(self):
        return []

    def activate_device(self, d_id, date):
        return True

    def block_device(self, d_id):
        return True

    def delete_device(self, d_id):
        return True
