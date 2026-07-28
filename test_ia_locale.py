import requests


# Définir l'URL du serveur local 
URL_API_LOCALE = "http://localhost:1234/v1/chat/completions" 


# Écrivez le nom EXACT du modèle que vous avez téléchargé en local
NOM_MODELE_LOCAL = "gemma4:e4b" 

# Données de test
temperature = 12.5
humidite = 85
ville = "Nantes"

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

    print("\n--- Réponse de l'IA Locale ---")
    print(reponse_ia)
    print("------------------------------")

except KeyError:
    print("\n[ERREUR] LM Studio a rejeté la demande.")
    # On affiche la réponse brute pour lire le message d'erreur de LM Studio
    print("Message d'erreur de LM Studio :", response.text)