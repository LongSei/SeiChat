from discord.ext import commands
from datetime import datetime, timedelta

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.expense_limit = 2000
        self.expense_period = 1
        self.expenses = {}
        self.last_reset = datetime.now()
        self.current_balance = {}

    @commands.command(name="spend", help="Dùng số tiền để uống trà sữa: !spend <số tiền>")
    async def spend_money(self, ctx, amount: int):
        user_id = ctx.author.id
        current_date = datetime.now()

        if current_date - self.last_reset > timedelta(days=self.expense_period):
            self.expenses.clear()
            self.last_reset = current_date

        if user_id not in self.expenses:
            self.expenses[user_id] = amount
        else:
            self.expenses[user_id] += amount

        total_expenses = sum(self.expenses.values())

        if total_expenses > self.expense_limit:
            await ctx.send("vượt mức chi tiêu")
        else:
            await ctx.send("tiêu tiền tiếp đi")
        
        await self.update_current_balance(ctx)

    @commands.command(name="addmoney", help="Nạp tiền vào tài khoản: !addmoney <số tiền>")
    async def add_money(self, ctx, amount: int):
        user_id = ctx.author.id
        self.current_balance[user_id] = self.current_balance.get(user_id, 0) + amount
        await ctx.send(f"Đã nạp thành công {amount} vào tài khoản của bạn.")
        
        await self.update_current_balance(ctx)

    @commands.command(name="amount", help="Số dư: !amount")
    async def get_amount(self, ctx):
        user_id = ctx.author.id
        user_balance = self.get_balance_from_database(user_id)
        
        current_balance = self.current_balance.get(user_id, 0)
        
        await ctx.send(f"Số dư của bạn là: {user_balance}. Số tiền hiện có: {current_balance}")

    async def update_current_balance(self, ctx):
        user_id = ctx.author.id
        user_balance = self.get_balance_from_database(user_id)
        self.current_balance[user_id] = user_balance

    def get_balance_from_database(user_id):
        return 1000

    def add_balance_to_database(user_id, amount):
        pass
