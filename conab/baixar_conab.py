import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-graos/boletim-da-safra-de-graos?b_start:int=0"

# Ajustando caminhos para respeitar a estrutura de pastas do projeto
PASTA_CONAB = "conab"
PASTA_RAW = os.path.join(PASTA_CONAB, "raw")
ARQUIVO_CONTROLE = os.path.join(PASTA_CONAB, "ultimo_xlsx.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def garantir_pastas():
    """Garante que as pastas do projeto existam antes de salvar os arquivos"""
    if not os.path.exists(PASTA_RAW):
        os.makedirs(PASTA_RAW, exist_ok=True)

def carregar_ultimo():
    if os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def salvar_ultimo(nome):
    with open(ARQUIVO_CONTROLE, "w", encoding="utf-8") as f:
        f.write(nome)

def baixar_arquivo(url, destino):
    resposta = requests.get(url, headers=HEADERS, stream=True)
    resposta.raise_for_status()

    with open(destino, "wb") as arquivo:
        for bloco in resposta.iter_content(8192):
            arquivo.write(bloco)

    print(f"Arquivo salvo com sucesso em: {destino}")

def encontrar_planilha():
    print("Verificando site da CONAB...")

    resposta = requests.get(URL, headers=HEADERS)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")
    links = soup.find_all("a", href=True)

    for link in links:
        href = link["href"]

        if "levantamento-safra" in href.lower():
            if not href.startswith("http"):
                href = "https://www.gov.br" + href

            print(f"Analisando página do boletim: {href}")

            pagina = requests.get(href, headers=HEADERS)
            pagina.raise_for_status()

            soup_boletim = BeautifulSoup(pagina.text, "html.parser")

            for arquivo in soup_boletim.find_all("a", href=True):
                href_arquivo = arquivo["href"]

                if ".xlsx" in href_arquivo.lower():
                    if not href_arquivo.startswith("http"):
                        href_arquivo = "https://www.gov.br" + href_arquivo

                    nome = href_arquivo.split("/")[-1]
                    return nome, href_arquivo

    return None, None

def main():
    # Garante que a estrutura conab/raw/ exista localmente ou no servidor
    garantir_pastas()

    nome_arquivo, url_xlsx = encontrar_planilha()

    if not url_xlsx:
        print("Nenhuma planilha XLSX encontrada.")
        return

    ultimo = carregar_ultimo()

    if nome_arquivo == ultimo:
        print(f"Nenhuma atualização encontrada. O último arquivo já era: {nome_arquivo}")
        return

    print(f"\nNova planilha encontrada: {nome_arquivo}")

    # MUDANÇA CRUCIAL: Agora salva dentro do próprio repositório (conab/raw/)
    caminho_destino = os.path.join(PASTA_RAW, "Boletim_Safra_Graos.xlsx")

    print("Iniciando download...")
    baixar_arquivo(url_xlsx, caminho_destino)

    salvar_ultimo(nome_arquivo)
    print("\nProcesso de download concluído!")

if __name__ == "__main__":
    main()