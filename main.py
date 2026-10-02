# ponte_bt.py
# Lê dados da porta COM do Bluetooth e repassa via UDP pro GameMaker

import serial
import socket
import time
import serial.tools.list_ports

# ============ CONFIGURAÇÃO ============
# Porta COM virtual criada pelo Windows após parear o Bluetooth
# Veja em Gerenciador de Dispositivos -> Portas (COM e LPT)
# Normalmente é a que tem "Outgoing" no nome
PORTA_BT = "COM5"        # troque pelo número real #COM3
BAUD_BT  = 9600       # esp32 115200

# Endereço onde o GameMaker vai escutar
GM_HOST = "127.0.0.1"
GM_PORT = 9999
# ======================================

def listar_portas():
    """Lista todas as portas seriais disponíveis, pra você achar a do Bluetooth"""
    portas = serial.tools.list_ports.comports()
    print("Portas disponíveis:")
    for p in portas:
        print(f"  {p.device} - {p.description}")
    return [p.device for p in portas]

def main():
    print("=== Ponte Bluetooth -> UDP ===")
    listar_portas()
    print()
    
    # Abre a porta Bluetooth
    try:
        ser = serial.Serial(PORTA_BT, BAUD_BT, timeout=1)
        print(f"[OK] Porta {PORTA_BT} aberta @ {BAUD_BT}")
    except Exception as e:
        print(f"[ERRO] Não consegui abrir {PORTA_BT}: {e}")
        print("Dica: confira o nome da porta COM do Bluetooth no Gerenciador de Dispositivos")
        return
    
    # Socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[OK] Destino UDP: {GM_HOST}:{GM_PORT}")
    print("Aguardando dados...\n")
    
    buffer = ""
    try:
        while True:
            if ser.in_waiting > 0:
                dados = ser.read(ser.in_waiting)
                try:
                    texto = dados.decode('utf-8', errors='ignore')
                except:
                    texto = str(dados)
                
                buffer += texto
                
                # Processa linha por linha (a ESP32 manda com \n no fim)
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    linha = linha.strip()
                    if linha:
                        print(f"[recebido] {linha}")
                        # Repassa pro GameMaker
                        try:
                            sock.sendto(linha.encode('utf-8'), (GM_HOST, GM_PORT))
                        except Exception as e:
                            print(f"[falha UDP] {e}")
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[saindo]")
    finally:
        ser.close()
        sock.close()

if __name__ == "__main__":
    main()