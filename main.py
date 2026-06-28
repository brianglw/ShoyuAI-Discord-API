import discord
import datetime
import os
import math
import logging
from ollama import Client
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
from app import _get_or_create_collection, query_sql, query_db, save_db, chat

load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
OLLAMA_HOST = os.getenv('OLLAMA_HOST') or os.getenv('PORT')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
client = Client(host=OLLAMA_HOST)
model_name = "shoyu_v1.03"
admin_role = 'secretary'

#in: a string of x words, limit of n words
#out: 
async def send_word_chunks(channel, resp : str, n : int = 2000):
    if (n <= 0): 
        raise ValueError("n must be greater than 0")

    msg_len = len(resp)

    for i in range(0, math.ceil(msg_len / 2000)):

        msg = " ".join(resp.split(" ")[:2000])
        await channel.send(msg)

        if (msg_len > 2000):
            complete_response = " ".join(complete_response.split(" ")[2000:])


@bot.event
async def on_ready():
    print("discord bot ready to run", bot.user.name)

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "cuck" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please refrain from using foul language in this server!")

    else:
        reply = ""
        user_query = message.content
        print(f"{message.author}", message.content)

        collection = _get_or_create_collection()
        docs = query_db(collection,user_query)
        save_db(collection,user_query)
        user_query += f"\nContext: {docs}\n"
        reply = chat(model_name,user_query)
        save_db(collection,reply)
        collection = _get_or_create_collection()

        await send_word_chunks(message.channel, reply)
    # await bot.process_commands(complete_response)
    #send messages over 2000 words long separately



@bot.command()
async def hello(ctx):
    await ctx.send(f"hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=admin_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned {admin_role}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=admin_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} is now unassigned {admin_role}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f'You said {msg}')

@bot.command()
async def reply(ctx):
    await ctx.reply('this is a reply to your message!')

@bot.command()
async def poll(ctx,*,question):
    embed = discord.Embed(title="Pokemon Quiz", description=question)
    poll = await ctx.send(embed=embed)
    await poll.add_reaction("🔥")

@bot.command()
@commands.has_role(admin_role)
async def secret(ctx):
    await ctx.send(f"Welcome to the admin team: {ctx.author.mention}")

@secret.error
async def secret_err(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the permission to do that")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)