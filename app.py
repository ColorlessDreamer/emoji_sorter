from flask import Flask, render_template, jsonify, request
from bot import bot
import asyncio
import os
import discord

app = Flask(__name__)

from flask import Flask, render_template, jsonify
from bot import bot
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emojis')
def get_emojis():
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    emoji_data = [
        {
            'id': str(emoji.id),
            'name': emoji.name,
            'url': str(emoji.url)
        }
        for emoji in guild.emojis
    ]
    return jsonify(emoji_data)


@app.route('/update-order', methods=['POST'])
async def update_order():
    new_order = request.json
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    
    # Create a mapping of emoji positions
    emoji_positions = {
        emoji.id: position for position, emoji in 
        enumerate(sorted(guild.emojis, key=lambda e: e.position))
    }
    
    # Update positions based on new order
    for item in new_order:
        emoji = discord.utils.get(guild.emojis, id=int(item['id']))
        if emoji:
            await emoji.edit(position=item['position'])
    
    return jsonify({'status': 'success'})
