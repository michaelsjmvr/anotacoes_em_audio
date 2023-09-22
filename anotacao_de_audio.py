# Importação de módulos necessários
import sys
import os
import wave
import threading
import pyaudio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog

# Definição da classe principal da aplicação
class AudioNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurações iniciais da janela principal
        self.setWindowTitle("Anotações de Áudio")
        self.setGeometry(100, 100, 400, 200)

        # Criação de um widget central
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout vertical para organizar os widgets
        self.layout = QVBoxLayout(self.central_widget)

        # Campo de edição para inserir o nome do arquivo
        self.file_name_edit = QLineEdit(self)
        self.layout.addWidget(self.file_name_edit)

        # Botão para selecionar o local de salvamento
        self.select_location_button = QPushButton("Selecionar Local", self)
        self.select_location_button.clicked.connect(self.select_location)
        self.layout.addWidget(self.select_location_button)

        # Botão para iniciar a gravação de áudio
        self.record_button = QPushButton("Gravar Áudio", self)
        self.record_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.record_button)

        # Botão para finalizar a gravação de áudio
        self.finish_button = QPushButton("Finalizar Gravação", self)
        self.finish_button.clicked.connect(self.finish_recording)
        self.finish_button.setEnabled(False)
        self.layout.addWidget(self.finish_button)

        # Inicialização de variáveis para controle da gravação
        self.output_file_path = ""
        self.recording = False
        self.audio_frames = []

        # Thread para gravar áudio em segundo plano
        self.audio_thread = None

    # Função para selecionar o local de salvamento
    def select_location(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        dialog = QFileDialog(self, "Selecione o Local para Salvar", "", "Arquivos de Áudio (*.wav);;Todos os Arquivos (*)", options=options)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.output_file_path = selected_files[0]
                # Adiciona ".wav" automaticamente se não estiver presente
                if not self.output_file_path.endswith(".wav"):
                    self.output_file_path += ".wav"
                self.file_name_edit.setText(self.output_file_path)

    # Função para iniciar a gravação de áudio
    def start_recording(self):
        if not self.recording:
            if not self.output_file_path:
                return

            self.recording = True
            self.audio_frames = []

            self.record_button.setText("Gravando...")
            self.finish_button.setEnabled(True)

            # Inicia uma thread para gravar áudio em segundo plano
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        else:
            self.finish_recording()

    # Função para finalizar a gravação de áudio
    def finish_recording(self):
        if self.recording:
            self.recording = False
            self.record_button.setText("Gravar Áudio")
            self.finish_button.setEnabled(False)

            if self.output_file_path and self.audio_frames:
                self.save_audio()

    # Função para gravar áudio em uma thread separada
    def record_audio(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)

        while self.recording:
            data = stream.read(1024)
            self.audio_frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

    # Função para salvar o áudio gravado em um arquivo WAV
    def save_audio(self):
        if self.output_file_path and self.audio_frames:
            with wave.open(self.output_file_path, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))

# Bloco de código para executar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioNotesApp()
    window.show()
    sys.exit(app.exec())
