import whisper
import openai
import os
import pandas as pd


def transcribe_meeting(file_path, FFMPEG_PATH):
    if os.getenv('DEBUG') != '0':
        return "mode DEBUG : transcribe_meeting()"

    # Configurer ffmpeg pour utiliser le chemin local
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]
    # print('os.environ["PATH"]', os.environ["PATH"])
    
    # Charger le modèle Whisper
    model = whisper.load_model("base")
    
    # Transcrire l'audio ou la vidéo
    result = model.transcribe(file_path)
    
    # Retourner la transcription en texte
    return result['text']


def summarize_meeting(transcription, pre_prompt):
    if os.getenv('DEBUG') != '0':
        return "mode DEBUG : summarize_meeting()"
    
    # Création du prompt avec la transcription
    prompt = pre_prompt + "\n\nTranscription:\n" + transcription
    
    # Appeler l'API de ChatGPT pour générer un CR
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            # SYSTEM - Option 1 : Contexte spécifique à la réunion (ChatGPT)
            # {"role": "system", "content": "Tu es un assistant spécialisé dans la création de comptes rendus de réunions. Résume de manière concise et claire les points clés de la transcription, en mettant en évidence les décisions prises, les tâches assignées et les prochaines étapes."},
            # SYSTEM - Option 2 : Contexte formel et axé sur la synthèse (ChatGPT)
            {"role": "system", "content": "Tu es un assistant professionnel chargé de rédiger des comptes rendus de réunions. Analyse la transcription et produis un résumé synthétique, en incluant les principaux sujets abordés et les conclusions."},
            # SYSTEM - Option 3 : Mise en forme spécifique (ChatGPT)
            # {"role": "system", "content": "Tu es un assistant qui rédige des comptes rendus de réunions. Résume la transcription en identifiant les principaux thèmes, les décisions prises, les actions à entreprendre, et présente le tout sous forme de liste à puces."},
            # USER
            {"role": "user", "content": prompt}
        ]
    )
    
    # Retourner le texte généré par ChatGPT
    return response['choices'][0]['message']['content']


def save_transcription_and_summary_to_file(transcription: str, transcription_output_file: str, summary: str, summary_output_file: str):
    # Enregistrement de la transcription
    with open(transcription_output_file, 'w', encoding='utf-8') as file:
        file.write(transcription)
    
    # Enregistrement du résumé avec une mise en forme Markdown
    with open(summary_output_file, 'w', encoding='utf-8') as file:
        file.write(summary)

def temps_moyen()->str:
    df = pd.read_csv("transcriptions_summaries.csv")
    transcription_time_exec = round(df['transcription'].mean(),2)
    summary_time_exec = round(df['summary'].mean(),2)
    total_time_exec = round(transcription_time_exec + summary_time_exec, 2)
    return f"{total_time_exec} min"