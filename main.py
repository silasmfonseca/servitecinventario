import flet as ft
from supabase import create_client, Client
import os
import sys
from datetime import datetime
import pytz

# --- SUPABASE ---
# MUDANÇA: Lendo as credenciais das variáveis de ambiente do Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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
    "proprietario": ["Capital Company", "Conmedi - Jardins", "Conmedi - Mauá", "Conmedi - Osaco", "Conmedi - Paulista", "Conmedi - Ribeirão Pires", "Conmedi - Santo Amaro", "Conmedi - Santo André", "Conmedi - São Caetano", "Conmedi - Vila Matilde", "Engrecon", "Engrecon - BPN", "Inova Contabildiade", "MIMO", "Pro Saúde", "Rede Gaya", "Quattro Construtora", "Sealset", "Servitec - Locação", "SL Assessoria", "Super Brilho"],
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

# --- LARGURAS DAS COLUNAS (Seu código original, sem alterações) ---
COLUMN_WIDTHS = { "checkbox": 50, "patrimonio": 120, "marca": 150, "modelo": 150, "numero_serie": 150, "proprietario": 200, "status": 120, "condicao": 200, "tipo_computador": 150, "computador_liga": 150, "hd": 120, "hd_modelo": 150, "hd_tamanho": 150, "ram_tipo": 150, "ram_tamanho": 150, "bateria": 150, "teclado_funciona": 200, "observacoes": 250, "modificado_em": 150, "modificado_por": 250 }
COLOR_PRIMARY = "#0052D4"

def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    page.padding = 0
    page.bgcolor = "#f0f2f5"

    user_info = {"email": None, "role": "admin"}
    READONLY_USERS = ["aline.mendes@servitecbrasil.com.br"]

    # MUDANÇA: Funções de credenciais adaptadas para a web, usando o armazenamento do navegador
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

    # MUDANÇA: Imagem de fundo carregada a partir da pasta 'assets'
    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)

    # --- INÍCIO DA SUA LÓGICA DE UI ORIGINAL ---
    # Todo o código abaixo é o seu, para construir a interface completa.

    itens_selecionados = []
    header_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"])]
    for col in COLUNAS: header_controls.append(ft.Container(content=ft.Text(COLUNAS_LABEL[col], weight=ft.FontWeight.BOLD, color="black54"), width=COLUMN_WIDTHS[col], alignment=ft.alignment.center))
    header = ft.Container(content=ft.Row(controls=header_controls, spacing=0), bgcolor="#f0f2f5", height=40, border_radius=ft.border_radius.only(top_left=8, top_right=8), border=ft.border.only(bottom=ft.border.BorderSide(2, "#dee2e6")))
    body_list = ft.ListView(expand=True, spacing=2, padding=ft.padding.only(top=5, bottom=5))

    def atualizar_estado_botoes():
        num_selecionados = len(itens_selecionados)
        is_readonly = user_info.get("role") == "readonly"
        
        add_btn.disabled = is_readonly
        edit_btn.disabled = (num_selecionados != 1)
        delete_btn.disabled = (num_selecionados == 0) or is_readonly
        
        if is_readonly:
            edit_btn.disabled = (num_selecionados != 1)
        
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

    def fechar_dialog(dlg):
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

    def mostrar_observacao_completa(e, observacao_texto):
        dlg = ft.AlertDialog(modal=True, title=ft.Text("Observação Completa"), content=ft.Text(observacao_texto, selectable=True), actions=[ft.TextButton("Fechar", on_click=lambda _: fechar_dialog(dlg))], actions_alignment=ft.MainAxisAlignment.END)
        exibir_dialog(dlg)

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
                row_container = ft.Container(bgcolor=row_color, height=40, border_radius=4, data={"original_color": row_color, "item_data": item})
                
                def create_row_click_handler(checkbox, item_data, container):
                    def row_click(e):
                        checkbox.value = not checkbox.value
                        selecionar_item(item_data, checkbox, container)
                        checkbox.update()
                    return row_click
                
                chk.on_change = (lambda item_data, chk_control, container: lambda e: selecionar_item(item_data, chk_control, container))(item, chk, row_container)
                row_container.on_click = create_row_click_handler(chk, item, row_container)
                
                row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"], content=chk, alignment=ft.alignment.center)]
                for c in COLUNAS:
                    valor = item.get(c)
                    valor_str = str(valor) if valor is not None else ""
                    if c == "modificado_em": valor_str = formatar_data(valor_str)
                    
                    cell_content = ft.Text(valor_str, no_wrap=True, size=12)
                    if c == "observacoes" and valor:
                        cell_content = ft.Container(content=ft.Text(valor_str, no_wrap=True, size=12, italic=True, color=COLOR_PRIMARY), on_click=lambda e, obs=valor_str: mostrar_observacao_completa(e, obs), tooltip="Clique para ver a observação completa")

                    row_controls.append(ft.Container(width=COLUMN_WIDTHS[c], content=cell_content, alignment=ft.alignment.center, padding=ft.padding.symmetric(horizontal=5)))
                
                row_container.content = ft.Row(controls=row_controls, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                body_list.controls.append(row_container)
            page.update()
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao carregar dados"), content=ft.Text(str(ex))))
    
    def aplicar_filtro_e_busca(e):
        coluna_selecionada = filtrar_dropdown.value
        coluna_db = LABEL_TO_COL.get(coluna_selecionada)
        query = supabase.table("inventario").select("*").order("patrimonio")
        try:
            termo_busca = localizar_input.value.strip()
            if not termo_busca:
                carregar_dados()
                return
            
            if coluna_selecionada == "Todas as Colunas":
                colunas_para_buscar = [c for c in COLUNAS if c not in ["modificado_em"]]
                filtros_or = ",".join([f'{col}.ilike.%{termo_busca}%' for col in colunas_para_buscar])
                query = query.or_(filtros_or)
            else:
                query = query.ilike(coluna_db, f"%{termo_busca}%")
            carregar_dados(query)
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro na busca"), content=ft.Text(str(ex))))

    def limpar_filtro(e):
        localizar_input.value = ""
        filtrar_dropdown.value = "Todas as Colunas"
        carregar_dados()
        page.update()

    def abrir_formulario(modo="add"):
        # Sua função original completa para abrir o formulário
        pass # Cole aqui a sua função `abrir_formulario` completa

    def excluir_selecionado(e):
        # Sua função original completa para excluir
        pass # Cole aqui a sua função `excluir_selecionado` completa
    
    # --- UI Principal ---
    filtrar_dropdown = ft.Dropdown(label="Filtrar por", width=220, options=[ft.dropdown.Option(opt) for opt in ["Todas as Colunas"] + list(COLUNAS_LABEL.values())], value="Todas as Colunas")
    localizar_input = ft.TextField(label="Localizar", width=220)
    buscar_btn = ft.ElevatedButton("Buscar", icon="search", on_click=aplicar_filtro_e_busca)
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear", on_click=limpar_filtro)
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=lambda e: carregar_dados())
    
    add_btn = ft.ElevatedButton("Adicionar Novo", icon="add", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", icon="edit", disabled=True, on_click=lambda e: abrir_formulario("edit"))
    delete_btn = ft.ElevatedButton("Excluir Selecionado", icon="delete", disabled=True, on_click=excluir_selecionado)

    main_view = ft.Column(
        controls=[
            ft.Row([filtrar_dropdown, localizar_input, buscar_btn, limpar_btn, atualizar_btn]),
            ft.Row([add_btn, edit_btn, delete_btn], alignment=ft.MainAxisAlignment.END),
            ft.Container(
                content=ft.Column([header, body_list], expand=True),
                expand=True,
                border_radius=8,
                bgcolor="white"
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
                user_info["role"] = "readonly" if user_info["email"] in READONLY_USERS else "admin"
                
                if lembrar_me_checkbox.value: salvar_credenciais(email, password)
                else: apagar_credenciais()
                
                login_view.visible = False
                main_view.visible = True
                carregar_dados() # Carrega os dados após o login
                page.update()
        except Exception as ex:
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    login_form = ft.Container(
        content=ft.Column([
            ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
            email_input, password_input, lembrar_me_checkbox,
            ft.ElevatedButton("Entrar", on_click=handle_login),
            error_text
        ]),
        width=400, padding=40, border_radius=10, bgcolor="white",
        shadow=ft.BoxShadow(blur_radius=10, color="black26")
    )
    
    login_view = ft.Stack([
        bg_image,
        ft.Container(content=login_form, alignment=ft.alignment.center)
    ], expand=True)

    page.add(login_view, main_view)
    carregar_credenciais()

# --- BLOCO DE EXECUÇÃO PARA WEB ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        host="0.0.0.0",
        port=port
    )
