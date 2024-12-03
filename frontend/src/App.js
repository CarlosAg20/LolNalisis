import React, { useState } from 'react';
import './App.css';

function App() {
  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [chartUrls, setChartUrls] = useState([]);
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
        const data = await response.json();
        setChartUrls(data.charts);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error desconocido');
      }
    } catch (err) {
      setError('Error al conectarse con el backend. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const splitUrls = (urls) => {
    const chunkSize = 2;
    return [
      urls.slice(0, chunkSize),
      urls.slice(chunkSize, chunkSize * 2),
      urls.slice(chunkSize * 2),
    ];
  };

  const [earlyUrls, midUrls, lateUrls] = splitUrls(chartUrls);

  return (
    <div className="summoner-tool">
      <header className="app-header">
        <h1>
          Herramienta de Invocador
        </h1>
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
          <span className="tooltip-trigger" aria-describedby="license-tooltip">
            ?
            <span id="license-tooltip" role="tooltip" className="tooltip">
              Resumen Licencia: Los derechos de autor de este activo pertenecen a Riot Games Inc. 
              Sin embargo: Riot Games permite el uso de su propiedad intelectual de League of Legends 
              siempre que se cumplan las condiciones establecidas en su política legal. 
              El activo sólo se utiliza para promocionar el producto. 
              Descargo de responsabilidad: La Herramienta de Analisis de League of Legends para jugadores no está avalada por Riot Games 
              ni refleja sus puntos de vista, opiniones o los de cualquier persona oficialmente involucrada 
              en la producción y/o gestión de League of Legends.
              Portada de Riot Games © Riot Games, Inc. Todos los derechos reservados. 
              Riot Games', 'League of Legends', 'Legends of Runaterra' y 'PvP.net' son marcas comerciales, 
              marcas de servicios o marcas registradas de Riot Games, Inc.
            </span>
          </span>
        </form>

        {error && <p className="error-message">Error: {error}</p>}

        {chartUrls.length > 0 && (
          <div className="results">
            <h2>Resultados de Análisis</h2>
            <div className="chart-section">
              <h3>Early Game</h3>
              {earlyUrls.map((url, index) => (
                <img
                  key={index}
                  src={url}
                  alt={`Early Game Gráfica ${index + 1}`}
                  className="chart-image"
                />
              ))}
            </div>
            <div className="chart-section">
              <h3>Mid Game</h3>
              {midUrls.map((url, index) => (
                <img
                  key={index}
                  src={url}
                  alt={`Mid Game Gráfica ${index + 1}`}
                  className="chart-image"
                />
              ))}
            </div>
            <div className="chart-section">
              <h3>Late Game</h3>
              {lateUrls.map((url, index) => (
                <img
                  key={index}
                  src={url}
                  alt={`Late Game Gráfica ${index + 1}`}
                  className="chart-image"
                />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

