import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

# --- Configuração ---
app = Flask(__name__)

# Conexão com Supabase usando as variáveis de ambiente do Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Opções dos Dropdowns (Copiado do seu projeto original) ---
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
    "computador_liga": ["Sim", "Não", "Não verificado"],
    "bateria": ["Sim", "Não", "Não verificado"],
    "teclado_funciona": ["Sim", "Não", "Não verificado"],
}

# --- Rotas da Aplicação ---

@app.route('/')
def home():
    """ Rota principal: busca todos os itens e exibe na tabela. """
    try:
        # MUDANÇA: Ordenando pela data de modificação, do mais recente para o mais antigo
        response = supabase.table('inventario').select('*').order('modificado_em', desc=True).execute()
        inventario = response.data
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        inventario = []
    return render_template('index.html', inventario=inventario, dropdown_options=DROPDOWN_OPTIONS)

@app.route('/add', methods=['POST'])
def add_item():
    """ Rota para adicionar um novo item com todos os campos. """
    try:
        novo_item = {
            'patrimonio': request.form.get('patrimonio'),
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'numero_serie': request.form.get('numero_serie'),
            'proprietario': request.form.get('proprietario'),
            'status': request.form.get('status'),
            'condicao': request.form.get('condicao'),
            'tipo_computador': request.form.get('tipo_computador'),
            'observacoes': request.form.get('observacoes'),
            'modificado_por': 'webapp' # No futuro, pode ser o email do usuário logado
        }
        supabase.table('inventario').insert(novo_item).execute()
    except Exception as e:
        print(f"Erro ao adicionar item: {e}")
    return redirect(url_for('home'))

@app.route('/edit/<patrimonio>', methods=['POST'])
def edit_item(patrimonio):
    """ Rota para editar um item existente com todos os campos. """
    try:
        item_atualizado = {
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'numero_serie': request.form.get('numero_serie'),
            'proprietario': request.form.get('proprietario'),
            'status': request.form.get('status'),
            'condicao': request.form.get('condicao'),
            'tipo_computador': request.form.get('tipo_computador'),
            'observacoes': request.form.get('observacoes'),
            'modificado_por': 'webapp' # No futuro, pode ser o email do usuário logado
        }
        supabase.table('inventario').update(item_atualizado).eq('patrimonio', patrimonio).execute()
    except Exception as e:
        print(f"Erro ao editar item: {e}")
    return redirect(url_for('home'))

@app.route('/delete/<patrimonio>', methods=['POST'])
def delete_item(patrimonio):
    """ Rota para excluir um item. """
    try:
        supabase.table('inventario').delete().eq('patrimonio', patrimonio).execute()
    except Exception as e:
        print(f"Erro ao excluir item: {e}")
    return redirect(url_for('home'))


# --- Execução do Servidor ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
