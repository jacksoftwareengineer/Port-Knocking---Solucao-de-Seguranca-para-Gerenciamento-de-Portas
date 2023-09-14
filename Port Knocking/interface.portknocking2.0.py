from tkinter import *
from PIL import Image, ImageTk
import pandas as pd
import os
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage
import time


arquivos = os.listdir()

if 'hosts.xlsx' in arquivos:
    df = pd.read_excel('hosts.xlsx')
    df = df.drop('Unnamed: 0', axis=1)

else:
     df = pd.DataFrame({'IP': [None, None, None, None, None, None, None, None, None, None],
                       'PORT 1': [None, None, None, None, None, None, None, None, None, None],
                       'PORT 2': [None, None, None, None, None, None, None, None, None, None],
                       'PORT 3': [None, None, None, None, None, None, None, None, None, None],
                       'PORT 4': [None, None, None, None, None, None, None, None, None, None]})

conjunto = set()

def create_background_image(image_path, width, height):
    # Abre a imagem usando o Pillow (PIL)
    image = Image.open(image_path)
    # Redimensiona a imagem para o tamanho desejado com suavização
    image = image.resize((width, height))
    # Converte a imagem para o formato compatível com Tkinter
    tk_image = ImageTk.PhotoImage(image)
    return tk_image

# Caminho para a imagem PNG
image_path_background = "BG-PORT-KNOCKING.png"

# Largura e altura da janela
janela_width_background = 500
janela_height_background = 300

def on_entry_click_ip(event):
    if entry_ip.get() == "Ip Here":
        entry_ip.delete(0, "end")
        entry_ip.insert(0, "")
        entry_ip.config(fg='black')  # Defina a cor do texto para preto quando o usuário começa a digitar

def on_focusout_ip(event):
    if entry_ip.get() == "":
        entry_ip.insert(0, "Ip Here")
        entry_ip.config(fg='grey')  # Defina a cor do texto para cinza quando não estiver em foco

def on_entry_click_port(event):
    if entry_ports.get() == "Ports":
        entry_ports.delete(0, "end")
        entry_ports.insert(0, "")
        entry_ports.config(fg='black')  # Defina a cor do texto para preto quando o usuário começa a digitar

def on_focusout_port(event):
    if entry_ports.get() == "":
        entry_ports.insert(0, "Ports")
        entry_ports.config(fg='grey')  # Defina a cor do texto para cinza quando não estiver em foco

def adicionar_hosts():
    global df
    novo_ip = entry_ip.get()
    novas_ports = entry_ports.get()
    novas_ports = novas_ports.split(',')
    entry_ip.delete(0, END)
    entry_ports.delete(0, END)
    for i, linha in df.iterrows():
        if linha.isnull().all():
            df.loc[i, 'IP'] = novo_ip
            for j, porta in enumerate(novas_ports):
                df.loc[i, f'PORT {j + 1}'] = int(porta)
            return True

def hosts(row):
    global df
    global conjunto
    ip = row['IP']
    portas = [str(row[col]) for col in row.index if col != 'IP' and row[col] is not None]
    # Verifique se a lista de portas está vazia e retorne apenas o IP se estiver
    if not portas:
        return ip
    conjunto.add(f'Host: {ip}: {", ".join(portas)}')
    if 'Host: nan: nan, nan, nan, nan' in conjunto:
        conjunto.remove('Host: nan: nan, nan, nan, nan')
    texto_var = StringVar()
    texto_var.set(conjunto)
    label_hosts_cadastrados = Label(janela, width=15, height=1, bg='white', relief='flat', text="Host's Cadastrados",
                                    font=('Ivy 10 bold'))
    label_hosts_cadastrados.place(x=265, y=15)
    label = Label(janela, bg='white', textvariable=texto_var, wraplength=220)  # Defina wraplength conforme necessário
    label.place(x=180, y=40)


def iniciar():
    global df
    janela_info = scrolledtext.ScrolledText(janela, width=38, height=7)
    janela_info.place(x=170, y=11)
    button_hosts.configure(state='disable')
    button_add_hosts.configure(state='disable')
    buttom_iniciar.configure(state='disable')
    entry_ip.configure(state='disable')
    entry_ports.configure(state='disable')
    for index, row in df.iterrows():
        ip = row['IP']
        if pd.notna(ip):
            for col in df.columns[1:]:
                port = row[col]
                if pd.notna(port) and isinstance(port, (int, float)):
                    try:
                        port = int(port)
                        time.sleep(1)
                        mensagem = f'Batendo na porta {port} para o IP: {ip}'
                        janela_info.insert(tk.END, mensagem + "\n")
                        janela_info.update_idletasks()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1)  # Define um timeout de 1 segundo para a conexão
                        s.connect((ip, port))
                        s.close()

                    except socket.error:
                        pass
            janela_info.insert(tk.END, f'Concluído para o IP: {ip}' + "\n")
            janela_info.update_idletasks()


def iniciar_portknocking():
    # Cria e inicia uma nova thread para executar o port knocking
    thread = threading.Thread(target=iniciar)
    thread.start()

def backup():
    global df
    df.to_excel('hosts.xlsx')


janela = Tk()
janela.title("Port Knocking")
janela.geometry('500x300')
janela.iconphoto(False, PhotoImage(file='port knocking.png'))

# Crie uma label para exibir a imagem como plano de fundo
background_image = create_background_image(image_path_background, janela_width_background, janela_height_background)
background_label = Label(janela, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

button_hosts = Button(janela, command=lambda : df.apply(hosts, axis=1).tolist(), width=10, height=1, bg='orange', text="Host's", font=('Helveltica 15 bold'), fg='white')
button_hosts.place(x=20, y=50)

label_dados = Label(janela, width=38, height=7, bg='white', relief='flat', text='', font=('Ivy 10 bold'))
label_dados.place(x=170, y=11)

button_add_hosts = Button(janela, command=adicionar_hosts, width=10, height=1, bg='orange', text="Add Host's", font=('Helveltica 15 bold'), fg='white')
button_add_hosts.place(x=20, y=150)

icon = PhotoImage(file="save.png")
button_backup = Button(janela, command=backup, width=38, height=30, bg='orange', image=icon)
button_backup.place(x=170, y=233)

entry_ip = Entry(janela, width=10, bg='white', font=('Helveltica 20 bold'), fg='black')
entry_ip.insert(0, "Ip Here")
entry_ip.bind("<FocusIn>", on_entry_click_ip)
entry_ip.bind("<FocusOut>", on_focusout_ip)
entry_ip.place(x=170, y=150)

entry_ports = Entry(janela, width=9, bg='white', font=('Helveltica 20 bold'), fg='black')
entry_ports.insert(0, "Ports")
entry_ports.bind("<FocusIn>", on_entry_click_port)
entry_ports.bind("<FocusOut>", on_focusout_port)
entry_ports.place(x=340, y=150)

buttom_iniciar = Button(janela, command=iniciar_portknocking, width=20, height=1, bg='orange', text='INICIAR', font=('Helveltica 15 bold'), fg='white')
buttom_iniciar.place(x=230, y=230)

# Restringir o redimensionamento da janela
janela.resizable(width=False, height=False)

janela.mainloop()
