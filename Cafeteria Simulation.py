import simpy
import random


def student_generator(env, mean_arrival, stand_salad, stand_food, stand_sandwich,
                      serving_salad, serving_food, serving_sandwich):
    global student_id

    while True:
        wp = activity_generator(env, student_id, stand_salad, stand_food, stand_sandwich,
                                serving_salad, serving_food, serving_sandwich)

        env.process(wp)

        t = random.expovariate(1 / mean_arrival)

        yield env.timeout(t)

        student_id += 1


def activity_generator(env, student_id, stand_salad, stand_food, stand_sandwich,
                                serving_salad, serving_food, serving_sandwich):
    
    decide_queue = random.uniform(0, 1)

    if decide_queue < 0.1765:
        time_entered_queue_sandwich = env.now
        global sandwich_queue
        with stand_sandwich.request() as req:
            yield req

            time_left_queue_sandwich = env.now
            time_in_queue_sandwich = time_left_queue_sandwich - time_entered_queue_sandwich
            print(" \\Student %s queued for sandwich %.2f minutes" % (
            student_id, time_in_queue_sandwich))
            sandwich_queue.append(time_in_queue_sandwich)

            sandwich_time = random.expovariate(1 / serving_sandwich)
            yield env.timeout(sandwich_time)

    elif 0.1765 < decide_queue < 0.6470:
        global food_queue
        time_entered_queue_food = env.now
        with stand_food.request() as req:
            yield req

            time_left_queue_food = env.now
            time_in_queue_food = time_left_queue_food - time_entered_queue_food
            print(" \\Student %s queued for food %.2f minutes" % (
            student_id, time_in_queue_food))
            food_queue.append(time_in_queue_food)

            food_time = random.expovariate(1 / serving_food)
            yield env.timeout(food_time)

    else:
        global salad_queue
        time_entered_queue_salad = env.now
        with stand_salad.request() as req:
            yield req

            time_left_queue_salad = env.now
            time_in_queue_salad = time_left_queue_salad - time_entered_queue_salad
            print(" \\Student %s queued for salad %.2f minutes" % (
            student_id, time_in_queue_salad))
            salad_queue.append(time_in_queue_salad)

            salad_time = random.expovariate(1 / serving_salad)
            yield env.timeout(salad_time)


random.seed(2023)
env = simpy.Environment()

student_id = 1

stand_salad = simpy.Resource(env, capacity=2)
stand_food = simpy.Resource(env, capacity=4)
stand_sandwich = simpy.Resource(env, capacity=1)

serving_salad = 2
serving_food = 3.5
serving_sandwich = 1.5

mean_arrival = 0.4

salad_queue = []
food_queue = []
sandwich_queue = []

env.process(student_generator(env, mean_arrival, stand_salad, stand_food, stand_sandwich,
                              serving_salad, serving_food, serving_sandwich))
env.run(until=120)

Mean_salad_queue = sum(salad_queue)/student_id
Mean_food_queue = sum(food_queue)/student_id
Mean_sandwich_queue = sum(sandwich_queue)/student_id

print(f'\nMean salad queue: {Mean_salad_queue}')
print(f'Mean food queue: {Mean_food_queue}')

print(f'Mean sandwich queue: {Mean_sandwich_queue}')
