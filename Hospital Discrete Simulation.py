import simpy
import random
import matplotlib.pyplot as plt


def arrival_generator(env, mean_arrival, mean_registration, mean_consultation, mean_book_surgery, receptionist, doctor):
    global patient_id

    while True:
        p = activity_generator(env, mean_registration, mean_consultation, mean_book_surgery, receptionist, doctor,
                               patient_id)
        env.process(p)
        t = random.expovariate(1 / mean_arrival)

        yield env.timeout(t)
        patient_id += 1


def call_generator(env, mean_call, mean_answering, receptionist):
    call_id = 1

    while True:
        q = call_activity(env, call_id, mean_answering, receptionist)
        env.process(q)

        w = random.expovariate(1 / mean_call)

        yield env.timeout(w)
        call_id += 1


def activity_generator(env, mean_registration, mean_consultation, mean_book_surgery, receptionist, doctor, patient_id):
    time_enter_registration = env.now
    global registration_queue
    global time_in_system

    with receptionist.request() as req:
        yield req

        time_left_registration = env.now
        time_in_registration = time_left_registration - time_enter_registration

        if env.now > warmup:
            print(f'Patient {patient_id} was in registration queue for {time_in_registration}')
            registration_queue.append(time_in_registration)

        registration_time = random.expovariate(1 / mean_registration)
        yield env.timeout(registration_time)

    time_enter_consultation = env.now
    global consultation_queue

    with doctor.request() as req:
        yield req

        time_left_consultation = env.now
        time_in_consultation = time_left_consultation - time_enter_consultation

        if env.now > warmup:
            print(f'Patient {patient_id} was in consultation queue for {time_in_consultation}')
            consultation_queue.append(time_in_consultation)

        consultation_time = random.expovariate(1 / mean_consultation)
        yield env.timeout(consultation_time)

    decision = random.uniform(0, 1)

    if decision < 0.25:

        time_enter_book_surgery = env.now
        global book_surgery_queue

        with receptionist.request() as req:
            yield req

            time_left_book_surgery = env.now
            time_in_book_surgery = time_left_book_surgery - time_enter_book_surgery

            if env.now > warmup:
                print(f'Patient {patient_id} was in book surgery queue for {time_in_book_surgery}')
                book_surgery_queue.append(time_in_book_surgery)

            book_surgery_time = random.expovariate(1 / mean_book_surgery)

            if env.now > warmup:
                time_in_system.append(time_left_book_surgery + book_surgery_time - time_enter_registration)

            yield env.timeout(book_surgery_time)

    else:
        if env.now > warmup:
            time_in_system.append(time_left_consultation + consultation_time - time_enter_registration)


def call_activity(env, call_id, mean_answering, receptionist):
    time_enter_call_queue = env.now
    with receptionist.request() as req:
        yield req

        time_left_call_queue = env.now
        time_in_call_queue = time_left_call_queue - time_enter_call_queue

        if env.now > warmup:
            print(f'Call {call_id} was in queue for {time_in_call_queue}')


        time_answering = random.expovariate(1 / mean_answering)
        yield env.timeout(time_answering)


runs = 100
random.seed(2024)

simulation_time = 60 * 8
warmup = 60 * 3

average_registration = []
average_consultation = []
average_book_surgery = []
average_time_in_system = []

for i in range(1, runs + 1):
    env = simpy.Environment()

    receptionist = simpy.Resource(env, capacity=1)
    doctor = simpy.Resource(env, capacity=2)

    patient_id = 1
    mean_arrival = 3
    mean_registration = 2
    mean_consultation = 8
    mean_book_surgery = 4

    mean_call = 10
    mean_answering = 4

    registration_queue = []
    consultation_queue = []
    book_surgery_queue = []
    time_in_system = []

    env.process(
        arrival_generator(env, mean_arrival, mean_registration, mean_consultation, mean_book_surgery, receptionist,
                          doctor))
    env.process(call_generator(env, mean_call, mean_answering, receptionist))

    env.run(until=warmup + simulation_time)

    Mean_registration_queue = sum(registration_queue) / patient_id
    Mean_consultation_queue = sum(consultation_queue) / patient_id
    Mean_book_surgery = sum(book_surgery_queue) / patient_id
    Mean_time_in_system = sum(time_in_system) / patient_id

    print(f'\nMean registration queue for run {i}: {Mean_registration_queue}')
    print(f'Mean consultation queue for run {i}: {Mean_consultation_queue}')
    print(f'Mean book surgery queue for run {i}: {Mean_book_surgery}')
    print(f'\nMean time in system for run {i}: {Mean_time_in_system}\n')

    average_registration.append(Mean_registration_queue)
    average_consultation.append(Mean_consultation_queue)
    average_book_surgery.append(Mean_book_surgery)
    average_time_in_system.append(Mean_time_in_system)

average_registration = sum(average_registration) / runs
average_consultation = sum(average_consultation) / runs
average_book_surgery = sum(average_book_surgery) / runs
average_time_in_system = sum(average_time_in_system) / runs

print(f'\nAverage registration queue for {runs} runs: {average_registration}')
print(f'Average consultation queue for {runs} runs: {average_consultation}')
print(f'Average book surgery queue for {runs} runs: {average_book_surgery}')
print(f'\nAverage time in system for {runs} runs: {average_time_in_system}\n')

categories = ['Average\nregistration queue', 'Average consultation\nqueue', 'Average\nbook surgery',
              'Average time\nin system']
values = [average_registration, average_consultation, average_book_surgery, average_time_in_system]
plt.bar(categories, values)
plt.title(f'Average time for queues for {runs} runs')
plt.ylabel('Time (minutes)')
for i, value in enumerate(values):
    plt.text(i, value + 0.1, f"{value:.4f}", ha='center', va='bottom')
plt.show()