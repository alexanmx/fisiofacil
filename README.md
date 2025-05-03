# Tutorial de Instalação do Projeto Django com PostgreSQL

Este tutorial guia você através do processo de instalação e execução do projeto Django em seu ambiente local, utilizando o PostgreSQL como banco de dados.

## Pré-requisitos

* Python 3.x instalado
* Pip (gerenciador de pacotes do Python) instalado
* Virtualenv (opcional, mas recomendado) instalado
* PostgreSQL instalado

## Passos de Instalação

1.  **Clone o Repositório (se aplicável):**

    * Se o projeto estiver em um repositório Git, clone-o para sua máquina local:

    ```bash
    git clone <URL_DO_REPOSITÓRIO>
    cd <NOME_DO_PROJETO>
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**

    * Crie um ambiente virtual para isolar as dependências do projeto:

    ```bash
    python -m venv venv
    ```

    * Ative o ambiente virtual:

        * No Linux/macOS:

        ```bash
        source venv/bin/activate
        ```

        * No Windows:

        ```bash
        venv\Scripts\activate
        ```

3.  **Instale as Dependências:**

    * Instale as dependências do projeto a partir do arquivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

    * Se você não tiver um arquivo `requirements.txt`, instale as dependências manualmente:

    ```bash
    pip install django djangorestframework psycopg2-binary requests
    ```

4.  **Configure o PostgreSQL:**

    * Crie um banco de dados e um usuário para seu projeto no PostgreSQL:

    ```bash
    sudo -u postgres psql
    CREATE DATABASE fisiofacil_api;
    CREATE USER default_user WITH PASSWORD 'default_password';
    GRANT ALL PRIVILEGES ON DATABASE fisiofacil_api TO default_user;
    \q
    ```


5.  **Configure o Django para usar o PostgreSQL:**

    * Abra o arquivo `fisiofacil_api/settings.py` e modifique a configuração `DATABASES`:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'fisiofacil_api',
            'USER': 'default_user',
            'PASSWORD': 'default_password',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
    ```

6.  **Aplique as Migrações:**

    * Aplique as migrações para criar as tabelas no banco de dados PostgreSQL:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

    * Se ocorrer erro ao executar as migrações, verifique as configurações e permissões do banco de dados.
    ```bash
    sudo -u postgres psql
       CREATE DATABASE fisiofacil_api;

        GRANT ALL PRIVILEGES ON SCHEMA public TO default_user;
        GRANT ALL PRIVILEGES ON DATABASE fisiofacil_api TO default_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO default_user;
    ```

    * Tente rodar as migrações novamente:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7.  **Crie um Superusuário (Opcional):**

    * Crie um superusuário para acessar o painel de administração do Django:

    ```bash
    python manage.py createsuperuser
    ```

8.  **Execute o Servidor de Desenvolvimento:**

    * Execute o servidor de desenvolvimento do Django:

    ```bash
    python manage.py runserver
    ```

    * Abra seu navegador e acesse `http://127.0.0.1:8000/` para ver o projeto em execução.

## Configuração Adicional

* **Variáveis de Ambiente:**
    * Em um ambiente de produção, é altamente recomendável armazenar as credenciais do banco de dados em variáveis de ambiente em vez de codificá-las diretamente no arquivo `settings.py`.
* **Arquivos Estáticos:**
    * Para servir arquivos estáticos em produção, execute o seguinte comando:

    ```bash
    python manage.py collectstatic
    ```

## Estrutura do Projeto

* `fisiofacil_api/`: Configurações principais do projeto Django.
    * `settings.py`: Configurações do projeto.
    * `urls.py`: Configurações de URL do projeto.
* `fisiofacil/`: Aplicativo Django com a lógica de negócios.
    * `models.py`: Definições dos modelos de dados.
    * `views.py`: Lógica das views.
    * `serializers.py`: Definições dos serializadores para a API REST.
    * `urls.py`: Configurações de URL do aplicativo.
    * `templates/`: Templates HTML para as páginas web.
    * `static/`: Arquivos estáticos (CSS, JavaScript, imagens).
    * `forms.py`: Formulários Django.
* `venv/`: Ambiente virtual (se criado).
* `requirements.txt`: Lista de dependências do projeto.

## Rotas da API

* `/api/fisiofacil/`: Lista de fisiofacil.
* `/api/servicos/`: Lista de serviços.
* `/api/profissional-servicos/`: Lista de fisiofacil/serviços.
* `/api/profissional-servicos-detalhado/`: Detalhes de fisiofacil/serviços.
* `/api/profissional-servicos-ativos/`: Lista de fisiofacil/serviços ativos.
* `/api/agendamentos/`: Lista de agendamentos e endpoint para criar agendamentos.

## Rotas do Front-end

* `/`: Página inicial.
* `/fisiofacil/`: Lista de fisiofacil.
* `/servicos/`: Lista de serviços ativos.
* `/agendamentos/`: Formulário de agendamento.

Este tutorial deve fornecer um guia completo para instalar e executar seu projeto Django localmente, utilizando o PostgreSQL como banco de dados. Se você tiver alguma dúvida ou precisar de ajuda adicional, me diga!