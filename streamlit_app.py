import requests
import streamlit as st
import pandas as pd
import geopandas as gpd



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

# Mostrando o df
df_municipio
