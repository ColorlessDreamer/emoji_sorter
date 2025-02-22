from flask import Flask, render_template, jsonify, request, session
from bot import bot, ConfirmView
import os
from datetime import timedelta
import discord

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)

@app.route('/sort')
def sort_page():
    session_id = request.args.get('session')
    if not session_id or session_id not in bot.active_sessions:
        return "Invalid session", 403
        
    session.permanent = True
    session['guild_id'] = bot.active_sessions[session_id]['guild_id']
    session['channel_id'] = bot.active_sessions[session_id]['channel_id']
    
    # Clean up the temporary storage
    del bot.active_sessions[session_id]
    
    return render_template('index.html')

@app.route('/emojis')
def get_emojis():
    if 'guild_id' not in session:
        return "Session expired", 403
        
    guild = bot.get_guild(int(session['guild_id']))
    emoji_data = [
        {
            'id': str(emoji.id),
            'name': emoji.name,
            'url': str(emoji.url)
        }
        for emoji in guild.emojis
    ]
    emoji_data.sort(key=lambda x: x['name'])
    return jsonify(emoji_data)

@app.route('/saveOrder', methods=['POST'])
async def save_order():
    if 'channel_id' not in session:
        return "Session expired", 403
        
    data = request.json
    new_order = data.get("order")
    channel_id = session['channel_id']
    bot.loop.create_task(send_confirmation_message(new_order, channel_id))
    return jsonify({'status': 'confirmation task scheduled'})



async def send_confirmation_message(order, channel_id):
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    if not guild:
        print("Guild not found!")
        return

    # Inside send_confirmation_message():
    emoji_tags = []
    for item in order:
        emoji = discord.utils.get(guild.emojis, id=int(item['id']))
        if emoji:
            if emoji.animated:
                emoji_tags.append(f"<a:{emoji.name}:{emoji.id}>")
            else:
                emoji_tags.append(f"<:{emoji.name}:{emoji.id}>")
        else:
            emoji_tags.append(f"EmojiID({item['id']})")



    full_content = " ".join(emoji_tags)
    discord_limit = 2000

    # Split the full_content in evenly sized parts if needed.
    if len(full_content) <= discord_limit:
        details_parts = [full_content]
    else:
        import math
        num_parts = math.ceil(len(full_content) / discord_limit)
        total_tags = len(emoji_tags)
        tags_per_part = math.ceil(total_tags / num_parts)
        details_parts = []
        for i in range(0, total_tags, tags_per_part):
            part = " ".join(emoji_tags[i:i+tags_per_part])
            if len(part) > discord_limit:
                part = part[:discord_limit-3] + "..."
            details_parts.append(part)

    # Now get the channel where the /sort command was issued.
    channel = bot.get_channel(int(channel_id))
    if not channel:
        print("Channel with ID", channel_id, "not found!")
        return

    # Build a SHORT main confirmation message.
    main_msg = f"This will be the new order for {len(emoji_tags)} emojis.\nThey gud?"
    view = ConfirmView(order, guild)
    try:
        confirmation_message = await channel.send(main_msg, view=view)
        print(f"Sent confirmation message to channel {channel_id} with message ID: {confirmation_message.id}")
    except discord.HTTPException as e:
        print("Failed to send confirmation message:", e)
        return

    for idx, part in enumerate(details_parts):
        try:
            await channel.send(f"Cool emojis (part {idx+1}):\n{part}")
        except discord.HTTPException as e:
            print("Failed to send order details part:", e)

    await view.wait()
    print("IT WORKED")

