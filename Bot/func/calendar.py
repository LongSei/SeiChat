import json
import asyncio
import aiofiles
from discord.ext import commands
from typing import List, Dict
from config.constant import *
from collections import deque
from datetime import datetime, timedelta
import copy

class CalendarUtils():
    def __init__(self, tasks):
        self.tasks = tasks

    def __remove_all_old_task(self):
        pass

    def __split_tasks_into_weeks(self):
        tasks_by_week = {}
        for task in self.tasks:
            task_datetime = datetime.strptime(task["time"], '%Y/%m/%d')
            start_of_week = task_datetime - timedelta(days=task_datetime.weekday())
            start_of_week_str = start_of_week.strftime('%Y/%m/%d')
            if start_of_week_str not in tasks_by_week:
                tasks_by_week[start_of_week_str] = [task]
            else:
                tasks_by_week[start_of_week_str].append(task)
        return tasks_by_week

    def __sort_task(self, week_tasks, start_of_week):
        dq = deque()
        AMOUNT_DAY_IN_WEEK = 7
        MAX_HOUR_PER_DAY = 12
        result = []

        non_const_task = []
        for task in week_tasks:
            if (task['is_constant'] == True):
                _ = datetime.strptime(task["time"], '%Y/%m/%d').weekday()
                schedule = [0 for __ in range(AMOUNT_DAY_IN_WEEK)]
                schedule[_] += task["duration"]
                schedule_detail = [[] for __ in range(AMOUNT_DAY_IN_WEEK)]
                schedule_detail[_].append(task)
                dq.append([0, schedule, schedule_detail])
            else:
                non_const_task.append(task)

        week_tasks = non_const_task
        for _ in range(AMOUNT_DAY_IN_WEEK):
            dayTime = datetime.strptime(start_of_week, "%Y/%m/%d") + timedelta(days=_)
            if (dayTime < (datetime.now() - timedelta(days=1))):
                continue
            else:
                schedule = [0 for _ in range(AMOUNT_DAY_IN_WEEK)]
                schedule[_] += week_tasks[0]["duration"]
                schedule_detail = [[] for _ in range(AMOUNT_DAY_IN_WEEK)]
                schedule_detail[_].append(week_tasks[0])
                dq.append([0, schedule, schedule_detail])

        AMOUNT_TASK = len(week_tasks)
        dp = [1000000 for _ in range(AMOUNT_TASK)]
        isAppend = [False for _ in range(AMOUNT_TASK)]

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
                        dayTime = datetime.strptime(start_of_week, "%Y/%m/%d") + timedelta(days=day)
                        if (dayTime < datetime.now()):
                            continue
                        elif (schedule[day] + week_tasks[new_task_index]["duration"]) <= MAX_HOUR_PER_DAY:
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

    def run(self):
        data = self.__split_tasks_into_weeks()
        day_in_next_week = datetime.strptime(list(data.keys())[-1], "%Y/%m/%d") + timedelta(days=7)
        next_week = datetime.strftime(day_in_next_week - timedelta(days=day_in_next_week.weekday()), "%Y/%m/%d")

        move_next_week = []
        for start_of_week in list(data.keys()):
            if (move_next_week):
                data[start_of_week] = data[start_of_week] + move_next_week
                move_next_week = []
            [data[start_of_week], move_next_week] = self.__sort_task(data[start_of_week], start_of_week)

            for dayIdx in range(0, len(data[start_of_week])):
                start_of_week_time = datetime.strptime(start_of_week, "%Y/%m/%d")
                new_date = start_of_week_time + timedelta(days=dayIdx)
                datetime_str = datetime.strftime(new_date, "%Y/%m/%d")
                for taskIdx in range(0, len(data[start_of_week][dayIdx])):
                    data[start_of_week][dayIdx][taskIdx]['time'] = datetime_str
        if (move_next_week):
            data[next_week] = move_next_week
        return data

class CalendarCog(commands.Cog):
    '''
    A cog within a Discord bot for managing calendar events efficiently.

    Functions include adding, viewing, and managing events.
    '''

    def __init__(self, bot):
        '''
        Initialize the CalendarCog class.

        Parameters
        ----------
        bot (discord.ext.commands.Bot): The Discord bot instance.
        '''
        self.bot = bot
        self.user_tasks = dict()
        asyncio.create_task(self.load_tasks())

    async def load_tasks(self):
        '''Load tasks from a JSON file asynchronously.'''
        try:
            async with aiofiles.open('user_tasks.json', 'r') as f:
                self.user_tasks = json.loads(await f.read())
        except FileNotFoundError:
            # Initialize to empty defaultdict if file doesn't exist
            pass
        except json.JSONDecodeError as e:
            # Log any JSON errors encountered during file reading
            print(f"Failed to decode JSON: {e}")

    async def save_tasks(self):
        '''Save the current tasks to a JSON file asynchronously.'''
        try:
            async with aiofiles.open('user_tasks.json', 'w') as f:
                await f.write(json.dumps(self.user_tasks, indent=4))
        except IOError as e:
            # Log any IO errors encountered during file writing
            print(f"Failed to write tasks to file: {e}")

    @commands.command(name="addtask", help="Add a task to the calendar.")
    async def add_task(self, ctx, category: str=None, task_name: str=None, time: str=None, duration: float=2.0, description: str=None):
        '''Add a task to the calendar.'''
        if None in (category, task_name, time, duration):
            await ctx.send("**There was an error, please enter the following command correctly:**\n```!addtask <Category> <Task Name> <Execution Time: 'YYYY/MM/DD'> [Execution Duration] [Description]```")
            return

        from datetime import datetime

        def check_datetime_format(input_str):
            try:
                datetime.strptime(input_str, "%Y/%m/%d")
                return True
            except ValueError:
                return False

        if not check_datetime_format(time):
            await ctx.send("**There is an error with the date data:** \n```Enter the date in the format: YYYY/MM/DD```")

        category = category.lower()
        task_name = task_name.lower()
        time = time.lower()

        try:
            new_task = {"category": category, "task_name": task_name, "time": time, "description": description, "duration": duration}

            message = await ctx.send("Do you want to set this as a recurring event?")
            await message.add_reaction(GREEN_TICK_EMOJI)
            await message.add_reaction(RED_CANCEL_EMOJI)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [RED_CANCEL_EMOJI, GREEN_TICK_EMOJI]

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=check)
                if str(reaction) == str(GREEN_TICK_EMOJI):
                    new_task["is_constant"] = True
                else:
                    new_task["is_constant"] = False
                self.user_tasks.setdefault(str(ctx.author), [])
                self.user_tasks[str(ctx.author)].append(new_task)
                await self.save_tasks()
                await ctx.send("Schedule added!")
            except:
                await ctx.send("An error occurred, please try again.")
        except:
            await ctx.send("An error occurred, please try again.")

    @commands.command(name="viewtasks", help="View all tasks in the calendar or modify a task.")
    async def view_tasks(self, ctx):
        '''View all tasks in the calendar or modify a task.'''
        if (str(ctx.author) not in self.user_tasks) or (not self.user_tasks[str(ctx.author)]):
            await ctx.send("You are completely free in the upcoming time.")
            return
        new_data = CalendarUtils(self.user_tasks[str(ctx.author)]).run()
        result = []
        for _ in new_data.values():
            for __ in _:
                for ___ in __:
                    result.append(___)
        self.user_tasks[str(ctx.author)] = result
        await self.save_tasks()

        tasks_map = {}

        for task_index, task in enumerate(self.user_tasks[str(ctx.author)], 1):
            tasks_display = f"------------------------\nCategory: {task['category']}\nTask Name: {task['task_name']}\nTime: {task['duration']} - {task['time']}\nDescription: {task['description']}\nRecurring Event: {'Yes' if task['is_constant'] else 'No'}\n"
            message = await ctx.send(f"Your tasks, {str(ctx.author)}:\n{tasks_display}")
            await message.add_reaction(RED_CANCEL_EMOJI)
            await message.add_reaction(SETTING_EMOJI)

            tasks_map[message.id] = task_index - 1

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [SETTING_EMOJI, RED_CANCEL_EMOJI] and reaction.message.id in tasks_map

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            if str(reaction) == str(RED_CANCEL_EMOJI):
                task_index = tasks_map[reaction.message.id]
                task = self.user_tasks[str(ctx.author)][task_index]
                self.user_tasks[str(ctx.author)].remove(task)
                await self.save_tasks()
                await reaction.message.delete()
                await self.view_tasks(ctx)
            elif str(reaction) == str(SETTING_EMOJI):
                task_index = tasks_map[reaction.message.id]
                task = self.user_tasks[str(ctx.author)][task_index]
                await self.modify_task(ctx, task)
        except asyncio.TimeoutError:
            print("Timeout: No reaction received.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    async def modify_task(self, ctx, task):
        '''Modify a task in the calendar.'''
        # Prompt user for modifications
        message = await ctx.send("What would you like to change?\n"
                                 "1. Category\n"
                                 "2. Name\n"
                                 "3. Time\n"
                                 "4. Description\n"
                                 "5. Duration\n"
                                 "6. Fixed or not")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == ctx.message.id and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

        # Define the reactions for each modification option
        options = {
            "1️⃣": "category",
            "2️⃣": "task_name",
            "3️⃣": "time",
            "4️⃣": "description",
            "5️⃣": "duration",
            "6️⃣": "is_constant"
        }

        for emoji in options.keys():
            await message.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            modification = options.get(str(reaction.emoji))

            if modification:
                await ctx.send(f"Enter the new {modification}:")
                new_value = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=60)

                if modification == "duration":
                    new_value = float(new_value.content)
                elif modification == "is_constant":
                    new_value = new_value.content.lower() == 'true'

                task[modification] = str(new_value.content)
                await self.save_tasks()
                await ctx.send("Schedule successfully updated")
            else:
                await ctx.send("Invalid selection")
        except asyncio.TimeoutError:
            print("Timeout: No reaction received.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
