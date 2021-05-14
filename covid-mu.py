import requests
from bs4 import BeautifulSoup as soup
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import csv
import pandas as pd

hoje = datetime.today()
inicio = datetime(2020, 5, 19)

intervalo = pd.date_range(inicio, hoje)

datas = list()
dose1 = list()
dose2 = list()
conf = list()
ativ = list()
obt = list()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51'}
url = 'https://muriae.mg.gov.br/coronavirus2/'

request = requests.get(url, headers=headers)
page_soup = soup(request.content, 'html.parser')

conteudo = page_soup.body.div.text.split()

for palavra in conteudo:
    if palavra == 'Epidemiológico':
        data = conteudo.index(palavra)
        string = conteudo[data + 2][0:10]
        d_type = datetime.strptime(string, '%d/%m/%Y')
        datas.append(d_type)
        conteudo.pop(data)
    elif palavra == 'Epidemiológico-':
        data = conteudo.index(palavra)
        string = conteudo[data + 1][0:10]
        d_type = datetime.strptime(string, '%d/%m/%Y')
        datas.append(d_type)
        conteudo.pop(data)
    elif palavra == 'confirmados:':
        confirmados = conteudo.index(palavra)
        inteiro = int(conteudo[confirmados + 1].replace('.',''))
        conf.append(inteiro)
        conteudo.pop(confirmados)
    elif palavra == 'covid-19:':
        confirmados = conteudo.index(palavra)
        inteiro = int(conteudo[confirmados + 1].replace('.',''))
        conf.append(inteiro)
        conteudo.pop(confirmados)
    elif palavra == 'ativos:':
        ativos = conteudo.index(palavra)
        ativ.append(int(conteudo[ativos + 1].replace('Pacientes','')))
        conteudo.pop(ativos)
    elif 'Óbitos:' in palavra:
        obitos = conteudo.index(palavra)
        obt.append(int(conteudo[obitos + 1].replace('Investigados', '')))
        conteudo.pop(obitos)
    elif palavra == 'dose:':
        dose = conteudo.index(palavra)
        dose1.append(int(conteudo[dose + 1].replace('Vacinados', '').replace('.','')))
        conteudo.pop(dose)
    elif palavra == 'doses:':
        dose = conteudo.index(palavra)
        dose2.append(int(conteudo[dose + 1].replace('PACIENTESTotal', '').replace('.','')))
        conteudo.pop(dose)
    else:
        pass

with open('covid-muriae.csv', 'r', encoding='utf8') as file:
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:

        data = row['\ufeffdata']
        d_type = datetime.strptime(data, '%d/%m/%Y')
        datas.append(d_type)

        dose1.append(int(row['dose 1']))
        dose2.append(int(row['dose 2']))
        conf.append(int(row['casos_totais']))
        ativ.append(int(row['casos_ativos']))
        obt.append(int(row['óbitos']))

d = {'Data': datas, 'Dose 1': dose1, 'Dose 2': dose2,
     'Casos Totais': conf, 'Casos Ativos': ativ, 'Óbitos': obt}

df = pd.DataFrame(data=d)
pd.set_option('display.max_rows', len(df))

d2 = {'Data': intervalo}
df2 = pd.DataFrame(data=d2)
pd.set_option('display.max_rows', len(df2))


joined = pd.merge(df2, df, on='Data', how='left').fillna(0)

joined[['Dose 1', 'Dose 2', 'Casos Totais', 'Casos Ativos', 'Óbitos']] = \
joined[['Dose 1', 'Dose 2', 'Casos Totais', 'Casos Ativos', 'Óbitos']].astype('int')


c = 1
nao_zero = int()
while True:

    for i, row in enumerate(joined.values):
        if row[c] != 0:
            nao_zero = row[c]
        else:
            if joined.loc[i, joined.columns[0]] != hoje.date():
                joined.loc[i, joined.columns[c]] = nao_zero
            else:
                joined.drop(i, inplace=True)
    else:
        c += 1
        nao_zero = int()
        if c == len(joined.columns):
            break

joined['Casos Diários'] = joined['Casos Totais'].diff().fillna(0).astype('int')
joined['Óbitos Diários'] = joined['Óbitos'].diff().fillna(0).astype('int')

pd.set_option('display.max_rows', len(joined.values))
pd.set_option('display.max_columns', len(joined.columns))

print(joined)

#joined.to_csv('C:/Users/GCPeppe/Documents/covid-muriae-auto.csv', encoding='latin-1', sep=';')




def plotar_casosVSimun(save=False, show=True):
    from numpy import max
    plt.figure(figsize=(1080/600, 1080/600), dpi=600)
    plt.plot(joined['Data'], joined['Dose 1'], color='green', linewidth=0.5)
    plt.plot(joined['Data'], joined['Dose 2'], color='green', linewidth=0.5)
    plt.plot(joined['Data'],joined['Casos Totais'], color='blue', linewidth=0.5)
    plt.subplots_adjust(top=0.86, bottom=0.1, left=0.15, right=0.96)
    plt.xticks(joined['Data'][::60], fontsize=2.5, rotation=20, y=0.04)
    plt.yticks(range(0, max(dose1), 800), fontsize=3, x=0.03)
    plt.ylabel('População', fontsize=6, labelpad=0.1)
    plt.title('Casos Totais vs Doses aplicadas em Muriaé \n'
              'segundo os boletins epidemiológicos da \n'
              'Prefeitura de Muriaé', fontsize=4, y=0.96)

    if save == True:
        plt.savefig('C:/Users/GCPeppe/Pictures/ativos-vs-imunizados.png', dpi=600)
    else:
        pass

    if show == True:
        plt.show()
    else:
        pass

def plotar_casosAtivos(save=False, show=True):
    from numpy import max

    plt.figure(figsize=(1080/600, 1080/600), dpi=600)
    plt.plot(joined['Data'], joined['Casos Ativos'], color='orange', linewidth=0.5)
    plt.subplots_adjust(top=0.86, bottom=0.1, left=0.15, right=0.96)
    plt.yticks(range(0, max(joined['Casos Ativos']), 45), fontsize=3, x=0.03)
    plt.xticks(joined['Data'][::60], fontsize=2.5, rotation=20, y=0.04)
    plt.ylabel('Casos Ativos', fontsize=6, labelpad=0.48)
    plt.title('Evolução dos Casos Ativos de COVID-19 em Muriaé \n '
          'segundo os boletins epidemiológicos \n da '
          'Prefeitura de Muriaé', fontsize=4, y=0.96)


    if save == True:
        plt.savefig('C:/Users/GCPeppe/Pictures/casos_ativos.png', dpi=600)
    else:
        pass

    if show == True:
        plt.show()
    else:
        pass

def plotar_obitos(save=False, show=True):
    from numpy import max

    plt.figure(figsize=(1080/600, 1080/600), dpi=600)
    plt.bar(joined['Data'], joined['Óbitos Diários'], color='red', width=1)
    plt.subplots_adjust(top=0.86, bottom=0.1, left=0.15, right=0.96)
    plt.yticks(range(0, max(joined['Óbitos Diários']) + 1), fontsize=3, x=0.02)
    plt.xticks(joined['Data'][::60], fontsize=2.5, rotation=20, y=0.04)
    plt.ylabel('Óbitos Diários', fontsize=6, labelpad=0.48)
    plt.title('Evolução dos Óbitos por COVID-19 em Muriaé \n '
          'segundo os boletins epidemiológicos \n da '
          'Prefeitura de Muriaé', fontsize=4, y=0.96)


    if save == True:
        plt.savefig('C:/Users/GCPeppe/Pictures/covid_obitos.png', dpi=600)
    else:
        pass

    if show == True:
        plt.show()
    else:
        pass

def plotar_casos_diarios(save=False, show=True):
    from numpy import max

    plt.figure(figsize=(1080/600, 1080/600), dpi=600)
    plt.bar(joined['Data'], joined['Casos Diários'], color='blue', width=1)
    plt.subplots_adjust(top=0.86, bottom=0.1, left=0.15, right=0.96)
    plt.yticks(range(0, max(joined['Casos Diários']), 20), fontsize=3, x=0.02)
    plt.xticks(joined['Data'][::60], fontsize=2.5, rotation=20, y=0.04)
    plt.ylabel('Casos Diários', fontsize=6, labelpad=0.48)
    plt.title('Evolução dos Óbitos por COVID-19 em Muriaé \n '
          'segundo os boletins epidemiológicos \n da '
          'Prefeitura de Muriaé', fontsize=4, y=0.96)


    if save == True:
        plt.savefig('C:/Users/GCPeppe/Pictures/casos_diarios.png', dpi=600)
    else:
        pass

    if show == True:
        plt.show()
    else:
        pass

#plotar_casosAtivos()
#plotar_casosVSimun()
plotar_obitos()
#plotar_casos_diarios()
