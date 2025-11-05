# Guia de Uso - Funcionalidade de Edição de Hosts

## Introdução

Este guia apresenta a nova funcionalidade de **edição de hosts** implementada no Sistema de Gerenciamento DHCP da Casa Civil. A funcionalidade permite modificar endereços MAC e IP de hosts já cadastrados no sistema, mantendo a integridade e consistência dos dados.

## Acessando a Funcionalidade

Para utilizar a funcionalidade de edição, siga os passos abaixo:

### Passo 1: Login no Sistema

Acesse o sistema utilizando suas credenciais de usuário. A tela de login solicita o **usuário ou email** e a **senha** de acesso. Após preencher os campos, clique no botão **"Entrar no Sistema"** para acessar o gerenciador DHCP.

### Passo 2: Navegação até Hosts Cadastrados

Após o login, você será direcionado para a tela principal do gerenciador. No topo da interface, existem duas abas principais: **"📝 Cadastro de IP"** e **"📋 Hosts Cadastrados"**. Clique na aba **"📋 Hosts Cadastrados"** para visualizar a lista completa de hosts registrados no sistema.

### Passo 3: Localização do Host

Na tela de hosts cadastrados, você encontrará uma tabela com todos os hosts registrados. A tabela apresenta as seguintes colunas: **Nome do Host**, **Endereço IP**, **Endereço MAC**, **Regra** e **Ações**. Utilize a barra de busca no topo da tabela para filtrar hosts por nome, IP ou MAC, facilitando a localização do host desejado.

## Editando um Host

### Abertura do Modal de Edição

Após localizar o host que deseja editar, clique no botão **"Editar"** (cor azul) localizado na coluna **"Ações"** da respectiva linha. Um modal será aberto na tela com o título **"✏️ Editar Host"**, contendo um formulário pré-preenchido com os dados atuais do host.

### Campos do Formulário

O formulário de edição apresenta os seguintes campos:

**Nome do Host**: Este campo exibe o nome do host em formato somente leitura. O nome do host não pode ser alterado para manter a integridade das referências no sistema. Uma mensagem informativa abaixo do campo indica: *"O nome do host não pode ser alterado"*.

**Endereço MAC**: Campo editável que permite modificar o endereço MAC do host. O sistema aplica formatação automática durante a digitação, inserindo os separadores (dois pontos) automaticamente. O formato esperado é `XX:XX:XX:XX:XX:XX`, onde X representa um dígito hexadecimal (0-9, A-F).

**Endereço IP**: Campo editável que permite modificar o endereço IP do host. O formato esperado é `XXX.XXX.XXX.XXX`, onde cada octeto deve estar entre 0 e 255. O sistema valida o formato antes de permitir o salvamento.

**Selecione uma Regra (opcional)**: Dropdown que permite alterar a regra associada ao host. Ao selecionar uma nova regra, o sistema exibe automaticamente os IPs disponíveis para aquela regra na seção **"IPs Disponíveis"** logo abaixo.

### Realizando Alterações

Para modificar o endereço MAC, clique no campo **"Endereço MAC"** e digite o novo endereço. O sistema formatará automaticamente conforme você digita. Para modificar o endereço IP, você pode digitar manualmente um novo IP no campo **"Endereço IP"** ou selecionar uma regra no dropdown e escolher um IP disponível da lista exibida.

### Salvando as Alterações

Após realizar as modificações desejadas, clique no botão **"Salvar Alterações"** (cor verde) localizado no rodapé do modal. O sistema executará as seguintes validações:

- Verificação do formato do endereço MAC
- Verificação do formato do endereço IP
- Verificação de duplicidade de MAC (se o novo MAC já está em uso por outro host)
- Verificação de duplicidade de IP (se o novo IP já está em uso por outro host)
- Verificação de disponibilidade do IP na regra selecionada

Se todas as validações forem bem-sucedidas, o sistema atualizará o arquivo de configuração DHCP (`dhcpd.conf`), criará um backup automático, fechará o modal e atualizará a tabela de hosts. Uma mensagem de sucesso será exibida confirmando a operação.

### Cancelando a Edição

Caso deseje cancelar a edição sem salvar as alterações, clique no botão **"Cancelar"** (cor vermelha) ou no ícone **"×"** no canto superior direito do modal. O modal será fechado e nenhuma alteração será aplicada.

## Validações e Restrições

O sistema implementa diversas validações para garantir a integridade dos dados:

### Formato de Endereço MAC

O endereço MAC deve seguir o padrão hexadecimal com 6 pares de dígitos separados por dois pontos. Exemplos válidos: `00:1A:2B:3C:4D:5E`, `A1:B2:C3:D4:E5:F6`. O sistema aceita letras maiúsculas e minúsculas.

### Formato de Endereço IP

O endereço IP deve seguir o padrão IPv4 com 4 octetos separados por pontos. Cada octeto deve estar entre 0 e 255. Exemplo válido: `10.8.2.100`.

### Duplicidade

O sistema não permite que dois hosts diferentes possuam o mesmo endereço MAC ou o mesmo endereço IP. Durante a edição, o sistema verifica se o novo MAC ou IP já está em uso por outro host. O próprio host sendo editado é excluído dessa verificação.

### Disponibilidade de IP

Se você selecionar uma nova regra, o IP informado deve estar disponível na faixa de IPs daquela regra. O sistema consulta a lista de IPs disponíveis e valida se o IP escolhido está livre para uso.

## Mensagens de Erro

Caso ocorra algum erro durante o processo de edição, o sistema exibirá mensagens específicas para auxiliar na correção:

- **"Formato de MAC inválido"**: O endereço MAC informado não segue o padrão esperado.
- **"Formato de IP inválido"**: O endereço IP informado não segue o padrão esperado.
- **"MAC já cadastrado"**: O endereço MAC informado já está em uso por outro host.
- **"IP já cadastrado"**: O endereço IP informado já está em uso por outro host.
- **"Host não encontrado"**: O host que você tentou editar não existe no sistema.
- **"IP não disponível para a regra selecionada"**: O IP informado não está disponível na regra escolhida.

## Backup Automático

O sistema cria automaticamente um backup do arquivo de configuração DHCP antes de aplicar qualquer modificação. Os backups são armazenados com timestamp no nome do arquivo, permitindo recuperação em caso de necessidade.

## Atualização da Lista

Após salvar as alterações com sucesso, a tabela de hosts é automaticamente atualizada para refletir as novas informações. Você pode também clicar no botão **"🔄 Atualizar Lista"** a qualquer momento para recarregar manualmente os dados da tabela.

## Dicas de Uso

**Verificação antes de editar**: Sempre verifique os dados atuais do host antes de realizar alterações para evitar modificações acidentais.

**Uso da busca**: Utilize a barra de busca para localizar rapidamente hosts em listas grandes, digitando parte do nome, IP ou MAC.

**Seleção de regra**: Ao trocar de regra, consulte a lista de IPs disponíveis antes de informar o novo IP manualmente.

**Formatação automática**: Aproveite a formatação automática do campo MAC para agilizar a digitação.

**Cancelamento seguro**: Caso tenha dúvidas durante a edição, utilize o botão Cancelar para sair sem aplicar alterações.

## Suporte

Em caso de dúvidas ou problemas com a funcionalidade de edição, entre em contato com o administrador do sistema ou consulte a documentação técnica completa no arquivo `CHANGELOG.md`.

---

**Sistema de Gerenciamento DHCP - Casa Civil**  
**Versão**: 2.1  
**Data**: Outubro de 2025
