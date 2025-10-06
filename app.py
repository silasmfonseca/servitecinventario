import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

# --- Configuração ---
app = Flask(__name__)

# Conexão com Supabase usando as variáveis de ambiente do Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Rotas da Aplicação ---

@app.route('/')
def home():
    """ Rota principal: busca todos os itens e exibe na tabela. """
    try:
        # Ordena pelo patrimônio para manter a consistência
        response = supabase.table('inventario').select('*').order('patrimonio').execute()
        inventario = response.data
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        inventario = []
    return render_template('index.html', inventario=inventario)

@app.route('/add', methods=['POST'])
def add_item():
    """ Rota para adicionar um novo item. """
    try:
        # Pega os dados do formulário enviado pelo modal "Adicionar"
        novo_item = {
            'patrimonio': request.form.get('patrimonio'),
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'proprietario': request.form.get('proprietario'),
            'status': request.form.get('status'),
            'modificado_por': 'webapp' # Exemplo de campo extra
        }
        supabase.table('inventario').insert(novo_item).execute()
    except Exception as e:
        print(f"Erro ao adicionar item: {e}")
    # Redireciona de volta para a página principal para atualizar a tabela
    return redirect(url_for('home'))

@app.route('/edit/<patrimonio>', methods=['POST'])
def edit_item(patrimonio):
    """ Rota para editar um item existente. """
    try:
        # Pega os dados do formulário enviado pelo modal "Editar"
        item_atualizado = {
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'proprietario': request.form.get('proprietario'),
            'status': request.form.get('status'),
            'modificado_por': 'webapp'
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