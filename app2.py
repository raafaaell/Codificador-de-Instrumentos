import os
from pypdf import PdfReader
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO ---
PASTA_ARQUIVOS = "/Users/rafaelba/Desktop/Codificação de Normativas/PMC_Estados"

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
    texto = texto.lower()
    registros = []
    for chave_categoria, palavras in CRITERIOS_DIRETOS.items():
        condicao, subcategoria = chave_categoria.split(" e ", 1)
        for palavra in palavras:
            qtd = texto.count(palavra.lower())
            if qtd > 0:
                registros.append({
                    "Arquivo": nome_arquivo.replace(".pdf", ""), # Remove .pdf para o gráfico ficar limpo
                    "Chave_Completa": chave_categoria,
                    "Condição": condicao.capitalize(),   
                    "Categoria": subcategoria.capitalize(), 
                    "Contagem": qtd
                })
    return registros

def gerar_graficos_comparativos(df):
    print("\n📊 Gerando gráficos comparativos entre estados...")
    
    # --- 1. GRÁFICO: AS 8 CATEGORIAS POR ESTADO ---
    plt.figure(figsize=(15, 8))
    pivot_8 = df.groupby(['Arquivo', 'Chave_Completa'])['Contagem'].sum().unstack(fill_value=0)
    pivot_8.plot(kind='bar', stacked=True, figsize=(15, 8), colormap='tab10')
    plt.title("Comparativo por Estado: As 8 Categorias Detalhadas", fontsize=16)
    plt.ylabel("Total de Termos")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Categorias", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("Comparativo_8_Categorias.png")
    
    # --- 2. GRÁFICO: SUBSTANTIVO vs PROCEDIMENTAL ---
    plt.figure(figsize=(15, 8))
    pivot_cond = df.groupby(['Arquivo', 'Condição'])['Contagem'].sum().unstack(fill_value=0)
    pivot_cond.plot(kind='bar', stacked=False, figsize=(12, 6), color=['#1f77b4', '#ff7f0e'])
    plt.title("Comparativo por Estado: Substantivo vs Procedimental", fontsize=16)
    plt.ylabel("Frequência de Termos")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("Comparativo_Condicao.png")

    # --- 3. GRÁFICO: GRANDES GRUPOS (Nodalidade, Autoridade, etc) ---
    plt.figure(figsize=(15, 8))
    pivot_cat = df.groupby(['Arquivo', 'Categoria'])['Contagem'].sum().unstack(fill_value=0)
    pivot_cat.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='viridis')
    plt.title("Comparativo por Estado: Tipos de Governança", fontsize=16)
    plt.ylabel("Frequência de Termos")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Eixos", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("Comparativo_Eixos_Governanca.png")

def iniciar_processamento():
    resultados_gerais = []
    if not os.path.exists(PASTA_ARQUIVOS):
        print(f"Pasta {PASTA_ARQUIVOS} não encontrada.")
        return

    arquivos = [f for f in os.listdir(PASTA_ARQUIVOS) if f.lower().endswith(".pdf")]
    
    for arquivo in arquivos:
        try:
            reader = PdfReader(os.path.join(PASTA_ARQUIVOS, arquivo))
            texto = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            dados = processar_texto_multiplas_categorias(texto, arquivo)
            if dados: resultados_gerais.extend(dados)
        except Exception as e:
            print(f"Erro em {arquivo}: {e}")

    if resultados_gerais:
        df = pd.DataFrame(resultados_gerais)
        gerar_graficos_comparativos(df)
        df.to_excel("Analise_Final_Consolidada.xlsx", index=False)
        print("\n✅ Concluído! Foram gerados 3 arquivos de imagem (.png) e 1 Excel.")
    else:
        print("Nenhum dado encontrado.")

if __name__ == "__main__":
    iniciar_processamento()
