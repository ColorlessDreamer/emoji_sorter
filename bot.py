import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands


load_dotenv()

# Define the command callback as a free async function.
async def show_emojis(interaction: discord.Interaction):
    guild = interaction.guild
    if guild:
        # Create list of emoji strings
        emoji_strings = [f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis]
        
        # Send initial response
        await interaction.response.send_message("Current emojis:")
        
        # Split emojis into chunks of 50 to stay well under the 2000 char limit
        chunk_size = 50
        for i in range(0, len(emoji_strings), chunk_size):
            chunk = ' '.join(emoji_strings[i:i + chunk_size])
            if chunk:  # Only send if chunk has content
                # Use followup since we can only use response once
                await interaction.followup.send(chunk)
    else:
        await interaction.response.send_message("No guild found for this interaction.")


# Manually wrap the function in an ApplicationCommand instance.
command_show_emojis = discord.app_commands.Command(
    callback=show_emojis,
    name="show_emojis",
    description="Display all server emojis"
)

async def update_emojis(order, guild):
    import re
    
    emoji_data = []
    for item in order:
        emoji = discord.utils.get(guild.emojis, id=int(item['id']))
        if emoji:
            # Strip existing sort prefix if present
            original_name = emoji.name
            if re.match(r'^j_\d{3}_', original_name):
                original_name = original_name[6:]  # Remove "f_XXX_" prefix
                
            emoji_data.append({
                'emoji': emoji,
                'original_name': original_name,
                'position': int(item['position'])
            })
    
    emoji_data.sort(key=lambda x: x['position'])
    
    for i, data in enumerate(emoji_data):
        await data['emoji'].edit(name=f"j_{i:03d}_{data['original_name']}")




class ConfirmView(discord.ui.View):
    def __init__(self, order, guild):
        super().__init__(timeout=60.0)
        self.order = order
        self.guild = guild

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Emoji order update confirmed!", ephemeral=True)
        await update_emojis(self.order, self.guild)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Emoji order update cancelled.", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True  # Add this line

        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        guild_id = int(os.getenv("GUILD_ID"))
        guild_obj = discord.Object(id=guild_id)
        
        @app_commands.command(name="sort", description="Get the link to sort emojis!")
        async def sort(interaction: discord.Interaction):
            # Permissions check: allow administrators, or optionally mods if enabled
            authorized = False
            # Check if the user is an administrator
            if interaction.user.guild_permissions.administrator:
                authorized = True

            if not authorized:
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
                return

            # Proceed if authorized
            domain_url = os.getenv("DOMAIN_URL")  # e.g., "https://yourdomain.com"
            channel_id = interaction.channel.id
            sort_link = f"{domain_url}/sort?channel_id={channel_id}"
            await interaction.response.send_message(
                f"Sort your emojis here: {sort_link}\nAfter saving your order on the page, I'll post a confirmation here.",
                ephemeral=True
            )
        self.tree.add_command(sort, guild=guild_obj)
        await self.tree.sync(guild=guild_obj)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

bot = Bot()

def run_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    run_bot()

