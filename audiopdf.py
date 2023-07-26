import os
import speech_recognition as sr
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import subprocess

def convert_to_wav(audio_file):
    base_name, ext = os.path.splitext(audio_file)
    output_file = base_name + ".wav"
    
    # Use o ffmpeg para converter para WAV
    subprocess.run(["ffmpeg", "-i", audio_file, output_file], capture_output=True, text=True)
    
    return output_file

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    
    try:
        transcript = recognizer.recognize_google(audio, language="pt-BR") # Google Web Speech API
        return transcript
    except sr.UnknownValueError:
        print("Não foi possível reconhecer o áudio.")
        return None
    except sr.RequestError as e:
        print(f"Não foi possível acessar o serviço de reconhecimento de fala; {e}")
        return None

def create_pdf(pdf_path, text):
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Quebra o texto em parágrafos e adiciona-os ao PDF
    for paragraph in text.split('\n'):
        p = Paragraph(paragraph, styles['Normal'])
        story.append(p)
    
    doc.build(story)

if __name__ == "__main__":
    audio_formats = [".mp3", ".mkv", ".wav", ".ogg"]
    
    audio_folder = input("Digite o caminho da pasta que contém o arquivo de áudio: ")
    audio_files = [f for f in os.listdir(audio_folder) if os.path.isfile(os.path.join(audio_folder, f)) and f.lower().endswith(tuple(audio_formats))]
    
    if not audio_files:
        print("Nenhum arquivo de áudio válido encontrado na pasta.")
    else:
        for audio_file in audio_files:
            print(f"Transcrevendo {audio_file}...")
            
            # Converta o arquivo de áudio para WAV
            wav_file = convert_to_wav(os.path.join(audio_folder, audio_file))
            if not wav_file:
                print("Falha ao converter o arquivo para WAV.\n")
                continue
            
            # Transcreva o arquivo WAV
            transcript = transcribe_audio(wav_file)
            os.remove(wav_file)  # Remova o arquivo WAV após a transcrição
            
            if transcript:
                pdf_filename = os.path.splitext(audio_file)[0] + ".pdf"
                pdf_path = os.path.join(os.path.expanduser("~"), "Downloads", pdf_filename)
                
                # Criar o arquivo PDF com o texto transcrito
                create_pdf(pdf_path, transcript)
                
                print(f"Transcrição salva em {pdf_path}\n")
            else:
                print("Falha na transcrição.\n")
