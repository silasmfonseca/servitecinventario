import flet as ft
from supabase import create_client, Client
import os
from datetime import datetime
import pytz

# --- SUPABASE (Lendo do Ambiente do Render) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Constantes do sistema ---
COLUNAS = [
    "patrimonio", "marca", "modelo", "numero_serie", "proprietario", "status", "condicao",
    "tipo_computador", "computador_liga", "hd", "hd_modelo", "hd_tamanho",
    "ram_tipo", "ram_tamanho", "bateria", "teclado_funciona",
    "observacoes", "modificado_em", "modificado_por"
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
DROPDOWN_OPTIONS = {
    "proprietario": ["Capital Company", "Conmedi - Jardins", "Conmedi - Mauá", "Conmedi - Osaco", "Conmedi - Paulista", "Conmedi - Ribeirão Pires", "Conmedi - Santo Amaro", "Conmedi - Santo André", "Conmedi - São Caetano", "Conmedi - Vila Matilde", "Engrecon", "Engrecon - BPN", "Inova Contabildiade", "MIMO", "Pro Saúde", "Rede Gaya", "Quattro Construtora", "Sealset", "Servitec - Locação", "SL Assessoria", "Super Brilho"],
    "status": ["Está na Servitec", "KLV/ Aguardando aprovação", "KLV / Reparando", "KLV / Aguardando Retirada", "Está com o proprietário"],
    "marca": ["Apple", "Acer", "Dell", "HP", "Lenovo", "Positivo", "Samsung"],
    "condicao": ["Nova", "Estado de Nova", "Estado de Nova (Com avarias)", "Boa", "Quebrada"],
    "tipo_computador": ["Desktop", "Notebook"],
    "computador_liga": ["Sim", "Não", "Não verificado"],
}
COLUMN_WIDTHS = {
    "checkbox": 50, "patrimonio": 120, "marca": 150, "modelo": 150, "numero_serie": 150,
    "proprietario": 200, "status": 200, "condicao": 200, "tipo_computador": 150, "computador_liga": 150,
    "hd": 120, "hd_modelo": 150, "hd_tamanho": 150, "ram_tipo": 150, "ram_tamanho": 150,
    "bateria": 150, "teclado_funciona": 200, "observacoes": 250, "modificado_em": 150, "modificado_por": 250
}
TABLE_WIDTH = sum(COLUMN_WIDTHS.values())

def main(page: ft.Page):
    page.title = "Gerenciamento de Equipamentos Servitec"
    page.theme_mode = "light"
    page.padding = 0
    page.bgcolor = "#f0f2f5"

    def salvar_credenciais(email, password):
        page.client_storage.set("auth.email", email.strip())
        page.client_storage.set("auth.password", password)

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

    bg_image = ft.Image(src="banner_servitec.png", fit=ft.ImageFit.COVER, expand=True)
    itens_selecionados = []

    header_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"])]
    for col in COLUNAS:
        header_controls.append(
            ft.Container(
                content=ft.Text(COLUNAS_LABEL.get(col, col), weight=ft.FontWeight.BOLD, color="black54"),
                width=COLUMN_WIDTHS.get(col, 150),
                alignment=ft.alignment.center,
            )
        )
    header = ft.Container(content=ft.Row(controls=header_controls, spacing=0), bgcolor="#f8f9fa", height=40)
    body_list = ft.ListView(expand=True, spacing=0)

    def fechar_dialog(dialog_instance):
        dialog_instance.open = False
        page.update()

    def exibir_dialog(dialog):
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def atualizar_estado_botoes():
        num_selecionados = len(itens_selecionados)
        edit_btn.disabled = (num_selecionados != 1)
        delete_btn.disabled = (num_selecionados == 0)
        page.update()

    def selecionar_item(item_data, checkbox_control):
        nonlocal itens_selecionados
        item_info = {"data": item_data}
        if checkbox_control.value:
            if item_info not in itens_selecionados:
                itens_selecionados.append(item_info)
        else:
            itens_selecionados = [item for item in itens_selecionados if item["data"]["patrimonio"] != item_data["patrimonio"]]
        atualizar_estado_botoes()

    def formatar_data(iso_string):
        if not iso_string:
            return ""
        try:
            utc_dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
            return utc_dt.astimezone(sao_paulo_tz).strftime("%d/%m/%Y %H:%M")
        except:
            return iso_string

    def mostrar_observacao_completa(e, observacao_texto):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Observação Completa"),
            content=ft.Text(observacao_texto, selectable=True),
            actions=[ft.TextButton("Fechar", on_click=lambda e: fechar_dialog(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
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
                chk.on_change = (lambda item_data=item, chk_control=chk: lambda e: selecionar_item(item_data, chk_control))()

                row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"], content=chk, alignment=ft.alignment.center)]
                for c in COLUNAS:
                    valor = item.get(c, "")
                    valor_str = str(valor) if valor is not None else ""
                    if c == "modificado_em":
                        valor_str = formatar_data(valor_str)

                    cell_content = ft.Text(valor_str, no_wrap=True, size=12)
                    if c == "observacoes" and valor_str:
                        texto_display = (valor_str[:30] + "...") if len(valor_str) > 30 else valor_str
                        cell_content = ft.Container(
                            content=ft.Text(texto_display, no_wrap=True, size=12, italic=True),
                            tooltip=valor_str,
                            on_click=lambda e, texto_completo=valor_str: mostrar_observacao_completa(e, texto_completo),
                        )

                    row_controls.append(
                        ft.Container(
                            width=COLUMN_WIDTHS.get(c, 150),
                            content=cell_content,
                            alignment=ft.alignment.center,
                            border=ft.border.only(left=ft.border.BorderSide(1, "#dee2e6")),
                        )
                    )

                row_color = "#e9ecef" if i % 2 != 0 else "white"
                body_list.controls.append(ft.Container(content=ft.Row(controls=row_controls, spacing=0), bgcolor=row_color))
            page.update()
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao carregar dados"), content=ft.Text(str(ex))))

    # Placeholder para funções de CRUD
    def abrir_formulario(modo="add"): pass
    def excluir_selecionado(e): pass

    # --- FILTRO APRIMORADO ---
    filtros_ativos = []

    def atualizar_controles_filtro(e):
        coluna_selecionada = filtrar_dropdown.value
        coluna_db = LABEL_TO_COL.get(coluna_selecionada)
        if coluna_db in DROPDOWN_OPTIONS:
            localizar_input.visible = False
            valor_filtro_dropdown.visible = True
            valor_filtro_dropdown.options = [ft.dropdown.Option(opt) for opt in DROPDOWN_OPTIONS[coluna_db]]
            valor_filtro_dropdown.value = None
        else:
            localizar_input.visible = True
            valor_filtro_dropdown.visible = False
        page.update()

    def atualizar_lista_filtros():
        filtros_list.controls.clear()
        for f in filtros_ativos:
            filtros_list.controls.append(
                ft.Row(
                    [
                        ft.Text(f"{COLUNAS_LABEL.get(f['coluna'], f['coluna'])}: {f['valor']}"),
                        ft.IconButton(icon="close", icon_color="red", on_click=lambda e, f=f: remover_filtro(f)),
                    ],
                    spacing=5,
                )
            )
        page.update()

    def adicionar_filtro(e):
        coluna_label = filtrar_dropdown.value
        if not coluna_label or coluna_label == "Todas as Colunas":
            exibir_dialog(ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Selecione uma coluna específica.")))
            return

        coluna_db = LABEL_TO_COL[coluna_label]
        valor = valor_filtro_dropdown.value if valor_filtro_dropdown.visible else localizar_input.value.strip()
        if not valor:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Informe um valor.")))
            return

        for f in filtros_ativos:
            if f["coluna"] == coluna_db:
                f["valor"] = valor
                break
        else:
            filtros_ativos.append({"coluna": coluna_db, "valor": valor})

        localizar_input.value = ""
        valor_filtro_dropdown.value = None
        atualizar_lista_filtros()

    def remover_filtro(filtro):
        filtros_ativos.remove(filtro)
        atualizar_lista_filtros()

    def aplicar_filtros(e):
        try:
            query = supabase.table("inventario").select("*")
            for f in filtros_ativos:
                if f["coluna"] in DROPDOWN_OPTIONS:
                    query = query.eq(f["coluna"], f["valor"])
                else:
                    query = query.ilike(f["coluna"], f"%{f['valor']}%")
            query = query.order("patrimonio")
            carregar_dados(query)
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao aplicar filtro"), content=ft.Text(str(ex))))

    def limpar_filtros(e):
        filtros_ativos.clear()
        atualizar_lista_filtros()
        carregar_dados()

    # --- UI Principal ---
    opcoes_filtro = ["Todas as Colunas"] + list(COLUNAS_LABEL.values())
    filtrar_dropdown = ft.Dropdown(width=200, label="Filtrar por", options=[ft.dropdown.Option(opt) for opt in opcoes_filtro], value="Todas as Colunas", on_change=atualizar_controles_filtro)
    localizar_input = ft.TextField(width=200, label="Valor", on_submit=adicionar_filtro)
    valor_filtro_dropdown = ft.Dropdown(label="Valor", visible=False, width=200)

    filtros_list = ft.Column(spacing=5, scroll=ft.ScrollMode.ALWAYS)

    buscar_btn = ft.ElevatedButton("Buscar", icon="search", on_click=aplicar_filtros)
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear", on_click=limpar_filtros)
    adicionar_btn = ft.ElevatedButton("Adicionar Filtro", icon="add", on_click=adicionar_filtro)
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=lambda e: carregar_dados(None))
    add_btn = ft.ElevatedButton("Adicionar Novo", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", disabled=True, on_click=lambda e: abrir_formulario("edit"))
    delete_btn = ft.ElevatedButton("Excluir Selecionado", disabled=True, on_click=excluir_selecionado)

    filter_panel_left = ft.Container(
        content=ft.Column(
            [
                ft.Row([filtrar_dropdown, localizar_input, valor_filtro_dropdown, adicionar_btn, buscar_btn, limpar_btn, atualizar_btn], spacing=10, wrap=True),
                ft.Divider(),
                filtros_list,
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor="white",
        border_radius=8,
        top=40,
        left=40,
        visible=False,
    )

    filter_panel_right = ft.Container(
        content=ft.Row([add_btn, edit_btn, delete_btn], spacing=10, wrap=True),
        padding=20,
        bgcolor="white",
        border_radius=8,
        top=40,
        right=40,
        visible=False,
    )

    table_panel = ft.Container(
        content=ft.Row([ft.Column([header, body_list], width=TABLE_WIDTH, expand=True)], scroll=ft.ScrollMode.ALWAYS),
        bgcolor="white",
        border_radius=8,
        padding=10,
        top=390,
        left=40,
        right=40,
        height=340,
        visible=False,
    )

    # --- Login ---
    email_input = ft.TextField(label="Usuário", width=300, autofocus=True)
    password_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, on_submit=lambda e: handle_login(e))
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
                page.session.set("user_email", user_session.user.email)
                if lembrar_me_checkbox.value:
                    salvar_credenciais(email, password)
                else:
                    apagar_credenciais()

                login_view.visible = False
                filter_panel_left.visible = True
                filter_panel_right.visible = True
                table_panel.visible = True
                carregar_dados()
                page.update()
        except Exception as ex:
            print(f"ERRO NO LOGIN: {ex}")
            error_text.value = "Usuário ou senha inválidos."
            error_text.visible = True
            page.update()

    login_form = ft.Container(
        content=ft.Column([ft.Text("Login", size=30), email_input, password_input, lembrar_me_checkbox, ft.ElevatedButton("Entrar", on_click=handle_login)], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=400,
        padding=40,
        border_radius=10,
        bgcolor="white",
        shadow=ft.BoxShadow(blur_radius=10, color="black26"),
    )
    login_view = ft.Container(content=login_form, alignment=ft.alignment.center, expand=True, visible=True, bottom=150, left=0, right=0)

    page.add(ft.Stack([bg_image, login_view, filter_panel_left, filter_panel_right, table_panel]))
    carregar_credenciais()

# --- Execução ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", host="0.0.0.0", port=port)
