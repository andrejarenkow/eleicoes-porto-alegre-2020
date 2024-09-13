import requests
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Configurações da página
st.set_page_config(
    page_title="Eleiçoes POA - 2020",
    #page_icon="",
    layout="wide",
    initial_sidebar_state='collapsed'
) 
col1, col2, col3 = st.columns([1,4,1])

col2.header('Painel Eleições Porto Alegre 2020')

# Mostrar todas colunas
pd.set_option('display.max_columns', None)

# Layout
coluna1, coluna2, coluna3 = st.columns([1,3,3])

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
    with coluna1:
        st.text('Painel de filtros')
        turno = st.selectbox('Selecione o turno', options=[1, 2])
        cargo = st.selectbox('Selecione o cargo', options=['Vereador', 'Prefeito'])
        candidato = st.selectbox('Selecione o candidato', options=sorted(df[(df['DS_CARGO'] == cargo)&(df['NR_TURNO'] == turno)]['NM_VOTAVEL'].unique()))

    # Filtro para município, prefeito e primeiro turno
    filtro = (df['DS_CARGO'] == cargo) & (df['NR_TURNO'] == turno) & (df['NM_VOTAVEL'] == candidato)
    df_municipio = df[filtro].reset_index(drop=True)

    # Chave única zona+secao
    df_municipio['chave'] = df_municipio['NR_ZONA'].astype(int).astype(str) + '-' + df_municipio['NR_SECAO'].astype(str)

    # Votos por local de votação
    votos_por_local = df_municipio.groupby(['NM_LOCAL_VOTACAO', 'DS_LOCAL_VOTACAO_ENDERECO'])['QT_VOTOS'].sum().sort_values(ascending=False).reset_index()

    # Juntando
    gdf_votos = gdf.merge(votos_por_local, left_on='_', right_on='DS_LOCAL_VOTACAO_ENDERECO')
    gdf_votos.to_crs("EPSG:4326")
    
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
        height=700,
        width=800,
        center={'lat': -30.08, 'lon': -51.2},
        hover_data=['NM_LOCAL_VOTACAO', 'QT_VOTOS'],
        title=f'Votos por local de votação {candidato} - 2020',
        labels={'QT_VOTOS': 'Votos'},
        mapbox_style='dark',
        color_continuous_scale=px.colors.sequential.GnBu_r,  # Tons de laranja
    )

    coluna2.plotly_chart(fig)

    # Top 10 locais com mais votos
    top10 = px.bar(
        gdf_votos.sort_values('QT_VOTOS', ascending=True).tail(20),
        y = 'NM_LOCAL_VOTACAO',
        x = 'QT_VOTOS',
        title = f'Top20 locais com mais votos para {candidato}',
        labels={'QT_VOTOS': 'Votos'},
    )

    coluna3.plotly_chart(top10)




