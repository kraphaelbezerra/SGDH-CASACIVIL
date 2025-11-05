# Identidade Visual - Casa Civil do Ceará

Com base na análise do site https://www.casacivil.ce.gov.br/ e nos manuais de identidade visual do Governo do Ceará, a paleta de cores e a tipografia a serem aplicadas no projeto são:

## Cores Principais

| Nome | Código HEX | Uso Sugerido |
| :--- | :--- | :--- |
| **Verde Primário** | `#009a44` | Fundo principal, botões primários (similar ao gradiente do site). |
| **Verde Secundário** | `#006738` | Destaques, hover de botões. |
| **Azul (Gradiente)** | `#0080ff` | Usado no gradiente do cabeçalho do site (em combinação com o verde). |
| **Branco** | `#FFFFFF` | Textos em fundos coloridos, fundo de cards e áreas de conteúdo. |
| **Cinza Escuro** | `#333333` | Textos de corpo principal. |

## Tipografia

A fonte padrão do Governo do Ceará é a **Open Sans** ou uma fonte sem serifa similar (como `Segoe UI` ou `Tahoma`). O projeto original usa `Segoe UI`. Manteremos a fonte `Segoe UI` ou similar, mas priorizaremos a remoção de fontes serifadas.

## Estratégia de Implementação

O projeto original usa CSS embutido no `index.html` com um gradiente verde-azulado (`linear-gradient(135deg, #00a651 0%, #00d4aa 100%)`). Iremos substituir essas cores pelas cores da identidade visual da Casa Civil.

1.  **Cor de Fundo do `body`:** Substituir o gradiente atual por um fundo branco ou cinza claro, e aplicar o gradiente nos elementos de destaque.
2.  **Cabeçalho (`.gov-header`):** Aplicar o gradiente com o Verde Primário e o Azul.
3.  **Botões Primários (`.btn-primary`):** Aplicar o gradiente com o Verde Primário e o Verde Secundário.
4.  **Destaques (`.hosts-table thead`, `form-group input:focus`):** Usar o Verde Primário.
