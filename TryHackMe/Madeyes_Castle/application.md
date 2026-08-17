
o index.html da pagina é a default page do apache, nada demais

---

consultando /backup/email temos:

![[Pasted image 20260817140220.png]]

Aparentemente Madeye criou um dominio hogwartz-castle.thm 

### Fato observado

O email contém explicitamente:

hogwartz-castle.thm

e também diz:

> Apache → virtual hosting → múltiplos sites no mesmo IP.

Além disso, o email menciona que o domínio foi **registrado para a box**.

Portanto, temos evidência forte de que esse hostname pode estar relacionado à aplicação.

### Hipótese

> O Apache pode estar servindo um virtual host diferente quando o `Host:` é `hogwartz-castle.thm`.

vamos agr alterar o /etc/hosts e apontar para esse dominio e ver se algo muda

![[Pasted image 20260817142636.png]]


acessando a aplicação:
![[Pasted image 20260817142714.png]]

hipotese comprovada, o apache serve um virtual host diferente quando é apontado para o dominio criado por Madeye

---


nao temos nada alem dessa interface simples de login , o mais obvio aqui pra ja é tentar SQLi, e foi isso que recebi ao injetar payload simples de SQLi `'OR+2=2--` no username
![[Pasted image 20260817143158.png]]recebemos uma resposta interessante... um erro, porem o erro, esta revelando um user REAL da aplicação


~~Isso levanta a hipotese de que talvez nosso SQLi tenha funcionado mas apenas conseguiu bypassear o username, passou da primeira etapa mas ainda ficou travado na senha, o mesmo erro aparece se eu colocar o username dele, e qualquer senha ou valor nulo no campo password, o que me levanta outra hipotese... Talvez o backend esteja programado pra retornar esse erro independente do payload ou senha que eu colocar, desde que o user seja valido... pq vamos pensar, nao faz sentido a aplicação me retornar um erro dizendo sobre SQLi, se eu nao injetei SQLi... ao backend da aplicação ja espera de nos testar o sqli e quando testar vai bypassear o primeiro campo mas vai travar no campo da password, e como eu cheguei até a password eu preciso de um user valido, e me é retornado Lucas Washington~~

~~de momento isso me cheira a `HYDRA`... Mas antes quero testar mais payloads SQLi~~




Vamos testar alguns payloads SQLi com UNION attack
vou jogar essa request para o burp para um melhor manuseamento dos testes e melhor visualização
![[Pasted image 20260817161044.png]]


![[Pasted image 20260817161138.png]]
aqui tivemos uma resposta interessante, nosso payload refletiu no backend e sugeriu que esse banco de dados pode nos retornar 4 colunas... agr precisamos ver quais colunas sao interessantes para nos:

![[Pasted image 20260817161813.png]]1 e 4 coluna, a primeira aparentemente é username e a 4 a password

antes precisamos saber qual banco de dados estamos lidando

dependendo do banco de dados, a sintaxe é diferente... por isso precisamos saber exatamente qual db estamos lidando


Comandos por Sistema de Banco de Dados

- **MySQL / MariaDB:** `SELECT VERSION();`

- **PostgreSQL:** `SELECT version();`

- **Microsoft SQL Server:** `SELECT @@VERSION;`

- **Oracle Database:** `SELECT * FROM v$version;`

- **SQLite:** `SELECT sqlite_version();`

temos aqui uma lista para sabermos as versoes (logo o db usado)

como ja sabemos que nossa payload deve retornar 4 colunas, e que as colunas visiveis para nos sao a 1 e a 4, devemos introduzir o codigo dentro de uma dessas duas colunas para conseguirmos ver o conteudo

![[Pasted image 20260817162946.png]]

![[Pasted image 20260817163022.png]]
esta ai... sqlite versao 3.31.1 confirmado



---


![[Pasted image 20260817163850.png]]aqui conseguimos extrair o schema do banco de dados... mas esta um pouco ruim de visualizar pq veio em uma unica linha, cada "/n" é uma quebra de linha, vamos apenas organizar para uma melhor visualização:

```
CREATE TABLE users(
name text not null,
password text not null,
admin int not null,
notes text not null)
```
perfeito, temos 4 coluna na tabela `users`, nossa query aceita 4 colunas, mas apenas duas sao visiveis... eu gosto sempre de concatenar as strings assim eu posso buscar tudo o que eu quiser em apenas um unica coluna:

![[Pasted image 20260817170545.png]]
temos um user Aaliyah Allen, um hash absurdamente grande o "0" (do parametro admin) e um texto no notes... neste caso nao precisamos incluir notes em nosso payload (ao menos por enquanto, pq ele aqui nao serve de nada ainda)

nosso payload retornou apenas um registro, mas provavelmente temos mais, vamos listar

listando a quantidade de registros que temos em users:
![[Pasted image 20260817170358.png]]
temos 40 registros


usando group_concat() eu posso puxar todos os registros, porem vai vir muito bagunçado, pois ira vir tudo concatenado em apenas uma linha:

![[Pasted image 20260817174959.png]]

sabemos que nosso conteudo esta bagunçado em uma linha unica porem tbm sabemos que o que separa cada linha desse output é apenas uma virgula

entao a seguir pegamos esse valor todo e criamos um txt com ele no terminal e usamos tr ',' '\n' no arquivo apra substituir as virgulas por quebra de linha:

![[Pasted image 20260817175259.png]]
criamos o txt Credentials bagunçado, e usamos o cat com o tr para organizar o conteudo e salvar em "cleaCredentials.txt"

assim temos:

![[Pasted image 20260817175423.png]]
~~as credenciais todas em lista~~

~~o problema, é que ainda nao temos nenhum user aqui nessa lista com privilegios de admin~~

~~vou quebrar essas hashes todas e vamos seguir pela aplicação para ver o que mais conseguimos fazer a partir daqui~~

![[Pasted image 20260817180434.png]]

~~rockyou nao conseguiu quebrar nenhuma das 40 senhas...~~


vamos fazer o mesmo agr, porem com o "notes"... esse registro todo que peguei nao me rendeu nada, vou resgatar ele novamente porem com o notes, pra ver se temos algo de interessante (e fazer o mesmo que fiz via terminal com o Credentials.txt)

payload:   'UNION SELECT NULL,NULL,NULL,group_concat(name||':'||password||':'||admin||':'||notes) FROM users;--

salvei a saida no nano e organizei com tr

![[Pasted image 20260817182832.png]]

GOTCHA, informaçao interessante agr, estava no notes o que eu precisava

user no linux de Harry Turner é apenas "Harry"

![[Pasted image 20260817183118.png]]
grep para uma visualizaçao mais limpa e ver se temos mais algo, é apenas o Harry msm, porem agr temos o formato em que seu hash foi construido... best64, agr sim vms voltar ao hashcat e quebrar isso

![[Pasted image 20260817183542.png]]
deixar o hash salvo para usar no hashcat

como usar best64:
![[Pasted image 20260817183846.png]]


![[Pasted image 20260817183858.png]]
o meu esta salvo na pasta do john em /usr/share/john/rules/best64.rule

comando:
hashcat -m 1700 -a 0 -r /usr/share/john/rules/best64.rule harryhash.txt /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

![[Pasted image 20260817184430.png]]
conseguimos... temos nossas credenciais

Harry:REDACTED

