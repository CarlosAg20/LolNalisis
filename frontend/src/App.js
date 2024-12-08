import React, { useState } from 'react';
import './App.css';

function App() {
  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [playerInfo, setPlayerInfo] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ summonerName, tagline }),
      });

      if (response.ok) {
        const responseData = await response.json();
        setPlayerInfo(responseData.player_info || null);
        setData(responseData.data || []);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Error desconocido');
      }
    } catch (err) {
      setError('Error al conectarse con el backend. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="summoner-tool">
      <header className="app-header">
        <h1>Herramienta de Invocador</h1>
      </header>
      <main className="app-main">
        <form onSubmit={handleSubmit} className="search-form">
          <div className="form-group">
            <label htmlFor="summonerName">Nombre de invocador:</label>
            <input
              type="text"
              id="summonerName"
              value={summonerName}
              onChange={(e) => setSummonerName(e.target.value)}
              placeholder="Ingresa el nombre"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="tagline">Tagline:</label>
            <input
              type="text"
              id="tagline"
              value={tagline}
              onChange={(e) => setTagline(e.target.value)}
              placeholder="Ingresa el tagline"
              required
            />
          </div>
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {error && <p className="error-message">Error: {error}</p>}

        {playerInfo && (
          <div className="player-info">
            <h2>Información de Perfil</h2>
            <p><strong>Nombre:</strong> {playerInfo.summoner_name}</p>
            <p><strong>Nivel:</strong> {playerInfo.account_level}</p>
            <h3>Clasificatorias:</h3>
            {Object.entries(playerInfo.ranked_info).map(([queue, info]) => (
              <div key={queue} className="ranked-section">
                <h4>{queue.replace('_', ' ')}</h4>
                <p><strong>{info.tier} {info.rank}</strong> - {info.lp} LP</p>
                <p>Victorias: {info.wins} | Derrotas: {info.losses}</p>
              </div>
            ))}
          </div>
        )}

        {data.length > 0 && (
          <div className="results">
            <h2>Resultados de Análisis</h2>
            {data.map((phase, index) => (
              <div key={index} className="phase-section">
                <h3>{phase.phase}</h3>
                {phase.charts.map((url, idx) => (
                  <img key={idx} src={url} alt={`Chart ${idx}`} className="chart-image" />
                ))}
                <h4>Recomendaciones</h4>
                <ul>
                  {phase.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
