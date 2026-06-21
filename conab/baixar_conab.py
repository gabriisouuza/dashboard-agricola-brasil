import requests
from bs4 import BeautifulSoup
import os


URL = "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-graos/boletim-da-safra-de-graos?b_start:int=0"

ARQUIVO_CONTROLE = "ultimo_xlsx.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

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

    print(f"Arquivo salvo em:\n{destino}")

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

            print(f"Analisando: {href}")

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

    nome_arquivo, url_xlsx = encontrar_planilha()

    if not url_xlsx:
        print("Nenhuma planilha XLSX encontrada.")
        return

    ultimo = carregar_ultimo()

    if nome_arquivo == ultimo:
        print("Nenhuma atualização encontrada.")
        return

    print("\nNova planilha encontrada:")
    print(nome_arquivo)

    pasta_downloads = os.path.join(
        os.path.expanduser("~"),
        "Downloads"
    )

    caminho_destino = os.path.join(
        pasta_downloads,
        "Boletim_Safra_Graos.xlsx"
    )

    baixar_arquivo(url_xlsx, caminho_destino)

    salvar_ultimo(nome_arquivo)

    print("\nDownload concluído com sucesso!")

if __name__ == "__main__":
    main()

