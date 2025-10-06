import flet as ft
from supabase import create_client, Client
import os
import sys
from datetime import datetime
import pytz

# --- SUPABASE (Lendo do Ambiente do Render) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Constantes do seu código original ---
COLUNAS = ["patrimonio", "marca", "modelo", "numero_serie", "proprietario", "status", "condicao", "tipo_computador", "computador_liga", "observacoes", "modificado_em", "modificado_por"]
COLUNAS_LABEL = {
    "patrimonio": "Patrimônio", "marca": "Marca", "modelo": "Modelo", "numero_serie": "Nº de Série", 
    "proprietario": "Proprietário", "status": "Status", "condicao": "Condição da Carcaça", 
    "tipo_computador": "Tipo de Computador", "computador_liga": "Computador Liga?",
    "observacoes": "Observações", "modificado_em": "Última Edição", "modificado_por": "Editado Por"
}
LABEL_TO_COL = {v: k for k, v in COLUNAS_LABEL.items()}

DROPDOWN_OPTIONS = {
    "proprietario": ["Capital Company", "Conmedi - Jardins", "Conmedi - Mauá", "Conmedi - Osaco", "Conmedi - Paulista", "Conmedi - Ribeirão Pires", "Conmedi - Santo Amaro", "Conmedi - Santo André", "Conmedi - São Caetano", "Conmedi - Vila Matilde", "Engrecon", "Engrecon - BPN", "Inova Contabildiade", "MIMO", "Pro Saúde", "Rede Gaya", "Quattro Construtora", "Sealset", "Servitec - Locação", "SL Assessoria", "Super Brilho"],
    "status": ["Está na Servitec", "KLV/ Aguardando aprovação", "KLV / Reparando", "KLV / Aguardando Retirada", "Está com o proprietário"],
    "marca": ["Apple", "Acer", "Dell", "HP", "Lenovo", "Positivo", "Samsung"],
    "condicao": ["Nova", "Estado de Nova", "Estado de Nova (Com avarias)", "Boa", "Quebrada"],
    "tipo_computador": ["Desktop", "Notebook"],
    "computador_liga": ["Sim", "Não", "Não verificado"],
}

COLUMN_WIDTHS = {
    "checkbox": 50, "patrimonio": 120, "marca": 150, "modelo": 150, "numero_serie": 150, "proprietario": 200,
    "status": 200, "condicao": 200, "tipo_computador": 150, "computador_liga": 150, "observacoes": 250, 
    "modificado_em": 150, "modificado_por": 250
}
TABLE_WIDTH = sum(COLUMN_WIDTHS.values())

def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    page.padding = 0
    page.bgcolor = "#f0f2f5"

    # --- Lógica de Navegação e Autenticação ---
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [login_page],
            )
        )
        if page.session.get("user_email"):
            page.views.append(
                ft.View(
                    "/app",
                    [main_app_layout],
                )
            )
        page.update()

    def logout(e):
        page.session.clear()
        page.go("/")

    # --- Funções de Credenciais para Web ---
    def salvar_credenciais(email, password):
        page.client_storage.set("auth.email", email.strip())

    def carregar_credenciais():
        email = page.client_storage.get("auth.email")
        if email:
            email_input.value = email
            lembrar_me_checkbox.value = True
            page.update()
    
    def apagar_credenciais():
        page.client_storage.remove("auth.email")

    # --- Lógica da Interface Principal ---
    # (O código para carregar dados, abrir formulários, etc. vai aqui)
    body_list = ft.ListView(expand=True, spacing=0) # Definido aqui para ser acessível globalmente em 'main'

    def carregar_dados(e=None):
        # ... (Sua função carregar_dados completa aqui)
        pass

    def abrir_formulario(modo="add"):
        # ... (Sua função abrir_formulario completa aqui)
        pass
        
    def excluir_selecionado(e):
        # ... (Sua função excluir_selecionado completa aqui)
        pass

    # --- Definição dos Controles da UI ---
    
    # UI Principal
    filtrar_dropdown = ft.Dropdown(width=200, label="Filtrar por")
    localizar_input = ft.TextField(width=200, label="Localizar")
    buscar_btn = ft.ElevatedButton("Buscar", icon="search")
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear")
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=carregar_dados)
    
    add_btn = ft.ElevatedButton("Adicionar Novo", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", disabled=True)
    delete_btn = ft.ElevatedButton("Excluir Selecionado", disabled=True)

    main_app_layout = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Tecnologia que move o seu negócio.", size=32, weight=ft.FontWeight.BOLD, color="#6c5ce7")
                ]
            ),
            ft.Container(
                 # ... (O resto do seu layout principal aqui) ...
            )
        ],
        expand=True
    )
    
    # UI de Login
    email_input = ft.TextField(label="Usuário", width=300, autofocus=True)
    password_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    lembrar_me_checkbox = ft.Checkbox(label="Lembrar-me")
    error_text = ft.Text(value="", color="red", visible=False)

    def handle_login(e):
        try:
            error_text.visible = False
            page.update()
            
            email = email_input.value.strip()
            password = password_input.value.strip()
            
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if user_session.user:
                # CORREÇÃO: Usando page.session para armazenar o login
                page.session.set("user_email", user_session.user.email)
                
                if lembrar_me_checkbox.value:
                    salvar_credenciais(email, password)
                else:
                    apagar_credenciais()
                
                page.go("/app") # Redireciona para a página principal
        except Exception as ex:
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    login_form = ft.Container(
        content=ft.Column(
            [
                ft.Text("Login", size=30), 
                email_input, 
                password_input, 
                lembrar_me_checkbox, 
                ft.ElevatedButton("Entrar", on_click=handle_login)
            ], 
            spacing=15, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ), 
        width=400, padding=40, border_radius=10, bgcolor="white", 
        shadow=ft.BoxShadow(blur_radius=10, color="black26")
    )
    
    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)
    
    login_page = ft.Stack(
        [
            bg_image,
            ft.Container(content=login_form, alignment=ft.alignment.center)
        ], 
        expand=True
    )
    
    # Configuração das rotas da página
    page.on_route_change = route_change
    page.go(page.route)
    carregar_credenciais()

# --- Bloco de Execução para WEB ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", host="0.0.0.0", port=port)
