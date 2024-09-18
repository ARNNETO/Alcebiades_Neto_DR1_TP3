# Importa bibliotecas
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt

# Função para carregar dados com cache
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df = df.dropna(how='all')
    return df

# Cria persistência de dados para as seleções de cores, filtros e colunas
if 'back_color' not in st.session_state:
    st.session_state['back_color'] = 'Branco'

if 'column_to_filter' not in st.session_state:
    st.session_state['column_to_filter'] = None

if 'selected_value' not in st.session_state:
    st.session_state['selected_value'] = None

if 'selected_columns' not in st.session_state:
    st.session_state['selected_columns'] = []

# Cria a lista de cores usando a barra lateral
back_color = st.sidebar.selectbox('Escolha uma cor para alterar o fundo do seu painel', ['Preto', 
                                                                                        'Branco', 
                                                                                        'Vermelho', 
                                                                                        'Verde', 
                                                                                        'Azul', 
                                                                                        'Amarelo', 
                                                                                        'Ciano', 
                                                                                        'Magenta', 
                                                                                        'Cinza',
                                                                                        'Laranja'])

# Cria a lista com os códigos das cores
colors_code = {
    'Preto': '#000000',
    'Branco': '#FFFFFF',
    'Vermelho': '#FF0000',
    'Verde': '#00FF00',
    'Azul': '#0000FF',
    'Amarelo': '#FFFF00',
    'Ciano': '#00FFFF',
    'Magenta': '#FF00FF',
    'Cinza': '#808080',
    'Laranja': '#FFA500'
}

# Aplica a cor de fundo
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {colors_code[back_color]};
           }}
    </style>
    """,
    unsafe_allow_html=True
)

# Apresenta um título
st.title('Carregue seu arquivo CSV e visualize os dados')
st.subheader('Caso queira baixar o arquivo com os campos selecionados, basta clicar em "Baixar dados filtrados em csv"')

# Carrega o arquivo CSV
file = st.sidebar.file_uploader('Carregue seu arquivo CSV aqui', type=['csv'])

# Cria a barra de progresso e o spinner
if file is not None:
    st.write('Carregando os dados...')
    progress_bar = st.progress(0)
    for counter in range(1, 101):
        time.sleep(0.04)
        progress_bar.progress(counter)

    with st.spinner('Processando os dados...'):
        time.sleep(3)

        # Le o arquivo CSV
        df = load_data(file)

        # Exibe a tabela interativa com o DataFrame completo
        st.write("### Tabela Interativa dos Dados Carregados")
        st.dataframe(df)  # Exibe o DataFrame completo como tabela interativa

        # Exibe métricas
        st.write("### Métricas Básicas dos Dados")

        # Mostra contagem total de registros
        st.metric(label="Contagem de Registros", value=len(df))

        # Mostra soma e média das colunas numéricas (se houver)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if not numeric_cols.empty:
            for col in numeric_cols:
                col_sum = df[col].sum()
                col_mean = df[col].mean()
                st.metric(label=f"Soma da coluna {col}", value=col_sum)
                st.metric(label=f"Média da coluna {col}", value=col_mean)
        else:
            st.write("Não há colunas numéricas para exibir métricas.")

        # Filtros na barra lateral
        st.sidebar.write("Filtrar os dados por uma coluna específica:")
        column_to_filter = st.sidebar.selectbox("Selecione a coluna para aplicar o filtro", df.columns)

        # Cria seletor radio button para filtrar valor específico na barra lateral
        unique_values = df[column_to_filter].unique()
        selected_value = st.sidebar.radio(f"Selecione o valor de {column_to_filter} para filtrar", unique_values)

        # Aplica o filtro no DataFrame
        df_filtered = df[df[column_to_filter] == selected_value]

        st.write(f"Dados filtrados por {column_to_filter} = {selected_value}:")

        # Exibe a tabela interativa com os dados filtrados
        st.dataframe(df_filtered)

        # Cria lista de checkbox para selecionar colunas na barra lateral
        st.sidebar.write("Selecione as colunas que você quer visualizar:")
        selected_columns = []

        # Itera sobre as colunas e cria checkboxes na barra lateral
        for column in df_filtered.columns:
            if st.sidebar.checkbox(column, key=column): 
                selected_columns.append(column)
        
        # Mostra as colunas selecionadas
        if selected_columns:
            st.write("Colunas selecionadas:")
            df_final = df_filtered[selected_columns]
            st.dataframe(df_final)  # Exibe a tabela interativa com as colunas selecionadas

            # Converte as colunas filtradas para CSV
            csv = df_final.to_csv(index=False).encode('utf-8')

            # Cria botão para download do CSV
            st.download_button(
                label="Baixar dados filtrados em CSV",
                data=csv,
                file_name='dados_filtrados.csv',
                mime='text/csv',
            )
        else:
            st.write("Nenhuma coluna selecionada.")

        # Gráficos
        st.write("### Gráficos de Visualização")

        # Seletor de gráfico na barra lateral
        chart_type = st.sidebar.selectbox("Escolha o tipo de gráfico", ["Gráfico de Barras", "Gráfico de Linhas", "Gráfico de Pizza", "Histograma"])

        # Se for um gráfico de barras, linhas ou histograma, selecionar a coluna para o eixo Y na barra lateral
        if chart_type in ["Gráfico de Barras", "Gráfico de Linhas", "Histograma"]:
            y_column = st.sidebar.selectbox("Selecione a coluna para o eixo Y", df.columns)

        # Criar o gráfico de acordo com o tipo selecionado
        if chart_type == "Gráfico de Barras":
            fig, ax = plt.subplots()
            ax.bar(df_final[column_to_filter], df_final[y_column], color='skyblue')
            ax.set_xlabel(column_to_filter)
            ax.set_ylabel(y_column)
            ax.set_title(f"Gráfico de Barras: {column_to_filter} vs {y_column}")
            st.pyplot(fig)

        elif chart_type == "Gráfico de Linhas":
            fig, ax = plt.subplots()
            ax.plot(df_final[column_to_filter], df_final[y_column], marker='o', color='green')
            ax.set_xlabel(column_to_filter)
            ax.set_ylabel(y_column)
            ax.set_title(f"Gráfico de Linhas: {column_to_filter} vs {y_column}")
            st.pyplot(fig)

        elif chart_type == "Gráfico de Pizza":
            # Para o gráfico de pizza, a coluna selecionada será usada como valores
            fig, ax = plt.subplots()
            sizes = df_final[column_to_filter].value_counts()
            ax.pie(sizes, labels=sizes.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax.set_title(f"Gráfico de Pizza: Distribuição de {column_to_filter}")
            st.pyplot(fig)

        elif chart_type == "Histograma":
            # Para o histograma, a coluna selecionada será usada para exibir a distribuição
            fig, ax = plt.subplots()
            ax.hist(df_final[y_column], bins=20, color='purple', edgecolor='black')
            ax.set_xlabel(y_column)
            ax.set_title(f"Histograma de {y_column}")
            st.pyplot(fig)

    # Remove a barra de progresso após o término do processamento
    progress_bar.empty()
