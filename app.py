import sqlite3

# --- Configuração do Banco ---
def conectar():
    return sqlite3.connect("sistema.db")

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Cria tabelas principais
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nome TEXT, data_nasc TEXT, email TEXT, cpf TEXT, telefone TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, preco REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY, cliente_id INTEGER, total REAL, data TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS itens_venda (id INTEGER PRIMARY KEY, venda_id INTEGER, produto_id INTEGER, quantidade INTEGER)')
    
    # Atualiza tabela produtos para ter colunas novas
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Usuário padrão
    cursor.execute("SELECT count(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ('admin', '1234'))
    
    conn.commit()
    conn.close()

# --- Funções do Sistema ---
def autenticar(user, pwd):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def cadastrar_cliente(nome, data_nasc, email, cpf, telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, data_nasc, email, cpf, telefone) VALUES (?, ?, ?, ?, ?)", 
                   (nome, data_nasc, email, cpf, telefone))
    conn.commit()
    conn.close()
    print("✅ Cliente cadastrado com sucesso!")

def cadastrar_produto(nome, preco, imagem, categoria):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco, imagem, categoria) VALUES (?, ?, ?, ?)", (nome, preco, imagem, categoria))
    conn.commit()
    conn.close()
    print("✅ Produto cadastrado com sucesso!")

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    print("\n--- Catálogo de Produtos ---")
    for p in produtos:
        print(f"ID: {p[0]} | Nome: {p[1]} | Preço: R${p[2]:.2f} | Imagem: {p[3]} | Categoria: {p[4]}")
    return produtos

def registrar_venda(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    produtos = listar_produtos()
    if not produtos:
        print("⚠️ Nenhum produto cadastrado!")
        conn.close()
        return

    itens = []
    total = 0.0

    while True:
        produto_id = input("Digite o ID do produto (ou ENTER para finalizar): ")
        if produto_id == "":
            break
        
        try:
            quantidade = int(input("Quantidade: "))
        except ValueError:
            print("⚠️ Quantidade inválida! Digite um número inteiro.")
            continue

        cursor.execute("SELECT preco FROM produtos WHERE id=?", (produto_id,))
        resultado = cursor.fetchone()
        if resultado:
            preco = resultado[0]
            subtotal = preco * quantidade
            total += subtotal
            itens.append((produto_id, quantidade))
            print(f"✔ Produto adicionado! Subtotal: R${subtotal:.2f}")
        else:
            print("⚠️ Produto não encontrado!")

    if total == 0:
        print("⚠️ Nenhum item foi adicionado à venda.")
        conn.close()
        return

    cursor.execute("INSERT INTO vendas (cliente_id, total, data) VALUES (?, ?, DATE('now'))", (cliente_id, total))
    venda_id = cursor.lastrowid

    for produto_id, quantity in itens:
        cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade) VALUES (?, ?, ?)", (venda_id, produto_id, quantity))

    conn.commit()
    conn.close()
    print(f"✅ Venda registrada com sucesso! Total: R${total:.2f}")

# --- Menu Principal ---
if __name__ == "__main__":
    inicializar_banco()
    
    print("--- Bem-vindo ao SisVenda ---")
    user = input("Usuário: ")
    pwd = input("Senha: ")

    if autenticar(user, pwd):
        print("\n🔓 Login realizado com sucesso!")
        while True:
            print("\n--- MENU ---")
            print("1. Cadastrar Cliente")
            print("2. Cadastrar Produto")
            print("3. Listar Produtos")
            print("4. Registrar Venda")
            print("5. Sair")
            opcao = input("Escolha uma opção: ")
            
            if opcao == '1':
                nome = input("Nome: ")
                data_nasc = input("Data de Nascimento (DD/MM/AAAA): ")
                email = input("Email: ")
                cpf = input("CPF: ")
                telefone = input("Telefone: ")
                cadastrar_cliente(nome, data_nasc, email, cpf, telefone)
                
            elif opcao == '2':
                nome_prod = input("Nome do produto: ")
                try:
                    preco_prod = float(input("Preço: "))
                    imagem_prod = input("Caminho/URL da imagem: ")
                    categoria_prod = input("Categoria (Roupas, Calçados, Eletrônicos...): ")
                    cadastrar_produto(nome_prod, preco_prod, imagem_prod, categoria_prod)
                except ValueError:
                    print("⚠️ Preço inválido! Use pontos para centavos (Ex: 10.50).")
                    
            elif opcao == '3':
                listar_produtos()
                
            elif opcao == '4':
                id_cliente = input("ID do Cliente: ")
                registrar_venda(id_cliente)

            elif opcao == '5':
                print("👋 Saindo...")
                break
            else:
                print("⚠️ Opção inválida!")
    else:
        print("❌ Acesso negado! Usuário ou senha incorretos.")