from iqoptionapi.stable_api import IQ_Option
import time
from configobj import ConfigObj
import json, sys
from datetime import datetime

#Arquivo Config
config = ConfigObj('config.txt')
email = config['LOGIN']['email']
senha = config['LOGIN']['senha']
tipo = config['AJUSTES']['tipo']
valor_entrada = config['AJUSTES']['valor_entrada']



print('Iniciando Conexão com a IQOption')
API = IQ_Option(email,senha)

# Função para conectar na IQOPTION
check, reason = API.connect()
if check:
    print('\nConectado com sucesso')
else:
    if reason == '{"code":"invalid_credentials","message":"You entered the wrong credentials. Please ensure that your login/password is correct."}':
        print('\nEmail ou senha incorreta')
        sys.exit()
        
    else:
        print('\nHouve um problema na conexão')

        print(reason)
        sys.exit()

### Função para Selecionar demo ou real ###
while True:
    escolha = input('\nSelecione a conta em que deseja conectar: demo ou real  - ')
    if escolha == 'demo':
        conta = 'PRACTICE'
        print('Conta demo selecionada')
        break
    if escolha == 'real':
        conta = 'REAL'
        print('Conta real selecionada')
        break
    else:
        print('Escolha incorreta! Digite demo ou real')
        
API.change_balance(conta)

par = input('\n>> Digite o ativo que você deseja operar: ').upper()
timeframe = 60
qnt_velas = 5
tempo = time.time()
minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S')[1:])
minutos = float(datetime.now().strftime('%M.%S')[1:])

#Converter tempo em formato padrão
def converter(x):
    y = datetime.fromtimestamp(x)
    time = y.strftime('%d/%m/%Y %H:%M:%S')
    return time

#Definir o tempo de espera para entrar no loop principal apenas com o início de uma nova vela

def esperar_execução(minutos, tempo_de_espera=0.60):
    minutos = minutos % 1
    tempo_de_espera = tempo_de_espera - minutos
    return minutos, tempo_de_espera

minutos_atuais = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S')[1:])
resultado_espera = esperar_execução(minutos_atuais)
tempo_de_espera_atual = resultado_espera[1]

tempo_de_espera_atual = int(tempo_de_espera_atual * 100)
time.sleep(tempo_de_espera_atual)

velas = API.get_candles(par, timeframe, qnt_velas, tempo)

#Função para compra
def compra(ativo,valor,direcao,exp,tipo):
    if tipo == 'digital':
        check, id = API.buy_digital_spot_v2(ativo,valor,direcao,exp)
    else:
        check, id = API.buy(valor,ativo,direcao,exp)


    if check:
        print('Ordem executada ',id)

        while True:
            time.sleep(0.1)
            status , resultado = API.check_win_digital_v2(id) if tipo == 'digital' else API.check_win_v4(id)

            if status:
                if resultado > 0:
                    print('WIN', round(resultado,2))
                elif resultado == 0:
                    print('EMPATE', round(resultado,2))
                else:
                    print('LOSS', round(resultado,2))
                break

    else:
        print('erro na abertura da ordem,', id)

while True:
    tempo = time.time()
    velas = API.get_candles(par, timeframe, qnt_velas, tempo)

    vela_1 = velas[0]
    vela_2 = velas[1]
    vela_3 = velas[2]
    vela_4 = velas[3]
    vela_5 = velas[4]
    #Print velas atuais (Opcional)
    print(converter(vela_1['from']))
    print(converter(vela_2['from']))
    print(converter(vela_3['from']))
    print(converter(vela_4['from']))
    print(converter(vela_5['from']))
    for i in velas:
        print(converter(i['from']) ,'valor máximo', (i['max']),'valor mínimo', (i['min']))
                    
    #fractal verificação
    if vela_3['max']> vela_2['max'] and vela_3['max']> vela_1['max'] and vela_4['max']< vela_3['max'] and vela_5['min']<vela_4['min']:#fractal de baixa para entrar vendido
        print('fractal de baixa formado')
        
        ativo = par
        valor = valor_entrada
        direcao = 'put'
        exp = 1
        tipo = 'binaria'
        compra(ativo, valor, direcao, exp, tipo)
        
    elif vela_3['min']< vela_2['min'] and vela_3['min']< vela_1['min'] and vela_4['min']> vela_3['min'] and vela_5['max']>vela_4['max']: #fractal de compra para entrar comprado
            print('fractal de alta formado')
            
            ativo = par
            valor = valor_entrada
            direcao = 'call'
            exp = 1
            tipo = 'binaria'
            compra(ativo, valor, direcao, exp, tipo)
    else:
        print('Nenhum fractal formado')
             
    time.sleep(60)
    continue


