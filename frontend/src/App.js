import React, { useState } from "react";

function SummonerTool() {
  const [summonerName, setSummonerName] = useState(""); 
  const [tagline, setTagline] = useState(""); 
  const [chartUrls, setChartUrls] = useState([]); 
  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(null); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); 
    setError(null); 

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ summonerName, tagline }),
      });

      if (response.ok) {
        const data = await response.json();
        setChartUrls(data.charts); 
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Error desconocido");
      }
    } catch (err) {
      setError("Error al conectarse con el backend. Intenta nuevamente.");
    } finally {
      setLoading(false); 
    }
  };

  const splitUrls = (urls) => {
    const chunkSize = 2; 
    return [urls.slice(0, chunkSize), urls.slice(chunkSize, chunkSize * 2), urls.slice(chunkSize * 2)];
  };

  const [earlyUrls, midUrls, lateUrls] = splitUrls(chartUrls);

  return (
    <div>
      <h1>Herramienta de Invocador</h1>
      <form onSubmit={handleSubmit}>
        <div>
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
        <div>
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
        <button type="submit" disabled={loading}>
          {loading ? "Buscando..." : "Buscar"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {chartUrls.length > 0 && (
        <div>
          <h2>Resultados de Análisis</h2>
          <h3>Early Game</h3>
          {earlyUrls.map((url, index) => (
            <img
              key={index}
              src={url}
              alt={`Early Game Gráfica ${index + 1}`}
              style={{ maxWidth: "100%", marginBottom: "20px" }}
            />
          ))}

          <h3>Mid Game</h3>
          {midUrls.map((url, index) => (
            <img
              key={index}
              src={url}
              alt={`Mid Game Gráfica ${index + 1}`}
              style={{ maxWidth: "100%", marginBottom: "20px" }}
            />
          ))}

          <h3>Late Game</h3>
          {lateUrls.map((url, index) => (
            <img
              key={index}
              src={url}
              alt={`Late Game Gráfica ${index + 1}`}
              style={{ maxWidth: "100%", marginBottom: "20px" }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default SummonerTool;
