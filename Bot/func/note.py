import discord
import asyncio
from discord.ext import commands
from collections import defaultdict
import json

CATEGORY_EMOJIS = {
    "red": "🔴",
    "yellow": "🟡",
    "blue": "🔵",
    "green": "🟢"
}

CATEGORY_ORDER = ["🔴", "🟡", "🔵", "🟢"]
GREEN_TICK_EMOJI = "✅"

class NoteCog(commands.Cog):
    ''' 
    NoteCog: A Discord bot cog for managing notes.

    Usage
    -----
    This cog allows users to take notes, view all notes, mark notes as completed, and delete specific notes.

    Commands
    --------
    takenote: Take a note and assign it to a category.
    viewnotes: View all notes and mark them as completed.
    deletenote: Delete a specific note from the note queue.
    '''

    def __init__(self, bot):
        ''' 
        Initialize the NoteCog class.

        Parameters
        ----------
        bot (discord.ext.commands.Bot): The Discord bot instance.
        '''
        self.bot = bot
        self.user_notes = defaultdict(list)  # Dictionary to store notes for each user
        self.load_notes()  # Load notes data on bot startup

    def load_notes(self):
        ''' 
        Load user notes data from JSON files.
        '''
        try:
            with open('user_notes.json', 'r') as f:
                self.user_notes = json.load(f)
        except FileNotFoundError:
            pass

    def save_notes(self):
        ''' 
        Save user notes data to a JSON file.
        '''
        with open('user_notes.json', 'w') as f:
            json.dump(self.user_notes, f)

    async def __print_remaining_notes(self, ctx):
        '''
        Usage
        ----- 
        Print the remaining notes in the note queue.

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The context in which the command was invoked.
        '''
        user_id = str(ctx.author.id)
        if user_id not in self.user_notes or not self.user_notes[user_id]:
            await ctx.send("No notes available")
            return

        remaining_notes = "\n".join([f'{index}. {note[0]}: {note[1]}' for index, note in enumerate(self.user_notes[user_id], 1)])
        await ctx.send(f"Your notes: \n{remaining_notes}")

    @commands.command(name="takenote", help=":Take a note")
    async def take_note(self, ctx, *, note: str = None):
        '''
        Usage
        ----- 
        Take a note and assign it to a category.

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The context in which the command was invoked.
        note (string, optional): The note to be taken. Defaults to None.
        '''
        if note is None:
            await ctx.send("Please provide a note.")
            return

        user_id = str(ctx.author.id)
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
        self.user_notes[user_id].append((category_emoji, note))
        self.save_notes()  # Save notes after adding a new note
        await ctx.send(f'Note added to category {category_emoji}: {note}')

    @commands.command(name="viewnotes", help=":View all notes")
    async def view_note(self, ctx):
        '''
        Usage
        ----- 
        View all notes and mark them as completed.

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The context in which the command was invoked.
        '''
        user_id = str(ctx.author.id)
        if user_id not in self.user_notes or not self.user_notes[user_id]:
            await ctx.send("No notes available")
            return
        
        sorted_notes = sorted(self.user_notes[user_id], key=lambda x: CATEGORY_ORDER.index(x[0]))
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
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=180.0, check=check)  # 3 minutes to wait
                await ctx.send("Note completed. ✅")
                message_id = reaction.message.id
                completed_category = self.note_messages.get(message_id)
                if completed_category:
                    self.user_notes[user_id] = [note for note in self.user_notes[user_id] if note[0] != completed_category] 
                    self.save_notes()  # Save notes after marking a note as completed
                    del self.note_messages[message_id] 
                    await reaction.message.delete()
                    await self.__print_remaining_notes(ctx)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="deletenote", help=":delete a note")
    async def delete_note(self, ctx, note_number: int):
        '''
        Usage
        ----- 
        Delete a specific note from the note queue.

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The context in which the command was invoked.
        note_number (int): The number of the note to be deleted.
        '''
        user_id = str(ctx.author.id)
        if user_id not in self.user_notes or not self.user_notes[user_id]:
            await ctx.send("No notes available")
            return

        if note_number < 1 or note_number > len(self.user_notes[user_id]):
            await ctx.send("Invalid note number.")
            return
        
        delete_note = self.user_notes[user_id].pop(note_number - 1)
        self.save_notes()  # Save notes after deleting a note
        await ctx.send(f'Note deleted: {delete_note}')
        await self.__print_remaining_notes(ctx)
