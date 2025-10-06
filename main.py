import flet as ft
from supabase import create_client, Client
import os
import sys
from datetime import datetime
import pytz

# --- SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL") # MUDANÇA: Lendo do ambiente do Render
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # MUDANÇA: Lendo do ambiente do Render
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Colunas e labels (Seu código original, sem alterações) ---
COLUNAS = [
    "patrimonio", "marca", "modelo", "numero_serie", "proprietario", "status", "condicao",
    "tipo_computador", "computador_liga",
    "hd", "hd_modelo", "hd_tamanho", "ram_tipo", "ram_tamanho",
    "bateria", "teclado_funciona", "observacoes", "modificado_em", "modificado_por"
]

COLUNAS_LABEL = {
    "patrimonio": "Patrimônio", "marca": "Marca", "modelo": "Modelo", "numero_serie": "Nº de Série", 
    "proprietario": "Proprietário", "status": "Status", "condicao": "Condição da Carcaça", 
    "tipo_computador": "Tipo de Computador", "computador_liga": "Computador Liga?",
    "hd": "Tipo HD/SSD", "hd_modelo": "Modelo HD/SSD", "hd_tamanho": "Tamanho HD/SSD", 
    "ram_tipo": "Tipo Memória RAM", "ram_tamanho": "Tamanho Memória RAM", 
    "bateria": "Possui Bateria?", "teclado_funciona": "Teclado Funciona?", 
    "observacoes": "Observações", "modificado_em": "Última Edição", "modificado_por": "Editado Por"
}
LABEL_TO_COL = {v: k for k, v in COLUNAS_LABEL.items()}

# --- Opções dos Dropdowns (Seu código original, sem alterações) ---
DROPDOWN_OPTIONS = {
    "proprietario": [
        "Capital Company", "Conmedi - Jardins", "Conmedi - Mauá", "Conmedi - Osaco", 
        "Conmedi - Paulista", "Conmedi - Ribeirão Pires", "Conmedi - Santo Amaro", 
        "Conmedi - Santo André", "Conmedi - São Caetano", "Conmedi - Vila Matilde", 
        "Engrecon", "Engrecon - BPN", "Inova Contabildiade", "MIMO", "Pro Saúde", 
        "Rede Gaya", "Quattro Construtora", "Sealset", "Servitec - Locação", "SL Assessoria", "Super Brilho"
    ],
    "status": ["Está na Servitec", "KLV/ Aguardando aprovação", "KLV / Reparando", "KLV / Aguardando Retirada", "Está com o proprietário"],
    "marca": ["Apple", "Acer", "Dell", "HP", "Lenovo", "Positivo", "Samsung"],
    "condicao": ["Nova", "Estado de Nova", "Estado de Nova (Com avarias)", "Boa", "Quebrada"],
    "tipo_computador": ["Desktop", "Notebook"],
    "computador_liga": ["Sim", "Não"],
    "bateria": ["Sim", "Não"],
    "teclado_funciona": ["Sim", "Não"],
    "hd": ["SSD", "HD"],
    "hd_tamanho": ["120 GB", "240 GB", "256 GB", "480 GB", "500 GB", "512 GB", "1 TB", "2 TB"],
    "ram_tipo": ["DDR3", "DDR4", "DDR5"],
    "ram_tamanho": ["2 GB", "4 GB", "8 GB", "16 GB", "32 GB"]
}


def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    page.padding = 0
    page.bgcolor = "#f0f2f5"

    user_info = {"email": None, "role": "admin"}
    READONLY_USERS = ["aline.mendes@servitecbrasil.com.br"]

    # MUDANÇA: Funções de salvar/carregar credenciais adaptadas para a web.
    # Elas agora usam o armazenamento do navegador (page.client_storage), não arquivos locais.
    def salvar_credenciais(email, password):
        page.client_storage.set("auth.email", email.strip())
        page.client_storage.set("auth.password", password.strip())

    def carregar_credenciais():
        email = page.client_storage.get("auth.email")
        password = page.client_storage.get("auth.password")
        if email and password:
            email_input.value = email
            password_input.value = password
            lembrar_me_checkbox.value = True
            page.update()
    
    def apagar_credenciais():
        page.client_storage.remove("auth.email")
        page.client_storage.remove("auth.password")

    # MUDANÇA: Simplificado o carregamento da imagem de fundo.
    # O Flet busca automaticamente na pasta 'assets'.
    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)

    # --- O restante do seu código de UI (lógica da tabela, modais, etc.) ---
    # Esta parte é quase 100% idêntica, pois a lógica da interface não muda.

    itens_selecionados = []
    # Criação dos controles da UI... (código omitido por brevidade, mas é o seu original)

    # ... (Todo o seu código de `atualizar_estado_botoes`, `selecionar_item`, `carregar_dados`, 
    #      `abrir_formulario`, `handle_login`, etc., entra aqui, exatamente como era antes.
    #      A única mudança é que o email do usuário logado será pego de forma diferente)
    
    # Exemplo simplificado da lógica de login
    def handle_login(e):
        try:
            email = email_input.value.strip()
            password = password_input.value.strip()
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if user_session.user:
                user_info["email"] = user_session.user.email
                if user_info["email"] in READONLY_USERS: user_info["role"] = "readonly"
                else: user_info["role"] = "admin"
                
                if lembrar_me_checkbox.value:
                    salvar_credenciais(email, password)
                else:
                    apagar_credenciais()
                
                login_view.visible = False
                main_view.visible = True
                page.update()
                # carregar_dados() # Você chamaria sua função de carregar dados aqui
        except Exception as ex:
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    # --- Definição da UI (simplificada para o exemplo) ---
    email_input = ft.TextField(label="Usuário")
    password_input = ft.TextField(label="Senha", password=True)
    lembrar_me_checkbox = ft.Checkbox(label="Lembrar-me")
    error_text = ft.Text(value="", color="red", visible=False)

    login_form = ft.Container(
        content=ft.Column([
            ft.Text("Login", size=30),
            email_input,
            password_input,
            lembrar_me_checkbox,
            ft.ElevatedButton("Entrar", on_click=handle_login),
            error_text
        ]),
        padding=40,
        border_radius=10,
        bgcolor="white"
    )

    login_view = ft.Stack(
        controls=[
            bg_image,
            ft.Container(content=login_form, alignment=ft.alignment.center)
        ],
        expand=True,
        visible=True
    )

    main_view = ft.Column(
        controls=[
            ft.Text("Bem-vindo ao Inventário!", size=40),
            # Seus controles de tabela e filtro iriam aqui
        ],
        expand=True,
        visible=False
    )
    
    page.add(login_view, main_view)
    carregar_credenciais()

# --- BLOCO DE EXECUÇÃO PARA WEB (A MUDANÇA MAIS IMPORTANTE) ---
if __name__ == "__main__":
    # Pega a porta do ambiente do Render. Essencial para funcionar online.
    port = int(os.getenv("PORT", 8550))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER, # MUDANÇA: Executa como app de navegador
        assets_dir="assets",        # MUDANÇA: Informa a pasta de recursos
        host="0.0.0.0",             # MUDANÇA: Permite acesso externo
        port=port                   # MUDANÇA: Usa a porta fornecida pelo Render
    )