import sqlite3
import pandas as pd

# Connexion et lecture de la table SQL via Pandas
conn = sqlite3.connect("meteo.db")
df_historique = pd.read_sql_query("SELECT * FROM historique_meteo", conn)
conn.close()

print("--- Contenu actuel de la base SQL ---")
print(df_historique)
print("-------------------------------------\n")