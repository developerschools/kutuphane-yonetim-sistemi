import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl
import sqlite3

class Veritabani:
    def __init__(self, dosya):
        self.dosya = dosya
        self.baglanti = sqlite3.connect(dosya)
        self.cursor = self.baglanti.cursor()

    def tablo_olustur(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kitaplar (
                                kitap_id TEXT PRIMARY KEY,
                                ad TEXT,
                                yazar TEXT
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS uyeler (
                                uye_id TEXT PRIMARY KEY,
                                ad TEXT,
                                soyad TEXT
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS odunc (
                                kitap_id TEXT,
                                uye_id TEXT,
                                FOREIGN KEY (kitap_id) REFERENCES kitaplar(kitap_id),
                                FOREIGN KEY (uye_id) REFERENCES uyeler(uye_id)
                                )''')
        self.baglanti.commit()

    def kitap_ekle(self, kitap_id, ad, yazar):
        self.cursor.execute("INSERT INTO kitaplar VALUES (?, ?, ?)", (kitap_id, ad, yazar))
        self.baglanti.commit()

    def uye_ekle(self, uye_id, ad, soyad):
        self.cursor.execute("INSERT INTO uyeler VALUES (?, ?, ?)", (uye_id, ad, soyad))
        self.baglanti.commit()

    def kitap_odunc_al(self, kitap_id, uye_id):
        self.cursor.execute("INSERT INTO odunc VALUES (?, ?)", (kitap_id, uye_id))
        self.baglanti.commit()

    def kitap_iade_et(self, kitap_id):
        self.cursor.execute("DELETE FROM odunc WHERE kitap_id=?", (kitap_id,))
        self.baglanti.commit()

class Kitap:
    def __init__(self, kitap_id, ad, yazar):
        self.kitap_id = kitap_id
        self.ad = ad
        self.yazar = yazar
        self.durum = "Mevcut"

    def durum_guncelle(self, durum):
        self.durum = durum

class Uye:
    def __init__(self, uye_id, ad, soyad):
        self.uye_id = uye_id
        self.ad = ad
        self.soyad = soyad

class Odunc:
    def __init__(self, kitap, uye):
        self.kitap = kitap
        self.uye = uye

class KutuphaneYonetimSistemi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kütüphane Yönetim Sistemi")
        self.veritabani = Veritabani("kutuphane.db")
        self.veritabani.tablo_olustur()
        self.kitaplar = []
        self.uyeler = []
        self.odunc_listesi = []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 800, 600)

        self.network_manager = QNetworkAccessManager()
        url = QUrl("https://trthaberstatic.cdn.wp.trt.com.tr/resimler/2058000/kutuphane-iha-2059040.jpg")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(self.on_image_download_finished)

        kitap_ekle_button = QPushButton("Kitap Ekle")
        kitap_ekle_button.clicked.connect(self.open_kitap_ekle_arayuz)

        uye_ekle_button = QPushButton("Üye Ekle")
        uye_ekle_button.clicked.connect(self.open_uye_ekle_arayuz)

        kitap_odunc_al_button = QPushButton("Kitap Ödünç Al")
        kitap_odunc_al_button.clicked.connect(self.open_kitap_odunc_al_arayuz)

        kitap_iade_et_button = QPushButton("Kitap İade Et")
        kitap_iade_et_button.clicked.connect(self.open_kitap_iade_et_arayuz)

        main_layout = QHBoxLayout()
        main_layout.addWidget(kitap_ekle_button)
        main_layout.addWidget(uye_ekle_button)
        main_layout.addWidget(kitap_odunc_al_button)
        main_layout.addWidget(kitap_iade_et_button)

        self.setLayout(main_layout)

    def on_image_download_finished(self):
        reply = self.sender()
        if reply.error():
            print("Image download failed:", reply.errorString())
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.background.setPixmap(pixmap)
            self.background.setScaledContents(True)

    def open_kitap_ekle_arayuz(self):
        self.kitap_ekle_arayuz = KitapEkleArayuz(self)
        self.kitap_ekle_arayuz.show()

    def open_uye_ekle_arayuz(self):
        self.uye_ekle_arayuz = UyeEkleArayuz(self)
        self.uye_ekle_arayuz.show()

    def open_kitap_odunc_al_arayuz(self):
        self.kitap_odunc_al_arayuz = KitapOduncAlArayuz(self)
        self.kitap_odunc_al_arayuz.show()

    def open_kitap_iade_et_arayuz(self):
        self.kitap_iade_et_arayuz = KitapIadeEtArayuz(self)
        self.kitap_iade_et_arayuz.show()

class KitapEkleArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Kitap Ekle")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.kitap_id_entry = QLineEdit()
        layout.addWidget(QLabel("Kitap ID:"))
        layout.addWidget(self.kitap_id_entry)

        self.kitap_ad_entry = QLineEdit()
        layout.addWidget(QLabel("Kitap Adı:"))
        layout.addWidget(self.kitap_ad_entry)

        self.kitap_yazar_entry = QLineEdit()
        layout.addWidget(QLabel("Yazar:"))
        layout.addWidget(self.kitap_yazar_entry)

        kitap_ekle_button = QPushButton("Kitap Ekle")
        kitap_ekle_button.clicked.connect(self.kitap_ekle)
        layout.addWidget(kitap_ekle_button)

        self.setLayout(layout)

    def kitap_ekle(self):
        kitap_id = self.kitap_id_entry.text()
        kitap_ad = self.kitap_ad_entry.text()
        kitap_yazar = self.kitap_yazar_entry.text()
        self.parent.veritabani.kitap_ekle(kitap_id, kitap_ad, kitap_yazar)
        QMessageBox.information(self, "Başarılı", f"{kitap_ad} kitabı kütüphaneye eklendi.")

class UyeEkleArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Üye Ekle")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.uye_id_entry = QLineEdit()
        layout.addWidget(QLabel("Üye ID:"))
        layout.addWidget(self.uye_id_entry)

        self.uye_ad_entry = QLineEdit()
        layout.addWidget(QLabel("Ad:"))
        layout.addWidget(self.uye_ad_entry)

        self.uye_soyad_entry = QLineEdit()
        layout.addWidget(QLabel("Soyad:"))
        layout.addWidget(self.uye_soyad_entry)

        uye_ekle_button = QPushButton("Üye Ekle")
        uye_ekle_button.clicked.connect(self.uye_ekle)
        layout.addWidget(uye_ekle_button)

        self.setLayout(layout)

    def uye_ekle(self):
        uye_id = self.uye_id_entry.text()
        uye_ad = self.uye_ad_entry.text()
        uye_soyad = self.uye_soyad_entry.text()
        self.parent.veritabani.uye_ekle(uye_id, uye_ad, uye_soyad)
        QMessageBox.information(self, "Başarılı", f"{uye_ad} üyesi kütüphaneye eklendi.")

class KitapOduncAlArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Kitap Ödünç Al")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.kitap_id_entry = QLineEdit()
        layout.addWidget(QLabel("Kitap ID:"))
        layout.addWidget(self.kitap_id_entry)

        self.uye_id_entry = QLineEdit()
        layout.addWidget(QLabel("Üye ID:"))
        layout.addWidget(self.uye_id_entry)

        odunc_al_button = QPushButton("Kitap Ödünç Al")
        odunc_al_button.clicked.connect(self.kitap_odunc_al)
        layout.addWidget(odunc_al_button)

        self.setLayout(layout)

    def kitap_odunc_al(self):
        kitap_id = self.kitap_id_entry.text()
        uye_id = self.uye_id_entry.text()

        self.parent.veritabani.kitap_odunc_al(kitap_id, uye_id)
        QMessageBox.information(self, "Başarılı", f"Kitap ödünç alındı.")

class KitapIadeEtArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Kitap İade Et")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.kitap_id_entry = QLineEdit()
        layout.addWidget(QLabel("Kitap ID:"))
        layout.addWidget(self.kitap_id_entry)

        iade_et_button = QPushButton("Kitap İade Et")
        iade_et_button.clicked.connect(self.kitap_iade_et)
        layout.addWidget(iade_et_button)

        self.setLayout(layout)

    def kitap_iade_et(self):
        kitap_id = self.kitap_id_entry.text()

        self.parent.veritabani.kitap_iade_et(kitap_id)
        QMessageBox.information(self, "Başarılı", f"Kitap iade edildi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kutuphane_sistemi = KutuphaneYonetimSistemi()
    kutuphane_sistemi.show()
    sys.exit(app.exec_())
