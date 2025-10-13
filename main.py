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

# --- Constantes Completas do seu código original ---
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
    "bateria": ["Sim", "Não", "Não verificado"],
    "teclado_funciona": ["Sim", "Não", "Não verificado"],
    "hd": ["SSD", "HD"],
    "hd_tamanho": ["120 GB", "240 GB", "256 GB", "480 GB", "500 GB", "512 GB", "1 TB", "2 TB"],
    "ram_tipo": ["DDR3", "DDR4", "DDR5"],
    "ram_tamanho": ["2 GB", "4 GB", "8 GB", "16 GB", "32 GB"]
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

    # --- Variáveis de Estado ---
    itens_selecionados = []
    active_filters = {}
    header_controls = {}

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
            if item_info not in itens_selecionados: itens_selecionados.append(item_info)
        else:
            itens_selecionados = [item for item in itens_selecionados if item["data"]["patrimonio"] != item_data["patrimonio"]]
        atualizar_estado_botoes()

    def formatar_data(iso_string):
        if not iso_string: return ""
        try:
            utc_dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
            return utc_dt.astimezone(sao_paulo_tz).strftime("%d/%m/%Y %H:%M")
        except: return iso_string
        
    def mostrar_observacao_completa(e, observacao_texto):
        dlg = ft.AlertDialog(modal=True, title=ft.Text("Observação Completa"), content=ft.Text(observacao_texto, selectable=True), actions=[ft.TextButton("Fechar", on_click=lambda e: fechar_dialog(dlg))], actions_alignment=ft.MainAxisAlignment.END)
        exibir_dialog(dlg)

    def atualizar_icones_filtro():
        for col, control_dict in header_controls.items():
            if col in COLUNAS:
                icon_btn = control_dict['icon']
                icon_btn.icon_color = "blue600" if col in active_filters else "black26"
        page.update()

    def abrir_dialog_filtro(e, column_name):
        try:
            response = supabase.table("inventario").select(column_name).execute()
            valores_unicos = sorted(list(set(item[column_name] for item in response.data if item[column_name] not in [None, ""])))
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text(f"Erro ao buscar valores para {column_name}"), content=ft.Text(str(ex))))
            return

        checkboxes = [ft.Checkbox(label=str(valor), value=(valor in active_filters.get(column_name, []))) for valor in valores_unicos]
        
        def aplicar_filtro_coluna(e):
            valores_selecionados = [cb.label for cb in checkboxes if cb.value]
            if valores_selecionados:
                active_filters[column_name] = valores_selecionados
            elif column_name in active_filters:
                del active_filters[column_name]
            
            fechar_dialog(dlg)
            atualizar_icones_filtro()
            carregar_dados()

        def limpar_filtro_coluna(e):
            if column_name in active_filters:
                del active_filters[column_name]
            fechar_dialog(dlg)
            atualizar_icones_filtro()
            carregar_dados()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Filtrar por {COLUNAS_LABEL.get(column_name, column_name)}"),
            content=ft.Container(
                content=ft.Column(controls=checkboxes, scroll="auto"),
                height=300, width=400
            ),
            actions=[
                ft.TextButton("Limpar Filtro", on_click=limpar_filtro_coluna),
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialog(dlg)),
                ft.ElevatedButton("Aplicar", on_click=aplicar_filtro_coluna)
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        exibir_dialog(dlg)

    def carregar_dados(e=None):
        try:
            body_list.controls.clear()
            itens_selecionados.clear()
            atualizar_estado_botoes()
            
            query = supabase.table("inventario").select("*").order("patrimonio")

            for column, values in active_filters.items():
                if values:
                    query = query.in_(column, values)

            search_term = localizar_input.value.strip()
            filter_column_label = filtrar_dropdown.value
            
            if search_term:
                if filter_column_label == "Todas as Colunas":
                    or_filters = [f"{col}.ilike.%{search_term}%" for col in COLUNAS if col not in ['modificado_em']]
                    query = query.or_(",".join(or_filters))
                else:
                    column_name = LABEL_TO_COL.get(filter_column_label)
                    if column_name:
                        query = query.ilike(column_name, f"%{search_term}%")

            registros = query.execute().data or []
            
            for i, item in enumerate(registros):
                chk = ft.Checkbox()
                chk.on_change = (lambda item_data=item, chk_control=chk: lambda e: selecionar_item(item_data, chk_control))()
                
                row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"], content=chk, alignment=ft.alignment.center)]
                for c in COLUNAS:
                    valor = item.get(c, "")
                    valor_str = str(valor) if valor is not None else ""
                    if c == "modificado_em": valor_str = formatar_data(valor_str)
                    
                    cell_content = ft.Text(valor_str, no_wrap=True, size=12)
                    if c == "observacoes" and valor_str:
                        texto_display = (valor_str[:30] + '...') if len(valor_str) > 30 else valor_str
                        cell_content = ft.Container(
                            content=ft.Text(texto_display, no_wrap=True, size=12, italic=True),
                            tooltip=valor_str,
                            on_click=lambda e, texto_completo=valor_str: mostrar_observacao_completa(e, texto_completo)
                        )
                    row_controls.append(ft.Container(width=COLUMN_WIDTHS.get(c, 150), content=cell_content, alignment=ft.alignment.center, border=ft.border.only(left=ft.border.BorderSide(1, "#dee2e6"))))
                
                row_color = "#e9ecef" if i % 2 != 0 else "white"
                body_list.controls.append(ft.Container(content=ft.Row(controls=row_controls, spacing=0), bgcolor=row_color))
            page.update()
        except Exception as ex:
            exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao carregar dados"), content=ft.Text(str(ex))))

    # --- Criação do Cabeçalho com Filtros ---
    header_row_controls = [ft.Container(width=COLUMN_WIDTHS["checkbox"])]
    for col in COLUNAS:
        filter_icon = ft.IconButton(
            icon="filter_alt_outlined",  # <<< CORREÇÃO APLICADA AQUI
            icon_size=16,
            icon_color="black26",
            on_click=lambda e, c=col: abrir_dialog_filtro(e, c),
            tooltip=f"Filtrar por {COLUNAS_LABEL.get(col, col)}"
        )
        header_controls[col] = {
            "text": ft.Text(COLUNAS_LABEL.get(col, col), weight=ft.FontWeight.BOLD, color="black54"),
            "icon": filter_icon
        }
        header_row_controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[header_controls[col]["text"], header_controls[col]["icon"]],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                width=COLUMN_WIDTHS.get(col, 150),
                alignment=ft.alignment.center
            )
        )
    header = ft.Container(content=ft.Row(controls=header_row_controls, spacing=0), bgcolor="#f8f9fa", height=40)

    def abrir_formulario(modo="add"):
        valores = {}; 
        if modo == "edit":
            if not itens_selecionados: return
            valores = itens_selecionados[0]["data"]
        
        campos_visiveis = [c for c in COLUNAS if c not in ["modificado_em", "modificado_por"]]
        campos = {}
        error_text_in_dialog = ft.Text(value="", color="red", visible=False)
        lista_de_controles = [error_text_in_dialog]
        
        for c in campos_visiveis:
            valor_atual = valores.get(c); valor_str = "" if valor_atual is None else str(valor_atual)
            control_criado = None
            if c in DROPDOWN_OPTIONS:
                control_criado = ft.Dropdown(label=COLUNAS_LABEL.get(c,c), options=[ft.dropdown.Option(opt) for opt in DROPDOWN_OPTIONS.get(c, [])], value=valor_str if valor_str in DROPDOWN_OPTIONS.get(c, []) else None, width=450)
            else:
                control_criado = ft.TextField(label=COLUNAS_LABEL.get(c,c), value=valor_str, width=450)
            campos[c] = control_criado
            lista_de_controles.append(control_criado)
        
        dlg = ft.AlertDialog()
        def salvar(e):
            dados_formulario = {c: campos[c].value for c in campos}
            dados_formulario['modificado_por'] = page.session.get('user_email')
            if not dados_formulario.get("patrimonio"):
                error_text_in_dialog.value = "O campo 'Patrimônio' é obrigatório."; error_text_in_dialog.visible = True
                dlg.content.update(); return
            try:
                if modo == "add": supabase.table("inventario").insert(dados_formulario).execute()
                else:
                    patrimonio_original = valores.get("patrimonio")
                    if str(dados_formulario.get("patrimonio")) != str(patrimonio_original):
                        error_text_in_dialog.value = "Não é permitido alterar o Patrimônio na edição."; error_text_in_dialog.visible = True
                        dlg.content.update(); return
                    supabase.table("inventario").update(dados_formulario).eq("patrimonio", patrimonio_original).execute()
                fechar_dialog(dlg); carregar_dados()
            except Exception as ex:
                error_text_in_dialog.value = f"Erro ao salvar: {ex}"; error_text_in_dialog.visible = True
                dlg.content.update()

        dlg.modal=True; dlg.title=ft.Text("Adicionar Equipamento" if modo == "add" else "Editar Equipamento")
        dlg.content=ft.Column(lista_de_controles, scroll="auto", height=400, width=500, spacing=10)
        dlg.actions=[ft.TextButton("Cancelar", on_click=lambda e: fechar_dialog(dlg)), ft.ElevatedButton("Salvar", on_click=salvar)]
        dlg.actions_alignment="end"; exibir_dialog(dlg)

    def excluir_selecionado(e):
        if not itens_selecionados: return
        patrimonios_para_excluir = [item["data"]["patrimonio"] for item in itens_selecionados]
        
        confirm_dlg = ft.AlertDialog()
        def confirmar(ev):
            try:
                supabase.table("inventario").delete().in_("patrimonio", patrimonios_para_excluir).execute()
                fechar_dialog(confirm_dlg); carregar_dados()
            except Exception as ex:
                exibir_dialog(ft.AlertDialog(title=ft.Text("Erro ao excluir"), content=ft.Text(str(ex))))
        
        confirm_dlg.modal=True; confirm_dlg.title=ft.Text("Confirmar Exclusão")
        confirm_dlg.content=ft.Text(f"Tem certeza que deseja excluir {len(patrimonios_para_excluir)} item(ns)?")
        confirm_dlg.actions=[ft.TextButton("Cancelar", on_click=lambda e: fechar_dialog(confirm_dlg)), ft.ElevatedButton("Excluir", on_click=confirmar)]
        exibir_dialog(confirm_dlg)
        
    def limpar_filtro(e):
        localizar_input.value = ""
        filtrar_dropdown.value = "Todas as Colunas"
        active_filters.clear()
        atualizar_icones_filtro()
        carregar_dados()

    # --- UI Principal ---
    opcoes_filtro = ["Todas as Colunas"] + list(COLUNAS_LABEL.values())
    filtrar_dropdown = ft.Dropdown(width=200, label="Filtrar por", options=[ft.dropdown.Option(opt) for opt in opcoes_filtro], value="Todas as Colunas")
    localizar_input = ft.TextField(width=200, label="Localizar", on_submit=carregar_dados)
    buscar_btn = ft.ElevatedButton("Buscar", icon="search", on_click=carregar_dados)
    limpar_btn = ft.ElevatedButton("Limpar", icon="clear", on_click=limpar_filtro)
    atualizar_btn = ft.ElevatedButton("Atualizar", icon="refresh", on_click=carregar_dados)
    add_btn = ft.ElevatedButton("Adicionar Novo", on_click=lambda e: abrir_formulario("add"))
    edit_btn = ft.ElevatedButton("Editar Selecionado", disabled=True, on_click=lambda e: abrir_formulario("edit"))
    delete_btn = ft.ElevatedButton("Excluir Selecionado", disabled=True, on_click=excluir_selecionado)

    filter_panel_left = ft.Container(
        content=ft.Row([filtrar_dropdown, localizar_input, buscar_btn, limpar_btn, atualizar_btn], spacing=10, wrap=True),
        padding=20, bgcolor="white", border_radius=8,
        top=40, left=40,
        visible=False 
    )

    filter_panel_right = ft.Container(
        content=ft.Row([add_btn, edit_btn, delete_btn], spacing=10, wrap=True),
        padding=20, bgcolor="white", border_radius=8,
        top=40, right=40,
        visible=False
    )

    table_panel = ft.Container(
        content=ft.Row(
            [ft.Column([header, body_list], width=TABLE_WIDTH, expand=True)], 
            scroll=ft.ScrollMode.ALWAYS, 
        ),
        bgcolor="white", border_radius=8, padding=10,
        top=140,
        left=40, right=40, bottom=40,
        visible=False 
    )

    # --- UI de Login ---
    email_input = ft.TextField(label="Usuário", width=300, autofocus=True)
    password_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, on_submit=lambda e: handle_login(e))
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

    login_form = ft.Container(content=ft.Column([ft.Text("Login", size=30), email_input, password_input, lembrar_me_checkbox, ft.ElevatedButton("Entrar", on_click=handle_login), error_text], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=400, padding=40, border_radius=10, bgcolor="white", shadow=ft.BoxShadow(blur_radius=10, color="black26"))
    login_view = ft.Container(
        content=login_form, 
        alignment=ft.alignment.center,
        expand=True,
        visible=True
    )
    
    page.add(
        ft.Stack([
            bg_image,
            login_view,
            filter_panel_left,
            filter_panel_right,
            table_panel
        ])
    )
    
    carregar_credenciais()

# --- Bloco de Execução para WEB ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", host="0.0.0.0", port=port)
