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
COLUNAS_LABEL = { "patrimonio": "Patrimônio", "marca": "Marca", "modelo": "Modelo", "numero_serie": "Nº de Série", "proprietario": "Proprietário", "status": "Status", "condicao": "Condição da Carcaça", "tipo_computador": "Tipo de Computador", "computador_liga": "Computador Liga?", "observacoes": "Observações", "modificado_em": "Última Edição", "modificado_por": "Editado Por"}
LABEL_TO_COL = {v: k for k, v in COLUNAS_LABEL.items()}
DROPDOWN_OPTIONS = { "proprietario": ["Capital Company", "Conmedi - Jardins", "Conmedi - Mauá", "Conmedi - Osaco", "Conmedi - Paulista", "Conmedi - Ribeirão Pires", "Conmedi - Santo Amaro", "Conmedi - Santo André", "Conmedi - São Caetano", "Conmedi - Vila Matilde", "Engrecon", "Engrecon - BPN", "Inova Contabildiade", "MIMO", "Pro Saúde", "Rede Gaya", "Quattro Construtora", "Sealset", "Servitec - Locação", "SL Assessoria", "Super Brilho"], "status": ["Está na Servitec", "KLV/ Aguardando aprovação", "KLV / Reparando", "KLV / Aguardando Retirada", "Está com o proprietário"], "marca": ["Apple", "Acer", "Dell", "HP", "Lenovo", "Positivo", "Samsung"], "condicao": ["Nova", "Estado de Nova", "Estado de Nova (Com avarias)", "Boa", "Quebrada"], "tipo_computador": ["Desktop", "Notebook"], "computador_liga": ["Sim", "Não", "Não verificado"] }
COLUMN_WIDTHS = { "checkbox": 50, "patrimonio": 120, "marca": 150, "modelo": 150, "numero_serie": 150, "proprietario": 200, "status": 200, "condicao": 200, "tipo_computador": 150, "computador_liga": 150, "observacoes": 250, "modificado_em": 150, "modificado_por": 250 }
TABLE_WIDTH = sum(COLUMN_WIDTHS.values())

def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    page.padding = 0
    page.bgcolor = "#f0f2f5"

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

    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)
    itens_selecionados = []
    
    header_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"])]
    for col in COLUNAS: header_controls.append(ft.Container(content=ft.Text(COLUNAS_LABEL.get(col, col), weight=ft.FontWeight.BOLD, color="black54"), width=COLUMN_WIDTHS.get(col, 150), alignment=ft.alignment.center))
    header = ft.Container(content=ft.Row(controls=header_controls, spacing=0), bgcolor="#f8f9fa", height=40)
    body_list = ft.ListView(expand=True, spacing=0)

    def fechar_dialog(e):
        page.dialog.open = False
        page.update()

    def exibir_dialog(dialog):
        page.dialog = dialog
        page.dialog.open = True
        page.update()

    def carregar_dados(e=None):
        try:
            body_list.controls.clear()
            registros = supabase.table("inventario").select("*").order("patrimonio").execute().data or []
            for item in registros:
                chk = ft.Checkbox()
                row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"], content=chk, alignment=ft.alignment.center)]
                for c in COLUNAS:
                     valor = item.get(c, "")
                     valor_str = str(valor) if valor is not None else ""
                     row_controls.append(ft.Container(width=COLUMN_WIDTHS.get(c, 150), content=ft.Text(valor_str, no_wrap=True, size=12), alignment=ft.alignment.center, border=ft.border.only(left=ft.border.BorderSide(1, "#dee2e6"))))
                body_list.controls.append(ft.Row(controls=row_controls, spacing=0))
            page.update()
        except Exception as ex:
            print(f"ERRO AO CARREGAR DADOS: {ex}")

    def abrir_formulario(modo="add"):
        # Sua função original completa para abrir o formulário
        # (Esta função precisa ser preenchida com seu código original)
        print("Função abrir_formulario chamada com modo:", modo)
        pass

    def excluir_selecionado(e):
        # Sua função original completa para excluir
        # (Esta função precisa ser preenchida com seu código original)
        print("Função excluir_selecionado chamada")
        pass

    # --- UI Principal ---
    filtrar_dropdown = ft.Dropdown(label="Filtrar por", width=220, options=[ft.dropdown.Option(opt) for opt in ["Todas as Colunas"] + list(COLUNAS_LABEL.values())], value="Todas as Colunas")
    localizar_input = ft.TextField(label="Localizar", width=220)
    buscar_btn = ft.ElevatedButton("Buscar", icon="search")
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear")
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=carregar_dados)
    add_btn = ft.ElevatedButton("Adicionar Novo", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", disabled=True, on_click=lambda e: abrir_formulario("edit"))
    delete_btn = ft.ElevatedButton("Excluir Selecionado", disabled=True, on_click=excluir_selecionado)

    main_view = ft.Column(
        [
            ft.Container(
                content=ft.Row([ft.Text("Tecnologia que move o seu negócio.", size=32, weight=ft.FontWeight.BOLD, color="#6c5ce7")]),
                padding=ft.padding.only(left=20, top=20)
            ),
            ft.Container(
                content=ft.Row([
                    ft.Row([filtrar_dropdown, localizar_input, buscar_btn, limpar_btn, atualizar_btn], spacing=10),
                    ft.Row([add_btn, edit_btn, delete_btn], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=20, bgcolor="rgba(255,255,255,0.8)", border_radius=8
            ),
            ft.Container(
                content=ft.Row([ft.Column([header, body_list], scroll=ft.ScrollMode.ADAPTIVE)], scroll=ft.ScrollMode.ADAPTIVE),
                expand=True, bgcolor="rgba(255,255,255,0.8)", border_radius=8, padding=10
            )
        ],
        expand=True, visible=False, spacing=20
    )

    # --- UI de Login ---
    email_input = ft.TextField(label="Usuário", width=300, autofocus=True)
    password_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    lembrar_me_checkbox = ft.Checkbox(label="Lembrar-me")
    error_text = ft.Text(value="", color="red", visible=False)

    def handle_login(e):
        try:
            error_text.visible = False; page.update()
            email = email_input.value.strip(); password = password_input.value.strip()
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user_session.user:
                page.session.set("user_email", user_session.user.email)
                if lembrar_me_checkbox.value: salvar_credenciais(email, password)
                else: apagar_credenciais()
                
                login_view.visible = False
                main_view.visible = True
                carregar_dados()
                page.update()
        except Exception as ex:
            # MUDANÇA CRUCIAL: Imprime o erro real no log do Render
            print(f"ERRO NO LOGIN: {ex}") 
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    login_form = ft.Container(content=ft.Column([ft.Text("Login", size=30), email_input, password_input, lembrar_me_checkbox, ft.ElevatedButton("Entrar", on_click=handle_login)], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=400, padding=40, border_radius=10, bgcolor="white", shadow=ft.BoxShadow(blur_radius=10, color="black26"))
    login_view = ft.Container(content=login_form, alignment=ft.alignment.center, expand=True, visible=True)

    # CORREÇÃO DE LAYOUT: A Stack agora envolve tudo para o fundo persistir
    page.add(
        ft.Stack([
            bg_image,
            login_view,
            ft.Container(content=main_view, padding=20)
        ])
    )
    
    carregar_credenciais()

# --- Bloco de Execução para WEB ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    app.secret_key = os.getenv("SECRET_KEY") # Chave para a sessão
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", host="0.0.0.0", port=port)
