#!/usr/bin/env python3
"""Synthetic regression tests for RULEA 0.1.

No corpus text is used. The examples are deliberately invented to verify decision
boundaries before the classifier is applied to LTMD fragments.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classify_fragments_A import classify_text


def meta(candidate_type, token_count=12, certainty='high'):
    return {
        'candidate_type': candidate_type,
        'token_count': str(token_count),
        'classification_certainty': certainty,
        'uncertain_boundary': '0',
    }


def check(text, ctype, expected_on=(), expected_off=()):
    acts, pos, types, evidence, uncertain = classify_text(text, meta(ctype))
    for a in expected_on:
        assert acts[a] == 1, (text, a, acts)
    for a in expected_off:
        assert acts[a] == 0, (text, a, acts)
    return acts, pos, types, evidence, uncertain


def main():
    # Contextual nouns in exposition must not become student actions.
    check('El termómetro permite conocer la temperatura.', 'expository_candidate', expected_off=['measure'])
    check('Un problema puede tener distintas soluciones.', 'expository_candidate', expected_off=['solve'])
    check('Las diferencias entre ambos materiales son visibles.', 'expository_candidate', expected_off=['compare'])
    check('El cartel muestra información sobre el ambiente.', 'expository_candidate', expected_off=['create','act_on_environment'])
    check('En este experimento se estudió la evaporación.', 'expository_candidate', expected_off=['experiment'])
    check('Se observa un cambio de color durante la reacción.', 'expository_candidate', expected_off=['observe'])

    # Directed context converts explicit contextual evidence into an operation.
    check('¿Qué diferencias encuentras entre los dos objetos?', 'question_candidate', expected_on=['compare'])
    check('Mide la temperatura con el termómetro y anota el resultado.', 'instruction_candidate', expected_on=['measure'])
    check('Resuelve el problema y explica cómo obtuviste la solución.', 'instruction_candidate', expected_on=['solve','explain'])
    check('Elabora un cartel para comunicar tus resultados.', 'instruction_candidate', expected_on=['create'])

    # Experiment requires explicit experiment action or manipulation structure.
    check('Materiales: agua y sal. Mezcla los materiales y observa el resultado.', 'activity_candidate', expected_on=['experiment','observe'])
    check('Realiza un experimento para comparar las mezclas.', 'instruction_candidate', expected_on=['experiment','compare'])

    # Higher-level positions derive only from valid actions.
    acts,pos,_,_,_=check('Investiga en varias fuentes y explica tus conclusiones.', 'instruction_candidate', expected_on=['investigate','explain'])
    assert pos['investigator']==1 and pos['reasoner']==1
    acts,pos,_,_,_=check('Decide cuál alternativa conviene y justifica tu elección.', 'question_candidate', expected_on=['decide','explain'])
    assert pos['decision_maker']==1 and pos['reasoner']==1

    # Community action needs both outward action and community/health/environment context.
    check('Propón una acción para cuidar el ambiente de tu comunidad.', 'instruction_candidate', expected_on=['act_on_environment'])
    check('La comunidad cuida el ambiente.', 'expository_candidate', expected_off=['act_on_environment'])

    print('RULEA synthetic regression tests: OK')


if __name__ == '__main__':
    main()
