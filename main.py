import streamlit as st
import folium 
from folium.plugins import Fullscreen
from streamlit.components.v1 import html
import extra_streamlit_components as stx
import pandas as pd
import numpy as np
import csv
import os
import chardet
import plotly.express as px
from pathlib import Path

#caminho da pasta Dados_Ar
caminho_pasta = Path.home() / "Documents" / "Importante" / "gases-IEMA" / "Dados_Ar"


#coordenadas das estações
estacoes = {'Rodoviária': [-15.793250313259408, -47.882858046886724],
                'Zoológico': [-15.848640375100038, -47.933209328640984],
                'Fercal': [-15.600853059139409, -47.871843351086284],
                'Samambaia': [-15.86281724026738, -48.05380043242077],

                }

def arquivos_df(caminho_pasta):

    arquivos = os.listdir(caminho_pasta)

    dataframes = {}
    for arquivo in arquivos:
        caminho_completo = os.path.join(caminho_pasta, arquivo)
        with open(caminho_completo, 'rb') as f:
            resultado = chardet.detect(f.read())

        encoding_detectado = resultado['encoding']
        print(f"🔍 {arquivo} → codificação detectada: {encoding_detectado}")

        df = pd.read_csv(caminho_completo, encoding=encoding_detectado)
        dataframes[arquivo[2:6]] = df


    print(f"DEBUG: {dataframes}")
    return dataframes
        



def mapa(estacoes):
    caminho_completo = os.path.join(caminho_pasta, 'DF2022.csv')
    with open(caminho_completo, 'rb') as f:
            resultado = chardet.detect(f.read())

    encoding_detectado = resultado['encoding']
    df = pd.read_csv(caminho_completo, encoding=encoding_detectado)
    df['Data'] = pd.to_datetime(df['Data'])
    mais_recentes = df.groupby('Estacao')['Data'].max().reset_index()
    df_mais_recente = pd.merge(df, mais_recentes, on=['Estacao', 'Data'])

    print(f"MAIS RECENT DEBUG: {df_mais_recente}")

    map = folium.Map(location=(-15.793948685420359, -47.882914318928044), zoom_start= 10, width='100%')


    for estacao, coordenadas in estacoes.items():
         # Filtra linhas onde o nome da estação do dicionário está contido no campo 'Estacao' do df
      dados_estacao = df_mais_recente[df_mais_recente['Estacao'].str.contains(estacao, case=False, na=False)]
      if not dados_estacao.empty:
        for _, row in dados_estacao.iterrows():
         # Gerando o HTML do popup para a estação
         popup_html = f"""
    <div style="font-family: Arial; font-size: 13px;">
        <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;">
            Estação {estacao}
        </div>
        <div><b>Poluente:</b> {row['Poluente']}</div>
        <div><b>Valor:</b> {row['Valor']} ug/m³</div>
    </div>
"""


    #     folium.Circle(
    #     location=[coordenadas[0], coordenadas[1]],
    #     radius=5000,
    #     color="black",
    #     weight=1,
    #     fill_opacity=0.6,
    #     opacity=1,
    #     fill_color="green",
    #     fill=False,  # gets overridden by fill_color
    # ).add_to(map)



        folium.Marker(
        location=[coordenadas[0], coordenadas[1]],
        # tooltip="Click me!",
        popup=popup_html,
        icon=folium.Icon(icon="cloud"),
    ).add_to(map)
        
    folium.plugins.Fullscreen(
                        position="topright",
                        title="Tela Cheia",
                        title_cancel="Sair",
                        force_separate_button=True,
                    ).add_to(map)


    map_html = map._repr_html_()
    return map_html



def main():

    chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id="tab1", title="Mapa", description=""),
    stx.TabBarItemData(id="tab2", title="Gráfico", description=""),
    stx.TabBarItemData(id="tab3", title="Dados", description="")])

    if chosen_id == 'tab1':
        with st.spinner("Carregando mapa.."):
            map_html = mapa(estacoes)
            st.title("Mapa Estações")
            html(map_html, width=1200, height=600)

    elif chosen_id == 'tab2':
        with st.spinner("Carregando Gráfico..."):

            st.title("Gráfico")
            df = arquivos_df(caminho_pasta)

            option = st.selectbox(
                "Selecione o ano:",
                ("2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015" ),
                index=0
            )

            df_grafico = df[option]

            print(f"DEBUG GRÀFICO: {df_grafico}")
            df_grafico['Data'] = pd.to_datetime(df_grafico['Data'])
            # Ordenar por data
            df_grafico = df_grafico.sort_values('Data')
            # df_grafico['Valor'] = df_grafico['Valor'].apply(lambda x: f"{x:.2f}")
            fig = px.line(
            df_grafico,
            x='Data',
            y='Valor',
            color='Estacao',
            labels={
                "Data": "Data",
                "Valor": "Valor (ug/m³)",
                "Estacao": "Estação",
                # "Poluente": "Poluente"
            }, hover_data=['Poluente'],  # <- aqui você adiciona o que quer exibir no tooltip
            title=f"Valores de Poluentes ao longo de {option}"
        )

        fig.update_layout(hovermode="x unified",width=1000, height=600,)   
        st.plotly_chart(fig, use_container_width=True)

    else:
        with st.spinner("Carregando Dataframe.."):
            dataframes = arquivos_df(caminho_pasta)
            st.title("Dataframe")
            option = st.selectbox(
                "Selecione o ano:",
                ("2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015" ),
                index=0
    )
            
            st.dataframe(dataframes[option])




if __name__ == "__main__": 
    main()




