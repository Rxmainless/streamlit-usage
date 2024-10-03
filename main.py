import pandas as pd
import streamlit as st
import chardet
import plotly.express as px

# Função para gerar relatório
def gerar_relatorio(df_1):
    try:
        df_relatorio = df_1[['Nome', 'CPF', 'Vínculo', 'Plano', 'Tempo de Casa', 'Anterior (R$)', 'Atual (R$)']]
        return df_relatorio
    except KeyError as e:
        st.error(f"Erro: Uma ou mais colunas não foram encontradas: {e}")
        return None

# Função para converter DataFrame em CSV
def convert_df_to_csv(df_2):
    return df_2.to_csv(index=False).encode('utf-8')

# Início do aplicativo Streamlit
st.title("Gerador de Faturas")

# Informações da empresa
st.markdown("""
### CNPJ: XXXXXXXXXXXXXX
### N° do Contrato: 1234
### Serviços Contratados: XXXXXXXXXXXX
""")

# Inicializar a variável df como None
df = None

# Upload de arquivo (CSV ou Excel)
uploaded_file = st.file_uploader("Escolha um arquivo (CSV ou Excel)", type=["csv", "xlsx"])
if uploaded_file:
    rawdata = uploaded_file.read(10000)  # Lê os primeiros 10k bytes
    result = chardet.detect(rawdata)
    encoding = result['encoding']
    uploaded_file.seek(0)

    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, encoding=encoding, delimiter=';')
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    if df is not None:
        st.write("Dados carregados com sucesso!")
        st.write("Colunas disponíveis no DataFrame:", df.columns.tolist())

        # Menu de navegação
        menu = st.sidebar.selectbox("Escolha uma aba:", ["Relatório", "Resumo"])

        # Relatório
        if menu == "Relatório":
            st.markdown("## Movimentações:")
            relatorio = gerar_relatorio(df)
            if relatorio is not None:
                st.table(relatorio)
                csv = convert_df_to_csv(relatorio)
                st.download_button(
                    label="Baixar Relatório em CSV",
                    data=csv,
                    file_name='relatorio_empresa.csv',
                    mime='text/csv',
                )

        # Resumo da fatura
        if menu == "Resumo":
            st.markdown("## Resumo da Fatura")

            # Definindo a lógica para os indicadores
            vencimento = "10/10/2024"  # Pode ser alterado conforme necessário

            # Calcular valores com base no DataFrame
            try:
                valor = df['Atual (R$)'].sum()  # Total de valores atuais
                acrescimos = df['Acréscimos (R$)'].sum() if 'Acréscimos (R$)' in df.columns else 0
                descontos = df['Descontos (R$)'].sum() if 'Descontos (R$)' in df.columns else 0
                valor_total = valor + acrescimos - descontos
            except Exception as e:
                st.error(f"Erro ao calcular indicadores: {e}")
                valor, acrescimos, descontos, valor_total = 0, 0, 0, 0

            # Exibir os indicadores em colunas
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Vencimento:**", vencimento)
                st.write("**Valor:** R$", valor)
            with col2:
                st.write("**Acréscimos:** R$", acrescimos)
                st.write("**Descontos:** R$", descontos)
                st.write("**Valor Total:** R$", valor_total)

            # Gráfico interativo
            labels = ['Valor', 'Acréscimos', 'Descontos', 'Valor Total']
            values = [valor, acrescimos, descontos, valor_total]
            fig = px.bar(x=labels, y=values, title="Resumo da Fatura", labels={'x':'Categoria', 'y':'Valores em R$'})
            st.plotly_chart(fig)
