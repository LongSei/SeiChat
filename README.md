# SeiChat

## Các tính năng: 
- Take note lại các việc cần làm (✅)
- Sắp xếp lịch trình (✅)
- Quản lí chi tiêu (In progress...)
- Quản lí thông tin
- Summarize kiến thức
- Kiểm tra lại kiến thức bằng câu hỏi

## Cách làm việc với một tính năng mới:

1.  Clone lại git này và tạo branch mới:
    
    ```bash
    $ git clone [https://github.com/LongSei/SeiChat.git](https://github.com/LongSei/SeiChat.git)
    $ git checkout -b <feature-branch-name>
    ```
    
2.  Di chuyển vào folder "func":
    
    ```bash
    $ cd Bot/func
    ```
    
3.  Cài đặt các tính năng thành các class Python, tham khảo mẫu:
    
    ```python
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
    
4.  Thêm tên class của bạn vào file "./config/env.py":
    
    ```python
    from func.example import PingCog
    
    BOT_AUTHORIZE_TOKEN="DISCORD_TOKEN"
    BOT_COMMAND_PREFIX="!"
    
    BOT_CONFIG_LIST = [PingCog, <Tên Class Tính Năng>, ...]
    ```
    
5.  Sau khi hoàn thành, tạo một pull request mới:
    
    ```bash
    $ git add .
    $ git commit -m "Comment Cho Commit"
    $ git push origin feature-branch-name
    ```
