import requests
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Mostrar todas colunas
pd.set_option('display.max_columns', None)

# Leitura do arquivo
@st.cache_data
def buscando_dados():
    try:
        df = pd.read_csv('votacao_secao_2020_RS_POA.zip', sep=';')
        gdf = gpd.read_file('locais_votacao.json')[['_', 'geometry']]
        return df, gdf
    except Exception as e:
        st.error(f"Erro ao ler os dados: {e}")
        return None, None

df, gdf = buscando_dados()

if df is not None and gdf is not None:
    turno = st.selectbox('Selecione o turno', options=[1, 2])
    cargo = st.selectbox('Selecione o cargo', options=['Vereador', 'Prefeito'])
    candidato = st.selectbox('Selecione o candidato', options=sorted(df['NM_VOTAVEL'].unique()))

    # Filtro para município, prefeito e primeiro turno
    filtro = (df['DS_CARGO'] == cargo) & (df['NR_TURNO'] == turno) & (df['NM_VOTAVEL'] == candidato)
    df_municipio = df[filtro].reset_index(drop=True)

    # Chave única zona+secao
    df_municipio['chave'] = df_municipio['NR_ZONA'].astype(int).astype(str) + '-' + df_municipio['NR_SECAO'].astype(str)

    # Votos por local de votação
    votos_por_local = df_municipio.groupby(['NM_LOCAL_VOTACAO', 'DS_LOCAL_VOTACAO_ENDERECO'])['QT_VOTOS'].sum().sort_values(ascending=False).reset_index()

    # Juntando
    gdf_votos = gdf.merge(votos_por_local, left_on='_', right_on='DS_LOCAL_VOTACAO_ENDERECO').to_crs("EPSG:3857")

    # Criar lat e lon
    gdf_votos['lat'] = gdf_votos['geometry'].centroid.y
    gdf_votos['lon'] = gdf_votos['geometry'].centroid.x

    token = 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw'
    px.set_mapbox_access_token(token)

    # Plotar com plotly.express o mapa
    fig = px.scatter_mapbox(
        gdf_votos,
        lat='lat',
        lon='lon',
        color='QT_VOTOS',
        size='QT_VOTOS',
        zoom=10,
        height=800,
        width=1000,
        center={'lat': -30.08, 'lon': -51.2},
        hover_data=['NM_LOCAL_VOTACAO', 'QT_VOTOS'],
        title='Votos por local de votação Cláudia Araújo - 2020',
        labels={'QT_VOTOS': 'Votos'},
        mapbox_style='dark',
        color_continuous_scale=px.colors.sequential.GnBu_r,  # Tons de laranja
    )

    fig
