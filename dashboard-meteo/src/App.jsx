import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

// Fonction utilitaire pour rendre la date plus lisible dans les textes
const formaterDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;

    const jourEnToutesLettres = date.toLocaleDateString('fr-FR', { weekday: 'long' });
    const jourDuMois = date.getDate();
    const mois = date.toLocaleDateString('fr-FR', { month: 'long' });
    const heures = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${jourEnToutesLettres} ${jourDuMois} ${mois} à ${heures}h${minutes}`;
  } catch (error) {
    return dateString;
  }
};

function App() {
  const [ville, setVille] = useState('');
  const [meteoActuelle, setMeteoActuelle] = useState(null);
  const [historique, setHistorique] = useState([]);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState('');

  // 1. Charger l'historique depuis la base SQL au démarrage du site
  const chargerHistorique = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/historique');
      const data = await response.json();
      setHistorique(data);
    } catch (err) {
      console.error("Erreur lors du chargement de l'historique:", err);
    }
  };

  useEffect(() => {
    chargerHistorique();
  }, []);

  // 2. Action lors du clic sur le bouton Consulter
  const gererRecherche = async (e) => {
    e.preventDefault();
    if (!ville) return;

    setChargement(true);
    setErreur('');
    setMeteoActuelle(null);

    try {
      const response = await fetch(`http://localhost:8000/api/meteo?ville=${ville}`);
      const data = await response.json();

      if (data.error) {
        setErreur(data.error);
      } else {
        setMeteoActuelle(data);
        chargerHistorique();
      }
    } catch (err) {
      setErreur("Impossible de contacter le serveur backend.");
    } finally {
      setChargement(false);
    }
  };

  // 3. Préparation des données pour le graphique afin d'avoir un axe X unique pour chaque recherche
  const donneesGraphique = historique.map((item, index) => {
    try {
      const date = new Date(item.date_heure);
      if (!isNaN(date.getTime())) {
        const jour = String(date.getDate()).padStart(2, '0');
        const mois = String(date.getMonth() + 1).padStart(2, '0');
        const heures = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        // Crée une étiquette unique : ex "Nantes (15/06 13h56)"
        return {
          ...item,
          labelAxeX: `${item.ville} (${jour}/${mois} ${heures}h${minutes})`
        };
      }
    } catch (e) {
      // En cas d'erreur de parsing, on utilise l'index pour éviter les doublons
    }
    return {
      ...item,
      labelAxeX: `${item.ville} (#${index + 1})`
    };
  });

  return (
    <div className="app-container">
      <h1 className="app-title">Dashboard Météo Intelligent (IA Locale)</h1>
      
      {/* Formulaire de recherche */}
      <form onSubmit={gererRecherche} className="search-form">
        <input 
          type="text" 
          placeholder="Entrez une ville (ex: Nantes)" 
          value={ville} 
          onChange={(e) => setVille(e.target.value)}
          className="search-input"
        />
        <button 
          type="submit" 
          disabled={chargement}
          className="search-button"
        >
          {chargement ? 'Consultation IA...' : 'Consulter'}
        </button>
      </form>

      {erreur && <p className="error-message">{erreur}</p>}

      {/* Affichage des résultats de la recherche actuelle */}
      {meteoActuelle && (
        <div className="weather-card">
          <h2>Météo actuelle à {meteoActuelle.ville} ({meteoActuelle.pays})</h2>
          <h3> Le {formaterDate(meteoActuelle.date_heure)}</h3>
          <p><strong>Température :</strong> {meteoActuelle.temperature}°C</p>
          <p><strong>Humidité :</strong> {meteoActuelle.humidite}%</p>
          <div className="ai-advice">
            <strong>Conseil de l'IA locale :</strong> <br/>
            "{meteoActuelle.conseil}"
          </div>
        </div>
      )}

      {/* Graphique de l'historique des données SQL */}
      {donneesGraphique.length > 0 && (
        <div className="chart-card">
          <h2>Historique de vos recherches (Données SQLite)</h2>
          <div className="chart-wrapper">
            <ResponsiveContainer>
              <LineChart data={donneesGraphique}> {/* Utilisation des données préparées */}
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="labelAxeX"/> {/* Utilisation de l'étiquette unique */}
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="temperature_celsius" name="Température (°C)" stroke="#e74c3c" activeDot={{ r: 7 }} />
                <Line type="monotone" dataKey="humidite_pourcent" name="Humidité (%)" stroke="#3498db" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Résumé des réponses IA*/}
      {historique.length > 0 && (
        <div className="summary-card">
          <h2>Résumé des conseils IA</h2>
          <ul className="summary-list">
            {historique.map((item, index) => (
              <li key={index} className="summary-item">
                <strong>{item.ville} ({item.pays}) le {formaterDate(item.date_heure)} avec {item.temperature_celsius} C° et {item.humidite_pourcent}% :<br /></strong>[IA] "{item.reponse_ia}"
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;