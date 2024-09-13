import requests
import streamlit as st
import pandas as pd

#mostrar todas colunas
pd.set_option('display.max_columns', None)

# leitura do arquivo
@st.cache_data
def buscando_dados():
  df = pd.read_csv('votacao_secao_2020_RS_POA.zip', sep = ';')

  return df

df = buscando_dados()

df

