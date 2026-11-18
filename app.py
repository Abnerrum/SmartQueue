"""SmartQueue demonstrativo — Flask + Redis. Não substitui o projeto original."""
import os
from flask import Flask, jsonify, request, render_template_string
import redis

app = Flask(__name__)
db = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

# Atomicamente, chama uma senha respeitando prioridade e apenas um atendimento ativo.
CHAMAR_SCRIPT = """
if redis.call('EXISTS', 'smartqueue:atual') == 1 then
    return redis.call('GET', 'smartqueue:atual')
end
local senha = redis.call('LPOP', 'smartqueue:prioritaria')
if not senha then senha = redis.call('LPOP', 'smartqueue:normal') end
if senha then redis.call('SET', 'smartqueue:atual', senha) end
return senha
"""

HTML = """
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmartQueue | Redis</title>
<style>body{font:16px Arial,sans-serif;background:#eef2f8;color:#17213b;margin:0;padding:30px}
main{max-width:750px;margin:auto;background:white;padding:28px;border-radius:18px}
button{padding:12px;margin:5px;border:0;border-radius:8px;background:#263b85;color:white;cursor:pointer}
section{background:#f3f5fa;padding:14px;border-radius:10px;margin-top:15px}
#atual{font-size:32px;font-weight:bold}ul{padding-left:22px}</style></head><body><main>
<h1>SmartQueue</h1><p>Gerenciamento de filas com Flask, Python, Redis e Docker.</p>
<button onclick="acao('/senha/normal')">Gerar senha normal</button>
<button onclick="acao('/senha/prioritaria')">Gerar senha prioritária</button>
<button onclick="acao('/chamar')">Chamar próxima</button>
<button onclick="acao('/finalizar')">Finalizar atendimento</button>
<section><b>Em atendimento:</b><div id="atual">—</div></section>
<section><h3>Fila prioritária</h3><ul id="p"></ul><h3>Fila normal</h3><ul id="n"></ul></section>
<section><h3>TTL (demonstração dos slides)</h3>
<button onclick="acao('/ttl')">Criar chave temporária de 60 segundos</button>
<span id="ttl"></span></section>
<p id="msg"></p></main>
<script>
async function acao(url){try{
 const resp=await fetch(url,{method:'POST'});const d=await resp.json();
 document.getElementById('msg').textContent=d.mensagem||d.erro||'';
 if(d.ttl!==undefined)document.getElementById('ttl').textContent='TTL: '+d.ttl+' segundos';
 await atualizar();
}catch(e){document.getElementById('msg').textContent='Erro: '+e.message;}}
async function atualizar(){try{
 const d=await(await fetch('/status')).json();
 document.getElementById('atual').textContent=d.atual||'—';
 for(const [id,lista] of [['p',d.prioritaria],['n',d.normal]]){
 document.getElementById(id).innerHTML=lista.map(x=>'<li>'+x+'</li>').join('');
 }}catch(e){document.getElementById('msg').textContent='Redis indisponível';}}
atualizar();setInterval(atualizar,3000);
</script></body></html>
"""

@app.get("/")
def pagina():
    return render_template_string(HTML)

@app.get("/status")
def status():
    return jsonify(
        atual=db.get("smartqueue:atual"),
        normal=db.lrange("smartqueue:normal", 0, -1),
        prioritaria=db.lrange("smartqueue:prioritaria", 0, -1),
    )

@app.post("/senha/<tipo>")
def gerar(tipo):
    if tipo not in ("normal", "prioritaria"):
        return jsonify(erro="Tipo inválido"), 400
    num = db.incr("smartqueue:contador")
    senha = f"{'P' if tipo == 'prioritaria' else 'A'}{num:03d}"
    db.rpush(f"smartqueue:{tipo}", senha)
    return jsonify(mensagem=f"Senha {senha} criada", senha=senha)

@app.post("/chamar")
def chamar():
    senha = db.eval(CHAMAR_SCRIPT, 0)
    return jsonify(mensagem=f"Senha em atendimento: {senha}" if senha else "Fila vazia", senha=senha)

@app.post("/finalizar")
def finalizar():
    senha = db.getdel("smartqueue:atual")
    return jsonify(mensagem=f"Atendimento {senha} finalizado" if senha else "Nenhum atendimento ativo")

@app.post("/ttl")
def ttl():
    db.set("demo:temporaria", "A004", ex=60)
    return jsonify(mensagem="Chave demo:temporaria criada", ttl=db.ttl("demo:temporaria"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
