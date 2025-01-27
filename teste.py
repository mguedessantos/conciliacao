import pandas as pd
import streamlit as st

# Função de pré-processamento e cálculo das somas no CSV
def conciliacao_financeira(arquivo_csv):
    bandeiras_df = pd.read_csv(arquivo_csv, sep=";", encoding="ISO-8859-1")
    bandeiras_df['Valor bruto'] = bandeiras_df['Valor bruto'].replace({r'R\$': '', r'\.': '', ' ': ''}, regex=True)
    bandeiras_df['Valor bruto'] = bandeiras_df['Valor bruto'].str.replace(',', '.', regex=False)
    bandeiras_df['Valor bruto'] = bandeiras_df['Valor bruto'].astype(float)

    categorias = [
        ('Visa', 'Crédito', 'Visa Cred'),
        ('Visa', 'Débito', 'Visa Deb'),
        ('Mastercard', 'Crédito', 'Master Cred'),
        ('Maestro', 'Débito', 'Maestro Deb'),
        ('Elo', 'Crédito', 'Elo Cred'),
        ('Elo', 'Débito', 'Elo Deb')
    ]
    
    somas_csv = {}
    for bandeira, tipo, nome_categoria in categorias:
        soma = bandeiras_df[(bandeiras_df['Bandeira'] == bandeira) & (bandeiras_df['Produto'] == tipo)]['Valor bruto'].sum()
        somas_csv[f"{nome_categoria}"] = soma
    
    return somas_csv

# Função para extrair os valores da planilha Excel
def extrair_dados_excel(df):
    valores_extraidos = {}

    keywords = [
        ("Bin Visa Cred", "Visa Cred"),
        ("Bin Visa Deb", "Visa Deb"),
        ("Bin Master Cred", "Master Cred"),
        ("Bin Maestro Deb", "Maestro Deb")
    ]
    
    for keyword, label in keywords:
        linha_index = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)].index
        if len(linha_index) > 0:
            linha_index = linha_index[0]
            dados_abaixo = df.iloc[linha_index + 1:]
            sub_total_index = dados_abaixo[dados_abaixo.apply(lambda row: row.astype(str).str.contains("SUB-TOTAL TIPO:", case=False).any(), axis=1)].index
            if len(sub_total_index) > 0:
                sub_total_index = sub_total_index[0]
                valor = df.iloc[sub_total_index]["Unnamed: 19"]
                valores_extraidos[label] = valor

    return valores_extraidos

# Função principal para rodar o Streamlit
def main():
    st.title("Conciliador de Planilhas")
    
    # Carregar o arquivo Excel
    excel_file = st.file_uploader("Carregar Planilha Excel", type=["xls", "xlsx"])
    if excel_file:
        df = pd.read_excel(excel_file)
        valores_excel = extrair_dados_excel(df)
        st.subheader("Valores extraídos da Planilha Excel:")
        for label, valor in valores_excel.items():
            st.write(f"{label}: R${valor:,.2f}")
    
    # Carregar o arquivo CSV
    csv_file = st.file_uploader("Carregar Arquivo CSV", type="csv")
    if csv_file:
        somas_csv = conciliacao_financeira(csv_file)
        st.subheader("Valores do arquivo CSV:")
        for label, soma in somas_csv.items():
            st.write(f"{label}: R${soma:,.2f}")
    
        # Comparação
        st.subheader("Comparação entre Excel e CSV:")
        for label in valores_excel:
            if label in somas_csv:
                st.write(f"{label}: Excel = R${valores_excel[label]:,.2f} | CSV = R${somas_csv[label]:,.2f}")
            else:
                st.write(f"{label} não encontrado no CSV.")

        # Somatória
        st.subheader("Somatórias:")
        for label in ["Visa Cred", "Visa Deb", "Master Cred", "Maestro Deb"]:
            if label in valores_excel and label in somas_csv:
                soma = valores_excel[label] + somas_csv[label]
                st.write(f"Somatória entre {label} do Excel e {label} do CSV: R${soma:,.2f}")
            else:
                st.write(f"{label} não encontrado no Excel ou no CSV para realizar a somatória.")

if __name__ == "__main__":
    main()
