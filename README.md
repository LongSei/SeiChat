# SeiChat

## Các tính năng: 
- Take note lại các việc cần làm (In progress...)
- Sắp xếp lịch trình (In progress...)
- Quản lí chi tiêu (In progress...)
- Quản lí thông tin

## Requirements
``` sh
pip install -r requirements.txt
```

## Cách làm việc với một tính năng mới: 
- Mọi người clone lại git này rồi tạo branch mới:
``` sh
$ git clone https://github.com/LongSei/SeiChat.git
$ git checkout -b <feature-branch-name>
```

- Rồi vào folder "func":
``` sh
$ cd Bot/func
```



- Trong đây mọi người sẽ nhìn thấy một tính năng của bot được cài đặt mẫu: 
``` python
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="Responds with 'pong'")
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command(name="pong", description="Responds with 'ping'")
    async def pong(self, ctx):
        await ctx.send("ping")
```

- Mọi người sẽ cài đặt các tính năng thành các class như trong mẫu xong sau đó ném file của mọi người vào thư mục này. 

- Add tên của class vào file "./config/env.py"
``` python
from func.example import PingCog

BOT_AUTHORIZE_TOKEN="MTIzMTUzNDY1Mjc4Nzc4NTc3OQ.GeUkOq.00YSAZ8r0ald6xKxitwJaXW0I4J9_aLEbFeows"
BOT_COMMAND_PREFIX="!"

BOT_CONFIG_LIST = [PingCog, <Tên Class Tính Năng>, ...]
``` 

- Sau khi code xong thì tạo một pull request mới: 

``` sh
$ git add .
$ git commit -m "Comment Cho Commit"
$ git push origin feature-branch-name
```

- Bạn sẽ check pull request của mọi người để merge vào project nhé. 