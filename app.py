import sqlite3

# --- Configuração do Banco ---
def conectar():
    return sqlite3.connect("sistema.db")

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    # Cria as tabelas
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nome TEXT, email TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, preco REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY, cliente_id INTEGER, total REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS itens_venda (id INTEGER PRIMARY KEY, venda_id INTEGER, produto_id INTEGER, quantidade INTEGER)')
   
    # Cria um usuário padrão se não existir nenhum
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

def cadastrar_cliente(nome, email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, email) VALUES (?, ?)", (nome, email))
    conn.commit()
    conn.close()
    print("✅ Cliente cadastrado com sucesso!")

def cadastrar_produto(nome, preco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
    conn.commit()
    conn.close()
    print("✅ Produto cadastrado com sucesso!")

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    print("\n--- Produtos Disponíveis ---")
    for p in produtos:
        print(f"ID: {p[0]} | Nome: {p[1]} | Preço: R${p[2]:.2f}")
    return produtos

def registrar_venda(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    # Lista produtos disponíveis
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
        quantidade = int(input("Quantidade: "))

        # Busca preço do produto
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

    # Registra venda
    cursor.execute("INSERT INTO vendas (cliente_id, total) VALUES (?, ?)", (cliente_id, total))
    venda_id = cursor.lastrowid

    # Registra itens da venda
    for produto_id, quantidade in itens:
        cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade) VALUES (?, ?, ?)", (venda_id, produto_id, quantidade))

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
            print("3. Registrar Venda")
            print("4. Sair")
            opcao = input("Escolha uma opção: ")
           
            if opcao == '1':
                cadastrar_cliente(input("Nome: "), input("Email: "))
            elif opcao == '2':
                cadastrar_produto(input("Nome do produto: "), float(input("Preço: ")))
            elif opcao == '3':
                registrar_venda(input("ID do Cliente: "))
            elif opcao == '4':
                print("👋 Saindo...")
                break
            else:
                print("⚠️ Opção inválida!")
    else:
        print("❌ Acesso negado! Usuário ou senha incorretos.")

