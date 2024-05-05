import click
import sys
import time
import requests
import logging
import warnings
import re
from colorama import init, Fore, Style
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Inicializar colorama para suportar estilos de texto no terminal
init()

logging.getLogger('bs4').setLevel(logging.ERROR)
# Suprimir os avisos emitidos pelo módulo de warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# Configuração de logging
logging.basicConfig(filename='mail_finder.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes
TIMEOUT = 5

# Variáveis globais para rastrear URLs para rastrear e URLs rastreadas
TO_CRAWL = []
CRAWLED = set()

# Função para exibir uma falsa barra de carregamento
def loading_bar():
    print("\nIniciando Mail Finder...")
    for _ in range(1):
        print("Bootando ", end="")
        for _ in range(10):
            print("█", end="", flush=True)
            time.sleep(0.2)
        print()

def is_valid_url(url):
    """Verifica se a URL fornecida está em um formato válido."""
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)

def is_directory(url):
    """Verifica se a URL fornecida é um diretório."""
    return url.endswith('/')

@click.command()
@click.option('--open-client', is_flag=True, help='Abrir o cliente')
@click.option('--possible-emails', is_flag=True, help='Exibir possíveis e-mails da URL especificada')
def main(open_client, possible_emails):
    if open_client:
        print("Abrindo o cliente...")
        # Aqui você pode adicionar o código para abrir o cliente desejado
        # Por exemplo, abrir um navegador web com uma interface gráfica para inserir a URL e a wordlist
    else:
        print_intro()
        url = prompt_for_url()
        if not is_valid_url(url):
            print("URL inválida. Certifique-se de incluir o esquema (http:// ou https://) e o nome do host.")
            logging.error("URL inválida fornecida: %s", url)
            sys.exit(1)
        elif urlparse(url).scheme != 'https':
            print("AVISO: Recomenda-se usar HTTPS para maior segurança.")
            logging.warning("URL não usa HTTPS: %s", url)
        loading_bar()
        TO_CRAWL.append(url)
        crawl(url, possible_emails)

def print_intro():
    print(Fore.RED + Style.BRIGHT + """
   _____                   _              _____            _      _         
  / ____|                 | |            / ____|          (_)    | |        
 | |     _ __ _____      _| | ___ _ __  | (___   ___   ___ _  ___| |_ _   _ 
 | |    | '__/ _ \ \ /\ / / |/ _ \ '__|  \___ \ / _ \ / __| |/ _ \ __| | | |
 | |____| | | (_) \ V  V /| |  __/ |     ____) | (_) | (__| |  __/ |_| |_| |
  \_____|_|  \___/ \_/\_/ |_|\___|_|    |_____/ \___/ \___|_|\___|\__|\__, |
                                                                       __/ |
                                                                      |___/ 

 """)
    print(Fore.CYAN + "            BY: Nekolial")
    print(Fore.BLUE + "            GitHub: " + Style.RESET_ALL + "https://github.com/Nekolial\n")
    print(Fore.MAGENTA)
    print("A humanidade está presa numa prisão. Vivendo em um mundo que não entende'")
    print("Você é uma fraude. Um holograma. A raiva de outra pessoa.")
    print("01010101010101010101010101010101010101010101010101010101.")
    print("O mundo é uma ilusão. O que fazemos nela é o que importa.")
    print("Tempos empolgantes no mundo agora, tempos empolgantes....")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

def prompt_for_url():
    return click.prompt('\nPor favor, insira a URL alvo:', type=str)

def request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as error:
        print("Error: {}".format(error))
        return None

def get_links(html):
    links = []
    try:
        soup = BeautifulSoup(html, "html.parser")
        tags_a = soup.find_all("a", href=True)
        for tag in tags_a:
            link = tag["href"]
            if link.startswith("http") and not is_directory(link):
                links.append(link)
        return links
    except Exception as e:
        print("Error in parsing links:", e)
        return []

def get_emails(html):
    emails = re.findall(r"\b[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Z|a-z]{2,}\b", html)
    return emails

def crawl(url, possible_emails):
    while TO_CRAWL:
        url = TO_CRAWL.pop()
        html = request(url)
        if html:
            links = get_links(html)
            if links:
                for link in links:
                    if is_same_domain(link, url) and link not in CRAWLED and link not in TO_CRAWL:
                        TO_CRAWL.append(link)
            emails = get_emails(html)
            if possible_emails:
                print("Possíveis e-mails encontrados em", url)
                for email in emails:
                    print("Email:", email)
                # Verificar se todos os e-mails relevantes foram encontrados
                if all(email.endswith('@g1.com.br') or email.endswith('@globo.com') for email in emails):
                    print("Todos os e-mails relevantes foram encontrados. Parando a busca.")
                    return
            else:
                for email in emails:
                    print("Email encontrado:", email)
                # Verificar se todos os e-mails relevantes foram encontrados
                if all(email.endswith('@g1.com.br') or email.endswith('@globo.com') for email in emails):
                    print("Todos os e-mails relevantes foram encontrados. Parando a busca.")
                    return
        else:
            for email in emails:
                print("Email encontrado:", email)
        CRAWLED.add(url)
    else:
        print("Operação concluída. Excluindo logs...")

def is_same_domain(link, base_url):
    """Verifica se o link pertence ao mesmo domínio que o URL base."""
    parsed_link = urlparse(link)
    parsed_base_url = urlparse(base_url)
    return parsed_link.netloc == parsed_base_url.netloc


if __name__ == "__main__":
    main()
