from library import *

def check_exist_command(bot, command_name): 
    if bot.get_command(command_name):
        exit("Command: {COMMAND} is exists !!!".format(COMMAND=command_name))
    return False

async def setup_command(bot, config_list):
    for config_name in config_list:
        config = config_name(bot)
        command_list = [_.name for _ in config.get_commands()]
        for command_name in command_list:
            check_exist_command(bot, command_name)
        await bot.add_cog(config)

async def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=BOT_COMMAND_PREFIX, intents=intents)
    await setup_command(bot, BOT_CONFIG_LIST)  
    await bot.start(BOT_AUTHORIZE_TOKEN) 

if __name__ == "__main__":
    import asyncio
    print("Bot Started !!!")
    asyncio.run(main()) 
