## Conceito

Nosso objetivo é criar um gerador procedural de fichas de jogadores para Pathfinder 2E, irá desde a matemática básica dos atributos até os últimos detalhes para a finalização de personagem, deixando a ficha pronta para o jogador usar. 
Iremos criar ele em Flask para todo o projeto. Como o pdf tem tabelas e colunas e caixas de texto caso você ache necessário use as ferramentas e crie arquivos que lhe forem melhor para a leitura e entendimento.
Os arquivos para transformarmos em "Json" está no "ref", lá tem todos os arquivos que usaremos para a conversão, porém não vamos converter todos de uma vez, vamos um por vez para irmos com calma, primeiro de tudo começaremos com o "ref\Tools.pdf", iremos transformar todos esses equipamentos que o pdf tem em "json".
Use a pasta "templates" para colocar os arquivos do Front End, e use a pasta "dados" para colocar as informações, convertidas em json, da ficha, classe, raça, atributos, habilidades, talentos, magias, equipamentos e quaisquer demais características que sejam ligadas a ficha do jogador. Se achar necessário, crie arquivos para extração do pdf, para ajudar na leitura e entendimento das informações do pdf.
A estrutura da criação será, um campo para escolher a ancestralidade e sua herança, depois é o campo biografia que pode ser procedural que seja copndizente com o conceito do personagem e também o usuário pode escolher entre as opções de biografia caso ele queira, depois o campo da classe que o usuário deve escolher. ( Os atributos/melhorias livres, você colonte de acordo com o conceito do personagem onde ficaria mais crível e interessante para o personagem ), vamos ter um campo de "subclasses" que será um norte/conceito para os personagens a serem gerados (ex: classe guerreiro -> subclasse: Combatente de 2 espadas), as perícias serão geradas proceduralmente de acordo com o conceito do personagem, os talentos serão gerados também proceduralmente de acordo c conceito do personagem, os talentos/talentos de ancestralidade/de classe/gerais/de perícias de classe serão gerados proceduralmente de acordo com o conceito do personagem.
Tudo isso foi o conceito para 

## Começando
Vamos começar destrinchando o princial do PF2, que são as tabelas de classe, equipamentos, talentos e etc...
Mas vamos por partes, vamos começar transformando os equipamentos em "JSON", agora sim é a prática, antes foi só o contexto para você fazer a estruturação de tudo.
O caminho dos Equipamentos é "ref\Tools.pdf", comece por eles.
Se tiver dúvidas me pergunte.