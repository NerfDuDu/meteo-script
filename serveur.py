from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import requests

app = FastAPI()

# Configuration de sécurité indispensable pour que votre page HTML puisse parler à votre serveur Python (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/meteo")
def recuperer_meteo(ville: str):
    # C'est ici que vous allez coller votre logique actuelle :
    # 1. Géocodage de la variable 'ville'
    # 2. Récupération de la météo
    # 3. Appel à LM Studio 
    # 4. Enregistrement SQL (optionnel pour commencer)

    # Appel à l'API de géocodage pour trouver les coordonnées de la ville
    # 'count=1' permet de ne récupérer que le premier résultat le plus pertinent
    url_geocodage = f"https://geocoding-api.open-meteo.com/v1/search?name={ville}&count=1&language=fr&format=json"
    reponse_geo = requests.get(url_geocodage)
    data_geo = reponse_geo.json()

    # Gestion d'erreur simple : on vérifie si l'API a trouvé la ville
    if "results" not in data_geo or len(data_geo["results"]) == 0:
        print(f"Désolé, la ville '{ville}' n'a pas été trouvée.")
    else:
        ville_trouvée = data_geo["results"][0]
        pays = ville_trouvée["country"]
        latitude = ville_trouvée["latitude"]
        longitude = ville_trouvée["longitude"]

        print(f"Ville trouvée : {ville}, {pays} (Latitude: {latitude}, Longitude: {longitude})")


    # Récupération des données via l'API gratuite Open-Meteo pour la météo actuelle
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m"
    response = requests.get(url)
    data = response.json()

    # Extraction des variables
    heure = data["current"]["time"]
    temperature = data["current"]["temperature_2m"]
    humidite = data["current"]["relative_humidity_2m"]



    # Définir l'URL du serveur local de l'IA (LM Studio) pour le chat
    URL_API_LOCALE = "http://localhost:1234/v1/chat/completions" 

    # IA locale via LM Studio
    NOM_MODELE_LOCAL = "gemma4:e4b" 

    print("Détection du modèle actif dans LM Studio...")
    prompt = (
        f"Tu es un assistant météo amical. "
        f"Rédige une seule phrase de conseil courte et chaleureuse en français pour un utilisateur "
        f"sachant qu'il fait actuellement {temperature}°C avec {humidite}% d'humidité dans la ville de {ville}."
    )

    # On prépare le payload (les données au format JSON attendues par le serveur local)
    payload = {
        "model": NOM_MODELE_LOCAL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"Envoi de la demande à l'IA locale ({NOM_MODELE_LOCAL})...")

    try:
        # On fait une requête POST standard sur notre localhost
        response = requests.post(URL_API_LOCALE, json=payload, headers=headers)
        
        # On vérifie si la requête a réussi (HTTP 200)
        response.raise_for_status()
        
        # Extraction de la réponse (format standard OpenAI)
        resultat = response.json()
        reponse_ia = resultat["choices"][0]["message"]["content"]

        print("\nL'IA locale a répondu avec succès !")

    except KeyError:
        print("\n[ERREUR] LM Studio a rejeté la demande.")
        # On affiche la réponse brute pour lire le message d'erreur de LM Studio
        print("Message d'erreur de LM Studio :", response.text)

    # 2. Structuration avec Pandas
    # Pour créer un DataFrame Pandas, on organise nos données dans un dictionnaire de listes
    donnees_meteo = {
        "date_heure": [heure],
        "ville": [ville],
        "pays": [pays],
        "temperature_celsius": [temperature],
        "humidite_pourcent": [humidite],
        "reponse_ia" : [reponse_ia]
    }

    df = pd.DataFrame(donnees_meteo)

    # On affiche le tableau Pandas dans le terminal pour vérification
    print("--- Aperçu du tableau Pandas ---")
    print(df)
    print("--------------------------------")
    print("--- Réponse de l'IA Locale ---")
    print(reponse_ia)
    print("------------------------------")

    # 3. Stockage dans une base de données SQL (SQLite)
    # Connexion à la base de données (le fichier 'meteo.db' sera créé automatiquement dans votre dossier)
    conn = sqlite3.connect("meteo.db")

    # Pandas possède une fonction magique 'to_sql' pour envoyer un tableau directement en base de données.
    # 'if_exists="append"' indique que si la table existe déjà, on ajoute la nouvelle ligne à la suite.
    df.to_sql("historique_meteo", conn, if_exists="append", index=False)

    # On ferme la connexion proprement
    conn.close()

    print("Succès : Les données ont été ajoutées à la base de données locale (meteo.db) !")
    # Pour tester le serveur, on renvoie une fausse réponse temporaire
    return {
        "ville": ville,
        "pays": pays,
        "temperature": temperature,
        "humidite": humidite,
        "conseil": reponse_ia
    }

# Pour lancer le serveur: uvicorn serveur:app --reload
