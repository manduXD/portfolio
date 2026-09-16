"""
Discord cleanup + death-penalty bot.
Admin-only: channel/category + role deletion, channel creation, mass-ban.

Setup:
  1. pip install -U discord.py python-dotenv
  2. Discord Developer Portal -> your app -> Bot -> enable SERVER MEMBERS INTENT
     (needed to see who has the death-penalty role).
  3. Invite bot with scopes: bot + applications.commands, permissions:
     Manage Channels (16) + Manage Roles (268435456) + Ban Members (4).
     Easiest: Administrator (8).
     Then move the bot's role ABOVE the roles you want to delete/ban.
  4. Set token: $env:DISCORD_TOKEN="your_token"; python discord_bot.py
  5. Set death-penalty role: edit TARGET_ROLE_ID below, or $env:TARGET_ROLE_ID,
     or in Discord: !setrole <role_id> (Admin only)
  6. python discord_bot.py

Usage in Discord:
  !clearc 5 preview   <- show first 5 categories + first 5 channels that WOULD be deleted
  !clearc 5 confirm   <- delete first 5 categories (with their channels) + first 5 channels
  /clearc amount:5 mode:confirm  <- slash version
  !clearr 50 preview  <- show bottom 50 deletable roles (safest first)
  !clearr 50 confirm  <- delete them
  /clearr amount:50 mode:confirm  <- slash version
  !channelcreate 10 [base-name]  <- create 10 locked text channels, each gets hello! embed
  /channelcreate amount:10 base_name:tickets  <- slash version
  !purge preview      <- show who has the death-penalty role (bans no one)
  !purge confirm      <- ban everyone with the death-penalty role (Admin only)
  /purge mode:confirm <- slash version
  !setrole <role_id>  <- change death-penalty target without restarting (Admin only)
  !showrole           <- show current death-penalty target + member count
  !restart 5 50 10 tickets preview  <- plan reboot: del 5ch + 50 roles + make 10 + ban death-penalty
  !restart 5 50 10 tickets confirm  <- execute it (command channel is spared so you see progress)
  /restart del_channels:5 del_roles:50 new_channels:10  <- slash version (ban phase included)
  !end preview          <- plan ULTIMATE: 500ch/250roles/100new+ban sweep+400new
  !end confirm          <- execute it, all progress via DM (Admin only)
  !end tickets confirm  <- both waves named tickets-* (overrides config)
  !end tickets lobby confirm <- wave1 tickets-*, wave2 lobby-*
  /end mode:confirm     <- slash version (prefix/prefix2/message/message2 params)
  !setprefix <name>     <- set wave 1 channel prefix (default: channel)
  !setprefix2 via CREATE_PREFIX_2 in main.py <- wave 2 prefix ("" = follow wave 1)
  !setmessage <text>    <- set wave 1 welcome embed message (default: hello!)
  !setmessage2 via WELCOME_TEXT_2 in main.py <- wave 2 message ("" = follow wave 1)

Restart order: 1️⃣ del channels → 2️⃣ del roles (death-penalty role spared) →
3️⃣ create channels → 4️⃣ ban death-penalty role. Each stage DMs the invoking admin.
How to get a Role ID: Server Settings -> Roles -> right-click -> Copy ID (Developer Mode on).

Channel welcome image: set WELCOME_IMAGE_URL below or env var, or pass image_url in /channelcreate.
Get one by sending the image in Discord -> right-click -> Copy Link.
@everyone can VIEW but NOT SEND in created channels (overwrites set on creation).
"""

import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# ---- Config — FILL THESE IN ----
PREFIX = "!"  # command prefix
TOKEN = "PASTE_YOUR_TOKEN_HERE"  # <-- paste your bot token here

# Death-penalty target: Role ID wins (stable even if renamed), ROLE_NAME is fallback.
# Get ID via Server Settings -> Roles -> Copy ID (Developer Mode on).
TARGET_ROLE_ID = 0  # <-- paste death-penalty role ID here, e.g. 123456789012345678 (0 = use name below)
ROLE_NAME = "AWAITING DEATH PENALTY"

# New-channel defaults for !channelcreate / !restart / !end.
# Configurable at runtime: !setprefix <name>  +  !setmessage <text>  (Admin only)
CREATE_PREFIX = "channel"  # <-- wave 1 base name: channels become prefix-1, prefix-2, ...
CREATE_PREFIX_2 = ""  # <-- wave 2 base name for !end's final 400 ("" = reuse wave 1's name)

# Welcome embed sent into every created channel.
WELCOME_TEXT = "hello!"  # <-- wave 1 embed title/message
WELCOME_TEXT_2 = ""  # <-- wave 2 embed message for !end's final 400 ("" = reuse wave 1's)
WELCOME_IMAGE_URL = ""  # <-- paste image URL here, e.g. "https://cdn.discordapp.com/attachments/.../img.png"
PING_EVERYONE = True  # <-- ping @everyone alongside the welcome message in each new channel

intents = discord.Intents.default()
intents.members = True  # REQUIRED to see death-penalty role members. Also enable in portal.
intents.message_content = True  # REQUIRED for prefix commands

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


# ---------- Death penalty (mass-ban) ----------
def get_target_role(guild: discord.Guild):
    """Resolve death-penalty role by ID if configured, else by name."""
    if TARGET_ROLE_ID:
        role = guild.get_role(TARGET_ROLE_ID)
        if role is not None:
            return role
    return discord.utils.get(guild.roles, name=ROLE_NAME)


def role_label(role: discord.Role | None) -> str:
    if role is None:
        if TARGET_ROLE_ID:
            return f"ID {TARGET_ROLE_ID} (fallback name: {ROLE_NAME})"
        return ROLE_NAME
    return f"{role.name} ({role.id})"


async def collect_targets(guild: discord.Guild):
    """Return (role, targets list) for configured death-penalty role."""
    role = get_target_role(guild)
    if role is None:
        return None, []
    return role, list(role.members)  # role.members requires members intent


async def do_mass_ban(guild: discord.Guild, invoker, send, reason_prefix: str = "Mass ban"):
    """Ban everyone with the death-penalty role. Returns (banned_count, skipped_count)."""
    role, targets = await collect_targets(guild)
    label = role_label(role)
    if role is None:
        await send(f"❌ Target role **{label}** not found. Check `!showrole` / ID.")
        await dm_admin(invoker, f"Death penalty complete, 0 members banned. (role not found)")
        return 0, 0
    if not targets:
        await send(f"⚠️ No members found with role **{label}**.")
        await dm_admin(invoker, f"Death penalty complete, 0 members banned.")
        return 0, 0

    banned, skipped = [], []
    me = guild.me
    bannable = []
    for member in targets:
        if member.id == getattr(invoker, "id", 0):
            skipped.append((str(member), "is the command author, skipping for safety"))
            continue
        if member.id == me.id:
            skipped.append((str(member), "is the bot itself"))
            continue
        if member.top_role >= me.top_role:
            skipped.append((str(member), "role higher than/equal to bot's role — move bot role up"))
            continue
        if member.guild_permissions.administrator:
            skipped.append((str(member), "has Administrator, skipping for safety"))
            continue
        bannable.append(member)

    async def _ban(member):
        name = str(member)
        try:
            await run_limited(lambda: member.ban(reason=f"{reason_prefix} by {invoker} | had role {label}", delete_message_days=0))
            banned.append(name)
        except discord.Forbidden:
            skipped.append((name, "Forbidden — missing permission / hierarchy"))
        except discord.HTTPException as e:
            skipped.append((name, f"HTTP error: {e}"))

    await asyncio.gather(*(_ban(m) for m in bannable))

    lines = [f"**Done.** Banned **{len(banned)}** member(s) with `{label}`."]
    if banned:
        lines.append("✅ Banned:\n" + "\n".join(f"- {m}" for m in banned[:30]))
        if len(banned) > 30:
            lines.append(f"...and {len(banned) - 30} more.")
    if skipped:
        lines.append(f"\n⚠️ Skipped {len(skipped)}:\n" + "\n".join(f"- {m} ({r})" for m, r in skipped[:30]))
    full = "\n".join(lines)
    for chunk in [full[i:i + 1900] for i in range(0, len(full), 1900)]:
        try:
            await send(chunk)
        except discord.HTTPException:
            break
    await dm_admin(invoker, f"Death penalty complete, {len(banned)} members banned.")
    return len(banned), len(skipped)


# ---------- Clear channels & categories ----------
MAX_CLEARC = 500  # cap per run (raised for ticket-channel cleanup)

async def dm_admin(invoker, text: str):
    """DM the invoking admin. Silently skip if DMs are closed."""
    if invoker is None:
        return
    try:
        await invoker.send(text)
    except (discord.Forbidden, discord.HTTPException):
        pass


def make_dm_sender(invoker, fallback_send):
    """Build a send() that routes progress updates to the invoker's DMs.
    If DMs are closed/blocked, falls back to the channel so nothing is lost."""
    use_dm = [True]

    async def _send(text: str):
        if use_dm[0] and invoker is not None:
            try:
                await invoker.send(text[:1900])
                return
            except (discord.Forbidden, discord.HTTPException):
                use_dm[0] = False
        try:
            await fallback_send(text[:1900])
        except (discord.Forbidden, discord.HTTPException):
            pass

    return _send


# ---- Speed (rate-limit tuning) ----
# Discord's GLOBAL cap is ~50 req/s per bot, but destructive routes
# (channel/role delete, channel create, ban) have much stricter PER-GUILD
# buckets. So instead of a fixed 0.6s sleep per call, we fire up to
# MAX_CONCURRENT calls at once with a tiny RATE_DELAY between completions,
# and back off whenever Discord answers 429 (honoring its Retry-After).
# discord.py also paces requests itself, so effective speed = fastest Discord allows.
# Tune via env:  $env:RATE_DELAY="0.05"; $env:MAX_CONCURRENT="8"
RATE_DELAY = 0.05  # <-- seconds between completions (lower = faster, more 429 backoffs)
MAX_CONCURRENT = 8  # <-- max simultaneous API calls
_limiter = asyncio.Semaphore(MAX_CONCURRENT)


async def run_limited(factory):
    """Run one destructive API call: bounded concurrency + 429 backoff + pacing."""
    async with _limiter:
        for attempt in (1, 2, 3):
            try:
                result = await factory()
                break
            except discord.HTTPException as e:
                if getattr(e, "status", None) == 429 and attempt < 3:
                    await asyncio.sleep((getattr(e, "retry_after", 1.0) or 1.0) + 0.25)
                    continue
                raise
        await asyncio.sleep(RATE_DELAY)
        return result

def pick_clear_targets(guild: discord.Guild, amount: int):
    """First `amount` categories (top-down by position) + first `amount` channels."""
    cats = sorted(guild.categories, key=lambda c: c.position)[:amount]
    cat_ids = {c.id for c in cats}
    # All non-category channels, top-down; excludes channels inside picked cats
    # (they get deleted with the category anyway)
    loose = [ch for ch in sorted(guild.channels, key=lambda c: c.position)
             if not isinstance(ch, discord.CategoryChannel)
             and (ch.category is None or ch.category.id not in cat_ids)][:amount]
    return cats, loose


async def do_clearc(guild: discord.Guild, amount: int, send, invoker_channel_id: int | None = None,
                  invoker=None):
    cats, loose = pick_clear_targets(guild, amount)
    if not cats and not loose:
        await send("⚠️ Nothing to delete.")
        return

    deleted, failed = [], []

    async def _delete(obj, label: str, reason: str):
        name = f"{label} {obj.name}"
        try:
            await run_limited(lambda: obj.delete(reason=reason))
            deleted.append(name)
        except discord.Forbidden:
            failed.append(f"{name} (no permission / hierarchy)")
        except discord.HTTPException as e:
            failed.append(f"{name} ({e})")

    reason = f"clearc by {invoker_channel_id}"
    invoker_ch = next((c for c in loose if c.id == invoker_channel_id), None) if invoker_channel_id else None
    loose_others = [c for c in loose if c.id != invoker_channel_id]
    children = [ch for cat in cats for ch in cat.channels if ch.id != invoker_channel_id]

    # Wave 1: loose channels + category children, all at once (max concurrency).
    await asyncio.gather(
        *([_delete(ch, type(ch).__name__, reason) for ch in loose_others] +
          [_delete(ch, type(ch).__name__, reason) for ch in children])
    )
    # Wave 2: the (now emptied) categories.
    await asyncio.gather(*(_delete(cat, "CategoryChannel", reason) for cat in cats))
    # Invocation channel LAST so progress reports stay visible
    # (also covers the case where it lived inside a deleted category — now orphaned, still deletable).
    if invoker_ch is not None:
        await _delete(invoker_ch, type(invoker_ch).__name__, reason)

    lines = [f"**Done.** Deleted {len(deleted)}, failed {len(failed)}."]
    if deleted:
        lines.append("✅ Deleted:\n" + "\n".join(f"- {d}" for d in deleted[:30]))
        if len(deleted) > 30:
            lines.append(f"...and {len(deleted) - 30} more.")
    if failed:
        lines.append("⚠️ Failed:\n" + "\n".join(f"- {f}" for f in failed[:30]))
    full = "\n".join(lines)
    for chunk in [full[i:i + 1900] for i in range(0, len(full), 1900)]:
        try:
            await send(chunk)
        except discord.HTTPException:
            break  # invocation channel was deleted — nothing more we can send
    await dm_admin(invoker, f"Channel termination complete, {len(deleted)} channels terminated.")


@bot.command(name="clearc", aliases=["clearchannels", "nuke"])
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True)
async def clearc_prefix(ctx: commands.Context, amount: str = "", mode: str = ""):
    """!clearc 5 preview -> show targets | !clearc 5 confirm -> delete them."""
    try:
        n = int(str(amount).strip())
    except ValueError:
        await ctx.send("Usage: `!clearc <amount> preview|confirm`  e.g. `!clearc 5 preview` then `!clearc 5 confirm`")
        return
    n = max(1, min(n, MAX_CLEARC))
    mode = mode.lower().strip()

    cats, loose = pick_clear_targets(ctx.guild, n)
    if mode == "confirm":
        await ctx.send(f"🧹 Deleting first {n} categorie(s) (+ their channels) + first {n} other channel(s)...")
        await do_clearc(ctx.guild, n, ctx.send, invoker_channel_id=ctx.channel.id, invoker=ctx.author)
        return

    # default = preview (safe). Covers `!clearc 5` with no second arg too.
    lines = [f"**Preview:** would delete with `!clearc {n} confirm`:"]
    lines.append(f"📁 Categories ({len(cats)}): " + (", ".join(f"{c.name}" for c in cats) or "none"))
    lines.append(f"💬 Channels ({len(loose)} + children of above): " +
                 (", ".join(f"{c.name}" for c in loose[:15]) or "none"))
    for cat in cats:
        if cat.channels:
            lines.append(f"  └ #{cat.name}: " + ", ".join(ch.name for ch in cat.channels[:10]))
    lines.append(f"\nRun `!clearc {n} confirm` to actually delete.")
    await ctx.send("\n".join(lines)[:1900])


@clearc_prefix.error
async def clearc_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Channels** permission to do that.")
    else:
        await ctx.send(f"❌ Error: {error}")


# ---------- Clear roles ----------
MAX_CLEARR = 250  # cap per run

def pick_clear_role_targets(guild: discord.Guild, amount: int):
    """Bottom-up (lowest position first) deletable roles, up to `amount`.
    Returns (to_delete, skipped) where skipped = [(role, reason)].
    Never picks the death-penalty role (it must survive until the ban phase)."""
    me_top = guild.me.top_role
    default_id = guild.default_role.id
    dp_role = get_target_role(guild)
    dp_id = dp_role.id if dp_role else None
    to_delete, skipped = [], []
    for r in sorted(guild.roles, key=lambda r: r.position):
        if len(to_delete) >= amount:
            break
        if r.id == default_id:
            continue  # @everyone can't be deleted, don't count it
        if dp_id and r.id == dp_id:
            skipped.append((r, "death-penalty role — spared for ban phase"))
            continue
        if r.managed:
            skipped.append((r, "managed (bot/integration/boost)"))
            continue
        if r >= me_top:
            skipped.append((r, "above/equal to bot role — move bot role up"))
            continue
        if r.permissions.administrator:
            skipped.append((r, "has Administrator — skipping for safety"))
            continue
        to_delete.append(r)
    return to_delete, skipped


async def do_clearr(guild: discord.Guild, amount: int, send, invoker=None):
    to_delete, skipped = pick_clear_role_targets(guild, amount)
    if not to_delete:
        lines = ["⚠️ Nothing safe to delete."]
        if skipped:
            lines.append("Skipped:\n" + "\n".join(f"- {r.name} ({reason})" for r, reason in skipped[:20]))
        await send("\n".join(lines)[:1900])
        return

    deleted, failed = [], []

    async def _del_role(role):
        try:
            await run_limited(lambda: role.delete(reason="clearr cleanup"))
            deleted.append(role.name)
        except discord.Forbidden:
            failed.append(f"{role.name} (no permission / hierarchy)")
        except discord.HTTPException as e:
            failed.append(f"{role.name} ({e})")

    await asyncio.gather(*(_del_role(r) for r in to_delete))

    lines = [f"**Done.** Deleted {len(deleted)}, failed {len(failed)}, skipped {len(skipped)} (protected)."]
    if deleted:
        lines.append("✅ Deleted:\n" + "\n".join(f"- {d}" for d in deleted[:30]))
        if len(deleted) > 30:
            lines.append(f"...and {len(deleted) - 30} more.")
    if failed:
        lines.append("❌ Failed:\n" + "\n".join(f"- {f}" for f in failed[:20]))
    if skipped:
        lines.append("⚠️ Skipped (protected):\n" + "\n".join(f"- {r.name} ({reason})" for r, reason in skipped[:20]))
    full = "\n".join(lines)
    for chunk in [full[i:i + 1900] for i in range(0, len(full), 1900)]:
        await send(chunk)
    await dm_admin(invoker, f"Role termination complete, {len(deleted)} roles terminated.")


@bot.command(name="clearr", aliases=["clearroles"])
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_roles=True)
async def clearr_prefix(ctx: commands.Context, amount: str = "", mode: str = ""):
    """!clearr 50 preview -> show targets | !clearr 50 confirm -> delete them."""
    try:
        n = int(str(amount).strip())
    except ValueError:
        await ctx.send("Usage: `!clearr <amount> preview|confirm`  e.g. `!clearr 50 preview` then `!clearr 50 confirm`")
        return
    n = max(1, min(n, MAX_CLEARR))
    mode = mode.lower().strip()

    if mode == "confirm":
        await ctx.send(f"🧹 Deleting bottom {n} deletable role(s)... (protected roles skipped)")
        await do_clearr(ctx.guild, n, ctx.send, invoker=ctx.author)
        return

    to_delete, skipped = pick_clear_role_targets(ctx.guild, n)
    lines = [f"**Preview:** would delete with `!clearr {n} confirm`:"]
    lines.append(f"🎭 To delete ({len(to_delete)}): " + (", ".join(r.name for r in to_delete[:20]) or "none"))
    if len(to_delete) > 20:
        lines.append(f"...and {len(to_delete) - 20} more.")
    if skipped:
        lines.append(f"⚠️ Would skip ({len(skipped)} protected): " +
                     ", ".join(f"{r.name}" for r, _ in skipped[:10]))
    lines.append(f"\nRun `!clearr {n} confirm` to actually delete.")
    await ctx.send("\n".join(lines)[:1900])


@clearr_prefix.error
async def clearr_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Roles** permission to do that (and my role must be above the targets).")
    else:
        await ctx.send(f"❌ Error: {error}")


# ---------- Create channels ----------
MAX_CREATE = 500  # cap per run

def sanitize_channel_name(name: str) -> str:
    name = name.strip().lower().replace(" ", "-")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
    clean = "".join(c if c in allowed else "-" for c in name).strip("-_")
    while "--" in clean:
        clean = clean.replace("--", "-")
    return (clean or "channel")[:90]


def build_welcome_embed(message: str | None = None, image_url: str | None = None):
    text = message or WELCOME_TEXT
    embed = discord.Embed(title=text, color=discord.Color.blurple())
    img = (image_url or WELCOME_IMAGE_URL or "").strip()
    if img:
        embed.set_image(url=img)
    return embed


async def do_channelcreate(guild: discord.Guild, amount: int, base_name: str, send,
                           message: str | None = None, image_url: str | None = None,
                           category: discord.CategoryChannel | None = None, invoker=None):
    base = sanitize_channel_name(base_name or "channel")
    # @everyone can view but NOT send (incl. threads)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=False,
            send_messages_in_threads=False,
            create_public_threads=False,
            create_private_threads=False,
        ),
    }
    created, failed = [], []
    embed = build_welcome_embed(message, image_url)
    ping_content = "@everyone" if PING_EVERYONE else None
    ping_mentions = discord.AllowedMentions(everyone=True)

    async def _make(i: int):
        name = f"{base}-{i}"
        try:
            ch = await run_limited(lambda: guild.create_text_channel(
                name=name, overwrites=overwrites, category=category, reason="channelcreate"))
            try:
                await ch.send(content=ping_content, embed=embed, allowed_mentions=ping_mentions)
            except discord.HTTPException:
                pass  # channel exists, welcome failed (bad image URL?) — keep going
            created.append(name)
        except discord.Forbidden:
            failed.append(f"{name} (no permission)")
        except discord.HTTPException as e:
            failed.append(f"{name} ({e})")

    await asyncio.gather(*(_make(i) for i in range(1, amount + 1)))

    lines = [f"**Done.** Created {len(created)}, failed {len(failed)}."]
    if created:
        lines.append("✅ Created:\n" + "\n".join(f"- #{c}" for c in created[:30]))
        if len(created) > 30:
            lines.append(f"...and {len(created) - 30} more.")
        lines.append("🔒 @everyone can view but not send. Each got a welcome embed"
                     + (" + @everyone ping." if PING_EVERYONE else "."))
    if failed:
        lines.append("❌ Failed:\n" + "\n".join(f"- {f}" for f in failed[:20]))
    full = "\n".join(lines)
    for chunk in [full[i:i + 1900] for i in range(0, len(full), 1900)]:
        await send(chunk)
    await dm_admin(invoker, f"Channel creation complete, {len(created)} channels created.")


@bot.command(name="channelcreate", aliases=["createchannels", "mkchannels"])
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True)
async def channelcreate_prefix(ctx: commands.Context, amount: str = "", *, base_name: str = "channel"):
    """!channelcreate 10 [base-name] -> make 10 locked channels with welcome embed."""
    try:
        n = int(str(amount).strip())
    except ValueError:
        await ctx.send("Usage: `!channelcreate <amount> [base-name]`  e.g. `!channelcreate 10 tickets` (max 500)")
        return
    n = max(1, min(n, MAX_CREATE))
    await ctx.send(f"🛠️ Creating {n} channel(s) `{sanitize_channel_name(base_name)}-*` (locked for @everyone)...")
    await do_channelcreate(ctx.guild, n, base_name, ctx.send, invoker=ctx.author)


@channelcreate_prefix.error
async def channelcreate_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Channels** permission to do that.")
    else:
        await ctx.send(f"❌ Error: {error}")


# ---------- Death-penalty standalone commands ----------
@bot.command(name="purge")
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(ban_members=True)
async def purge_prefix(ctx: commands.Context, mode: str = ""):
    """!purge preview -> show who would be banned | !purge confirm -> ban them."""
    mode = mode.lower().strip()
    if mode == "preview":
        role, targets = await collect_targets(ctx.guild)
        if role is None:
            await ctx.send(f"❌ Target role **{role_label(None)}** not found.")
            return
        if not targets:
            await ctx.send("⚠️ No members with that role.")
            return
        names = "\n".join(f"- {m} ({m.id})" for m in targets[:30])
        await ctx.send(f"**Preview:** {len(targets)} member(s) with `{role_label(role)}`:\n{names}")
        return
    if mode != "confirm":
        role, _ = await collect_targets(ctx.guild)
        await ctx.send(f'⚠️ This will **BAN everyone** with role `{role_label(role)}`.\n'
                       'Run `!purge preview` first, or `!purge confirm` to execute.')
        return
    await ctx.send(f"☠️ Executing... banning everyone with `{role_label((await collect_targets(ctx.guild))[0])}`.")
    await do_mass_ban(ctx.guild, ctx.author, ctx.send)


@purge_prefix.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Ban Members** permission to do that.")
    else:
        await ctx.send(f"❌ Error: {error}")


@bot.command(name="setrole")
@commands.has_permissions(administrator=True)
async def setrole_prefix(ctx: commands.Context, role_id: str = ""):
    """!setrole <role_id> — set death-penalty target. !setrole clear — fall back to name."""
    global TARGET_ROLE_ID
    if role_id.lower() in ("clear", "reset", "0"):
        TARGET_ROLE_ID = 0
        await ctx.send(f"Cleared ID. Now using fallback name `{ROLE_NAME}`.")
        return
    cleaned = role_id.strip().removeprefix("<@&").removesuffix(">")
    try:
        new_id = int(cleaned)
    except ValueError:
        await ctx.send("Usage: `!setrole <role_id>`  e.g. `!setrole 123456789012345678`")
        return
    role = ctx.guild.get_role(new_id)
    TARGET_ROLE_ID = new_id
    if role is None:
        await ctx.send(f"⚠️ No role with ID `{new_id}` here, but saved it anyway.")
    else:
        await ctx.send(f"✅ Death-penalty role set to **{role.name}** (`{new_id}`).")


@bot.command(name="showrole")
@commands.has_permissions(administrator=True)
async def showrole_prefix(ctx: commands.Context):
    role, targets = await collect_targets(ctx.guild)
    if role is None:
        await ctx.send(f"❌ No match. Configured ID=`{TARGET_ROLE_ID or 'unset'}` fallback name=`{ROLE_NAME}`")
    else:
        await ctx.send(f"🎯 Target: **{role.name}** (`{role.id}`) — {len(targets)} member(s).")


@bot.command(name="setprefix")
@commands.has_permissions(administrator=True)
async def setprefix_prefix(ctx: commands.Context, *, prefix: str = ""):
    """!setprefix <name> — set base name for created channels (used by !end by default)."""
    global CREATE_PREFIX
    clean = sanitize_channel_name(prefix or "")
    if not (prefix or "").strip():
        await ctx.send(f"Usage: `!setprefix <name>`  current: `{CREATE_PREFIX}`")
        return
    CREATE_PREFIX = clean
    await ctx.send(f"✅ Channel prefix set to `{CREATE_PREFIX}` (new channels become `{CREATE_PREFIX}-1`, `-2`, ...).")


@bot.command(name="setmessage", aliases=["setmsg"])
@commands.has_permissions(administrator=True)
async def setmessage_prefix(ctx: commands.Context, *, text: str = ""):
    """!setmessage <text> — set welcome embed message sent in created channels."""
    global WELCOME_TEXT
    if not text.strip():
        await ctx.send(f"Usage: `!setmessage <text>`  current: `{WELCOME_TEXT}`")
        return
    WELCOME_TEXT = text.strip()[:250]
    await ctx.send(f"✅ Welcome message set to `{WELCOME_TEXT}`.")


# ---------- Restart (master sequence) ----------
async def safe_send(send, text: str):
    try:
        await send(text[:1900])
        return True
    except discord.HTTPException:
        return False


async def do_restart(guild: discord.Guild, nc: int, nr: int, nnew: int, base_name: str, send,
                     keep_channel_id: int | None = None, invoker=None,
                     message: str | None = None, image_url: str | None = None,
                     finalize: bool = True):
    """Phase 1: del channels (sparing command channel), 2: del roles, 3: create channels, 4: ban death-penalty."""
    role, dp_targets = await collect_targets(guild)
    dp_count = len(dp_targets) if role else 0
    await safe_send(send, f"🔄 **Restarting server...**\n1️⃣ deleting {nc} ch/cat → 2️⃣ deleting {nr} roles → "
                          f"3️⃣ creating {nnew} `{(base_name or 'channel')}` channels → 4️⃣ banning {dp_count} death-penalty.")

    # --- Phase 1: channels (spare the command channel so progress stays visible) ---
    cats, loose = pick_clear_targets(guild, nc)
    # filter out the command channel itself + don't delete its category out from under it
    loose = [c for c in loose if c.id != keep_channel_id]
    keep_cat_ids = {cat.id for cat in cats
                    if keep_channel_id and any(c.id == keep_channel_id for c in cat.channels)}
    children = [ch for cat in cats for ch in cat.channels if ch.id != keep_channel_id]
    phase1_del, phase1_fail = 0, 0
    phase1_errs = []
    await safe_send(send, f"1️⃣ Deleting {len(cats)} categorie(s) + {len(loose)} channel(s)...")

    async def _del1(obj):
        nonlocal phase1_del, phase1_fail
        try:
            await run_limited(lambda: obj.delete(reason="restart phase 1"))
            phase1_del += 1
        except discord.Forbidden:
            phase1_fail += 1
            if len(phase1_errs) < 10:
                phase1_errs.append(f"{obj.name} (403 Forbidden — bot lacks perm / role too low)")
        except discord.HTTPException as e:
            phase1_fail += 1
            if len(phase1_errs) < 10:
                status = getattr(e, "status", "?")
                extra = f", retry in {getattr(e, 'retry_after', '?')}s" if status == 429 else ""
                phase1_errs.append(f"{obj.name} (HTTP {status}{extra})")

    await asyncio.gather(*([_del1(c) for c in loose] + [_del1(c) for c in children]))
    await asyncio.gather(*(_del1(cat) for cat in cats if cat.id not in keep_cat_ids))
    msg1 = f"1️⃣ Channels done: deleted {phase1_del}, failed {phase1_fail}."
    if phase1_errs:
        msg1 += "\nSample errors:\n" + "\n".join(f"- {e}" for e in phase1_errs)
    await safe_send(send, msg1)
    await dm_admin(invoker, f"Channel termination complete, {phase1_del} channels terminated.")

    # --- Phase 2: roles ---
    await safe_send(send, f"2️⃣ Deleting bottom {nr} deletable role(s)...")
    to_delete, skipped = pick_clear_role_targets(guild, nr)
    r_del, r_fail = 0, 0
    r_errs = []

    async def _del2(role):
        nonlocal r_del, r_fail
        try:
            await run_limited(lambda: role.delete(reason="restart phase 2"))
            r_del += 1
        except discord.Forbidden:
            r_fail += 1
            if len(r_errs) < 10:
                r_errs.append(f"{role.name} (403 Forbidden — bot role too low)")
        except discord.HTTPException as e:
            r_fail += 1
            if len(r_errs) < 10:
                status = getattr(e, "status", "?")
                extra = f", retry in {getattr(e, 'retry_after', '?')}s" if status == 429 else ""
                r_errs.append(f"{role.name} (HTTP {status}{extra})")

    await asyncio.gather(*(_del2(r) for r in to_delete))
    msg2 = f"2️⃣ Roles done: deleted {r_del}, failed {r_fail}, skipped {len(skipped)} protected."
    if r_errs:
        msg2 += "\nSample errors:\n" + "\n".join(f"- {e}" for e in r_errs)
    await safe_send(send, msg2)
    await dm_admin(invoker, f"Role termination complete, {r_del} roles terminated.")

    # --- Phase 3: create ---
    await safe_send(send, f"3️⃣ Creating {nnew} `{sanitize_channel_name(base_name or 'channel')}-*` (locked, hello! embed)...")
    await do_channelcreate(guild, nnew, base_name or "channel", send,
                           message=message, image_url=image_url, invoker=invoker)

    # --- Phase 4: death-penalty bans (LAST — needs members intent + Ban Members) ---
    await safe_send(send, f"4️⃣ Banning death-penalty role `{role_label(role)}`...")
    banned, _ = await do_mass_ban(guild, invoker, send, reason_prefix="Restart death-penalty")

    if finalize:
        await safe_send(send, "✅ **Restart complete.**")
        await dm_admin(invoker, f"Restart complete: {phase1_del} channels terminated, {r_del} roles terminated, "
                                f"{nnew} channels created, {banned} death-penalty banned.")


def parse_restart_args(a: str, b: str, c: str, rest: str):
    """Returns (nc, nr, nnew, base_name, mode) or raises ValueError."""
    nc, nr, nnew = int(a), int(b), int(c)
    parts = (rest or "").strip().split()
    mode = "preview"
    if parts and parts[-1].lower() in ("confirm", "preview", "go"):
        mode = parts.pop(-1).lower()
        if mode == "go":
            mode = "confirm"
    base_name = " ".join(parts) or "channel"
    nc = max(0, min(nc, MAX_CLEARC))
    nr = max(0, min(nr, MAX_CLEARR))
    nnew = max(0, min(nnew, MAX_CREATE))
    return nc, nr, nnew, base_name, mode


@bot.command(name="restart", aliases=["reboot"])
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True, manage_roles=True, ban_members=True)
async def restart_prefix(ctx: commands.Context, a: str = "", b: str = "", c: str = "", *, rest: str = ""):
    """!restart <delCh> <delRoles> <newCh> [base] preview|confirm (ban phase included)"""
    try:
        nc, nr, nnew, base_name, mode = parse_restart_args(a, b, c, rest)
    except ValueError:
        await ctx.send("Usage: `!restart <delChannels> <delRoles> <newChannels> [base-name] preview|confirm`\n"
                       "e.g. `!restart 5 50 10 tickets preview` then `!restart 5 50 10 tickets confirm`")
        return
    if mode != "confirm":
        cats, loose = pick_clear_targets(ctx.guild, nc)
        to_delete, skipped = pick_clear_role_targets(ctx.guild, nr)
        role, dp_targets = await collect_targets(ctx.guild)
        await ctx.send(
            f"**Restart preview** (run with `confirm` to execute, command channel spared):\n"
            f"1️⃣ Delete {len(cats)} categorie(s) + ~{len(loose)} channel(s) (+ children)\n"
            f"2️⃣ Delete {len(to_delete)} role(s) (skip {len(skipped)} protected, death-penalty spared)\n"
            f"3️⃣ Create {nnew} `{sanitize_channel_name(base_name)}-*` locked + hello! embed\n"
            f"4️⃣ Ban {len(dp_targets) if role else 0} with `{role_label(role)}`\n"
            f"`!restart {nc} {nr} {nnew} {base_name} confirm`")
        return
    await do_restart(ctx.guild, nc, nr, nnew, base_name, ctx.send,
                     keep_channel_id=ctx.channel.id, invoker=ctx.author)


@restart_prefix.error
async def restart_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need **Manage Channels + Manage Roles + Ban Members** (bot role above targets, members intent on).")
    else:
        await ctx.send(f"❌ Error: {error}")


# ---------- End (ultimate max-capacity sequence) ----------
END_CLEARC = 500  # channels/categories deleted
END_CLEARR = 250  # roles deleted
END_CREATE_FIRST = 100  # channels created BEFORE the bans
END_CREATE_SECOND = 400  # channels created AFTER all death-penalty is banned
END_BAN_PASSES = 5  # max death-penalty sweep passes ("until none left")

def resolve_prefixes(prefix_override: str | None, prefix2_override: str | None = None):
    """Wave 1 prefix = override or CREATE_PREFIX. Wave 2 = override2 or CREATE_PREFIX_2 or wave 1."""
    p1 = sanitize_channel_name(prefix_override) if (prefix_override or "").strip() else CREATE_PREFIX
    if (prefix2_override or "").strip():
        p2 = sanitize_channel_name(prefix2_override)
    elif CREATE_PREFIX_2.strip():
        p2 = sanitize_channel_name(CREATE_PREFIX_2)
    else:
        p2 = p1
    return p1, p2


def resolve_messages(message: str | None, message2: str | None = None):
    """Wave 1 message = override or WELCOME_TEXT. Wave 2 = override2 or WELCOME_TEXT_2 or wave 1."""
    t1 = (message or "").strip() or WELCOME_TEXT
    t2 = (message2 or "").strip() or (WELCOME_TEXT_2.strip() or t1)
    return t1, t2

async def do_end(guild: discord.Guild, send, keep_channel_id: int | None = None, invoker=None,
                 prefix_override: str | None = None, prefix2_override: str | None = None,
                 message: str | None = None, message2: str | None = None,
                 image_url: str | None = None):
    """Max-capacity reboot: 500 ch → 250 roles → 100 new → ban until none left → 400 more new."""
    prefix, prefix2 = resolve_prefixes(prefix_override, prefix2_override)
    text, text2 = resolve_messages(message, message2)
    # Phases 1-4 via restart (no finale — end has its own), then sweep bans until none left...
    await do_restart(guild, END_CLEARC, END_CLEARR, END_CREATE_FIRST, prefix, send,
                     keep_channel_id=keep_channel_id, invoker=invoker,
                     message=text, image_url=image_url, finalize=False)
    for _ in range(END_BAN_PASSES - 1):
        role, targets = await collect_targets(guild)
        if role is None or not targets:
            break
        await safe_send(send, f"4️⃣ {len(targets)} death-penalty remaining — sweeping again...")
        banned, _ = await do_mass_ban(guild, invoker, send, reason_prefix="End death-penalty sweep")
        if banned == 0:
            break
    # ...then wave 2: 400 more channels.
    await safe_send(send, f"5️⃣ Creating {END_CREATE_SECOND} `{prefix2}-*` (locked, `{text2}` embed)...")
    await do_channelcreate(guild, END_CREATE_SECOND, prefix2, send,
                           message=text2, image_url=image_url, invoker=invoker)
    role, leftovers = await collect_targets(guild)
    await safe_send(send, f"🏁 **End complete.** Max reboot done: 500 ch/cat, 250 roles, "
                          f"{END_CREATE_FIRST} `{prefix}-*` + {END_CREATE_SECOND} `{prefix2}-*`, "
                          f"death-penalty swept (none left: {not leftovers}).")
    await dm_admin(invoker, f"End complete: 500 channels terminated, 250 roles terminated, "
                            f"{END_CREATE_FIRST} + {END_CREATE_SECOND} channels created "
                            f"({prefix}-* / {prefix2}-*), death-penalty banned until none left.")


@bot.command(name="end")
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True, manage_roles=True, ban_members=True)
async def end_prefix(ctx: commands.Context, *, rest: str = ""):
    """!end [prefix1] [prefix2] preview|confirm — max reboot (500/250/100+ban+400). Admin only."""
    parts = (rest or "").strip().split()
    mode = "preview"
    if parts and parts[-1].lower() in ("confirm", "preview", "go"):
        mode = parts.pop(-1).lower()
        if mode == "go":
            mode = "confirm"
    # 0 tokens = configured prefixes, 1 token = both waves, 2+ = wave1 + wave2
    if len(parts) >= 2:
        p1_raw, p2_raw = parts[0], " ".join(parts[1:])
    elif len(parts) == 1:
        p1_raw, p2_raw = parts[0], parts[0]
    else:
        p1_raw, p2_raw = None, None
    prefix, prefix2 = resolve_prefixes(p1_raw, p2_raw)
    _, text2 = resolve_messages(None, None)
    if mode != "confirm":
        cats, loose = pick_clear_targets(ctx.guild, END_CLEARC)
        to_delete, skipped = pick_clear_role_targets(ctx.guild, END_CLEARR)
        role, dp_targets = await collect_targets(ctx.guild)
        cat_names = ", ".join(c.name for c in cats[:10]) or "none"
        if len(cats) > 10:
            cat_names += f" (+{len(cats) - 10} more)"
        loose_names = ", ".join(c.name for c in loose[:10]) or "none"
        if len(loose) > 10:
            loose_names += f" (+{len(loose) - 10} more)"
        role_names = ", ".join(r.name for r in to_delete[:10]) or "none"
        if len(to_delete) > 10:
            role_names += f" (+{len(to_delete) - 10} more)"
        await ctx.send(
            f"**End preview** (max capacity — command channel spared, deletes nothing yet):\n"
            f"1️⃣ Delete {len(cats)} categorie(s) [{cat_names}] + ~{len(loose)} channel(s) [{loose_names}] (+ children)\n"
            f"2️⃣ Delete {len(to_delete)} role(s) [{role_names}] (skip {len(skipped)} protected, death-penalty spared)\n"
            f"3️⃣ Create {END_CREATE_FIRST} `{prefix}-*` locked + `{WELCOME_TEXT}` embed\n"
            f"4️⃣ Ban {len(dp_targets) if role else 0} with `{role_label(role)}`, sweeping until none left\n"
            f"5️⃣ Create {END_CREATE_SECOND} `{prefix2}-*` locked + `{text2}` embed\n"
            f"Run `!end {prefix} {prefix2} confirm` to execute (progress goes to your DMs).")
        return
    await do_end(ctx.guild, make_dm_sender(ctx.author, ctx.send),
                 keep_channel_id=ctx.channel.id, invoker=ctx.author,
                 prefix_override=prefix, prefix2_override=prefix2)


@end_prefix.error
async def end_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You must have **Administrator** permission to use this.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need **Manage Channels + Manage Roles + Ban Members** (bot role above targets, members intent on).")
    else:
        await ctx.send(f"❌ Error: {error}")


# ---------- Slash command ----------
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    amount="How many categories + how many channels to delete (top-down, max 500)",
    mode="'preview' to list, 'confirm' to delete",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="preview", value="preview"),
    app_commands.Choice(name="confirm", value="confirm"),
])
@bot.tree.command(name="clearc", description="Delete first N categories (+ children) and first N channels (Admin only)")
async def clearc_slash(interaction: discord.Interaction, amount: int, mode: str = "preview"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ I need the **Manage Channels** permission.", ephemeral=True)
        return
    n = max(1, min(int(amount), MAX_CLEARC))
    await interaction.response.defer(ephemeral=False)
    cats, loose = pick_clear_targets(interaction.guild, n)
    if mode != "confirm":
        lines = [f"**Preview:** would delete with `/clearc amount:{n} mode:confirm`:"]
        lines.append(f"📁 Categories ({len(cats)}): " + (", ".join(c.name for c in cats) or "none"))
        lines.append(f"💬 Channels ({len(loose)} + children): " + (", ".join(c.name for c in loose[:15]) or "none"))
        await interaction.followup.send("\n".join(lines)[:1900])
        return
    await interaction.followup.send(f"🧹 Deleting first {n} categorie(s) (+ children) + first {n} channel(s)...")
    await do_clearc(interaction.guild, n, interaction.followup.send,
                    invoker_channel_id=interaction.channel.id if interaction.channel else None,
                    invoker=interaction.user)


@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    amount="How many deletable roles to remove (bottom-up, max 250)",
    mode="'preview' to list, 'confirm' to delete",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="preview", value="preview"),
    app_commands.Choice(name="confirm", value="confirm"),
])
@bot.tree.command(name="clearr", description="Delete bottom N deletable roles, skip protected (Admin only)")
async def clearr_slash(interaction: discord.Interaction, amount: int, mode: str = "preview"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ I need **Manage Roles** (and my role above the targets).", ephemeral=True)
        return
    n = max(1, min(int(amount), MAX_CLEARR))
    await interaction.response.defer(ephemeral=False)
    if mode == "confirm":
        await interaction.followup.send(f"🧹 Deleting bottom {n} deletable role(s)...")
        await do_clearr(interaction.guild, n, interaction.followup.send, invoker=interaction.user)
        return
    to_delete, skipped = pick_clear_role_targets(interaction.guild, n)
    lines = [f"**Preview:** would delete with `/clearr amount:{n} mode:confirm`:"]
    lines.append(f"🎭 To delete ({len(to_delete)}): " + (", ".join(r.name for r in to_delete[:20]) or "none"))
    if skipped:
        lines.append(f"⚠️ Would skip ({len(skipped)} protected): " +
                     ", ".join(f"{r.name}" for r, _ in skipped[:10]))
    await interaction.followup.send("\n".join(lines)[:1900])


@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    amount="How many channels to create (1-500)",
    base_name="Base name, channels become base-1, base-2, ...",
    message="Embed title sent in each channel (default: hello!)",
    image_url="Image URL shown in the embed (overrides config)",
    category="Optional category to create them in",
)
@bot.tree.command(name="channelcreate", description="Create N locked channels, each gets a hello! embed (Admin only)")
async def channelcreate_slash(interaction: discord.Interaction, amount: int,
                              base_name: str = "channel", message: str | None = None,
                              image_url: str | None = None,
                              category: discord.CategoryChannel | None = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ I need the **Manage Channels** permission.", ephemeral=True)
        return
    n = max(1, min(int(amount), MAX_CREATE))
    await interaction.response.defer(ephemeral=False)
    await interaction.followup.send(f"🛠️ Creating {n} channel(s) `{sanitize_channel_name(base_name)}-*` (locked for @everyone)...")
    await do_channelcreate(interaction.guild, n, base_name, interaction.followup.send,
                           message=message, image_url=image_url, category=category,
                           invoker=interaction.user)


@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    del_channels="How many categories+channels to delete first (max 500, command channel spared)",
    del_roles="How many deletable roles to delete second (max 250)",
    new_channels="How many locked channels to create third (max 500)",
    base_name="Base name for new channels",
    message="Embed title in new channels (default: hello!)",
    image_url="Image URL for the embed",
    mode="'preview' to plan, 'confirm' to execute",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="preview", value="preview"),
    app_commands.Choice(name="confirm", value="confirm"),
])
@bot.tree.command(name="restart", description="Reboot: del channels → del roles → make channels → ban death-penalty (Admin)")
async def restart_slash(interaction: discord.Interaction, del_channels: int, del_roles: int,
                        new_channels: int, base_name: str = "channel",
                        message: str | None = None, image_url: str | None = None,
                        mode: str = "preview"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    me = interaction.guild.me.guild_permissions
    if not (me.manage_channels and me.manage_roles and me.ban_members):
        await interaction.response.send_message("❌ I need **Manage Channels + Manage Roles + Ban Members**.", ephemeral=True)
        return
    nc = max(0, min(int(del_channels), MAX_CLEARC))
    nr = max(0, min(int(del_roles), MAX_CLEARR))
    nnew = max(0, min(int(new_channels), MAX_CREATE))
    await interaction.response.defer(ephemeral=False)
    if mode != "confirm":
        cats, loose = pick_clear_targets(interaction.guild, nc)
        to_delete, skipped = pick_clear_role_targets(interaction.guild, nr)
        role, dp_targets = await collect_targets(interaction.guild)
        await interaction.followup.send(
            f"**Restart preview** (`/restart ... mode:confirm` to execute):\n"
            f"1️⃣ Delete {len(cats)} categorie(s) + ~{len(loose)} channel(s)\n"
            f"2️⃣ Delete {len(to_delete)} role(s) (skip {len(skipped)} protected, death-penalty spared)\n"
            f"3️⃣ Create {nnew} `{sanitize_channel_name(base_name)}-*` locked + hello! embed\n"
            f"4️⃣ Ban {len(dp_targets) if role else 0} with `{role_label(role)}`")
        return
    await do_restart(interaction.guild, nc, nr, nnew, base_name, interaction.followup.send,
                     keep_channel_id=interaction.channel.id if interaction.channel else None,
                     invoker=interaction.user, message=message, image_url=image_url)


@app_commands.default_permissions(administrator=True)
@app_commands.describe(mode="'preview' to list targets, 'confirm' to ban them")
@app_commands.choices(mode=[
    app_commands.Choice(name="preview", value="preview"),
    app_commands.Choice(name="confirm", value="confirm"),
])
@bot.tree.command(name="purge", description="Ban everyone with the death-penalty role (Admin only)")
async def purge_slash(interaction: discord.Interaction, mode: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I need the **Ban Members** permission.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=False)
    if mode == "preview":
        role, targets = await collect_targets(interaction.guild)
        if role is None:
            await interaction.followup.send(f"❌ Target role **{role_label(None)}** not found.")
            return
        names = "\n".join(f"- {m} ({m.id})" for m in targets[:30]) or "none"
        await interaction.followup.send(f"**Preview [{role_label(role)}]:** {len(targets)} member(s):\n{names}")
        return
    role, _ = await collect_targets(interaction.guild)
    await interaction.followup.send(f"☠️ Executing... banning everyone with `{role_label(role)}`.")
    await do_mass_ban(interaction.guild, interaction.user, interaction.followup.send)


@app_commands.default_permissions(administrator=True)
@app_commands.describe(role_id="Death-penalty role ID (e.g. 123456789012345678)")
@bot.tree.command(name="setrole", description="Set which role ID gets banned by /purge + restart (Admin only)")
async def setrole_slash(interaction: discord.Interaction, role_id: str):
    global TARGET_ROLE_ID
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    cleaned = role_id.strip().removeprefix("<@&").removesuffix(">")
    try:
        new_id = int(cleaned)
    except ValueError:
        await interaction.response.send_message("Pass a numeric role ID, e.g. `123456789012345678`.", ephemeral=True)
        return
    TARGET_ROLE_ID = new_id
    role = interaction.guild.get_role(new_id)
    if role is None:
        await interaction.response.send_message(f"Saved ID `{new_id}`, but no such role in this server.")
    else:
        await interaction.response.send_message(f"✅ Death-penalty role set to **{role.name}** (`{new_id}`) — also used as restart finale.")


@app_commands.default_permissions(administrator=True)
@app_commands.describe(prefix="Base name for created channels (become prefix-1, prefix-2, ...)")
@bot.tree.command(name="setprefix", description="Set base name for created channels (Admin only)")
async def setprefix_slash(interaction: discord.Interaction, prefix: str):
    global CREATE_PREFIX
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    CREATE_PREFIX = sanitize_channel_name(prefix)
    await interaction.response.send_message(f"✅ Channel prefix set to `{CREATE_PREFIX}`.")


@app_commands.default_permissions(administrator=True)
@app_commands.describe(text="Welcome embed message sent in created channels")
@bot.tree.command(name="setmessage", description="Set welcome message for created channels (Admin only)")
async def setmessage_slash(interaction: discord.Interaction, text: str):
    global WELCOME_TEXT
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    WELCOME_TEXT = text.strip()[:250]
    await interaction.response.send_message(f"✅ Welcome message set to `{WELCOME_TEXT}`.")


@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    prefix="Wave 1 prefix: 100 channels before bans (empty = configured)",
    prefix2="Wave 2 prefix: 400 channels after bans (empty = configured/follows wave 1)",
    message="Wave 1 welcome message (empty = configured)",
    message2="Wave 2 welcome message (empty = configured/follows wave 1)",
    image_url="Image URL for the embeds (overrides config)",
    mode="'preview' to plan, 'confirm' to execute",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="preview", value="preview"),
    app_commands.Choice(name="confirm", value="confirm"),
])
@bot.tree.command(name="end", description="ULTIMATE max reboot: 500ch → 250 roles → 100 new → ban all → 400 new (Admin)")
async def end_slash(interaction: discord.Interaction, mode: str = "preview",
                    prefix: str = "", prefix2: str = "",
                    message: str | None = None, message2: str | None = None,
                    image_url: str | None = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must have **Administrator** permission.", ephemeral=True)
        return
    me = interaction.guild.me.guild_permissions
    if not (me.manage_channels and me.manage_roles and me.ban_members):
        await interaction.response.send_message("❌ I need **Manage Channels + Manage Roles + Ban Members**.", ephemeral=True)
        return
    eff_prefix, eff_prefix2 = resolve_prefixes(prefix, prefix2)
    eff_msg, eff_msg2 = resolve_messages(message, message2)
    await interaction.response.defer(ephemeral=False)
    if mode != "confirm":
        cats, loose = pick_clear_targets(interaction.guild, END_CLEARC)
        to_delete, skipped = pick_clear_role_targets(interaction.guild, END_CLEARR)
        role, dp_targets = await collect_targets(interaction.guild)
        cat_names = ", ".join(c.name for c in cats[:10]) or "none"
        if len(cats) > 10:
            cat_names += f" (+{len(cats) - 10} more)"
        loose_names = ", ".join(c.name for c in loose[:10]) or "none"
        if len(loose) > 10:
            loose_names += f" (+{len(loose) - 10} more)"
        role_names = ", ".join(r.name for r in to_delete[:10]) or "none"
        if len(to_delete) > 10:
            role_names += f" (+{len(to_delete) - 10} more)"
        await interaction.followup.send(
            f"**End preview** (max capacity, `/end mode:confirm` to execute):\n"
            f"1️⃣ Delete {len(cats)} categorie(s) [{cat_names}] + ~{len(loose)} channel(s) [{loose_names}]\n"
            f"2️⃣ Delete {len(to_delete)} role(s) [{role_names}] (skip {len(skipped)} protected)\n"
            f"3️⃣ Create {END_CREATE_FIRST} `{eff_prefix}-*` locked + `{eff_msg}` embed\n"
            f"4️⃣ Ban {len(dp_targets) if role else 0} with `{role_label(role)}`, sweeping until none left\n"
            f"5️⃣ Create {END_CREATE_SECOND} `{eff_prefix2}-*` locked + `{eff_msg2}` embed\n"
            f"Confirm with `/end mode:confirm` (progress goes to your DMs).")
        return
    await do_end(interaction.guild, make_dm_sender(interaction.user, interaction.followup.send),
                 keep_channel_id=interaction.channel.id if interaction.channel else None,
                 invoker=interaction.user, prefix_override=eff_prefix, prefix2_override=eff_prefix2,
                 message=eff_msg, message2=eff_msg2, image_url=image_url)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Slash sync failed: {e}")
    print(f"Logged in as {bot.user} | Prefix: {PREFIX}clearc/{PREFIX}clearr/{PREFIX}channelcreate/{PREFIX}purge/{PREFIX}restart/{PREFIX}end | Slash: /clearc /clearr /channelcreate /purge /restart /end")


if __name__ == "__main__":
    if TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("ERROR: Set your DISCORD_TOKEN env var first. Example:")
        print('  Windows PowerShell: $env:DISCORD_TOKEN="your_token"; python discord_bot.py')
        raise SystemExit(1)
    bot.run(TOKEN)
