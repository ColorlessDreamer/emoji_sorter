from flask import Flask, render_template, jsonify, request
from bot import bot, ConfirmView
import os
import math
import asyncio
import discord

app = Flask(__name__)

@app.route('/sort')
def sort_page():
    # You might want to use request.args.get("channel_id") if needed.
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
    # Sort emojis by name
    emoji_data.sort(key=lambda x: x['name'])
    return jsonify(emoji_data)


@app.route('/saveOrder', methods=['POST'])
async def save_order():
    data = request.json
    # If data is a list, assign it directly
    if isinstance(data, list):
        new_order = data
        channel_id = None  # you might need to get channel_id via another mechanism, e.g. query parameter
    else:
        new_order = data.get("order")
        channel_id = data.get("channel_id")
    print("Received new order:", new_order)
    # Schedule sending the confirmation message if channel_id is provided, otherwise handle it appropriately.
    if channel_id:
        bot.loop.create_task(send_confirmation_message(new_order, channel_id))
    else:
        print("No channel_id provided; cannot send confirmation message.")
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

