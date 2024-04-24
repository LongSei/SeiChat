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

CATEGORY_ORDER = ["🔴", "🟡", "🔵", "🟢"]
GREEN_TICK_EMOJI ="✅"

class NoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.note_queue = deque(maxlen = 10)
    

    async def print_remaining_notes(self, ctx):
        remaining_notes = "\n".join([f'{index}. {note[0]}: {note[1]}' for index, note in enumerate(self.note_queue, 1)])
        await ctx.send(f"Update notes: \n{remaining_notes}")

    @commands.command(name="takenote", help ="Take a note")
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
     
    @commands.command(name="viewnotes", help="View all notes")
    async def view_note(self, ctx):
        if not self.note_queue:
            await ctx.send("No notes available")
            return
        sorted_notes = sorted(self.note_queue, key=lambda x: CATEGORY_ORDER.index(x[0]))
        self.note_messages = {}
        note_counter = 1

        for index, note in enumerate(sorted_notes):
            note_text = f'{note_counter}. {note[0]}: {note[1]}'  
            message = await ctx.send(note_text)
            self.note_messages[message.id] = note[0]  
            await message.add_reaction(GREEN_TICK_EMOJI)
            note_counter += 1

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == GREEN_TICK_EMOJI and reaction.message.id in self.note_messages

        try:
            while True:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=180.0, check=check) #3 minutes to wait
                await ctx.send("Note completed. ✅")
                message_id = reaction.message.id
                completed_category = self.note_messages.get(message_id)
                if completed_category:
                    self.note_queue = [note for note in self.note_queue if note[0] != completed_category] 
                    del self.note_messages[message_id] 
                    await reaction.message.delete()
                    await self.print_remaining_notes(ctx)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="deletenote", help="delete a note")
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
            await self.print_remaining_notes(ctx)
        else:
            await ctx.send('Invalid note number')

