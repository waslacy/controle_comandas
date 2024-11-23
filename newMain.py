from customtkinter import *
from PIL import Image
from tkinter import messagebox
import ctypes
import time
import serial
import threading
import json
from datetime import datetime
ctypes.windll.shcore.SetProcessDpiAwareness(2)

porta_ard = ""
try:
    with open("config.json", "r") as file:
        temp_data = json.load(file)
        porta_ard = temp_data["porta_arduino"]["porta"]
except (FileNotFoundError, json.JSONDecodeError):
    print("Arquivo de configuração não encontrado")

popup_open = False
print(porta_ard)
ser = serial.Serial(porta_ard, 9600, timeout=1)
    
intervalo = 0
alerta = 0
bip = True
mesas = []
garcom_btn = []

def get_config_info():
    global intervalo, alerta, bip, mesas, garcom_btn

    try:
        with open("config.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Arquivo de configuração não encontrado")
        
    intervalo = data["intervalo"]["tempo"]
    alerta = data["alerta"]["tempo"]
    bip = data["bip"]["bip"]
    mesas = data["mesas"]
    garcom_btn = data["garcom"]



# Função para salvar no JSON em seções específicas
def salvar_em_json(secao, chave, valor):
    try:
        # Carrega o conteúdo atual do arquivo, se existir
        with open("config.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio, inicia com um dicionário vazio
        data = {}    

    if "mesas" in data:
            data["mesas"] = {k: v for k, v in data["mesas"].items() if v != valor}
        
    # Verifica e remove o código se ele existir nos arrays de "garcom"
    if "garcom" in data:
        for k, v in data["garcom"].items():
            if isinstance(v, list) and valor in v:
                data["garcom"][k] = [item for item in v if item != valor]

    # Garante que a seção existe no dicionário
    if secao not in data:
        data[secao] = {}

    # Verifica se é a seção "garcom" e deve armazenar uma lista de valores
    if secao == "garcom":
        if chave not in data[secao]:
            data[secao][chave] = []
        # Adiciona o valor ao array, se ainda não estiver presente
        if valor not in data[secao][chave]:
            data[secao][chave].append(valor)
    else:
        # Para outras seções, como "mesas", armazena chave: valor diretamente
        data[secao][chave] = valor

    # Salva o dicionário atualizado no arquivo
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)






def set_fullscreen(window):
    # Define a janela para tela cheia e remove bordas
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Define o tamanho da janela para o tamanho da tela
    window.geometry(f"{screen_width}x{screen_height}-10+0")
    window.attributes("-fullscreen", True)
    window.bind("<Escape>", lambda e: exit_fullscreen(window))  # Permite sair do fullscreen com Esc

def exit_fullscreen(window):
    # Remove o modo tela cheia e restaura o tamanho da janela
    window.attributes("-fullscreen", False)
    window.state('normal')
    
def center_window(window, width, height):
    # Obtém as dimensões da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = ((screen_width - width) // 2) - 40
    y = ((screen_height - height) // 2) - 40

    # Define o tamanho e a posição da janela
    window.geometry(f"{width}x{height}+{x}+{y}")


# Cria a aplicação
app = CTk(fg_color="#e7e7e7")
app._set_appearance_mode("light")

# Ajusta a janela para usar toda a resolução do monitor
set_fullscreen(app)

fonte = CTkFont(family="Futura", size=180, weight="bold")
fonteMenor = CTkFont(family="Futura", size=100, weight="bold")





def success_popup():
    # Cria uma nova janela secundária (popup)
    popup_success = CTkToplevel(master=app, fg_color="#4c4c4c")
    popup_success.title("Mensagem")
    popup_success.geometry("600x300")

    # Remove as bordas e a barra de título da janela
    popup_success.overrideredirect(True)

    # Centraliza o popup na tela
    screen_width = popup_success.winfo_screenwidth()
    screen_height = popup_success.winfo_screenheight()
    window_width = 600
    window_height = 300

    x_position = int((screen_width / 2) - (window_width / 2))
    y_position = int((screen_height / 2) - (window_height / 2))
    popup_success.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    
    
    # Frame externo para simular a borda
    border_frame_popup_success = CTkFrame(popup_success, corner_radius=20, fg_color="#4c4c4c")
    border_frame_popup_success.pack(fill="both", expand=True, padx=2, pady=2)  # Adiciona preenchimento para simular a borda

    # Frame interno para a cor de fundo
    rounded_frame_popup_success = CTkFrame(border_frame_popup_success, corner_radius=20, fg_color="#e7e7e7")
    rounded_frame_popup_success.pack(fill="both", expand=True)

    # Label dentro do popup com a mensagem
    label = CTkLabel(master=rounded_frame_popup_success, text="Salvo com sucesso!", font=("Arial", 30), text_color="#292b64")
    label.pack(expand=True, fill="both")
    
    # Faz com que o popup apareça na frente e receba o foco
    popup_success.lift()
    popup_success.attributes("-topmost", True)
    popup_success.focus_force()

    
    # Fecha o popup após 1 segundo (1000 ms)
    popup_success.after(1000, popup_success.destroy)
    
    
def fail_popup():
    # Cria uma nova janela secundária (popup)
    popup_fail = CTkToplevel(master=app, fg_color="#4c4c4c")
    popup_fail.title("Mensagem")
    popup_fail.geometry("600x300")

    # Remove as bordas e a barra de título da janela
    popup_fail.overrideredirect(True)

    # Centraliza o popup na tela
    screen_width = popup_fail.winfo_screenwidth()
    screen_height = popup_fail.winfo_screenheight()
    window_width = 600
    window_height = 300

    x_position = int((screen_width / 2) - (window_width / 2))
    y_position = int((screen_height / 2) - (window_height / 2))
    popup_fail.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    
    
    # Frame externo para simular a borda
    border_frame_popup_fail = CTkFrame(popup_fail, corner_radius=20, fg_color="#4c4c4c")
    border_frame_popup_fail.pack(fill="both", expand=True, padx=2, pady=2)  # Adiciona preenchimento para simular a borda

    # Frame interno para a cor de fundo
    rounded_frame_popup_fail = CTkFrame(border_frame_popup_fail, corner_radius=20, fg_color="#e7e7e7")
    rounded_frame_popup_fail.pack(fill="both", expand=True)

    # Label dentro do popup com a mensagem
    label = CTkLabel(master=rounded_frame_popup_fail, text="Algo deu errado!", font=("Arial", 30), text_color="#292b64")
    label.pack(expand=True, fill="both")
    
    # Faz com que o popup apareça na frente e receba o foco
    popup_fail.lift()
    popup_fail.attributes("-topmost", True)
    popup_fail.focus_force()

    
    # Fecha o popup após 1 segundo (1000 ms)
    popup_fail.after(1000, popup_fail.destroy)






def abrir_config():
    config_screen = CTkToplevel(master=app, fg_color="#e7e7e7")
    set_fullscreen(config_screen)
    global popup_open
    popup_open = True
    
    def read_rf_data(id_controle):
        global popup_open, ser
        
        def read_serial():
            print(popup_open)
            while popup_open:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    # Atualiza o label com o valor lido
                    id_controle.configure(text=f"{line}")

        # Executa a leitura serial em uma nova thread para não travar a interface
        thread = threading.Thread(target=read_serial, daemon=True)
        thread.start()
    
    def load_config(intervalo, alerta, bip_save):
        try:
            with open("config.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("não foi possível abrir o arquivo de configuração")
            
        array_opts = [
            ["intervalo", "tempo", intervalo],
            ["alerta", "tempo", alerta],
            ["bip", "bip", bip_save],
            
            ["porta_arduino", "porta", porta]
        ]
        
        for opt in array_opts:
            option = opt[0]
            chave = opt[1]
            el = opt[2]
            
            if option in data:
                valor = data[option][chave]
                
                if option == "bip":
                    bip_val = "✓" if valor else " "
                    el.configure(text=bip_val)
                else:
                    el.insert(0, valor)


    
    # HEADER
    config_frame_header = CTkFrame(master=config_screen, corner_radius=0, fg_color="transparent")
    config_frame_header.pack(fill="both", anchor="n", padx=10, pady=(10, 20))

    logo_img = CTkImage(light_image=Image.open('images/logo.png'), size=(220, 36)) # WidthxHeight

    logo = CTkLabel(master=config_frame_header, text="", image=logo_img)
    logo.place(relx=0, rely=0, anchor="nw", x=10, y=20) 
    

    CTkLabel(master=config_frame_header, text="Configurações", font=("Arial", 50), text_color="#292b64").pack(anchor="n", side="top", pady=(10, 0))
    
    version = CTkLabel(master=config_frame_header, text="v24.1.0", font=("Arial", 18), text_color="#292b64")
    version.place(relx=1, rely=0, anchor="ne", x=-10, y=20)
    
    
    #ID DA MESA
    id_frame = CTkFrame(master=config_screen, corner_radius=0, fg_color="transparent")
    id_frame.pack(anchor="n", fill="x", padx=40, pady=20)
    
    ghost_frame_id = CTkFrame(master=id_frame, corner_radius=0, fg_color="transparent", height=45)
    ghost_frame_id.pack(side="left", fill="x")
    
    true_frame_id = CTkFrame(master=id_frame, corner_radius=0, fg_color="transparent", width=409, height=45)
    true_frame_id.pack(side="right", padx=(20, 182))
    true_frame_id.pack_propagate(False)
    
    #id
    CTkLabel(master=true_frame_id, text="Id: ", text_color="#292b64", font=("Arial", 32)).pack(side="left", anchor="w", padx=(0, 5)) 
    
    #fake input
    id_label_frame = CTkFrame(master=true_frame_id, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, corner_radius=0, height=30)
    id_label_frame.pack(anchor="w", expand=True, fill="x")
    id_controle = CTkLabel(master=id_label_frame, text="Aguardando...", font=("Arial Black", 30), text_color="#4c4c4c")
    id_controle.pack(anchor="w", pady=5, padx=20)
    
    read_rf_data(id_controle)

    #Número mesa
    def salva_n_mesa():
        mesa = n_mesa.get()
        codigo = id_controle.cget("text")
        if mesa != "" and len(codigo) >= 2:
            print(f"Mesa {mesa} recebe o código: {codigo}")
            salvar_em_json("mesas", mesa, codigo)
            success_popup()
        else: 
            fail_popup()
            
    
    mesa_frame = CTkFrame(master=config_screen, fg_color="transparent")
    mesa_frame.pack(anchor="n", pady=(20, 10), fill="x", padx=40)

    # Container principal para cada chamada
    select_frame = CTkFrame(master=mesa_frame, fg_color="transparent", border_color="#4c4c4c", border_width=1, width=653, height=60)
    select_frame.pack(side="left", padx=(0, 20))
    select_frame.pack_propagate(False)
    
    select_center = CTkFrame(master=select_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    select_center.pack(expand=True, fill="both")
    
    select_menu = CTkOptionMenu(master=select_center, values=['Gravar guarda sol', 'Gravar mesa'], fg_color="#d3d4d6", text_color="#24265f", button_color="#d3d4d6", button_hover_color="#d3d4d6", corner_radius=0, font=("Arial", 28))
    select_menu.pack(side="left", anchor="w", pady=20, padx=20, expand=True, fill="both")
    select_menu.set("Gravar guarda sol")
    
    
    input_save_frame = CTkFrame(master=mesa_frame, fg_color="transparent")
    input_save_frame.pack(side="right", expand=True, fill="x", padx=(20, 0))
    
    input_frame = CTkFrame(master=input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    input_frame.pack(side="left", expand=True, anchor="w", fill="both", padx=20)
    
    n_mesa = CTkEntry(master=input_frame, placeholder_text="N° da mesa", font=("Arial Black", 27), text_color="#24265f", fg_color="transparent", justify="center", border_width=0, border_color="none")
    n_mesa.pack(expand=True, fill="both", pady=10, padx=20)
    
    save_frame = CTkFrame(master=input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    save_frame.pack(side="right", anchor="e", padx=(20, 0), fill="y")
    
    save = CTkButton(master=save_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", command=salva_n_mesa)
    save.pack(pady=1, padx=(1,2))
    
    
    
    #BOTÃO GARÇOM
    garcom_btn = ""

    # Função para selecionar o botão e alterar cor de hover
    def seleciona_botao(btn, button_widget):
        global garcom_btn
        
        garcom_btn = btn

        a_btn.configure(fg_color="#d3d4d6", text_color="#4f4f4f")  # Restaura a cor do botão anterior
        b_btn.configure(fg_color="#d3d4d6", text_color="#4f4f4f")  # Restaura a cor do botão anterior
        c_btn.configure(fg_color="#d3d4d6", text_color="#4f4f4f")  # Restaura a cor do botão anterior
        d_btn.configure(fg_color="#d3d4d6", text_color="#4f4f4f")  # Restaura a cor do botão anterior
        
        button_widget.configure(fg_color="#292b64", text_color="#ffffff")  # Define a cor azul para o botão clicado

    def salva_garcom():
        global garcom_btn
        codigo = id_controle.cget("text")
        if garcom_btn != "" and len(codigo) >= 2:
            salvar_em_json("garcom", garcom_btn, codigo)
            success_popup()
        else: 
            fail_popup()
        
    garcom_frame = CTkFrame(master=config_screen, fg_color="transparent")
    garcom_frame.pack(anchor="n", pady=(20, 10), fill="x", padx=40)
    
    label_frame = CTkFrame(master=garcom_frame, fg_color="transparent", width=653, height=100)
    label_frame.pack(side="left", padx=(0, 50))
    CTkLabel(master=label_frame, text="Gravar botão liberação: ", font=("Arial", 30), text_color="#4f4f4f").pack(anchor="w", pady=(10, 0), fill="y")
    
    buttons_frame = CTkFrame(master=garcom_frame, corner_radius=0, height=90, fg_color="transparent")
    buttons_frame.pack(side="right", expand=True, anchor="e", fill="both", padx=(20,0))
    
    save = CTkButton(master=buttons_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", border_color="#4c4c4c", border_width=1, command=salva_garcom)
    save.pack(pady=1, padx=(20,1), side="right", anchor="e")
    d_btn = CTkButton(master=buttons_frame, text="D", text_color="#292b64", font=("Arial Black", 26), corner_radius=80, width=60, height=60,  fg_color="#d3d4d6", hover_color="#d3d4d6", border_color="#4c4c4c", border_width=2, command=lambda: seleciona_botao("D", d_btn))
    d_btn.pack(pady=1, padx=(1,20), side="right", anchor="e")
    c_btn = CTkButton(master=buttons_frame, text="C", text_color="#292b64", font=("Arial Black", 26), corner_radius=80, width=60, height=60,  fg_color="#d3d4d6", hover_color="#d3d4d6", border_color="#4c4c4c", border_width=2, command=lambda: seleciona_botao("C", c_btn))
    c_btn.pack(pady=1, padx=(1,20), side="right", anchor="e")
    b_btn = CTkButton(master=buttons_frame, text="B", text_color="#292b64", font=("Arial Black", 26), corner_radius=80, width=60, height=60, fg_color="#d3d4d6", hover_color="#d3d4d6", border_color="#4c4c4c", border_width=2, command=lambda: seleciona_botao("B", b_btn))
    b_btn.pack(pady=1, padx=(1,20), side="right", anchor="e")
    a_btn = CTkButton(master=buttons_frame, text="A", text_color="#292b64", font=("Arial Black", 26), corner_radius=80, width=60, height=60, fg_color="#d3d4d6", hover_color="#d3d4d6", border_color="#4c4c4c", border_width=2, command=lambda: seleciona_botao("A", a_btn))
    a_btn.pack(pady=1, padx=(1,20), side="right", anchor="e")



    #INTERVALO INFO
    #Número mesa
    def salva_intervalo():
        valor = intervalo.get()
        
        if len(valor) >= 1:
            salvar_em_json("intervalo", "tempo", valor)
            success_popup()
        else: 
            fail_popup()
            
    intervalo_frame = CTkFrame(master=config_screen, fg_color="transparent")
    intervalo_frame.pack(anchor="n", pady=(20, 10), fill="x", padx=40)

    intervalo_label_frame = CTkFrame(master=intervalo_frame, fg_color="transparent", width=653, height=100)
    intervalo_label_frame.pack(side="left", padx=(0, 50))
    CTkLabel(master=intervalo_label_frame, text="Intervalo para chamado: ", font=("Arial", 30), text_color="#4f4f4f").pack(anchor="w", pady=(10, 0), fill="y")

    intervalo_input_save_frame = CTkFrame(master=intervalo_frame, fg_color="transparent")
    intervalo_input_save_frame.pack(side="right", expand=True, fill="x", padx=(20, 0))
    
    intervalo_save_frame = CTkFrame(master=intervalo_input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    intervalo_save_frame.pack(side="right", anchor="e", padx=(20, 0), fill="y")
    
    intervalo_save = CTkButton(master=intervalo_save_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", command=salva_intervalo)
    intervalo_save.pack(pady=1, padx=(1,2))

    intervalo_input_frame = CTkFrame(master=intervalo_input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60, width=480)
    intervalo_input_frame.pack(side="right", anchor="e", fill="y", padx=20)
    
    intervalo = CTkEntry(master=intervalo_input_frame, placeholder_text="30 segundos", font=("Arial Black", 27), text_color="#24265f", fg_color="transparent", justify="center", border_width=0, border_color="none", width=480)
    intervalo.pack(expand=True, fill="both", pady=10, padx=20)



    #ALERTA INFO   
    def salva_alerta():
        valor = alerta.get()
        
        if len(valor) >= 1:
            salvar_em_json("alerta", "tempo", valor)
            success_popup()
        else: 
            fail_popup()
            
    alerta_frame = CTkFrame(master=config_screen, fg_color="transparent")
    alerta_frame.pack(anchor="n", pady=(20, 10), fill="x", padx=40)

    alerta_label_frame = CTkFrame(master=alerta_frame, fg_color="transparent", width=653, height=100)
    alerta_label_frame.pack(side="left", padx=(0, 50))
    CTkLabel(master=alerta_label_frame, text="Alerta para tempo ocioso: ", font=("Arial", 30), text_color="#4f4f4f").pack(anchor="w", pady=(10, 0), fill="y")

    alerta_input_save_frame = CTkFrame(master=alerta_frame, fg_color="transparent")
    alerta_input_save_frame.pack(side="right", expand=True, fill="x", padx=(20, 0))
    
    alerta_save_frame = CTkFrame(master=alerta_input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    alerta_save_frame.pack(side="right", anchor="e", padx=(20, 0), fill="y")
    
    alerta_save = CTkButton(master=alerta_save_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", command=salva_alerta)
    alerta_save.pack(pady=1, padx=(1,2))

    alerta_input_frame = CTkFrame(master=alerta_input_save_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60, width=480)
    alerta_input_frame.pack(side="right", anchor="e", fill="y", padx=20)
    
    alerta = CTkEntry(master=alerta_input_frame, placeholder_text="60 segundos", font=("Arial Black", 27), text_color="#24265f", fg_color="transparent", justify="center", border_width=0, border_color="none", width=480)
    alerta.pack(expand=True, fill="both", pady=10, padx=20)


    #BIP
    def salva_bip():
        try:
            with open("config.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"bip": {"bip": True}}  # Valor padrão se o JSON não existir ou estiver vazio
        
        # Verificar e inverter o valor de "bip"
        if "bip" in data and "bip" in data["bip"]:
            data["bip"]["bip"] = not data["bip"]["bip"]
        else:
            data["bip"] = {"bip": True}  # Define como False se a chave "bip" não existir
        
        # Salvar o arquivo JSON com a atualização
        with open("config.json", "w") as file:
            json.dump(data, file, indent=4)
            
        if data["bip"]["bip"]:
            bip_save.configure(text="✓")
        else:
            bip_save.configure(text="")
            
            
    def salva_porta():
        valor = porta.get()
        
        if len(valor) >= 1:
            salvar_em_json("porta_arduino", "porta", valor)
            success_popup()
        else: 
            fail_popup()
    
            
    bip_frame = CTkFrame(master=config_screen, fg_color="transparent")
    bip_frame.pack(anchor="n", pady=(20, 10), fill="x", padx=40)

    bip_save_frame = CTkFrame(master=bip_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=58)
    bip_save_frame.pack(side="left", anchor="w", padx=(0), fill="y")
    
    bip_save = CTkButton(master=bip_save_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", command=salva_bip)
    bip_save.pack(pady=1, padx=(2))

    bip_label_frame = CTkFrame(master=bip_frame, fg_color="transparent")
    bip_label_frame.pack(side="left", padx=(20, 0))
    CTkLabel(master=bip_label_frame, text="Sem bip / Sem som: ", font=("Arial", 30), text_color="#4f4f4f").pack(anchor="w", pady=(5 , 0), fill="y")
    
    
    porta_save_frame = CTkFrame(master=bip_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60)
    porta_save_frame.pack(side="right", anchor="e", padx=(20, 0), fill="y")
    
    porta_save = CTkButton(master=porta_save_frame, text="✓", text_color="#4c4c4c", font=("Arial Black", 32), corner_radius=0, fg_color="#d3d4d6", hover_color="#d3d4d6", command=salva_porta)
    porta_save.pack(pady=1, padx=(1,2))
    
    porta_input_frame = CTkFrame(master=bip_frame, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, height=60, width=480)
    porta_input_frame.pack(side="right", anchor="e", fill="y", padx=(20, 0))
    
    porta = CTkEntry(master=porta_input_frame, placeholder_text="COM3", font=("Arial Black", 27), text_color="#24265f", fg_color="transparent", justify="center", border_width=0, border_color="none", width=200)
    porta.pack(expand=True, fill="both", pady=10, padx=20)
    
    porta_label_frame = CTkFrame(master=bip_frame, fg_color="transparent")
    porta_label_frame.pack(side="right", padx=(0, 20))
    CTkLabel(master=porta_label_frame, text="Porta dispositivo:", font=("Arial", 30), text_color="#4f4f4f").pack(anchor="e", pady=(5 , 0), fill="y")
    
    
    
    #voltar
    def close_config():
        global popup_open
        popup_open = False
        
        config_screen.destroy()
        atualizar_codigo()
        get_config_info()
        


    back_frame = CTkFrame(master=config_screen, fg_color="transparent")
    back_frame.pack(anchor="s", fill="x", padx=20, pady=20)

    back_button = CTkLabel(master=back_frame, text="Voltar", font=("Arial", 28), fg_color="#2d2f62", width=120, height=60, text_color="#ffffff")
    back_button.pack(anchor="n") 
    back_button.bind("<Button-1>", lambda e: close_config())
    
    
    load_config(intervalo, alerta, bip_save)













# Função para alternar a visibilidade da senha
def toggle_password_visibility():
    if senha_entry.cget("show") == "*":  # Se a senha está oculta
        senha_entry.configure(show="")   # Mostra a senha
        show_password_button.configure(image=eye_closed_image)  
    else:
        senha_entry.configure(show="*")  # Oculta a senha
        show_password_button.configure(image=eye_open_image)  # Altera o ícone

# POPUP SENHA
def psswd_popup():
    # Cria uma nova janela (popup)
    popup = CTkToplevel(master=app, fg_color="#e7e7e7")
    popup.title("Digite sua senha")
    center_window(popup, 300, 130)
    
    # Traz o popup para frente e dá foco
    popup.transient(app)  # Define o popup como uma janela filha
    popup.grab_set()      # Impede interação com a janela principal
    popup.focus()         # Dá o foco ao popup

    # Label de instrução
    label = CTkLabel(popup, text="Insira sua senha:", font=("Arial", 18), text_color="#4f4f4f")
    label.pack(pady=10)
    
    # Frame para colocar o campo de senha e o botão de mostrar senha
    frame_senha = CTkFrame(popup, fg_color="#e7e7e7", corner_radius=0)
    frame_senha.pack(pady=10)

    # Campo de entrada de senha com cor de texto personalizada
    global senha_entry
    senha_entry = CTkEntry(frame_senha, show="*", width=200, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1, text_color="#333", corner_radius=0)  # Define o texto na cor vermelha
    senha_entry.pack(side="left", padx=10)
    popup.after(100, senha_entry.focus)
    
    # Botão para alternar a visibilidade da senha
    global show_password_button
    global eye_open_image, eye_closed_image

    # Carregar as imagens para os ícones
    eye_open_image = CTkImage(Image.open("images/view.png"), size=(20, 20))  # Caminho para a imagem de olho aberto
    eye_closed_image = CTkImage(Image.open("images/hide.png"), size=(20, 20))  # Caminho para a imagem de olho fechado

    # Botão para alternar a visibilidade da senha
    global show_password_button
    show_password_button = CTkButton(master=frame_senha, text="", image=eye_open_image, width=40, fg_color="#e7e7e7", hover_color="#e7e7e7", command=toggle_password_visibility)
    show_password_button.pack(side="right")

    # Função para verificar a senha
    def verificar_senha(event=None):
        global popup_open
        
        senha = senha_entry.get()
        if senha == "1":  # Exemplo de senha correta
            popup.destroy()
            abrir_config()
            popup_open = True
        else:
            messagebox.showerror("Erro", "Senha incorreta!")

    # Vincula o evento "Enter" ao campo de entrada
    senha_entry.bind("<Return>", verificar_senha)








#TELA REAL
chamados = []

get_config_info()

def atualiza_frontend():
    print(chamados)
    
    tabela_conversao = {
        0: [label_a, timestamp_a],
        1: [label_b, timestamp_b],
        2: [label_c, timestamp_c],
        3: [label_d, timestamp_d]
    }
    
    for index in range(4):
        elements = tabela_conversao[index]
        
        elements[0].configure(text=" ") 
        elements[1].configure(text="--:--")
        
        try: 
            el = chamados[index]
            elements[0].configure(text=el[0]) 
            elements[1].configure(text=datetime.fromtimestamp(el[1]).strftime("%H:%M"))
        except:
            return
        
chamados_dia = 0
def atualiza_chamados_dia():
    global chamados_dia
    
    chamados_dia += 1
    
    label_chamados_dia.configure(text=f"Total de chamados no dia: {chamados_dia}")

ultimo_chamado = 0
chamado_delay = 0.5
def chamado(codigo):
    global chamados, mesas, ultimo_chamado, intervalo
    numero_mesa = 0
    
    tempo_atual = time.time()
    
    if tempo_atual - ultimo_chamado >= chamado_delay:
        for mesa, valor in mesas.items():
            if valor == codigo:
                numero_mesa = mesa
                break 
        
        if int(numero_mesa) > 0:
            chamado_existente = next((sub_array for sub_array in chamados if sub_array[0] == numero_mesa), None)
            
            if chamado_existente:
                tempo_chamado_existente = chamado_existente[1]
                
                if tempo_atual - tempo_chamado_existente > int(intervalo):
                    chamados = [sub_array for sub_array in chamados if sub_array[0] != numero_mesa]

                    chamados.insert(0, [numero_mesa, tempo_atual])
                    atualiza_chamados_dia()
            else: 
                chamados.insert(0, [numero_mesa, tempo_atual])
                atualiza_chamados_dia()
                
        atualiza_frontend()
        ultimo_chamado = tempo_atual


ultimo_garcom_press = 0
garcom_delay = 2
def garcom_press(codigo):
    global chamados, garcom_btn, ultimo_garcom_press, garcom_delay
    
    tempo_atual = time.time()
    
    if tempo_atual - ultimo_garcom_press >= garcom_delay:
        tabela_conversao = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3
        }
        
        index_chamado = 0
        code_found = False

        for btn, valores in garcom_btn.items():
            if codigo in valores:
                index_chamado = btn
                code_found = True
                break
        
        if code_found:
            try:
                chamados.pop(tabela_conversao[index_chamado])
            except:
                print('index não encontrado')
                
            atualiza_frontend()
            ultimo_garcom_press = tempo_atual
    
    
def button_pressed(btn):
    if int(btn) > 100:
        if btn in mesas.values():
            chamado(btn)
        else:
            garcom_press(btn)
    

def atualizar_codigo():
    # Substitua 'COM3' pelo nome da porta serial do Arduino (ex.: '/dev/ttyUSB0' no Linux)
    global ser, popup_open
    
    def read_serial():
        print(popup_open)
        while not popup_open:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                button_pressed(line)

# Executa a leitura serial em uma nova thread para não travar a interface
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()

atualizar_codigo()


# HEADER
frame_header = CTkFrame(master=app, corner_radius=0, fg_color="transparent")
frame_header.pack(fill="both", anchor="n", padx=10, pady=10)

logo_img = CTkImage(light_image=Image.open('images/logo.png'), size=(220, 36)) # WidthxHeight

logo = CTkLabel(master=frame_header, text="", image=logo_img)
logo.place(relx=0, rely=0, anchor="nw", x=10, y=20) 

CTkLabel(master=frame_header, text="Chamados", font=("Arial", 50), text_color="#292b64").pack(anchor="n", side="top", pady=(10, 0))




# PRIMEIRO CHAMADO
frame_first_call = CTkFrame(master=app, fg_color="transparent")
frame_first_call.pack(anchor="n", padx=20, pady=20, fill="x")

#app.frame_first_call_container(master=frame_first_call)

# Frame para centralizar verticalmente o label "22"
frame_center = CTkFrame(master=frame_first_call, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1)
frame_center.pack(expand=True, fill="both")  # Expande e preenche o espaço disponível

timestamp_a = CTkLabel(master=frame_center, font=("Arial", 28), text="--:--", text_color="#4f4f4f")
timestamp_a.pack(anchor="n", pady=(15, 0))

# Label centralizado verticalmente
label_a = CTkLabel(master=frame_center, font=fonte, text="", text_color="#292b64")
label_a.pack(anchor="center", pady=(0,10))

# LABEL A
label_first_call = CTkLabel(master=frame_center, font=("Arial", 40), text="A", text_color="#292b64")
label_first_call.place(relx=0, rely=1, anchor="sw", x=10, y=-10) 






#TRES CHAMADOS
three_col_frame = CTkFrame(master=app, fg_color="transparent")
three_col_frame.pack(anchor="n", pady=(20, 10), fill="x")


frame_call_b = CTkFrame(master=three_col_frame, fg_color="transparent")
frame_call_b.pack(side="left", expand=True, fill="both", padx=20)

# Frame para centralizar verticalmente os elementos
frame_center_b = CTkFrame(master=frame_call_b, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1)
frame_center_b.pack(expand=True, fill="both")

# Label para o timestamp (horário)
timestamp_b = CTkLabel(master=frame_center_b, font=("Arial", 28), text="--:--", text_color="#4f4f4f")
timestamp_b.pack(anchor="n", pady=(15, 0))

# Label centralizado para o número da chamada
label_b = CTkLabel(master=frame_center_b, font=fonteMenor, text="", text_color="#292b64")
label_b.pack(anchor="center", pady=(10,0))

# Label inferior para a letra (ex. "A")
label_call_b = CTkLabel(master=frame_center_b, font=("Arial", 40), text="B", text_color="#292b64")
label_call_b.pack(anchor="sw", padx=10, pady=(0, 10))



frame_call_c = CTkFrame(master=three_col_frame, fg_color="transparent")
frame_call_c.pack(side="left", expand=True, fill="both", padx=20)

# Frame para centralizar verticalmente os elementos
frame_center_c = CTkFrame(master=frame_call_c, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1)
frame_center_c.pack(expand=True, fill="both")

# Label para o timestamp (horário)
timestamp_c = CTkLabel(master=frame_center_c, font=("Arial", 28), text="--:--", text_color="#4f4f4f")
timestamp_c.pack(anchor="n", pady=(15, 0))

# Label centralizado para o número da chamada
label_c = CTkLabel(master=frame_center_c, font=fonteMenor, text="", text_color="#292b64")
label_c.pack(anchor="center", pady=(10,0))

# Label inferior para a letra (ex. "A")
label_call_c = CTkLabel(master=frame_center_c, font=("Arial", 40), text="C", text_color="#292b64")
label_call_c.pack(anchor="sw", padx=10, pady=(0, 10))



frame_call_d = CTkFrame(master=three_col_frame, fg_color="transparent")
frame_call_d.pack(side="left", expand=True, fill="both", padx=20)

# Frame para centralizar verticalmente os elementos
frame_center_d = CTkFrame(master=frame_call_d, corner_radius=0, fg_color="#d3d4d6", border_color="#4c4c4c", border_width=1)
frame_center_d.pack(expand=True, fill="both")

# Label para o timestamp (horário)
timestamp_d = CTkLabel(master=frame_center_d, font=("Arial", 28), text="--:--", text_color="#4f4f4f")
timestamp_d.pack(anchor="n", pady=(15, 0))

# Label centralizado para o número da chamada
label_d = CTkLabel(master=frame_center_d, font=fonteMenor, text="", text_color="#292b64")
label_d.pack(anchor="center", pady=(10,0))

# Label inferior para a letra (ex. "A")
label_call_d = CTkLabel(master=frame_center_d, font=("Arial", 40), text="D", text_color="#292b64")
label_call_d.pack(anchor="sw", padx=10, pady=(0, 10))









#LAST FRAME
last_frame = CTkFrame(master=app, corner_radius=0, fg_color="transparent")
last_frame.pack(anchor="s", fill="x", padx=20, pady=20)

def atualizar_horario():
    # Obter a hora atual no formato HH:MM:SS
    horario_atual = time.strftime("%H:%M:%S")
    # Atualizar o texto do label
    hora_atual.configure(text=horario_atual)
    # Agendar a próxima atualização em 1000 milissegundos (1 segundo)
    hora_atual.after(1000, atualizar_horario)

hora_atual = CTkLabel(master=last_frame, font=("Arial Black", 30), text_color="#4f4f4f")
hora_atual.pack(anchor="n", side="top")
atualizar_horario()

label_chamados_dia = CTkLabel(master=last_frame, text="Total de chamados no dia: 0", font=("Arial", 18), text_color="#4f4f4f")
label_chamados_dia.pack(anchor="n", side="top")

config_icon = CTkImage(light_image=Image.open('images/settings.png'), size=(60,60)) # WidthxHeight

config = CTkLabel(master=last_frame, text="", image=config_icon)
config.place(relx=1, rely=1, anchor="se", x=-10, y=-5) 
config.bind("<Button-1>", lambda e: psswd_popup())



app.mainloop()