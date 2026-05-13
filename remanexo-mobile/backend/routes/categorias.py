from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from ..database import db, CategoriaModel, PalavraChaveModel

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# ═══════════════════════════════════════════════════════
# LISTAR CATEGORIAS
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_categorias():
    """lista todas as categorias com suas palavras-chave (rf06)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    categorias = CategoriaModel.query.all()
    return render_template('categorias.html', categorias=categorias)


# ═══════════════════════════════════════════════════════
# CRIAR CATEGORIA
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['POST'])
def criar_categoria():
    """cria uma nova categoria (rf06)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    nome = request.form.get('nome', '').strip().lower()
    cor = request.form.get('cor', '#6b7280').strip()

    if not nome or len(nome) < 2:
        flash('❌ nome da categoria deve ter pelo menos 2 caracteres', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    # valida se já existe
    if CategoriaModel.query.filter_by(nome=nome).first():
        flash(f'❌ categoria "{nome}" já existe', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    # cria categoria nova
    categoria = CategoriaModel(nome=nome, cor=cor)
    db.session.add(categoria)
    db.session.commit()

    flash(f'✅ categoria "{nome}" criada com sucesso', 'sucesso')
    return redirect(url_for('categorias.listar_categorias'))


# ═══════════════════════════════════════════════════════
# ADICIONAR PALAVRA-CHAVE
# ═══════════════════════════════════════════════════════

@bp.route('/<int:categoria_id>/palavras', methods=['POST'])
def adicionar_palavra(categoria_id):
    """adiciona palavra-chave a uma categoria (rf06)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    categoria = CategoriaModel.query.get(categoria_id)
    if not categoria:
        flash('❌ categoria não encontrada', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    palavra = request.form.get('palavra', '').strip().lower()

    if not palavra or len(palavra) < 2:
        flash('❌ palavra deve ter pelo menos 2 caracteres', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    # valida duplicata — salva sempre em minúsculo pra não ter problema no match
    if PalavraChaveModel.query.filter_by(palavra=palavra, categoria_id=categoria_id).first():
        flash(f'❌ palavra "{palavra}" já existe nesta categoria', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    # adiciona palavra
    palavra_chave = PalavraChaveModel(palavra=palavra, categoria_id=categoria_id)
    db.session.add(palavra_chave)
    db.session.commit()

    flash(f'✅ palavra "{palavra}" adicionada à categoria "{categoria.nome}"', 'sucesso')
    return redirect(url_for('categorias.listar_categorias'))


# ═══════════════════════════════════════════════════════
# DELETAR PALAVRA-CHAVE
# ═══════════════════════════════════════════════════════

@bp.route('/palavras/<int:palavra_id>', methods=['POST'])
def deletar_palavra(palavra_id):
    """remove uma palavra-chave específica"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    palavra = PalavraChaveModel.query.get(palavra_id)
    if not palavra:
        flash('❌ palavra não encontrada', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    palavra_texto = palavra.palavra
    categoria_nome = palavra.categoria.nome

    db.session.delete(palavra)
    db.session.commit()

    flash(f'✅ palavra "{palavra_texto}" removida de "{categoria_nome}"', 'sucesso')
    return redirect(url_for('categorias.listar_categorias'))


# ═══════════════════════════════════════════════════════
# DELETAR CATEGORIA
# ═══════════════════════════════════════════════════════

@bp.route('/<int:categoria_id>', methods=['POST'])
def deletar_categoria(categoria_id):
    """deleta uma categoria (cascade apaga as palavras junto)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    categoria = CategoriaModel.query.get(categoria_id)
    if not categoria:
        flash('❌ categoria não encontrada', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    # 'outros' é sagrada, não deixa deletar
    if categoria.nome == 'outros':
        flash('❌ não pode deletar a categoria "outros" (sagrada)', 'erro')
        return redirect(url_for('categorias.listar_categorias'))

    nome = categoria.nome
    db.session.delete(categoria)  # cascade garante que as palavras somem junto
    db.session.commit()

    flash(f'✅ categoria "{nome}" deletada com sucesso', 'sucesso')
    return redirect(url_for('categorias.listar_categorias'))
