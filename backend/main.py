import os
import subprocess
import sys
import requests
import pandas as pd
import urllib.parse
import json
import io
from pydantic import BaseModel
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles


import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


def install_requirements():
    try:
        # Comando para instalar las dependencias
        subprocess.check_call([sys.executable, "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Error instalando dependencias: {e}")


matplotlib.use('Agg')
# Crea la carpeta "staticc" si no existe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta relativa para "staticc"
STATIC_DIR = os.path.join(BASE_DIR, "../staticc")  # Asume que "staticc" está al nivel del proyecto, no en backend

# Crear la carpeta "staticc" si no existe
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

#app.mount("/staticc", StaticFiles(directory="C:/Users/Charli/Documents/prueba/staticc"), name="staticc")
app.mount("/staticc", StaticFiles(directory="C:/Users/Maest/OneDrive/Escritorio/Pr2/LolNalisis/staticc"), name="staticc")

#DEFINIR PARÁMETROS=========================================================
API_KEY = "RGAPI-3b6a6097-957f-4176-8dd0-5e22fb9df736"
headers = {"X-Riot-Token": API_KEY}

base_dir = os.path.dirname(os.path.abspath(__file__))
early_game_path = os.path.join(base_dir, 'data', 'early_game_data.csv')
mid_game_path = os.path.join(base_dir, 'data', 'mid_game_data.csv')
late_game_path = os.path.join(base_dir, 'data', 'late_game_data.csv')

early_game = pd.read_csv(early_game_path)
mid_game = pd.read_csv(mid_game_path)
late_game = pd.read_csv(late_game_path)

#early_game = pd.read_csv('./data/early_game_data.csv')
#mid_game = pd.read_csv('./data/mid_game_data.csv')
#late_game = pd.read_csv('./data/late_game_data.csv')
def toplaners(df):
    df['player_id'] = df.groupby('match_id').cumcount() + 1
    top_df = df[df['player_id'].isin([1, 6])].copy()
    return top_df

top_early = toplaners(early_game)
top_mid = toplaners(mid_game)
top_late = toplaners(late_game)
#Eliminar junglas y supps
top_early = top_early[top_early['cs_per_min'] > 3]
top_mid = top_mid[top_mid['cs_per_min'] > 3]
top_late = top_late[top_late['cs_per_min'] > 3]

top_early = top_early.reset_index(drop=True)
top_mid = top_mid.reset_index(drop=True)
top_late = top_late.reset_index(drop=True)

#DATOS TOPS EARLY===============================
tops_clusters_early = top_early
print(tops_clusters_early.head(8))

#Estadísticas
tops_clusters_early['KDA'] = (tops_clusters_early['kills'] + tops_clusters_early['assists']) / tops_clusters_early['deaths'].replace(0, 1)
metrics = ['KDA', 'cs_per_min']
descriptive_stats = tops_clusters_early[metrics].agg(['mean', 'median', 'std'])

correlation_matrix = tops_clusters_early[['KDA','cs_per_min', 'win']].corr()
# Clustering
X_cluster = tops_clusters_early[['KDA', 'cs_per_min']]
kmeans = KMeans(n_clusters=3, random_state=42)
tops_clusters_early['cluster'] = kmeans.fit_predict(X_cluster)

#DATOS TOPS Midgame=============================
tops_clusters_mid = top_mid
print(tops_clusters_mid.head(8))

#Estadísticas
tops_clusters_mid['KDA'] = (tops_clusters_mid['kills'] + tops_clusters_mid['assists']) / tops_clusters_mid['deaths'].replace(0, 1)
metrics = ['KDA', 'cs_per_min']
descriptive_stats = tops_clusters_mid[metrics].agg(['mean', 'median', 'std'])
print("Descriptive Statistics:\n", descriptive_stats)


correlation_matrix = tops_clusters_mid[['KDA','cs_per_min', 'win']].corr()


# Clustering
X_cluster = tops_clusters_mid[['KDA', 'cs_per_min']]
kmeans = KMeans(n_clusters=3, random_state=42)
tops_clusters_mid['cluster'] = kmeans.fit_predict(X_cluster)

#DATOS TOPS LATE================================
tops_clusters_late = top_late
print(tops_clusters_late.head(8))
# Calculate KDA
tops_clusters_late['KDA'] = (tops_clusters_late['kills'] + tops_clusters_late['assists']) / tops_clusters_late['deaths'].replace(0, 1)

#Estadísticas
metrics = ['KDA', 'cs_per_min']
descriptive_stats = tops_clusters_late[metrics].agg(['mean', 'median', 'std'])
print("Descriptive Statistics:\n", descriptive_stats)


correlation_matrix = tops_clusters_late[['KDA','cs_per_min', 'win']].corr()


# Clustering
X_cluster = tops_clusters_late[['KDA', 'cs_per_min']]
kmeans = KMeans(n_clusters=3, random_state=42)
tops_clusters_late['cluster'] = kmeans.fit_predict(X_cluster)


#FUNCION ANÁLISIS DE DESEMPEÑO Y GENERACIÓN DE GRÁFICAS
def Clustering_Analisis(df_analisis, tops_clusters, fase, summoner_name):

    import matplotlib
    matplotlib.use('Agg')
    import pandas as pd
    import matplotlib.pyplot as plt

    # WINRATE
    best_cluster = tops_clusters.groupby('cluster')['win'].mean().idxmax()
    print(f"Cluster con mayor winrate: {best_cluster}")

    best_cluster_data = tops_clusters[tops_clusters['cluster'] == best_cluster]
    best_cluster_avg = best_cluster_data[['kills', 'deaths', 'assists', 'gold_earned', 'cs_per_min', 'damage_done', 'damage_taken']].mean()
    user_avg = df_analisis[['kills', 'deaths', 'assists', 'gold_earned', 'cs_per_min', 'damage_done', 'damage_taken']].mean()

    main_stats = ['kills', 'deaths', 'assists', 'cs_per_min']
    alternativas = ['gold_earned', 'damage_done', 'damage_taken']

    # GRÁFICO 1
    plt.figure(figsize=(10, 6))
    x = range(len(main_stats))
    plt.bar([i - 0.2 for i in x], best_cluster_avg[main_stats], width=0.4, label="Mejor Cluster", color='#007acc', edgecolor='black')
    plt.bar([i + 0.2 for i in x], user_avg[main_stats], width=0.4, label=summoner_name, color='#f08080', edgecolor='black')
    plt.xticks(x, main_stats)
    plt.xlabel("Métricas", fontsize=12)
    plt.ylabel("Promedio", fontsize=12)
    plt.title(f"Comparación desempeño {summoner_name} vs Objetivo para {fase}", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Guardar gráfico
    chart1_path = f"../staticc/graph1_{summoner_name}_{fase}.png"
    print(f"Gráfica guardada en {chart1_path}")
    plt.savefig(chart1_path)


    #graph1_path = f"graph1_{summoner_name}_{fase}.png"
    #plt.savefig(graph1_path)
    plt.close()

    # GRÁFICO 2
    plt.figure(figsize=(10, 6))
    x = range(len(alternativas))
    plt.bar([i - 0.2 for i in x], best_cluster_avg[alternativas], width=0.4, label="Objetivo", color='#007acc', edgecolor='black')
    plt.bar([i + 0.2 for i in x], user_avg[alternativas], width=0.4, label=summoner_name, color='#f08080', edgecolor='black')
    plt.xticks(x, alternativas)
    plt.xlabel("Métricas", fontsize=12)
    plt.ylabel("Promedio", fontsize=12)
    plt.title(f"Comparación de Variables Alternativas {summoner_name} vs Objetivo", fontsize=14)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)

    # Guardar gráfico
    chart2_path = f"../staticc/graph2_{summoner_name}_{fase}.png"
    print(f"Gráfica guardada en {chart2_path}")
    plt.savefig(chart2_path)
    #graph2_path = f"graph2_{summoner_name}_{fase}.png"
    #plt.savefig(graph2_path)
    plt.close()

    recomendaciones = []

    for metric in main_stats:
      user_stat = user_avg[metric]
      cluster_stat = best_cluster_avg[metric]


      diferencia_porcentual = abs((user_stat - cluster_stat) / cluster_stat) * 100


      if metric == 'deaths':
          if user_stat > cluster_stat:
              if diferencia_porcentual < 27:
                  recomendaciones.append(f"¡Casi lo logras en {metric}! Intenta reducir ligeramente tus muertes para igualar el promedio de los  mejores jugadores.")
              else:
                  recomendaciones.append(f"(-) Reduce la cantidad de {metric} para estar más cerca del promedio de los mejores jugadores.")
          else:
              recomendaciones.append(f"(+) Buen desempeño en {metric}: mantén o mejora este nivel bajo.")
      else:
          if user_stat < cluster_stat:
              if diferencia_porcentual < 27:
                  #print(f"{diferencia_porcentual} en {metric}")
                  recomendaciones.append(f"¡Estás muy cerca en {metric}! Solo necesitas un pequeño aumento para alcanzar el nivel de los mejores jugadores.")
              else:
                  recomendaciones.append(f"(-) Mejora en {metric}: Incrementa tu {metric} para alcanzar el promedio de los mejores jugadores.")
          else:
              recomendaciones.append(f"(+) Buen desempeño en {metric}: mantén este nivel o sigue mejorando.")

    for metric in alternativas:
      user_stat = user_avg[metric]
      cluster_stat = best_cluster_avg[metric]

      diferencia_porcentual = abs((user_stat - cluster_stat) / cluster_stat) * 100

      if user_stat < cluster_stat:
          if diferencia_porcentual < 27:
              recomendaciones.append(f"¡Estás muy cerca en {metric}! Solo necesitas un pequeño ajuste para igualar el promedio de los mejores jugadores.")
          else:
              recomendaciones.append(f"(-) Mejora en {metric}: Incrementa tu {metric} para acercarte al promedio de los mejores jugadores.")
      else:
          recomendaciones.append(f"(+) Buen desempeño en {metric}: mantén este nivel o sigue mejorando.")

    # Retornar las rutas de los gráficos
    #return graph1_path, graph2_path
    print("REEECOMENDACIONES", recomendaciones)
    return [chart1_path, chart2_path], recomendaciones

matches_data_early = []
matches_data_mid = []
matches_data_late = []



# Función TIMELINE ----------------------------------------------------------------------------
def get_timeline_data(match_id):
    timeline_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    response = requests.get(timeline_url, headers={"X-Riot-Token": API_KEY})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener datos de timeline de la partida {match_id}: {response.status_code}")
        return None

# Función TIMELINE INGAME ----------------------------------------------------------------------------
def process_timeline(timeline_data, participants, start_time, end_time):
    participant_frames = {participant['participantId']: {'kills': 0, 'deaths': 0, 'assists': 0, 'gold_earned': 0, 'cs_per_min': 0, 'damage_done': 0, 'damage_taken': 0} for participant in participants}

    # Almacenar el oro del minuto anterior para calcular solo el incremento
    previous_gold = {participant['participantId']: 0 for participant in participants}

    for frame in timeline_data['info']['frames']:
        frame_minute = frame['timestamp'] // 60000
        if start_time <= frame_minute < end_time:
            for event in frame['events']:
                # Procesar
                if event['type'] == 'CHAMPION_KILL':
                    killer_id = event['killerId']
                    victim_id = event['victimId']
                    assisting_ids = event.get('assistingParticipantIds', [])

                    if killer_id in participant_frames:
                        participant_frames[killer_id]['kills'] += 1
                    if victim_id in participant_frames:
                        participant_frames[victim_id]['deaths'] += 1
                    for assist_id in assisting_ids:
                        if assist_id in participant_frames:
                            participant_frames[assist_id]['assists'] += 1

            # Procesar oro, minions, daño en cada frame
            for pid, participant_frame in frame['participantFrames'].items():
                participant_id = int(pid)
                if participant_id in participant_frames:

                    gold_diff = participant_frame['totalGold'] - previous_gold[participant_id]
                    participant_frames[participant_id]['gold_earned'] += gold_diff
                    previous_gold[participant_id] = participant_frame['totalGold']

                    participant_frames[participant_id]['cs_per_min'] = participant_frame['minionsKilled'] / (frame_minute + 1)


                    damage_stats = participant_frame.get('damageStats', {})
                    participant_frames[participant_id]['damage_done'] = damage_stats.get('totalDamageDoneToChampions', 0)
                    participant_frames[participant_id]['damage_taken'] = damage_stats.get('totalDamageTaken', 0)

    return participant_frames

# FUNCIÓN FASES ----------------------------------------------------------------------------
def process_match(match_id, phase, start_time, end_time, puuid):
    
    (print(match_id, phase, start_time, end_time, puuid))
    match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    match_response = requests.get(match_url, headers={"X-Riot-Token": API_KEY})
    

    if match_response.status_code == 200:
        match_data = match_response.json()
        print("Partida ID:",match_id,'Análisis realizado.')
        participants = match_data['info']['participants']
        timeline_data = get_timeline_data(match_id)

        if timeline_data:
            
            phase_data = process_timeline(timeline_data, participants, start_time, end_time)

            phase_dataset = []
            for participant in participants:
                #print(participant['puuid'], "pruebapuuid2")
                if participant['puuid'] == puuid and participant['participantId'] in [1, 6]:
                    pid = participant['participantId']
                    participant_data = {
                        'match_id': match_id,
                        'summoner_name': participant['summonerName'],
                        'champion': participant['championName'],
                        'kills': phase_data[pid]['kills'],
                        'deaths': phase_data[pid]['deaths'],
                        'assists': phase_data[pid]['assists'],
                        'gold_earned': phase_data[pid]['gold_earned'],
                        'cs_per_min': phase_data[pid]['cs_per_min'],
                        'damage_done': phase_data[pid]['damage_done'],
                        'damage_taken': phase_data[pid]['damage_taken'],
                        #'participant_id': pid,
                        'win': participant['win']
                    }
                    phase_dataset.append(participant_data)
                    print("datos guardados")

            if phase == 'early':
                print("pHASEDATASET", phase_dataset)
                matches_data_early.extend(phase_dataset)
                print("matchess",matches_data_early)

            elif phase == 'mid':
                matches_data_mid.extend(phase_dataset)
            elif phase == 'late':
                matches_data_late.extend(phase_dataset)

        #time.sleep(1.2)
    else:
        print(f"Error al obtener los datos de la partida3: {match_response.status_code}")

def obtener_historial_partidas(puuid):
  url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=50"
  response = requests.get(url, headers=headers)

  partidas_usuario = []
  if response.status_code == 200:
      match_ids = response.json()
      for match_id in match_ids:
          if len(partidas_usuario) >= 15:
              break

          match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
          match_response = requests.get(match_url, headers=headers)

          if match_response.status_code == 200:
              match_data = match_response.json()
              if match_data['info']['queueId'] in [420,440]:  # SoloQ y flex
                print(match_id,'hola como estas')
                partidas_usuario.append(match_id)

          else:
              print(f"Error al obtener los detalles de la partida2: {match_response.status_code}")
  else:
      print(f"Error al obtener el historial de partidas: {response.status_code}, {response.text}")

  print(f"Últimas {len(partidas_usuario)} partidas de SoloQ y flex: {partidas_usuario}")
  return partidas_usuario

def obtener_puuid(summoner_name, tagline):
    codificado_sn = urllib.parse.quote(summoner_name)
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{codificado_sn}/{tagline}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        summoner_data = response.json()
        puuid = summoner_data.get("puuid")
        print(f"PUUID del invocador {summoner_name}: {puuid}")
    else:
        # Retornar el texto del error al cliente.
        error_message = f"Error al obtener el PUUID: {response.status_code}, {response.text}"
        print(error_message)
        raise HTTPException(status_code=response.status_code, detail=f"Error al obtener PUUID, no se encuentra usuario {summoner_name}#{tagline}")
    return puuid


# Instalar dependencias
install_requirements()

# DATOS DE REACT JS
class SummonerData(BaseModel):
    summonerName: str
    tagline: str


@app.post("/set-summoner/")
async def set_summoner(data: SummonerData):
    summoner_name = data.summoner_name
    tagline = data.tagline

    if not summoner_name or not tagline:
        raise HTTPException(status_code=400, detail="El nombre de invocador y el tagline son obligatorios")

    # Aquí puedes usar summoner_name y tagline en tu lógica
    print(f"Nombre del invocador: {summoner_name}")
    print(f"Tagline: {tagline}")

    return {"message": "Datos recibidos correctamente"}


class MatchData(BaseModel):
    puuid: str
    phase: str
    start_time: int
    end_time: int

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)
# Endpoint para ejecutar la función y devolver las gráficas
#print(summoner_name, tagline)




df_analisis_early = pd.DataFrame(matches_data_early)
df_analisis_mid = pd.DataFrame(matches_data_mid)
df_analisis_late = pd.DataFrame(matches_data_late)

# Endpoint para servir las gráficas
@app.get("/get-graph/{filename}")
def get_graph(filename: str):
    file_path = os.path.join(".", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
puuid_global = None

def obtener_info_jugador(puuid):
    try:
        # URL para obtener el perfil del jugador
        summoner_url = f"https://la1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response_summoner = requests.get(summoner_url, headers=headers)
        
        if response_summoner.status_code != 200:
            raise Exception(f"Error al obtener datos del perfil: {response_summoner.status_code}, {response_summoner.text}")
        
        summoner_data = response_summoner.json()
        
        # Extraer información básica del perfil
        summoner_id = summoner_data.get("id")
        account_level = summoner_data.get("summonerLevel")
        summoner_name = summoner_data.get("name")
        
        # URL para obtener el rango en clasificatorias
        ranked_url = f"https://la1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        response_ranked = requests.get(ranked_url, headers=headers)
        
        if response_ranked.status_code != 200:
            raise Exception(f"Error al obtener datos de liga: {response_ranked.status_code}, {response_ranked.text}")
        
        ranked_data = response_ranked.json()
        
        # Procesar la información de clasificatorias
        ranked_info = {}
        for queue in ranked_data:
            queue_type = queue.get("queueType", "Unknown")
            ranked_info[queue_type] = {
                "tier": queue.get("tier", "Unranked"),
                "rank": queue.get("rank", ""),
                "lp": queue.get("leaguePoints", 0),
                "wins": queue.get("wins", 0),
                "losses": queue.get("losses", 0),
            }
        
        # Consolidar la información
        jugador_info = {
            "summoner_name": summoner_name,
            "account_level": account_level,
            "ranked_info": ranked_info,
        }
        
        return jugador_info

    except Exception as e:
        return {"error": str(e)}


@app.post("/analyze")
async def analyze_data(data: SummonerData):
    try:
        puuid = obtener_puuid(data.summonerName, data.tagline)
        player_info = obtener_info_jugador(puuid)

        partidas_usuario = obtener_historial_partidas(puuid)  # Implementar esta función
        static_url_base = "http://localhost:8000/staticc"
        chart_data = []

        for i, match_id in enumerate(partidas_usuario):
            if i >= 10:
                break
            process_match(match_id, 'early', 0, 15, puuid)
            process_match(match_id, 'mid', 0, 30, puuid)
            process_match(match_id, 'late', 0, 999, puuid)

        df_early = pd.DataFrame(matches_data_early)
        df_mid = pd.DataFrame(matches_data_mid)
        df_late = pd.DataFrame(matches_data_late)

        for phase, df_analysis, tops_clusters in zip(
            ['Early Game', 'Mid Game', 'Late Game'],
            [df_early, df_mid, df_late],
            [tops_clusters_early, tops_clusters_mid, tops_clusters_late]
        ):
            chart_paths, recommendations = Clustering_Analisis(df_analysis, tops_clusters, phase, data.summonerName)
            public_chart_paths = [
                f"{static_url_base}/{os.path.basename(chart_path)}"
                for chart_path in chart_paths
            ]

            chart_data.append({
                "phase": phase,
                "charts": public_chart_paths,
                "recommendations": recommendations,
            })

        return {
            "player_info": player_info,
            "data": chart_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


