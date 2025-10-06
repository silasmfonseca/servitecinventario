import flet as ft
from supabase import create_client, Client
import os
import sys
from datetime import datetime
import pytz

# --- SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Colunas e labels ---
COLUNAS = ["patrimonio", "marca", "modelo", "numero_serie", "proprietario", "status", "condicao", "tipo_computador", "computador_liga", "observacoes", "modificado_em", "modificado_por"]
COLUNAS_LABEL = {
    "patrimonio": "Patrimônio", "marca": "Marca", "modelo": "Modelo", "numero_serie": "Nº de Série", 
    "proprietario": "Proprietário", "status": "Status", "condicao": "Condição da Carcaça", 
    "tipo_computador": "Tipo de Computador", "computador_liga": "Computador Liga?",
    "observacoes": "Observações", "modificado_em": "Última Edição", "modificado_por": "Editado Por"
}
LABEL_TO_COL = {v: k for k, v in COLUNAS_LABEL.items()}

# --- Opções dos Dropdowns ---
DROPDOWN_OPTIONS = {
    "proprietario": ["Quattro Construtora", "Outro Cliente"],
    "status": ["Está na Servitec", "KLV/ Aguardando aprovação", "KLV / Reparando", "KLV / Aguardando Retirada", "Está com o proprietário"],
    "marca": ["Lenovo", "Dell", "HP", "Acer", "Apple"],
    "condicao": ["Nova", "Estado de Nova", "Estado de Nova (Com avarias)", "Boa", "Quebrada"],
    "tipo_computador": ["Desktop", "Notebook"],
    "computador_liga": ["Sim", "Não", "Não verificado"],
}

# --- Larguras das Colunas ---
COLUMN_WIDTHS = {
    "checkbox": 50, "patrimonio": 120, "marca": 150, "modelo": 150, "numero_serie": 150, "proprietario": 200,
    "status": 200, "condicao": 200, "tipo_computador": 150, "computador_liga": 150, 
    "observacoes": 250, "modificado_em": 150, "modificado_por": 250
}
TABLE_WIDTH = sum(COLUMN_WIDTHS.values())

def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    # MUDANÇA: Adicionado padding para o conteúdo não colar nas bordas
    page.padding = ft.padding.all(20)
    page.bgcolor = "#f0f2f5"

    user_info = {"email": None}

    # MUDANÇA: Funções de credenciais para a web
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

    # MUDANÇA: Carregamento da imagem para a web
    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)

    # --- Lógica da Interface (Seu código original) ---
    itens_selecionados = []
    
    header_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"])]
    for col in COLUNAS:
        if col in COLUMN_WIDTHS: # Garante que só colunas com largura definida entrem
            header_controls.append(ft.Container(content=ft.Text(COLUNAS_LABEL[col], weight=ft.FontWeight.BOLD, color="black54"), width=COLUMN_WIDTHS[col], alignment=ft.alignment.center))
    header = ft.Container(content=ft.Row(controls=header_controls, spacing=0), bgcolor="#f0f2f5", height=40)
    
    body_list = ft.ListView(expand=True, spacing=2)

    def atualizar_estado_botoes():
        num_selecionados = len(itens_selecionados)
        edit_btn.disabled = (num_selecionados != 1)
        delete_btn.disabled = (num_selecionados == 0)
        page.update()

    def selecionar_item(item_data, checkbox_control, row_container):
        nonlocal itens_selecionados
        item_info = {"data": item_data, "checkbox": checkbox_control, "container": row_container}
        if checkbox_control.value:
            if item_info not in itens_selecionados: itens_selecionados.append(item_info)
            row_container.bgcolor = "#d3e3fd"
        else:
            itens_selecionados = [item for item in itens_selecionados if item["data"]["patrimonio"] != item_data["patrimonio"]]
            row_container.bgcolor = row_container.data.get("original_color")
        row_container.update()
        atualizar_estado_botoes()

    def fechar_dialog(e):
        page.dialog.open = False
        page.update()

    def exibir_dialog(dialog):
        page.dialog = dialog
        page.dialog.open = True
        page.update()

    def formatar_data(iso_string):
        if not iso_string: return ""
        try:
            utc_dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
            return utc_dt.astimezone(sao_paulo_tz).strftime("%d/%m/%Y %H:%M")
        except: return iso_string

    def carregar_dados(query=None):
        try:
            body_list.controls.clear()
            itens_selecionados.clear()
            atualizar_estado_botoes()
            if query is None:
                query = supabase.table("inventario").select("*").order("patrimonio")
            registros = query.execute().data or []
            
            for i, item in enumerate(registros):
                chk = ft.Checkbox()
                row_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                row_container = ft.Container(bgcolor=row_color, height=40, data={"original_color": row_color})
                
                chk.on_change = (lambda item_data=item, chk_control=chk, container=row_container: lambda e: selecionar_item(item_data, chk_control, container))()
                
                row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"], content=chk, alignment=ft.alignment.center)]
                for c in COLUNAS:
                     if c in COLUMN_WIDTHS:
                        valor = item.get(c, "")
                        valor_str = str(valor) if valor is not None else ""
                        if c == "modificado_em": valor_str = formatar_data(valor_str)
                        row_controls.append(ft.Container(width=COLUMN_WIDTHS[c], content=ft.Text(valor_str, no_wrap=True, size=12), alignment=ft.alignment.center))
                
                row_container.content = ft.Row(controls=row_controls, spacing=0)
                body_list.controls.append(row_container)
            page.update()
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao carregar dados"), content=ft.Text(str(ex))))
    
    # --- UI Principal ---
    filtrar_dropdown = ft.Dropdown(label="Filtrar por", width=220, options=[ft.dropdown.Option(opt) for opt in ["Todas as Colunas"] + list(COLUNAS_LABEL.values())], value="Todas as Colunas")
    localizar_input = ft.TextField(label="Localizar", width=220)
    buscar_btn = ft.ElevatedButton("Buscar", icon="search", on_click=lambda e: carregar_dados()) # A lógica de busca precisa ser implementada
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear")
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=lambda e: carregar_dados())
    
    add_btn = ft.ElevatedButton("Adicionar Novo", icon="add", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", icon="edit", disabled=True)
    delete_btn = ft.ElevatedButton("Excluir Selecionado", icon="delete", disabled=True)

    # RESTAURADO: Seu layout original com painéis flutuantes e scroll
    main_view = ft.Stack(
        [
            ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                filtrar_dropdown, localizar_input, buscar_btn, limpar_btn, atualizar_btn
                            ],
                            alignment=ft.MainAxisAlignment.START
                        ),
                        padding=20,
                        bgcolor="white",
                        border_radius=8
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                add_btn, edit_btn, delete_btn
                            ],
                            alignment=ft.MainAxisAlignment.END
                        ),
                        padding=ft.padding.only(top=10)
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column([header, body_list], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
                            ],
                            scroll=ft.ScrollMode.ADAPTIVE, # Garante a rolagem horizontal
                        ),
                        expand=True,
                        bgcolor="white",
                        border_radius=8,
                        padding=10
                    )
                ]
            )
        ],
        expand=True,
        visible=False
    )

    # --- UI de Login ---
    email_input = ft.TextField(label="Usuário", width=300, autofocus=True)
    password_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    lembrar_me_checkbox = ft.Checkbox(label="Lembrar-me")
    error_text = ft.Text(value="", color="red", visible=False)

    def handle_login(e):
        try:
            email = email_input.value.strip()
            password = password_input.value.strip()
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if user_session.user:
                user_info["email"] = user_session.user.email
                if lembrar_me_checkbox.value: salvar_credenciais(email, password)
                else: apagar_credenciais()
                
                login_view.visible = False
                main_view.visible = True
                carregar_dados()
                page.update()
        except Exception as ex:
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    login_form = ft.Container(content=ft.Column([ft.Text("Login", size=30), email_input, password_input, lembrar_me_checkbox, ft.ElevatedButton("Entrar", on_click=handle_login), error_text]), width=400, padding=40, border_radius=10, bgcolor="white", shadow=ft.BoxShadow(blur_radius=10, color="black26"))
    login_view = ft.Stack([bg_image, ft.Container(content=login_form, alignment=ft.alignment.center)], expand=True)

    page.add(login_view, main_view)
    carregar_credenciais()

# --- Bloco de Execução para WEB ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets", # Flet vai procurar a imagem aqui
        host="0.0.0.0",
        port=port
    )
