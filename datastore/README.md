Se você encontrar problemas ao acessar o serviço de outro host, pode ser necessário habilitar algumas configurações usando os seguintes comandos:

```bash
sudo firewall-cmd --zone=public --add-port=9494/tcp --permanent
```

```bash
sudo firewall-cmd --reload
```

Para verificar as alterações, você pode listar as portas abertas com:

```bash
sudo firewall-cmd --list-ports
```
