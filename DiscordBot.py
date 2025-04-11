import discord
from discord.ext import commands

class Client(commands.Bot):
    GUILD_ID = discord.Object(id="Your guild ID")
    SCOREBOARD_CHANNEL_ID = "your channel ID"
    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to {guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

def makeEmbed():
    embed = discord.Embed(
        title="💰 Bar' Kas",
        color=discord.Color.gold()  # You can customize this
    )
    return embed

class View(discord.ui.View):
    async def update_scoreboard(self, button, name: str):
        channel = client.get_channel(SCOREBOARD_CHANNEL_ID)
        messages = [msg async for msg in channel.history(limit=10) if msg.author == client.user]
        
        scores = {"Kjeldsen": 0, "Amstrup": 0, "Sommer": 0}

        if messages:
            last_message = messages[0]
            content = last_message.embeds[0].fields if last_message.embeds else []

            for field in content:
                try:
                    score_line = field.value  # Example: "**Score:** 2\n**Beløb:** 10 kr"
                    lines = score_line.split("\n")
                    score = int(lines[0].split("**")[2])  # "**Score:** 2"
                    scores[field.name] = score
                except Exception as e:
                    print(f"Failed to parse embed field: {field.name}, error: {e}")
        if name in scores:
            scores[name] += 1
        else:
            scores[name] = 1
        embed = makeEmbed()
        for user, score in scores.items():
            embed.add_field(
                name=user,
                value=f"**#Bare:** {score}\n**Beløb:** {score * 5} kr",
                inline=False
            )
        await channel.send(embed=embed, view=View())
        await button.response.defer()

    @discord.ui.button(label="Name 1", style=discord.ButtonStyle.blurple)
    async def kjeldsen_callback(self, button, interaction):
        await self.update_scoreboard(button, 'Name 1')
    
    @discord.ui.button(label="Name 2", style=discord.ButtonStyle.red)
    async def amstrup_callback(self, button, interaction):
        await self.update_scoreboard(button, "Name 2")

    @discord.ui.button(label="Name 3", style=discord.ButtonStyle.green)
    async def sommer_callback(self, button, interaction):
        await self.update_scoreboard(button, "Name 3")

@client.tree.command(name="buttons", description="make buttons", guild=GUILD_ID)
async def button(interaction: discord.Interaction):
    await interaction.response.send_message(view=View())

@client.tree.command(name="resume", description="Resume the scoreboard if the bot restarts", guild=GUILD_ID)
async def resume(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    channel = client.get_channel(SCOREBOARD_CHANNEL_ID)
    messages = [msg async for msg in channel.history(limit=10) if msg.author == client.user and msg.embeds]

    if not messages:
        await interaction.followup.send("No previous scoreboard found.", ephemeral=True)
        return

    last_embed = messages[0].embeds[0]
    new_embed = makeEmbed()

    for field in last_embed.fields:
        new_embed.add_field(name=field.name, value=field.value, inline=False)

    await channel.send(embed=new_embed, view=View())
    await interaction.followup.send("Scoreboard resumed!", ephemeral=True)

client.run('your token here')
