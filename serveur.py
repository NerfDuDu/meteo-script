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
    # 1. Appel à l'API de géocodage
    url_geocodage = f"https://geocoding-api.open-meteo.com/v1/search?name={ville}&count=1&language=fr&format=json"
    reponse_geo = requests.get(url_geocodage)
    data_geo = reponse_geo.json()

    # CORRECTIF : Gestion d'erreur propre si la ville n'est pas trouvée
    if "results" not in data_geo or len(data_geo["results"]) == 0:
        return {"error": f"Désolé, la ville '{ville}' n'a pas été trouvée par l'API de géocodage."}

    # Si la ville est trouvée, on continue l'exécution
    ville_trouvee_data = data_geo["results"][0]
    ville_officielle = ville_trouvee_data["name"]
    pays = ville_trouvee_data.get("country", "Inconnu")
    latitude = ville_trouvee_data["latitude"]
    longitude = ville_trouvee_data["longitude"]

    print(f"[OK] Ville trouvée : {ville_officielle}, {pays} (Lat: {latitude}, Lon: {longitude})")

    # 2. Récupération des données météo
    url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m"
    response_meteo = requests.get(url_meteo)
    data_meteo = response_meteo.json()

    # Extraction des variables
    heure = data_meteo["current"]["time"]
    temperature = data_meteo["current"]["temperature_2m"]
    humidite = data_meteo["current"]["relative_humidity_2m"]

    # 3. AUTO-DÉTECTION DU MODÈLE ACTIF DANS LM STUDIO
    URL_BASE_LM_STUDIO = "http://localhost:1234/v1"
    
    try:
        # On demande à LM Studio quel modèle est chargé
        reponse_models = requests.get(f"{URL_BASE_LM_STUDIO}/models")
        reponse_models.raise_for_status()
        models_data = reponse_models.json()

        if not models_data.get("data"):
            return {"error": "LM Studio est démarré mais aucun modèle n'est chargé en mémoire vive."}
            
        nom_modele_charge = models_data["data"][0]["id"]
        print(f"[IA] Modèle détecté automatiquement : {nom_modele_charge}")
        
    except Exception as e:
        return {"error": f"Impossible de joindre le serveur local LM Studio sur le port 1234. Est-il bien démarré ? Détail : {e}"}

    # 4. APPEL À L'IA LOCALE (LM Studio)
    prompt = (
        f"Tu es un assistant météo amical. "
        f"Rédige une seule phrase de conseil courte et chaleureuse en français pour les habitants de {ville_officielle} "
        f"sachant qu'il y fait actuellement {temperature}°C avec un taux d'humidité de {humidite}%."
    )

    # On prépare le payload (les données au format JSON attendues par le serveur local)
    payload = {
        "model": nom_modele_charge,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response_ia_call = requests.post(f"{URL_BASE_LM_STUDIO}/chat/completions", json=payload, headers=headers)
        response_ia_call.raise_for_status()
        resultat_ia = response_ia_call.json()
        reponse_ia = resultat_ia["choices"][0]["message"]["content"]
        print("[IA] Réponse générée avec succès !")
    except Exception as e:
        print(f"[ERREUR IA] Échec : {e}")
        reponse_ia = "Aucun conseil d'IA disponible en raison d'une erreur de traitement."

    # 5. Structuration avec Pandas et Enregistrement SQLite
    donnees_meteo = {
        "date_heure": [heure],
        "ville": [ville_officielle],
        "pays": [pays],
        "temperature_celsius": [temperature],
        "humidite_pourcent": [humidite],
        "reponse_ia": [reponse_ia]
    }

    df = pd.DataFrame(donnees_meteo)

    try:
        conn = sqlite3.connect("meteo.db")
        # On écrit dans la table
        df.to_sql("historique_meteo", conn, if_exists="append", index=False)
        conn.close()
        print("[SQL] Données ajoutées avec succès dans la base 'meteo.db' !")
    except Exception as e:
        print(f"[ERREUR SQL] Impossible d'écrire en base de données : {e}")

    # 6. On renvoie la vraie réponse finale à notre page HTML !
    return {
        "ville": ville_officielle,
        "pays": pays,
        "temperature": temperature,
        "humidite": humidite,
        "conseil": reponse_ia
    }

# Pour lancer le serveur: uvicorn serveur:app --reload
