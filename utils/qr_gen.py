import qrcode
import os

class QRGenerator:
    @staticmethod
    def generate(data, filename):
        os.makedirs("images/barcodes", exist_ok=True)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        path = os.path.join("images/barcodes", filename)
        img.save(path)
        return path
