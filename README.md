# Pokemon Battle

Um jogo de batalha Pokémon em tempo real desenvolvido com Python e Pygame, utilizando dados da [PokéAPI](https://pokeapi.co/).

## Requisitos

- Python 3.7+
- pygame
- requests

## Instalação

```bash
# Clone ou baixe o repositório
cd pokemon-battle

# Instale as dependências
pip install pygame requests
```

## Executar o Jogo

```bash
python pokemon.py
```

## Mecânicas 

- **Dano**: Calculado baseado em nível, ataque e defesa
- **STAB**: Ataques do mesmo tipo causam 75% mais dano
- **Crítico**: 6.25% de chance de causar 50% mais dano
- **Velocidade**: Determina quem ataca primeiro
