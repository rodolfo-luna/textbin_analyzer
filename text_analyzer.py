from bs4 import BeautifulSoup
import requests
import re
import nltk
from collections import Counter
from textblob import TextBlob
from deep_translator import GoogleTranslator
import json 
nltk.download('stopwords')
nltk.download('punkt')

class ExtraiDados:

    def __init__(self, url: str):
        self.url = url

    def acessa_url(self):
        '''
        Acessa a página.
        :param url: Página a ser acessada.
        :return: Texto e códigos HTML da página.
        '''
        pagina = requests.get(self.url)
        pagina = pagina.text

        return pagina
    
    def converte_para_soup(self, pagina):
        '''
        Converte os textos extraídos da página para um objeto BeautifulSoup.
        :param pagina: Textos e códigos HTML da página carregada.
        :return: Objeto BeautifulSoup.
        '''
        soup = BeautifulSoup(pagina, 'html.parser')

        return soup

class TrataTextos:

    def extrai_emails(self, texto: str):
        '''
        Extrai todos os e-mails do texto.
        :param texto: Texto em formato string.
        :return: Lista com os e-mails extraídos do texto.
        '''
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', texto)

        return emails

    def extrai_usernames(self, lista_emails: list):
        '''
        Extrai os usernames da lista de e-mails.
        :param lista_emails: Lista com os e-mails extraídos do texto.
        :return: Lista dos usernames.
        '''
        usernames = [x.split('@')[0] for x in lista_emails]

        return usernames

    def extrai_dominios(self, lista_emails: list):
        '''
        Extrai os domínios da lista de e-mails.
        :param lista_emails: Lista com os e-mails extraídos do texto.
        :return: Lista dos domínios.
        '''
        dominios = [x.split('@')[1] for x in lista_emails]

        return dominios

    def extrai_dominios(self, lista_emails: list):
        '''
        Extrai os domínios da lista de e-mails.
        :param lista_emails: Lista com os e-mails extraídos do texto.
        :return: Lista dos domínios.
        '''
        dominios = [x.split('@')[1] for x in lista_emails]

        return dominios

    def contagem_dominios(self, dominios: list):
        '''
        Conta a quantidade de repetições dos domínios da lista.
        :param dominios: Lista com os domínios dos e-mails.
        :return: Listas aninhadas com os domínios da lista e a quantidade de vezes que eles se repetem.
        '''
        contagem = [[x,dominios.count(x)] for x in set(dominios)]

        return contagem

    def remove_stopwords(self, texto: str):
        '''
        Remove os stopwords do texto.
        :param texto: Texto extraído do site.
        :return: Lista das palavras do texto sem os stopwords.
        '''
        stopwords = nltk.corpus.stopwords.words('portuguese')
        tokens = nltk.word_tokenize(texto)
        texto_sem_stopwords = [palavra for palavra in tokens if palavra not in stopwords]

        return texto_sem_stopwords

    def remove_pontuacao(self, texto: list):
        '''
        Remove as pontuações do texto.
        :param texto: Lista com as palavras do texto sem as stopwords.
        :return: Lista com as palavras do texto sem pontuação.
        '''
        palavras = [palavra for palavra in texto if palavra.isalpha()]

        return palavras

    def palavras_mais_frequentes(self, texto: list):
        '''
        Conta a frequência das palavras e retornas as 8 mais frequentes no texto.
        :param texto: Lista com as palavras do texto sem as stopwords e pontuações.
        :return: Lista aninhada com as 8 palavras mais frequentes e suas frequências no texto. 
        '''
        texto_sem_pontuaca = self.remove_pontuacao(texto)
        texto_sem_pontuaca = [x.lower() for x in texto_sem_pontuaca]
        contador = Counter(texto_sem_pontuaca)
        mais_frequentes = contador.most_common(8)

        return mais_frequentes

    def converte_texto_para_ingles(self, texto: str):
        '''
        Traduz o texto para inglês.
        :param texto: Texto em português.
        :return: Texto traduzido para o inglês.
        '''
        texto_em_ingles_parte_1 = GoogleTranslator(source='portuguese', target='english').translate(texto[:4999]) # limitação de caracteres da API.
        texto_em_ingles_parte_2 = GoogleTranslator(source='portuguese', target='english').translate(texto[5000:])
        texto_em_ingles = texto_em_ingles_parte_1 + texto_em_ingles_parte_2

        return texto_em_ingles

    def analise_de_sentimento(self, texto: str):
        '''
        Faz a análise de sentimento e retorna a polaridade.
        :param texto: Texto em inglês.
        :return: A polaridade e o score.
        '''
        score = TextBlob(texto).polarity
        if score < 0:
            return 'Negativo', score
        elif score == 0:
            return 'Neutro', score
        else:
            return 'Positivo', score

if __name__ == "__main__":
    extrator = ExtraiDados('https://pt.textbin.net/raw/qjgvaozdh2')
    driver = extrator.acessa_url()
    texto = str(extrator.converte_para_soup(driver))

    dados = TrataTextos()
    emails = dados.extrai_emails(texto)
    usernames = dados.extrai_usernames(emails)

    dominios = dados.extrai_dominios(emails)

    contagem = dados.contagem_dominios(dominios)

    texto_sem_stopwords = dados.remove_stopwords(texto)

    texto_em_ingles = dados.converte_texto_para_ingles(texto)    
    polaridade, score = dados.analise_de_sentimento(texto_em_ingles)

    texto_infos = {"usernames" : usernames,
                    "dominios" : dominios,
                    "frequencia dos dominios" : contagem,
                    "8 palavras mais frequentes" : dados.palavras_mais_frequentes(texto_sem_stopwords),
                    "polaridade" : polaridade,
                    "score" : score,
                    "Tokens" : str(len(texto_sem_stopwords)),
                    "Palavras" : str(len(re.findall(r'\w+', texto))),
                    "Caracteres" : str(len(texto))}

    infos_json = json.dumps(texto_infos, indent = 4)

    with open("texto_infos.json", "w") as outfile:
        json.dump(texto_infos, outfile)