#!/usr/bin/env python3
"""Build an independent Spanish educational-language stress suite for SEMB.

The suite is synthetic and corpus-independent. It must not read CONALITEG text,
classifier A/B outputs, or historical results. It is diagnostic/development
support only and never substitutes for human validation.
"""
from __future__ import annotations
import csv, hashlib
from pathlib import Path

OUT=Path('data/validation/semb03_synthetic_stress_cases.csv')
VERSION='SEMB03_SYNTH_STRESS_0.1'

ACTIONS={
'observe':[
'Observa con atención las hojas y registra los cambios que notes.',
'Examina la muestra durante dos minutos y señala lo que puedes ver.',
'Mira ambos recipientes y anota cualquier cambio visible.' ],
'describe':[
'Describe con tus palabras las características del animal de la imagen.',
'Escribe cómo es la superficie de cada roca.',
'Di qué cambios observaste durante el proceso.' ],
'recall':[
'Menciona dos funciones del sistema respiratorio estudiadas anteriormente.',
'Recuerda qué significa evaporación y escríbelo en una oración.',
'Anota el nombre de los tres estados físicos de la materia.' ],
'explain':[
'Explica por qué se forman gotas en la parte exterior del vaso frío.',
'Justifica por qué la sombra cambia de tamaño durante el día.',
'¿Por qué una planta puede marchitarse si no recibe agua? Explica tu respuesta.' ],
'compare':[
'Compara las dos imágenes y escribe una semejanza y una diferencia.',
'Contrasta las propiedades del agua líquida y del hielo.',
'Establece en qué se parecen y en qué se diferencian ambos ecosistemas.' ],
'classify':[
'Clasifica los objetos según sean conductores o aislantes.',
'Agrupa los animales de acuerdo con el tipo de alimentación.',
'Organiza los materiales en categorías según su origen.' ],
'measure':[
'Mide la longitud de la mesa con una cinta y registra el resultado.',
'Obtén la temperatura del agua con el termómetro y anótala.',
'Mide durante un minuto cuántos latidos percibes.' ],
'experiment':[
'Realiza una prueba cambiando la cantidad de luz y observa qué ocurre.',
'Modifica una sola condición del montaje y registra el resultado del experimento.',
'Pon a prueba la hipótesis variando la temperatura y comparando los resultados.' ],
'investigate':[
'Investiga en dos fuentes confiables cómo se produce la electricidad en tu localidad.',
'Busca evidencia para responder qué animales polinizan las plantas de tu región.',
'Consulta varias fuentes y reúne información sobre el consumo de agua en casa.' ],
'predict':[
'Predice qué sucederá si colocas el recipiente al sol antes de hacer la prueba.',
'Antes de observar, anticipa cuál objeto caerá primero y escribe tu predicción.',
'Di qué resultado esperas obtener antes de realizar el experimento.' ],
'infer':[
'Infiere a partir de los datos qué material conserva mejor el calor.',
'Con los resultados de la tabla, deduce qué factor influyó más.',
'Concluye qué ocurrió basándote únicamente en las evidencias registradas.' ],
'discuss':[
'Discute con tu equipo cuál explicación está mejor sustentada.',
'Debatan sus argumentos y lleguen a una conclusión común.',
'Intercambia puntos de vista con tus compañeros sobre las dos propuestas.' ],
'solve':[
'Resuelve el problema y muestra el procedimiento que utilizaste.',
'Calcula cuánta agua se necesita en total y explica cómo obtuviste la respuesta.',
'Encuentra una solución al problema usando los datos de la tabla.' ],
'create':[
'Diseña un cartel que explique cómo prevenir enfermedades respiratorias.',
'Construye un modelo sencillo del ciclo del agua.',
'Elabora una representación que muestre las relaciones de la cadena alimentaria.' ],
'decide':[
'Elige cuál de las tres alternativas es más adecuada y justifica tu decisión.',
'Decide qué material conviene utilizar después de valorar ventajas y desventajas.',
'Escoge la opción más segura con base en la información disponible.' ],
'act_on_environment':[
'Organicen una acción para reducir el desperdicio de agua en la escuela.',
'Aplica durante una semana una medida de prevención en tu hogar y registra su efecto.',
'Realiza con tu grupo una acción de cuidado del entorno de la comunidad.' ],
}

NEGATIVES=[
'La evaporación ocurre cuando el agua líquida pasa al estado gaseoso.',
'Los mamíferos alimentan a sus crías con leche.',
'En una cadena alimentaria la energía pasa de unos organismos a otros.',
'La temperatura es una medida relacionada con el estado térmico de un cuerpo.',
'Un termómetro permite medir la temperatura.',
'La observación es importante en el trabajo científico.',
'La clasificación permite organizar objetos de acuerdo con criterios.',
'La experimentación puede ayudar a contrastar explicaciones.',
'Investigar implica buscar y valorar información de diversas fuentes.',
'Una predicción anticipa un resultado antes de observarlo.',
'Inferir significa obtener una conclusión a partir de indicios o datos.',
'La discusión científica permite contrastar ideas.',
'Resolver problemas es una actividad frecuente en ciencias.',
'Crear modelos ayuda a representar fenómenos que no pueden verse directamente.',
'Tomar decisiones informadas requiere valorar alternativas.',
'El cuidado del ambiente incluye acciones individuales y colectivas.',
'La palabra «observa» aparece con frecuencia en las instrucciones escolares.',
'El maestro dijo: «compara los resultados», y después explicó el procedimiento.',
'En el ejemplo anterior se pidió a los alumnos que midieran la longitud.',
'El recuadro titulado «Investiga» forma parte del diseño de la página.',
'La sección de experimentos contiene materiales, procedimientos y resultados.',
'Las preguntas del capítulo permiten recordar conceptos estudiados.',
'La imagen muestra a varios alumnos discutiendo alrededor de una mesa.',
'El texto explica cómo decidir entre distintas fuentes de energía.',
'La comunidad realizó una campaña para cuidar el agua el año pasado.',
'Los científicos compararon las muestras y publicaron sus resultados.',
'La niña midió la temperatura antes de iniciar la actividad.',
'El investigador predijo el resultado con base en trabajos previos.',
'El grupo construyó un modelo que después fue exhibido en la escuela.',
'La tabla describe los valores obtenidos durante el experimento.'
]

POSITIONS={
'receiver':[
'La fotosíntesis transforma energía luminosa en energía química.',
'Los pulmones forman parte del aparato respiratorio.',
'El agua puede encontrarse en estado sólido, líquido o gaseoso.' ],
'instruction_follower':[
'Sigue los pasos indicados: coloca el papel, agrega agua y espera cinco minutos.',
'Realiza el procedimiento exactamente en el orden señalado en el recuadro.',
'Completa la actividad siguiendo cada instrucción sin cambiar el procedimiento.' ],
'observer':[
'Observa durante cinco minutos el comportamiento de las hormigas y registra lo que veas.',
'Examina la superficie con la lupa y anota tus observaciones.',
'Mira sistemáticamente los cambios del recipiente cada minuto.' ],
'experimenter':[
'Elige una variable, modifícala y compara el resultado con el montaje de control.',
'Pon a prueba tu hipótesis manipulando una condición del experimento.',
'Cambia la cantidad de luz y registra cómo responde la planta.' ],
'investigator':[
'Formula una pregunta y busca evidencias en distintas fuentes para responderla.',
'Investiga qué explicación está mejor respaldada y documenta las fuentes consultadas.',
'Reúne información de varias fuentes y decide qué evidencia es pertinente.' ],
'reasoner':[
'Explica la relación entre los datos de la tabla y la conclusión propuesta.',
'Usa la evidencia para inferir qué causa explica mejor el resultado.',
'Compara los casos y construye una respuesta razonada.' ],
'collaborator':[
'En equipo, discutan las evidencias y construyan una explicación compartida.',
'Trabaja con tus compañeros para comparar argumentos y acordar una conclusión.',
'Colaboren para elaborar una respuesta conjunta a partir de las ideas de todos.' ],
'decision_maker':[
'Valora las alternativas y decide cuál solución conviene aplicar.',
'Elige una opción después de comparar sus riesgos y beneficios.',
'Toma una decisión informada usando los datos disponibles.' ],
'community_agent':[
'Organiza con tu grupo una acción para reducir residuos en la escuela.',
'Aplica en tu comunidad una medida de cuidado del agua y evalúa su resultado.',
'Participa en una acción colectiva para mejorar el entorno cercano.' ],
}


def sid(kind,idx,text):
    return 'SYN-'+hashlib.sha256(f'{VERSION}|{kind}|{idx}|{text}'.encode()).hexdigest()[:16].upper()


def main():
    rows=[]
    for lab,texts in ACTIONS.items():
        for i,text in enumerate(texts,1):
            rows.append({'case_id':sid('action-'+lab,i,text),'suite_version':VERSION,'focus':'action','text':text,
                         'expected_actionable':'1','expected_action_labels':lab,'expected_position_labels':'','difficulty':'clear'})
    for i,text in enumerate(NEGATIVES,1):
        rows.append({'case_id':sid('negative',i,text),'suite_version':VERSION,'focus':'gate_negative','text':text,
                     'expected_actionable':'0','expected_action_labels':'','expected_position_labels':'receiver','difficulty':'stress'})
    for lab,texts in POSITIONS.items():
        for i,text in enumerate(texts,1):
            rows.append({'case_id':sid('position-'+lab,i,text),'suite_version':VERSION,'focus':'position','text':text,
                         'expected_actionable':'0' if lab=='receiver' else '1','expected_action_labels':'','expected_position_labels':lab,'difficulty':'clear'})
    assert len(rows)==48+30+27==105
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0])
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print('synthetic_cases',len(rows),'action',48,'negative',30,'position',27)

if __name__=='__main__':main()
