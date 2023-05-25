import random
from random import randrange

def random_workout_generator():
    peitoral = ['Supino Reto com halter', 'Supino reto com barra', 'Supino Inclinado com halter', 'Supino inclinado com barra',
                'Suplino Reto máquina', 'Supino Inclinado máquina', 'Flexão', 'Voador máquina', 'Crossover na polia alta', 'Crossover na polia baixa',
                'Voador com halter', 'Supino declinado']
    
    ombro = ['Desenvolvimento com halter', 'Desenvolvimento máquina', 'Elevação Lateral com halter', 'Elevação Lateral na polia', 'Elevação Frontar com Halter',
             'Face Pull', 'Remada Alta', 'Crucifixo Inverso']
    
    triceps = ['Triceps Corda', 'Triceps Francês com halter', 'Triceps Paralelo', 'Triceps Testa com a barra W', 'Supino pegada fechada',
               'Triceps testa na polia']
    
    costas = ['Barra fixa', 'Puxada alta pegada aberta', 'Puxada alta pegada neutra', 'Puxada alta pegada fechada', 'Remada curvada pegada supinada',
              'Remada Curvada pegada pronada', 'Remada Cavalinho', 'Remada Baixa pegada fechada', 'Remada Baixa pegada neutra', 'Remada Baixa pegada aberta',
              'Pulldown']
    
    biceps = ['Rosca Direta com halter', 'Rosca alternada com halter', 'Rosca Martelo com halter', 'Rosca Concentrada', 'Rosca Spider',
              'Rosca Scott', 'Rosca Martelo na polia', 'Rosca Direta na polia']
    
    perna = ['Agachamento com barra livre', 'Agachamento no Smith', 'Leg Press 45', 'Leg Press 180', 'Extensora', 'Flexora deitado',
             'Flexora sentada', 'Flexora em pé', 'Stiff com barra', 'Agachamento Búlgaro', 'Afundo', 'Adutora', 'Abdutora', 'Gêmeos em Pé',
             'Gêmeos sentado']
    
    number_of_sets = [3, 4, 5]
    repetitions = [6, 8, 10, 12, 15]

    workout = []

    for i in range(4):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(peitoral)
        weight = randrange(30)

        peitoral.remove(name)
        muscle = 'Peitoral'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)
    
    for i in range(2):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(triceps)
        weight = randrange(30)

        triceps.remove(name)
        muscle = 'Triceps'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)
    
    for i in range(2):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(ombro)
        weight = randrange(30)

        ombro.remove(name)
        muscle = 'Ombro'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)
    
    for i in range(4):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(costas)
        weight = randrange(30)

        costas.remove(name)
        muscle = 'Costas'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)
    
    for i in range(2):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(biceps)
        weight = randrange(30)

        biceps.remove(name)
        muscle = 'Biceps'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)
    
    for i in range(6):
        sets = random.choice(number_of_sets)
        reps = random.choice(repetitions)
        name = random.choice(perna)
        weight = randrange(30)

        perna.remove(name)
        muscle = 'Perna'
        exercise = (name, sets, reps, weight, muscle)
        
        workout.append(exercise)

    return workout