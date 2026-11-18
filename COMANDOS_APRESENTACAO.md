# SmartQueue — apresentação prática de 3 minutos

Este repositório contém uma **versão demonstrativa** de SmartQueue, criada para execução no GitHub Codespaces. Não é uma cópia verificada do projeto original.

## Instalação (terminal bash do Codespaces)

```bash
docker compose up -d
python -m pip install -r requirements.txt
python app.py
```

Na aba **Portas** do Codespaces, abra a porta **5000** para ver o painel web. Não é necessário instalar Docker no computador local.

## Demonstração do Redis (em um SEGUNDO terminal)

```bash
docker exec -it smartqueue-redis redis-cli
```

Digite os comandos abaixo **dentro do redis-cli**, um por vez:

```redis
PING
SET demo:senha 0
INCR demo:senha
INCR demo:senha
GET demo:senha
DEL demo:fila
RPUSH demo:fila A001 A002 A003
LRANGE demo:fila 0 -1
LPOP demo:fila
LRANGE demo:fila 0 -1
SET demo:temporaria A004 EX 60
TTL demo:temporaria
```

**Explicação curta:** PING testa a conexão; INCR incrementa; RPUSH inclui no fim da fila; LRANGE mostra; LPOP remove o primeiro; TTL informa o tempo restante.

**Importante:** as chaves `demo:` são independentes da aplicação. A aplicação usa `smartqueue:` para suas próprias filas e contador.

## Verificar as filas reais pelo terminal

Depois de gerar senhas no painel web:

```redis
LRANGE smartqueue:normal 0 -1
LRANGE smartqueue:prioritaria 0 -1
GET smartqueue:atual
GET smartqueue:contador
```

## Próximas execuções

```bash
docker compose up -d
python app.py
```

Parar o Redis: `docker compose stop`. Não use `docker compose down -v` se quiser conservar os dados.
