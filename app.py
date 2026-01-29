import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Analisador de Normativas PMC", layout="wide")

# O SEU DICIONÁRIO DE CRITÉRIOS
CRITERIOS_DIRETOS = {
    "Substantivo e nodalidade": ["transparência", "acesso à informação", "dados abertos", "princípio da publicidade", "sigilo"],
    "Substantivo e autoridade": ["poder de polícia", "competência legal", "hierarquia", "ordem pública", "soberania", "lei"],
    "Substantivo e tesouro": ["transferência", "taxas", "multa", "receita pública", "crédito suplementar"],
    "Substantivo e organização": ["estrutura administrativa", "personalidade jurídica", "organograma", "cargos e funções"],
    "Procedimental e nodalidade": ["Auditorias externas independentes", "Avaliação de impacto ambiental", "Etnomapeamento", "Monitoramento das emissões"],
    "Procedimental e autoridade": ["Cadastro de empreendimentos", "Inventário", "Licitação sustentavel", "Sistema de registro", "Avaliação Ambiental Estratégica"],
    "Procedimental e tesouro": ["dotação orçamentária"],
    "Procedimental e organização": ["Comissão Estadual de Validação", "Comitê Científico", "Coletivo de conselhos", "Comitê Técnico-Científico", "Conselho Estadual de Meio Ambiente", "Fórum Amapaense de Mudanças Climáticas", "Núcleo de Adaptação", "Fórum Amazonense de Mudanças Climáticas", "Comitê Gestor", "Conselho Estadual de Recursos Hídricos", "Criação de centros de inovação", "Fórum Paraense", "Fóruns Municipais", "Painel científico"],
}

def processar_texto_multiplas_categorias(texto, nome_arquivo):
    """Sua lógica original de análise adaptada para o Streamlit"""
    texto = texto.lower()
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
                texto = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
                
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