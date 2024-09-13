import requests
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px


#mostrar todas colunas
pd.set_option('display.max_columns', None)

# leitura do arquivo
@st.cache_data
def buscando_dados():
  df = pd.read_csv('votacao_secao_2020_RS_POA.zip', sep = ';')

  #load o arquivo geojson e transformar em geodataframe
  gdf = gpd.read_file('locais_votacao.json')[['_', 'geometry']]

  return df, gdf

df, gdf = buscando_dados()

turno = st.selectbox('Selecione o turno', options = [1, 2])
cargo = st.selectbox('Selecione o cargo', options = ['Vereador', 'Prefeito'])
candidato = st.selectbox('Selecione o candidato', options = sorted(df['NM_VOTAVEL'].unique()))

# filtro para município, prefeito e primeiro turno
filtro = (df['DS_CARGO']==cargo)&(df['NR_TURNO']==turno)&(df['NM_VOTAVEL']==candidato)
df_municipio = df[filtro].reset_index(drop=True)

# Chave unica zona+secao
df_municipio['chave'] = df_municipio['NR_ZONA'].astype(int).astype(str) + '-' + df_municipio['NR_SECAO'].astype(str)

# Votos por local de votacao
votos_por_local = df_municipio.groupby(['NM_LOCAL_VOTACAO','DS_LOCAL_VOTACAO_ENDERECO'])['QT_VOTOS'].sum().sort_values(ascending=False).reset_index()

# Juntando 
gdf_votos = gdf.merge(votos_por_local, left_on='_', right_on='DS_LOCAL_VOTACAO_ENDERECO')

# criar lat e lon
gdf_votos['lat'] = gdf_votos['geometry'].centroid.y
gdf_votos['lon'] = gdf_votos['geometry'].centroid.x




# Plotar com plotly.express o mapa
fig = px.scatter_map(
    gdf_votos,
    lat='lat',
    lon='lon',
    color='QT_VOTOS',
    size='QT_VOTOS',
    zoom=10,
    #mapbox_style='Decimal',  # Mapa mais escuro
    height=800,
    width = 1000,
    center={'lat': -30.08, 'lon': -51.2},
    hover_data=['NM_LOCAL_VOTACAO', 'QT_VOTOS'],
    title='Votos por local de votação Cláudia Araújo - 2020',
    labels={'QT_VOTOS': 'Votos'},
    color_continuous_scale=px.colors.sequential.GnBu_r  # Tons de laranja
)

fig.update_layout(map_style="dark")

st.plotly_chart(fig)
