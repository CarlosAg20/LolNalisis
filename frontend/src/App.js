import React, { useState } from 'react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
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
        setError(errorData.error || 'Usuario no encontrado');
      }
    } catch (err) {
      setError('Error al conectarse con el backend. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSummonerName('');
    setTagline('');
    setPlayerInfo(null);
    setData([]);
    setError(null);
  };

  const handleSavePDF = () => {
    const doc = new jsPDF();
    // eslint-disable-next-line
    const playerInfoTable = [
      [ 'Nombre', playerInfo.summoner_name ],
      [ 'Nivel', playerInfo.account_level ],
    ];
    // eslint-disable-next-line
    const rankedInfoTable = Object.entries(playerInfo.ranked_info).map(([queue, info]) => [
      queue.replace('_', ' '),
      `${info.tier} ${info.rank} - ${info.lp} LP`,
      `Victorias: ${info.wins} | Derrotas: ${info.losses}`,
    ]);

    doc.autoTable({ html: '#player-info-table' });
    doc.autoTable({ html: '#ranked-info-table' });

    doc.save('player_info.pdf');
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
          <div className="button-group">
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
            <button type="button" onClick={handleClear} className="clear-button">
              Limpiar
            </button>
          </div>
          <span className="tooltip-trigger" aria-describedby="license-tooltip">
            ?
            <span id="license-tooltip" role="tooltip" className="tooltip">
              Resumen Licencia: Los derechos de autor de este activo pertenecen a Riot Games Inc. 
              Sin embargo: Riot Games permite el uso de su propiedad intelectual de League of Legends 
              siempre que se cumplan las condiciones establecidas en su política legal. 
              Esta Wiki cree que el uso entra dentro de la ley de uso justo de EE.UU. porque:
              Los beneficios de Riot Games no están limitados en modo alguno. 
              El activo sólo se utiliza para promocionar el producto. 
              Descargo de responsabilidad: La Wiki de League of Legends de Fandom no está avalada por Riot Games 
              ni refleja sus puntos de vista, opiniones o los de cualquier persona oficialmente involucrada 
              en la producción y/o gestión de League of Legends.
              Portada de Riot Games © Riot Games, Inc. Todos los derechos reservados. 
              Riot Games', 'League of Legends', 'Legends of Runaterra' y 'PvP.net' son marcas comerciales, 
              marcas de servicios o marcas registradas de Riot Games, Inc.
            </span>
          </span>
        </form>

        {error && <p className="error-message">Error: {error}</p>}

        {playerInfo && (
          <div className="player-info">
            <h2>Información de Perfil</h2>
            <p><strong>Nivel:</strong> {playerInfo.account_level}</p>
            <h3>Clasificatorias:</h3>
            {Object.entries(playerInfo.ranked_info).map(([queue, info]) => (
              <div key={queue} className="ranked-section">
                <h4>{queue.replace('_', ' ')}</h4>
                <p><strong>{info.tier} {info.rank}</strong> - {info.lp} LP</p>
                <p>Victorias: {info.wins} | Derrotas: {info.losses}</p>
              </div>
            ))}
            <button type="button" onClick={handleSavePDF} className="save-pdf-button">
              Guardar PDF
            </button>
          </div>
        )}

        {data.length > 0 && (
          <div className="results">
            <h2>Resultados de Análisis</h2>
            {data.map((phase, index) => (
              <div key={index} className="phase-section">
                <h3>{phase.phase}</h3>
                {phase.charts.map((url, idx) => (
                  <img key={idx} src={url} alt={`Chart ${idx + 1}`} className="chart-image" />
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

