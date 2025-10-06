import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from functools import wraps

# --- Configuração ---
app = Flask(__name__)

# IMPORTANTE: Configura a chave secreta para a sessão de login
# Vamos adicionar essa variável no Render
app.secret_key = os.getenv("SECRET_KEY")

# Conexão com Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Opções dos Dropdowns
DROPDOWN_OPTIONS = {
    # ... seu dicionário de opções continua aqui ...
}


# --- Lógica de Autenticação ---

def login_required(f):
    """ Decorator para proteger rotas que exigem login. """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Rota para a página de login e para processar o login. """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Usa a autenticação do Supabase
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user'] = user_session.user.email # Armazena o email do usuário na sessão
            return redirect(url_for('home'))
        except Exception:
            flash('Email ou senha inválidos.') # Mostra uma mensagem de erro
            return redirect(url_for('login'))
    
    # Se for GET, apenas mostra a página de login
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ Rota para fazer logout. """
    session.clear() # Limpa a sessão
    return redirect(url_for('login'))


# --- Rotas da Aplicação (Agora Protegidas) ---

@app.route('/')
@login_required # Protege a rota principal
def home():
    try:
        response = supabase.table('inventario').select('*').order('modificado_em', desc=True).execute()
        inventario = response.data
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        inventario = []
    return render_template('index.html', inventario=inventario, dropdown_options=DROPDOWN_OPTIONS)

@app.route('/add', methods=['POST'])
@login_required # Protege a rota de adicionar
def add_item():
    try:
        novo_item = { 'patrimonio': request.form.get('patrimonio'), 'marca': request.form.get('marca'), 'modelo': request.form.get('modelo'), 'numero_serie': request.form.get('numero_serie'), 'proprietario': request.form.get('proprietario'), 'status': request.form.get('status'), 'condicao': request.form.get('condicao'), 'tipo_computador': request.form.get('tipo_computador'), 'observacoes': request.form.get('observacoes'), 'modificado_por': session.get('user') }
        supabase.table('inventario').insert(novo_item).execute()
    except Exception as e:
        print(f"Erro ao adicionar item: {e}")
    return redirect(url_for('home'))

@app.route('/edit/<patrimonio>', methods=['POST'])
@login_required # Protege a rota de editar
def edit_item(patrimonio):
    try:
        item_atualizado = { 'marca': request.form.get('marca'), 'modelo': request.form.get('modelo'), 'numero_serie': request.form.get('numero_serie'), 'proprietario': request.form.get('proprietario'), 'status': request.form.get('status'), 'condicao': request.form.get('condicao'), 'tipo_computador': request.form.get('tipo_computador'), 'observacoes': request.form.get('observacoes'), 'modificado_por': session.get('user') }
        supabase.table('inventario').update(item_atualizado).eq('patrimonio', patrimonio).execute()
    except Exception as e:
        print(f"Erro ao editar item: {e}")
    return redirect(url_for('home'))

@app.route('/delete/<patrimonio>', methods=['POST'])
@login_required # Protege a rota de excluir
def delete_item(patrimonio):
    try:
        supabase.table('inventario').delete().eq('patrimonio', patrimonio).execute()
    except Exception as e:
        print(f"Erro ao excluir item: {e}")
    return redirect(url_for('home'))


# --- Execução do Servidor ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
