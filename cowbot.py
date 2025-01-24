import asyncio
import discord
from discord.ext import commands
from config import TOKEN

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
#intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents,help_command=None)  # Disable the default help command

# Store user data and tasks
user_data = {}  # {user_id: {"xp": xp_value, "study_time": time_in_channel, "tasks": [task_ids]}}
tasks_data = {}  # {task_id: {"task_name": "Task Name", "difficulty": level, "completed": bool}}

# Task difficulty mapping
difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}


# Helper function to update XP
def add_xp(user_id, xp):
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "study_time": 0, "tasks": []}
    user_data[user_id]["xp"] += xp


# Helper function to calculate XP from study time
def calculate_xp_from_study_time(time):
    # Assume 1 XP per minute
    return time

# Command to start and stop studying
@bot.command()
async def study(ctx):
    """Start or stop studying in the study channel."""
    user_id = ctx.author.id
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "study_time": 0, "tasks": [], "study_task": None}

    if user_data[user_id]["study_time"] == 0:
        # Start studying, track time (set study_time to 1 minute immediately)
        embed_start = discord.Embed(
            title=f"🌌🚀 {ctx.author.name} has blasted off to study! 🛸🌠",
            description="Yeehaw! You're off to the stars, partner. Let's rack up them XP points and get some good ol' brain fuel!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed_start)
        user_data[user_id]["study_time"] = 1  # Starts with 1 minute (instead of 0)
        user_data[user_id]["xp"] = 0  # Award 0 XP when study starts

        # Start a task to increase XP every minute and remind every 30 minutes
        async def study_timer():
            while user_data[user_id]["study_time"] > 0:  # Continue as long as study_time > 0
                # Wait for 1 minute
                await asyncio.sleep(60)
                user_data[user_id]["study_time"] += 1  # Increase study time by 1 minute
                user_data[user_id]["xp"] += 1  # Award 1 XP per minute

                # Embed for study progress
                #embed_progress = discord.Embed(
                #    title=f"🚀 Study Progress for {ctx.author.name} 🛸",
                #    description=f"Yeehaw! You've studied for {user_data[user_id]['study_time']} minutes in deep space!",
                #    color=discord.Color.blue()
                #)
                #embed_progress.add_field(name="Total XP", value=f"{user_data[user_id]['xp']} XP (That's some good space brainpower!)", inline=False)
                #await ctx.send(embed=embed_progress)

                # Every 30 minutes, remind the user to take a break
                if user_data[user_id]["study_time"] % 30 == 0:
                    embed_reminder = discord.Embed(
                        title="🌠 Time for a Cosmic Break! 🛸",
                        description=f"Whoa there, {ctx.author.name}! You've been studying for 30 minutes. Time to stretch those space legs and grab some space-moo-lk!",
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=embed_reminder)

        user_data[user_id]["study_task"] = asyncio.create_task(study_timer())

    else:
        # Stop studying, finalize XP
        embed_finish = discord.Embed(
            title=f"🚀 {ctx.author.name} has returned to the mothership! 🌌",
            description=f"Well done, space cadet! You’ve earned {user_data[user_id]['xp']} XP from your stellar study session. Time to recharge and get ready for the next adventure!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed_finish)

        # Stop the study timer
        user_data[user_id]["study_task"].cancel()
        user_data[user_id]["study_time"] = 0  # Reset the study timer
        user_data[user_id]["study_task"] = None  # Reset the task reference



# Command to create a new task
@bot.command()
async def create_task(ctx, name: str = None, difficulty: str = None):
    """Create a new task with a name and difficulty level."""

    # Check if task name is provided
    if not name:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description="Howdy Partner, please provide a task name! It can't be empty.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if difficulty is provided
    if not difficulty:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description="Howdy Partner, please provide a difficulty level (1 for Easy, 2 for Medium, or 3 for Hard).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if task name is valid (non-empty and doesn't contain special characters)
    if len(name.strip()) == 0:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description="Howdy Partner, task name can't be empty.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if task name is already taken
    if name in [task['task_name'] for task in tasks_data.values()]:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description=f"Yeehaw! A task with the name '{name}' already exists. Try another name!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Attempt to convert the difficulty level to an integer
    try:
        difficulty = int(difficulty)
    except ValueError:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description="Howdy Partner, difficulty level must be a valid integer. Choose 1 for Easy, 2 for Medium, or 3 for Hard.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if difficulty is valid
    if difficulty not in difficulty_map:
        embed_error = discord.Embed(
            title="❌ Task Creation Failed!",
            description="Invalid difficulty! Choose from: \n1 - Easy \n2 - Medium \n3 - Hard",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Create the task
    task_id = len(tasks_data) + 1
    tasks_data[task_id] = {"task_name": name, "difficulty": difficulty, "completed": False}

    # Success embed
    embed_success = discord.Embed(
        title="✅ Task Created Successfully!",
        description=f"Yeehaw! Task '{name}' has been successfully created.",
        color=discord.Color.green()
    )
    embed_success.add_field(name="Difficulty", value=f"{difficulty_map[difficulty]}", inline=False)
    embed_success.add_field(name="Task ID", value=str(task_id), inline=False)
    embed_success.set_footer(text="Time to get to work, partner! 🤠")

    await ctx.send(embed=embed_success)

# Command to list tasks
@bot.command()
async def list_tasks(ctx):
    """List all tasks."""

    if not tasks_data:
        embed_no_tasks = discord.Embed(
            title="🛑 No Tasks Available",
            description="Looks like there are no tasks at the moment, partner! Get to work and add some tasks to get started!",
            color=discord.Color.red()
        )
        embed_no_tasks.set_footer(text="No tasks yet")
        await ctx.send(embed=embed_no_tasks)
        return

    embed = discord.Embed(
        title="📝 List of Tasks",
        description="Here's a list of all tasks. Let's get to work!",
        color=discord.Color.blue()
    )

    # Loop through tasks and add them to the embed
    for task_id, task in tasks_data.items():
        difficulty = difficulty_map.get(task['difficulty'], "Unknown Difficulty")  # Fallback for unknown difficulty
        completion_status = "✅ Completed" if task["completed"] else "❌ Not Completed"

        # Add each task to the embed with more information
        embed.add_field(
            name=f"Task {task_id}: {task['task_name']}",
            value=f"**Difficulty**: {difficulty}\n**Status**: {completion_status}",
            inline=False
        )

    # Handle pagination if too many tasks
    if len(tasks_data) > 10:
        embed.add_field(name="Too many tasks to list!",
                        value="Showing the first 10 tasks. Use !tasks next or !tasks 2 to see more.", inline=False)

    # Adding footer and thumbnail
    embed.set_footer(text="Task List Updated")
    embed.set_thumbnail(url=bot.user.avatar.url)

    await ctx.send(embed=embed)


# Command to mark a task as completed
@bot.command()
async def complete_task(ctx, task_id: str):
    """Mark a task as completed."""

    # Try to convert task_id to integer
    try:
        task_id = int(task_id)
    except ValueError:
        embed_error = discord.Embed(
            title="❌ Invalid Task ID",
            description="Howdy Partner, we don't take kindly to strings around here! Try again with a valid integer.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if task exists and is not completed
    task = tasks_data.get(task_id)
    if not task:
        embed_not_found = discord.Embed(
            title="🚫 Task Not Found",
            description=f"Yeehaw! We couldn't find a task with ID {task_id}. Make sure the task ID is correct.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed_not_found)
        return

    if task["completed"]:
        embed_already_completed = discord.Embed(
            title="🚀 Task Already Completed",
            description=f"Looks like you've already completed **{task['task_name']}**. No need to do it again, partner!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed_already_completed)
        return

    # Mark task as completed and award XP
    task["completed"] = True
    user_id = ctx.author.id
    difficulty = task["difficulty"]
    xp = difficulty * 10  # XP based on difficulty level
    add_xp(user_id, xp)

    embed_success = discord.Embed(
        title="🌠 Task Completed!",
        description=f"Yeehaw, **{ctx.author.name}**! You've completed **{task['task_name']}** and earned {xp} XP! 🎉",
        color=discord.Color.green()
    )
    embed_success.set_thumbnail(url=ctx.author.avatar.url)  # Optional: Add user avatar as thumbnail
    await ctx.send(embed=embed_success)

@bot.command()
async def remove_task(ctx, task_id: str):
    """Remove a task."""

    # Check if task_id is a valid integer
    try:
        task_id = int(task_id)
    except ValueError:
        embed_error = discord.Embed(
            title="❌ Invalid Task ID",
            description="Howdy Partner, we don't take kindly to strings around here! Try again with a valid integer.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Check if the task_id exists in tasks_data
    if task_id not in tasks_data:
        embed_not_found = discord.Embed(
            title="🚫 Task Not Found",
            description=f"Task with ID {task_id} doesn't exist. Please check the task ID and try again.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed_not_found)
        return

    # Ask for confirmation before deleting the task
    embed_confirm = discord.Embed(
        title="🛑 Task Removal Confirmation",
        description=f"Are you sure you want to remove task **{tasks_data[task_id]['task_name']}** (ID: {task_id})? Type `yes` to confirm.",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed_confirm)

    def check(msg):
        return msg.author == ctx.author and msg.content.lower() in ["yes", "no"]

    try:
        # Wait for the user's response to confirm deletion
        user_msg = await bot.wait_for('message', check=check, timeout=30.0)

        if user_msg.content.lower() == "yes":
            # Check if the task still exists before removing
            if task_id in tasks_data:
                # Remove the task from tasks_data
                del tasks_data[task_id]
                embed_removed = discord.Embed(
                    title="✅ Task Removed",
                    description=f"Task **{tasks_data.get(task_id, {}).get('task_name', 'Unknown')}** (ID: {task_id}) has been successfully removed.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed_removed)
            else:
                embed_error = discord.Embed(
                    title="⚠️ Task Already Removed",
                    description=f"Task **{task_id}** was already removed or doesn't exist.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed_error)
        else:
            embed_cancelled = discord.Embed(
                title="🛑 Task Removal Cancelled",
                description="Task removal has been cancelled. No changes made.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed_cancelled)

    except asyncio.TimeoutError:
        # If no response after 30 seconds, cancel the task removal
        embed_timeout = discord.Embed(
            title="⏰ Task Removal Timed Out",
            description="You took too long to respond. Task removal has been cancelled.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_timeout)

@bot.command()
async def leaderboard(ctx):
    """Show the leaderboard of users with their XP."""
    leaderboard_data = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)

    # Creating an embed for the leaderboard
    embed = discord.Embed(title="Leaderboard", description="Top users based on XP", color=discord.Color.blue())

    # Add each user to the embed
    for i, (user_id, data) in enumerate(leaderboard_data[:10], start=1):  # Show top 10 users
        print(f"Checking user ID: {user_id}")  # Debug print to check the user_id

        try:
            # Fetch the member by their user ID from the guild
            member = await ctx.guild.fetch_member(user_id)
            member_name = f"{member.name} ({member.display_name})"  # Use display_name if available
        except discord.NotFound:
            # If the member is not found (e.g., they left the server), use the fallback
            print(f"Could not find member for user_id {user_id}")  # Debug print for missing member
            member_name = f"{ctx.author.name} (Unknown User)"
        except discord.Forbidden:
            # If the bot doesn't have permission to view the member, use the fallback
            member_name = f"{ctx.author.name} (Unknown User)"

        # Add the user and their XP to the embed
        embed.add_field(name=f"{i}. {member_name}", value=f"{data['xp']} XP", inline=False)

    # Adding footer and thumbnail
    embed.set_footer(text="Updated just now")
    embed.set_thumbnail(url=bot.user.avatar.url)

    # Send the embed
    await ctx.send(embed=embed)

# Testing
@bot.command()
async def test(ctx):
    """Test various aspects of the bot and server."""

    # Test if the bot is online and responsive
    bot_status = "Online" if bot.is_ready() else "Offline"

    # Test bot latency (ping)
    bot_ping = bot.latency * 1000  # Convert latency to ms

    # Test bot permissions in the current channel
    permissions = ctx.channel.permissions_for(ctx.guild.me)
    can_send = "Yes" if permissions.send_messages else "No"
    can_read = "Yes" if permissions.read_messages else "No"

    # Test server information
    server_name = ctx.guild.name
    member_count = ctx.guild.member_count
    total_channels = len(ctx.guild.channels)

    # Test if specific roles exist in the server
    role_name = "Admin"  # Example role
    role_exists = any(role.name == role_name for role in ctx.guild.roles)

    # Attempt to fetch the member by their user ID in the current guild
    try:
        member = await ctx.guild.fetch_member(ctx.author.id)
    except discord.NotFound:
        member = None  # If the member cannot be found, set member to None
    except discord.Forbidden:
        member = None  # If the bot doesn't have permission to fetch the member

    # Create an embed with all the gathered info
    embed = discord.Embed(title="Bot and Server Test Results", color=discord.Color.blue())

    # Display bot and server status
    embed.add_field(name="Bot Status", value=f"Bot is {bot_status}", inline=False)
    embed.add_field(name="Bot Latency", value=f"{bot_ping:.2f} ms", inline=True)
    embed.add_field(name="Can Send Messages", value=can_send, inline=True)
    embed.add_field(name="Can Read Messages", value=can_read, inline=True)
    embed.add_field(name="Server Name", value=server_name, inline=False)
    embed.add_field(name="Member Count", value=str(member_count), inline=True)
    embed.add_field(name="Total Channels", value=str(total_channels), inline=True)
    embed.add_field(name=f"Does '{role_name}' Role Exist?", value="Yes" if role_exists else "No", inline=True)

    # If the member is found, include details about the member
    if member:
        roles = ", ".join(
            [role.name for role in member.roles if role.name != "@everyone"])  # List roles (excluding @everyone)
        account_creation = member.created_at.strftime("%B %d, %Y")  # Format account creation date
        joined_date = member.joined_at.strftime("%B %d, %Y")  # Format date the member joined the server

        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="Roles", value=roles if roles else "No roles assigned", inline=True)
        embed.add_field(name="Account Created", value=account_creation, inline=True)
        embed.add_field(name="Joined Server", value=joined_date, inline=True)

    else:
        embed.add_field(name="Member Info", value=f"Could not find member with ID {ctx.author.id}.", inline=False)

    # Send the embed with test results
    await ctx.send(embed=embed)


import time
from datetime import timedelta

# Store bot's start time
bot_start_time = time.time()


# !ping command - Measures bot's latency and shows uptime
@bot.command()
async def ping(ctx):
    """Check the bot's latency and uptime."""
    # Calculate bot's latency (ping to the Discord API)
    latency = bot.latency * 1000  # Convert latency to milliseconds

    # Calculate bot's uptime
    uptime_seconds = time.time() - bot_start_time
    uptime = str(timedelta(seconds=int(uptime_seconds)))

    # Display results in a fun space-themed message
    embed = discord.Embed(
        title="🚀 CowBot Ping Report",
        description="Yeehaw! Checking the space signal... Let's see how we're cruisin' through the stars.",
        color=discord.Color.blue()
    )

    embed.add_field(name="Latency", value=f"{latency:.2f} ms", inline=False)
    embed.add_field(name="Uptime", value=uptime, inline=False)

    # Optionally: Add some space-themed emojis for flair
    embed.set_footer(text="CowBot’s cosmic network is always ready to serve, partner! 🌌🚀")

    # Send the message
    await ctx.send(embed=embed)


# !info command - Shows basic information about the bot
@bot.command()
async def info(ctx):
    """Show information about the bot."""
    embed = discord.Embed(
        title="CowBot Information",
        description="Yeehaw, partner! Here’s a bit about me.",
        color=discord.Color.green()
    )
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Server Count", value=len(bot.guilds), inline=True)
    embed.add_field(name="Developer", value="Your Space Cowboy 🐄", inline=True)
    embed.set_footer(text="CowBot is here to help you study and earn XP, space cadet!")
    await ctx.send(embed=embed)



@bot.command()
async def help(ctx):
    """Displays a space cowboy-themed help message for the bot."""

    embed = discord.Embed(
        title="🌌🤠 CowBot's Galactic Guide",
        description="Yeehaw, partner! Welcome aboard my space ranch. Here's your map of commands to rope up some XP and get things done!",
        color=discord.Color.purple()
    )

    # Adding fields for each command section with space cowboy flavor
    embed.add_field(
        name="📚 Space Study Commanders",
        value="`!study` - Strap in, space cadet! Start studying and rack up them XP points.\n`!leaderboard` - Check out who’s leading the space rodeo with the most XP!\n`!test` - Test the bot’s systems and see if we're ready to blast off.",
        inline=False
    )

    embed.add_field(
        name="🛠 Task Wranglers",
        value="`!create_task <name> <difficulty>` - Set your sights on a new task, and let’s get to work!\n`!list_tasks` - See all the tasks we’ve wrangled up in the galaxy.\n`!complete_task <task_id>` - Complete a task and earn your rightful XP!\n`!remove_task <task_id>` - If a task is no good, we can send it to the asteroid belt.",
        inline=False
    )

    embed.add_field(
        name="⚙️ CowBot Control Room",
        value="`!help` - Get this here guide again, partner! Need a refresher?\n`!ping` - Check how fast we’re cruisin' through space with our connection.\n`!info` - Get the scoop on this here bot and the galaxy we're in.",
        inline=False
    )

    # Adding footer for the embed
    embed.set_footer(text="CowBot is your trusty space cowboy, ready to guide you through the stars! 🌠🚀")

    # Sending the help embed
    await ctx.send(embed=embed)


# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)