# Troubleshooting - Health Check do Railway

## 🚨 Problema: Health Check Falhando

Se o health check do Railway está falhando, aqui estão as possíveis causas e soluções:

## 🔍 Diagnóstico

### 1. Verificar Logs do Railway
```bash
# No Railway Dashboard
1. Acesse seu projeto
2. Clique na aba "Deployments"
3. Clique no deployment mais recente
4. Verifique os logs para erros
```

### 2. Testar Health Check Localmente
```bash
# Execute a aplicação localmente
python main.py

# Em outro terminal, teste o health check
curl http://localhost:5000/health
```

### 3. Verificar Variáveis de Ambiente
Certifique-se de que estas variáveis estão configuradas no Railway:
```bash
API_SECRET_KEY=sua-chave-secreta
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
```

## 🛠️ Soluções

### Solução 1: Health Check Simplificado
O health check foi simplificado para evitar dependências complexas:

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check global da API"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'message': 'API funcionando normalmente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500
```

### Solução 2: Configuração do Railway
Atualize o `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

### Solução 3: Arquivos de Configuração
Adicione estes arquivos na raiz do projeto:

**Procfile:**
```
web: python main.py
```

**runtime.txt:**
```
python-3.11.7
```

## 🔧 Problemas Comuns

### 1. **Erro: ModuleNotFoundError**
**Causa:** Dependências não instaladas
**Solução:**
```bash
# Verificar se requirements.txt está na raiz
# Certifique-se de que todas as dependências estão listadas
```

### 2. **Erro: Port already in use**
**Causa:** Conflito de porta
**Solução:**
```bash
# Configure a variável PORT no Railway
PORT=5000
```

### 3. **Erro: Permission denied**
**Causa:** Problemas de permissão
**Solução:**
```bash
# O Railway deve gerenciar permissões automaticamente
# Verifique se não há arquivos com permissões especiais
```

### 4. **Erro: Import error**
**Causa:** Problemas com imports dos módulos
**Solução:**
```python
# Verifique se todos os __init__.py estão presentes
# Teste os imports localmente
```

## 📊 Monitoramento

### 1. Logs em Tempo Real
```bash
# No Railway Dashboard
1. Vá para a aba "Deployments"
2. Clique no deployment ativo
3. Monitore os logs em tempo real
```

### 2. Health Check Manual
```bash
# Teste manualmente após o deploy
curl -v https://sua-app.railway.app/health
```

### 3. Status da Aplicação
```bash
# Verifique se a aplicação está respondendo
curl https://sua-app.railway.app/
```

## 🚀 Deploy Manual

Se o deploy automático falhar, tente um deploy manual:

```bash
# No Railway Dashboard
1. Vá para "Settings"
2. Clique em "Deploy"
3. Selecione "Deploy from GitHub"
4. Escolha a branch main
```

## 🔄 Rollback

Se necessário, faça rollback para uma versão anterior:

```bash
# No Railway Dashboard
1. Vá para "Deployments"
2. Encontre um deployment que funcionava
3. Clique em "Redeploy"
```

## 📞 Suporte

Se o problema persistir:

1. **Verifique os logs** no Railway Dashboard
2. **Teste localmente** para isolar o problema
3. **Verifique as variáveis de ambiente**
4. **Consulte a documentação** do Railway
5. **Abra uma issue** no repositório

## ✅ Checklist de Verificação

- [ ] Health check funciona localmente
- [ ] Todas as variáveis de ambiente estão configuradas
- [ ] Requirements.txt está na raiz
- [ ] Procfile está presente
- [ ] runtime.txt está presente
- [ ] railway.json está configurado corretamente
- [ ] Logs não mostram erros críticos
- [ ] Aplicação responde na porta correta

---

**💡 Dica:** O health check simplificado deve resolver a maioria dos problemas. Se ainda falhar, verifique os logs do Railway para identificar o erro específico.
