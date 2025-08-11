# Configuração de CI/CD com GitHub Actions e Railway

## 📋 Visão Geral

Este documento explica como configurar o pipeline de CI/CD (Continuous Integration/Continuous Deployment) para a API de Web Scraping usando GitHub Actions e Railway.

## 🚀 Pipeline Implementado

### Jobs do Workflow

1. **Test** - Executa testes e linting
2. **Build and Deploy** - Faz deploy no Railway
3. **Security Scan** - Análise de segurança
4. **Docker Build** - Constrói imagem Docker

## 🔧 Configuração Necessária

### 1. Secrets do GitHub

Configure os seguintes secrets no seu repositório GitHub:

#### Acesse: `Settings > Secrets and variables > Actions`

| Secret | Descrição | Como obter |
|--------|-----------|------------|
| `RAILWAY_TOKEN` | Token de autenticação do Railway | [Instruções abaixo](#obtendo-o-railway-token) |
| `RAILWAY_PROJECT_ID` | ID do projeto no Railway | [Instruções abaixo](#obtendo-o-project-id) |
| `RAILWAY_URL` | URL da aplicação no Railway | Será gerada automaticamente |

### 2. Obtendo o Railway Token

1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Vá em **Account Settings**
3. Clique em **Tokens**
4. Clique em **New Token**
5. Copie o token gerado
6. Cole no secret `RAILWAY_TOKEN` do GitHub

### 3. Obtendo o Project ID

1. No Railway Dashboard, acesse seu projeto
2. Vá em **Settings**
3. Copie o **Project ID**
4. Cole no secret `RAILWAY_PROJECT_ID` do GitHub

### 4. Configurando o Projeto no Railway

1. Crie um novo projeto no Railway
2. Conecte com seu repositório GitHub
3. Configure as variáveis de ambiente:

```bash
# Variáveis obrigatórias
API_SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=production
PORT=5000

# Credenciais do LinkedIn (opcional)
LINKEDIN_EMAIL=seu-email@exemplo.com
LINKEDIN_PASSWORD=sua-senha

# API Keys para clientes
API_KEY_CLIENT1=api-key-1-change-in-production
API_KEY_CLIENT2=api-key-2-change-in-production

# Configurações de logging
LOG_LEVEL=INFO
```

## 📁 Estrutura de Arquivos

```
.github/
└── workflows/
    └── deploy.yml          # Workflow principal do CI/CD

railway.json               # Configuração específica do Railway
docs/
└── CI_CD_SETUP.md        # Este arquivo
```

## 🔄 Como Funciona o Pipeline

### 1. Trigger
- **Push** para `main` ou `master` → Executa todos os jobs
- **Pull Request** → Executa apenas testes e security scan

### 2. Job: Test
```yaml
- Instala dependências Python
- Executa linting com flake8
- Roda testes com pytest
- Gera relatório de cobertura
- Upload para Codecov
```

### 3. Job: Build and Deploy
```yaml
- Instala Railway CLI
- Faz login no Railway
- Deploy da aplicação
- Health check
- Notificação de status
```

### 4. Job: Security Scan
```yaml
- Executa Bandit (análise de segurança)
- Gera relatório JSON
- Upload como artifact
```

### 5. Job: Docker Build
```yaml
- Constrói imagem Docker
- Tag com SHA do commit
- Upload como artifact
```

## 🛠️ Configuração Adicional

### 1. Dependências de Teste

Adicione ao `requirements.txt`:

```txt
pytest==7.4.3
pytest-cov==4.1.0
flake8==6.1.0
bandit==1.7.5
```

### 2. Configuração do Flake8

Crie `.flake8`:

```ini
[flake8]
max-line-length = 127
exclude = .git,__pycache__,build,dist
ignore = E203, W503
```

### 3. Configuração do Pytest

Crie `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=. --cov-report=html --cov-report=xml
```

## 📊 Monitoramento

### 1. GitHub Actions
- Acesse a aba **Actions** no seu repositório
- Visualize o status dos workflows
- Veja logs detalhados de cada job

### 2. Railway Dashboard
- Monitore o status da aplicação
- Veja logs em tempo real
- Configure alertas

### 3. Health Check
- Endpoint: `https://sua-app.railway.app/health`
- Retorna status dos módulos
- Útil para monitoramento externo

## 🚨 Troubleshooting

### Problema: Deploy falha no Railway
**Solução:**
1. Verifique as variáveis de ambiente
2. Confirme se o `railway.json` está correto
3. Verifique os logs no Railway Dashboard

### Problema: Testes falham
**Solução:**
1. Execute testes localmente: `python -m pytest tests/`
2. Verifique se todas as dependências estão instaladas
3. Confirme se os mocks estão configurados corretamente

### Problema: Linting falha
**Solução:**
1. Execute localmente: `flake8 .`
2. Corrija os problemas de estilo
3. Configure exceções no `.flake8` se necessário

## 🔒 Segurança

### 1. Secrets
- Nunca commite tokens ou senhas
- Use sempre GitHub Secrets
- Rotacione tokens regularmente

### 2. Dependências
- Mantenha dependências atualizadas
- Use `pip-audit` para verificar vulnerabilidades
- Configure dependabot para atualizações automáticas

### 3. Código
- Execute security scans regularmente
- Revise relatórios do Bandit
- Implemente SAST (Static Application Security Testing)

## 📈 Próximos Passos

### 1. Melhorias Sugeridas
- [ ] Adicionar testes de integração
- [ ] Implementar cache de dependências
- [ ] Configurar dependabot
- [ ] Adicionar notificações (Slack, Discord)
- [ ] Implementar rollback automático

### 2. Monitoramento Avançado
- [ ] Configurar New Relic ou DataDog
- [ ] Implementar métricas customizadas
- [ ] Configurar alertas de performance
- [ ] Implementar tracing distribuído

### 3. Segurança
- [ ] Configurar dependabot security alerts
- [ ] Implementar SAST com CodeQL
- [ ] Configurar container scanning
- [ ] Implementar secret scanning

## 📞 Suporte

Se encontrar problemas:

1. **GitHub Actions**: Verifique os logs na aba Actions
2. **Railway**: Acesse o dashboard e veja os logs
3. **Documentação**: Consulte este arquivo e o README.md
4. **Issues**: Abra uma issue no repositório

## ✅ Checklist de Configuração

- [ ] Criar projeto no Railway
- [ ] Configurar secrets no GitHub
- [ ] Adicionar variáveis de ambiente no Railway
- [ ] Testar deploy manual
- [ ] Configurar domínio customizado (opcional)
- [ ] Configurar monitoramento
- [ ] Testar pipeline completo

---

**🎉 Parabéns! Seu pipeline de CI/CD está configurado e funcionando!**
