from collections import deque
import copy 

class TaskScheduler:
    def __init__(self):
        pass

    def sort_task(self, week_tasks):
        dq = deque()
        AMOUNT_TASK = len(week_tasks)
        AMOUNT_DAY_IN_WEEK = 7
        MAX_HOUR_PER_DAY = 12

        dp = [1000000 for _ in range(AMOUNT_TASK)]
        result = []
        isAppend = [False for _ in range(AMOUNT_TASK)]

        for _ in range(AMOUNT_DAY_IN_WEEK):
            schedule = [0 for _ in range(AMOUNT_DAY_IN_WEEK)]
            schedule[_] += week_tasks[0]["duration"]
            schedule_detail = [[] for _ in range(AMOUNT_DAY_IN_WEEK)]
            schedule_detail[_].append(week_tasks[0])
            dq.append([0, schedule, schedule_detail])
        isAppend[0] = True
        while dq:
            task_index, schedule, schedule_detail = dq.popleft()
            diff = max(schedule) - min(schedule)
            if dp[task_index] > diff:
                dp[task_index] = diff
                result = schedule_detail
                if task_index == AMOUNT_TASK - 1:
                    continue
                else:
                    new_task_index = task_index + 1
                    for day in range(AMOUNT_DAY_IN_WEEK):
                        if (schedule[day] + week_tasks[new_task_index]["duration"]) <= MAX_HOUR_PER_DAY:
                            isAppend[new_task_index] = True
                            new_schedule = copy.deepcopy(schedule)
                            new_schedule[day] += week_tasks[new_task_index]["duration"]
                            new_schedule_detail = copy.deepcopy(schedule_detail)
                            new_schedule_detail[day].append(week_tasks[new_task_index])
                            dq.append([new_task_index, new_schedule, new_schedule_detail])

        for taskIdx in range(AMOUNT_TASK):
            if not isAppend[taskIdx]:
                return [result, [week_tasks[idx] for idx in range(taskIdx, AMOUNT_TASK)]]
        return [result, []]

# Create an instance of TaskScheduler
scheduler = TaskScheduler()

# Sample data of tasks for the week
# Replace this with your own data
sample_data = [
    {"task": "Task 1", "duration": 2},
    {"task": "Task 2", "duration": 3},
    {"task": "Task 3", "duration": 1},
    {"task": "Task 4", "duration": 2},
    {"task": "Task 5", "duration": 2},
    {"task": "Task 6", "duration": 1},
    {"task": "Task 7", "duration": 3},
    {"task": "Task 8", "duration": 2}
]

# Run the scheduling algorithm
result = scheduler.sort_task(sample_data)

# Print the result
for _ in result[0]: 
    print(_)
