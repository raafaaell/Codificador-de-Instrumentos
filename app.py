import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io
import re

from criterios import CRITERIOS_DIRETOS

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Analisador de Normativas PMC", layout="wide")

# O SEU DICIONÁRIO DE CRITÉRIOS (ver criterios.py)

def processar_texto_multiplas_categorias(texto, nome_arquivo):
    """Sua lógica original de análise adaptada para o Streamlit"""
    # Normaliza quebras de linha e espaços do PDF para que termos longos sejam encontrados
    texto = re.sub(r"\s+", " ", texto).lower()
    registros = []
    
    for chave_categoria, palavras in CRITERIOS_DIRETOS.items():
        # Separa a condição e a categoria (ex: Substantivo e Tesouro)
        if " e " in chave_categoria:
            condicao, subcategoria = chave_categoria.split(" e ", 1)
        else:
            condicao, subcategoria = chave_categoria, "Geral"

        for palavra in palavras:
            contagem = texto.count(palavra.lower())
            if contagem > 0:
                registros.append({
                    "Arquivo": nome_arquivo,
                    "Condição": condicao.capitalize(),   
                    "Categoria": subcategoria.capitalize(), 
                    "Termo Encontrado": palavra,
                    "Contagem": contagem
                })
    return registros

# --- INTERFACE VISUAL ---
st.title("📂 Analisador de Normativas")
st.write("Selecione os arquivos PDF para processamento em lote.")

# Seletor de arquivos (substitui a pasta local fixa)
uploaded_files = st.file_uploader("Suba seus arquivos PDF aqui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Iniciar Análise"):
        resultados_gerais = []
        
        # Barra de progresso visual
        progresso = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Lê o PDF diretamente da memória (não precisa salvar no disco)
                reader = PdfReader(uploaded_file)
                texto = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
                
                # Executa a sua análise
                dados = processar_texto_multiplas_categorias(texto, uploaded_file.name)
                if dados:
                    resultados_gerais.extend(dados)
                
                # Atualiza barra de progresso
                progresso.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                st.error(f"Erro ao ler {uploaded_file.name}: {e}")

        # --- EXIBIÇÃO DOS RESULTADOS ---
        if resultados_gerais:
            df = pd.DataFrame(resultados_gerais)
            
            st.divider()
            st.success(f"Análise concluída! {len(df)} ocorrências encontradas.")
            
            # Mostra uma prévia na tela
            st.subheader("Prévia dos Dados")
            st.dataframe(df.head(10), use_container_width=True)

            # --- GERAÇÃO DO EXCEL PARA DOWNLOAD ---
            # Criamos os resumos conforme seu código original
            resumo_condicao = df['Condição'].value_counts().reset_index()
            resumo_condicao.columns = ['Condição', 'Qtd Termos Encontrados']
            
            resumo_cruzado = df.groupby(['Condição', 'Categoria']).size().reset_index(name='Quantidade')

            # Salva o Excel em um "buffer" na memória (essencial para Web/Mac/Windows)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Detalhado", index=False)
                resumo_condicao.to_excel(writer, sheet_name="Totais por Condição", index=False)
                resumo_cruzado.to_excel(writer, sheet_name="Matriz Cruzada", index=False)
            
            st.download_button(
                label="📥 Baixar Relatório Excel Completo",
                data=output.getvalue(),
                file_name="Relatorio_Analise_Normativas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum termo foi encontrado nos arquivos enviados.")