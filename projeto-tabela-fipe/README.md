# Tabela FIPE

Este projeto consiste em uma interface similar à de consulta de preços na tabela FIPE. Além da tela para o usuário comum, a aplicação permite login via Google e disponibiliza páginas específicas para gestores e pesquisadores de preços.

## Requisitos

Antes de executar o projeto, certifique-se de ter o Python instalado em sua máquina. Recomendamos o uso de um ambiente virtual para gerenciar as dependências.

## Instalação

Siga os passos abaixo para configurar o ambiente e executar a aplicação:

1. Clone este repositório:
   ```bash
   git clone https://github.com/heloeng/projeto-tabela-fipe.git
   cd projeto-tabela-fipe
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows use: .venv\Scripts\activate
   ```

3. Instale o Streamlit:
   ```bash
   pip install streamlit
   ```

4. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```

## Execução

Para iniciar a aplicação, execute o seguinte comando:
```bash
streamlit run tela_inicial.py
```

## Contribuição

Caso queira contribuir com o projeto, sinta-se à vontade para abrir um Pull Request ou relatar problemas na seção de Issues.

