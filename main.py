import flet as ft
from supabase import create_client, Client
import pytz
import os

# --- CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÃO PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Inventário Servitec"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F5F5F5"

    # --- BANNER ---
    banner = ft.Image(
        src="assets/banner_servitec.png",
        fit=ft.ImageFit.COVER,
        height=250,
        width=page.width,
    )

    # --- CAMPOS DE LOGIN ---
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    login_message = ft.Text(value="", color="red")

    def login_click(e):
        email = email_field.value.strip()
        password = password_field.value.strip()
        if not email or not password:
            login_message.value = "Preencha todos os campos."
            page.update()
            return

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                login_view.visible = False
                table_panel.visible = True
                load_data()
                page.update()
            else:
                login_message.value = "Credenciais inválidas."
                page.update()
        except Exception as ex:
            login_message.value = f"Erro ao conectar: {ex}"
            page.update()

    login_button = ft.ElevatedButton("Entrar", on_click=login_click, width=300)
    login_form = ft.Column(
        [
            email_field,
            password_field,
            login_button,
            login_message
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # --- LOGIN VIEW ---
    login_view = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=220),  # espaço para o banner
                ft.Container(
                    content=login_form,
                    alignment=ft.alignment.center,
                    border_radius=10,
                    padding=40,
                    bgcolor="white",
                    shadow=ft.BoxShadow(blur_radius=10, color="black26"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        bgcolor="transparent",
        visible=True,
    )

    # --- LISTA DE EQUIPAMENTOS ---
    body_list = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=False)

    def load_data():
        body_list.controls.clear()
        try:
            data = supabase.table("equipamentos").select("*").execute().data
            for item in data:
                row = ft.Row(
                    controls=[
                        ft.Text(item["nome"], expand=2),
                        ft.Text(item["categoria"], expand=1),
                        ft.Text(item["status"], expand=1),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                body_list.controls.append(
                    ft.Container(content=row, padding=10, border=ft.border.all(1, "#DDD"), border_radius=5)
                )
        except Exception as e:
            body_list.controls.append(ft.Text(f"Erro ao carregar dados: {e}", color="red"))
        page.update()

    # --- CABEÇALHO TABELA ---
    header = ft.Row(
        controls=[
            ft.Text("Nome", expand=2, weight=ft.FontWeight.BOLD),
            ft.Text("Categoria", expand=1, weight=ft.FontWeight.BOLD),
            ft.Text("Status", expand=1, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # --- PAINEL DA TABELA ---
    table_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(content=header, padding=ft.padding.only(bottom=10)),
                ft.Container(
                    content=body_list,
                    expand=True,
                    scroll=ft.ScrollMode.ALWAYS,
                )
            ],
            spacing=0,
        ),
        bgcolor="white",
        border_radius=8,
        padding=20,
        margin=ft.margin.only(top=20, left=40, right=40, bottom=20),
        expand=True,
        visible=False,
    )

    # --- LAYOUT FINAL ---
    layout = ft.Column(
        [
            banner,
            login_view,
            table_panel
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    page.add(layout)

# --- EXECUÇÃO ---
ft.app(target=main)
