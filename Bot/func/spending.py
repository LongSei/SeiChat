import json
import asyncio
import aiofiles
from discord.ext import commands
from collections import defaultdict
from config.constant import *
from datetime import datetime, timedelta
from typing import List, Dict
import os

class SpendingCog(commands.Cog):
    
    #print("Working directory : ", os.getcwd())
    '''
    SpedingCog : A Discord bot cog for managing spending

    Commands
    --------
    record
    classify
    remind
    '''
    
    def __init__(self, bot):
        self.bot = bot
        self.user_spedings = defaultdict(list)
        asyncio.create_task(self.load_records())
    
    '''
    async def load_records(self) :
        try :
            async with aiofiles.open('user_spedings.json', 'r') as f :
                self.user_spedings = json.loads(await f.read())
        except FileNotFoundError :
            print("FileNotFoundError")
        except json.JSONDecodeError as e :
            print(f"Failed to decode JSON : {e}")
        except IOError :
    '''
    async def load_records(self):
        try:
            async with aiofiles.open('user_spedings.json', 'r') as f:
                self.user_spedings = json.loads(await f.read())
        except FileNotFoundError :
            print("failed")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
        except IOError:
            print("IOError: Creating a new file.")
            # Tạo một tệp mới nếu nó không tồn tại
            await self.save_records()
        else:
            print("Records loaded successfully.")

    async def save_records(self) :
        try :
            async with aiofiles.open('user_spedings.json', 'w') as f :
                await f.write(json.dumps(self.user_spedings, indent = 4))
        except IOError as e :
            print(f"Failed to write decision to file: {e}")

    
    @commands.command(name = "record", help="Record each time they spend by entering an amount and transaction description.")
    async def record(self, ctx, time: str = None, money: int = 0, cript: str = None):
        if None in (time, cript):
            await ctx.send("**There was an error, please enter the following command correctly :**\n ```!record <Time: 'YYYY/MM/DD'> <Money> <Description>```")
            return
        
        from datetime import datetime

        def check_datetime_format(input_str):
            try:
                datetime.strptime(input_str, "%Y/%m/%d")
                return True
            except ValueError:
                return False
            
        if not check_datetime_format(time):
            await ctx.send("**There is an error with the date data:**\n ```Enter the date in the format: YYYY/MM/DD```")
        
        time = time.lower()
        cript = cript.lower()

        try : 
            new_record = {"time": time, "money": money, "description": cript}

            message = await ctx.send("**Do you receive money or spend money?**")
            await message.add_reaction(RECEIVE_MONEY_EMOJI)
            await message.add_reaction(SPEND_MONEY_EMOJI)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [RECEIVE_MONEY_EMOJI, SPEND_MONEY_EMOJI]
            
            try :
                reaction, _ = await self.bot.await_for('reaction_add', check=check)
                if str(reaction) == str(RECEIVE_MONEY_EMOJI) :
                    new_record["receive_money"] = True
                else :
                    new_record["receive_money"] = False
                
                self.user_spedings.setdefault(str(ctx.author), [])
                self.user_spedings[str(ctx.author)].append(new_record)
                await self.save_records()
                await ctx.send("**Record added!**")
            except :
                await ctx.send("**An error occurred, please try again!**")
        except :
            await ctx.send("**An error occured, please try again!**")