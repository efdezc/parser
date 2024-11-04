import sys
import shutil

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, \
    QFileDialog, QMessageBox
from PyQt6.QtGui import QScreen


class Ventana(QMainWindow):
    def realizar_operaciones(self):
        origen = Path(self.url_origen.text())
        destino = Path(self.url_destino.text())
        lista_errores_renombrar = []
        lista_errores_existe = []

        if self.convertir_archivo:
            renombrar_archivos(origen, destino, lista_errores_renombrar, lista_errores_existe)
        if self.convertir_carpeta:
            lista = sorted(origen.glob("*.ttf"))
            for i in range(len(lista)):
                lista[i] = str(lista[i]).replace("\\", "/")
                renombrar_archivos(Path(lista[i]), destino, lista_errores_renombrar, lista_errores_existe)

        errores = ""
        if len(lista_errores_renombrar) != 0:
            for i in lista_errores_renombrar:
                errores = errores + "\n" + str(i).split("\\")[-1]
            continuar = QMessageBox.question(self, "Parser!", f"Si no se elige un carpeta diferente, los siguientes archivos serán renombrados:\n\n{destino}\n{errores}\n\n¿Continuar?")
            if continuar == QMessageBox.StandardButton.Yes:
                for i in lista_errores_renombrar:
                    renombrar_archivos(Path(i), destino, lista_errores_renombrar, lista_errores_existe, True)
        errores = ""
        if len(lista_errores_existe) != 0:
            for i in lista_errores_existe:
                errores = errores + "\n" + str(i).replace("\\", "/")
            QMessageBox.warning(self, "Parser!", f"Los siguientes archivos ya existen:\n\n{destino}\n{errores}")

        QMessageBox.information(self, "Parser!", "Finalizado")

    def seleccionar_carpeta(self):
        url = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if url:
            self.url_origen.setText(url)
            if not self.carpeta_destino_seleccionada:
                self.url_destino.setText(url + "/ttf_files")
            self.convertir_carpeta = True
            self.convertir_archivo = False

    def seleccionar_archivo(self):
        url, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "(*.ttf)")
        if url:
            self.url_origen.setText(url)
            url_sin_archivo = str(Path(url).parent).replace("\\", "/")
            if not self.carpeta_destino_seleccionada:
                self.url_destino.setText(url_sin_archivo + "/ttf_files")
            self.convertir_carpeta = False
            self.convertir_archivo = True

    def carpeta_salida(self):
        url = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if url:
            self.url_destino.setText(url)
            self.carpeta_destino_seleccionada = True

    def center(self):
        qr = self.frameGeometry()
        cp = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        qr.moveCenter(cp)
        top_left = qr.topLeft()
        top_left.setY(top_left.y() - 50)
        self.move(top_left)

    def __init__(self):
        super().__init__()

        # Variables
        self.carpeta_destino_seleccionada = False
        self.convertir_archivo = False
        self.convertir_carpeta = False

        # Contenedor
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        # layout_principal
        layout_principal = QVBoxLayout()
        contenedor.setLayout(layout_principal)

        # layout_seleccion
        self.url_origen = QLineEdit()
        self.url_origen.setDisabled(True)
        self.url_origen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_origen.setPlaceholderText("Selecciona un archivo o una carpeta con archivos (.ttf)")
        layout_principal.addWidget(self.url_origen)

        # layout_botones
        layout_botones = QHBoxLayout()
        self.boton_seleccionar_archivo = QPushButton("Seleccionar archivo")
        self.boton_seleccionar_archivo.clicked.connect(self.seleccionar_archivo)
        layout_botones.addWidget(self.boton_seleccionar_archivo)
        self.boton_seleccionar_carpeta = QPushButton("Seleccionar carpeta")
        self.boton_seleccionar_carpeta.clicked.connect(self.seleccionar_carpeta)
        layout_botones.addWidget(self.boton_seleccionar_carpeta)
        layout_principal.addLayout(layout_botones)

        # layout_import
        layout_import = QHBoxLayout()
        self.boton_carpeta_import = QPushButton("Guardar en..")
        self.boton_carpeta_import.setMinimumSize(100, 0)
        self.boton_carpeta_import.clicked.connect(self.carpeta_salida)
        layout_import.addWidget(self.boton_carpeta_import)
        self.url_destino = QLineEdit()
        self.url_destino.setDisabled(True)
        self.url_destino.setPlaceholderText("Si no se selecciona se creará la carpeta ttf_files")
        self.url_destino.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_import.addWidget(self.url_destino)
        layout_principal.addLayout(layout_import)

        layout_principal.addSpacing(5)

        # layout_aceptar
        self.boton_aceptar = QPushButton("Cambiar títulos")
        self.boton_aceptar.setStyleSheet(leer_css())
        self.boton_aceptar.clicked.connect(self.realizar_operaciones)
        layout_principal.addWidget(self.boton_aceptar)

        # Ajustes
        self.adjustSize()
        self.setFixedHeight(self.height())
        self.resize(550, 0)
        self.center()
        self.setWindowTitle("Parser!")
        self.show()


def renombrar_archivos(origen: Path, destino: Path, lista_errores_renombrar: list, lista_errores_existe: list, renombrar: bool = False):
    if not destino.exists():
        crear_carpeta(destino)

    if origen.parent == destino:
        if not renombrar:
            lista_errores_renombrar.append(origen)
            return
    else:
        copiar_archivo(origen, destino)

    cambiar_nombre(origen, destino, lista_errores_existe)


def crear_carpeta(destino: Path):
    try:
        Path.mkdir(destino)
    except Exception as e:
        print(str(e))


def copiar_archivo(origen: Path, destino: Path):
    try:
        shutil.copy(origen, destino)
    except Exception as e:
        print(str(e))


def cambiar_nombre(origen: Path, destino: Path, lista_errores_existe: list):
    nuevo_origen = Path(f"{destino}/{origen.name}")
    nuevo_nombre = origen.name.lower().replace("-","_")
    nuevo_destino = Path(f"{destino}/{nuevo_nombre}")
    try:
        if nuevo_destino.exists():
            lista_errores_existe.append(nuevo_nombre)
            if nuevo_origen == nuevo_destino:
                return
            else:
                Path.unlink(nuevo_origen)
                return
        else:
            Path.rename(nuevo_origen, nuevo_destino)
    except Exception as e:
        print(str(e))


def leer_css():
    with open("estilo_boton.css", "r") as css:
        return css.read()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    sys.exit(app.exec())
