import discord
import asyncio
from discord.ext import commands
from collections import deque

CATEGORY_EMOJIS = {
    "red": "🔴",
    "yellow": "🟡",
    "blue": "🔵",
    "green": "🟢"
}

class NoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.note_queue = deque(maxlen = 10)
    

    @commands.command(name="takenote", description ="Take a note")
    async def take_note(self, ctx, *, note):
        note_message = await ctx.send(f'Note added: {note}, please select your category:')
        for emoji in CATEGORY_EMOJIS.values():
            await note_message.add_reaction(emoji)
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in CATEGORY_EMOJIS.values()
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timed out. No category selected.")
            return
        category_emoji = reaction.emoji
        category = [key for key, value in CATEGORY_EMOJIS.items() if value == category_emoji][0]
        self.note_queue.append((category_emoji, note))
        await ctx.send(f'Note added to category {category_emoji}: {note}')
     
    @commands.command(name="viewnotes", description = "View all notes")
    async def view_note(self, ctx):
        notes = '\n'.join([f'{note[0]}: {note[1]}' for note in self.note_queue])
        if notes:
            await ctx.send(f'Notes:\n{notes}')
        else:
            await ctx.send("No notes available")

    @commands.command(name="deletenote", description="delete a note")
    async def delete_note(self, ctx, note_number: int):
        try:
            note_number = int(note_number)
        except ValueError:
            await ctx.send("Invalid note number. Please enter a valid integer.")
            return
        
        if 1 <= note_number <= len(self.note_queue):
            delete_note = self.note_queue[note_number - 1]
            del self.note_queue[note_number - 1]
            await ctx.send(f'Note deleted: {delete_note}')
        else:
            await ctx.send('Invalid note number')

