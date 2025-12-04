import subprocess
import uuid
import os

def synthesize_with_piper(text: str, output_path: str = None):
    """
    Genera un audio WAV usando Piper TTS local.
    """
    try:
        # Crear nombre de archivo si no se pasa uno
        if output_path is None:
            output_path = f"tts_output_{uuid.uuid4().hex}.wav"5

        # Ruta a Piper y al modelo
        piper_path = ".\\app\\service\\piper\\piper.exe"
        model_path = ".\\app\\service\\piper\\es_ES-sharvard-low.onnx"

        # Ejecutar Piper
        process = subprocess.Popen(
            [
                piper_path,
                "--model", model_path,
                "--output_file", output_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Pasar texto al stdin del proceso
        process.communicate(text)

        if process.returncode != 0:
            raise Exception("Error en Piper TTS")

        return output_path

    except Exception as e:
        print(f"Piper TTS error: {e}")
        return None
