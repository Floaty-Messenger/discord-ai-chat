"""
启动：
  python bot.py                       连接 Discord（正式使用）
  python bot.py --local               在终端里聊天，不需要 Discord（先测试三个 AI 能不能正常调用）
  python bot.py --local --project 我的项目  终端模式下指定项目
"""
import argparse
import asyncio
import contextlib
import io
import os
import re
import sys
import time
from pathlib import Path

from core import (DISPLAY, GroupChat, Usage, load_config, log, notice_snippet, save_setting,
                  sync_pull_all, sync_url)

DISCORD_LIMIT = 1900             # Discord 单条消息上限 2000 字，留点余量
ATTACH_LIMIT = 20 * 1024 * 1024  # 免费用户单文件 20MB


def chunks(text, n=DISCORD_LIMIT):
    out = []
    while len(text) > n:
        cut = text.rfind("\n", 0, n)
        cut = cut if cut > n // 2 else n
        out.append(text[:cut])
        text = text[cut:].lstrip("\n")
    if text:
        out.append(text)
    return out


HELP = ("命令：\n"
        "!停　　　　　当前 AI 说完这句就停\n"
        "!状态　　　　看项目、轮数、额度\n"
        "!记住 内容　　存进这个项目的共享记忆\n"
        "!记住 @GPT 内容　存进指定成员的记忆（@大小姐 / @GPT / @DeepSeek）\n"
        "!记忆　　　　看这个项目的记忆文件在哪、多大\n"
        "!清空　　　　归档聊天记录，开始新话题（记忆保留）\n"
        "!高强度 / !默认强度　手动切换这个任务的思考强度\n"
        "!头脑风暴 / !头脑风暴 关　只要简短点子，不查资料不写报告\n"
        "!轮数 N　　　默认最多连续几轮（1–30）\n"
        "!大小姐上限 次数　0 = 不限次数（默认），只在 Claude 真的报额度用完时才暂停\n"
        "!新会话　　　让三个 AI 重新开对话（聊天记录和记忆都保留，AI 好像糊涂了时用）\n"
        "!旅行 开/关　旅行模式：只有 DeepSeek 回复（对所有项目生效）\n"
        "!新项目 名字　新建一个项目频道和文件夹\n"
        "!下线　　　　关闭整个群聊程序（三个机器人都下线）\n"
        "!撤回 编号　　撤回一条 AI 消息（从所有 AI 的上下文里拿掉，原文留在记录里）\n"
        "!批准 / !否决 原因　亲自拍板 GPT 提交的改文件方案\n"
        "不 @ 任何人默认交给 GPT。")


def handle_command(chat, cfg, text):
    """返回字符串表示这是命令（已处理）；返回 None 表示是普通消息。"""
    t = text.strip()
    if not t.startswith("!"):
        return None
    if t in ("!停", "!stop"):
        chat.stop()
        return "收到，当前 AI 说完这句就停。"
    if t in ("!状态", "!status"):
        return chat.status()
    if t in ("!清空", "!clear"):
        chat.clear()
        return "聊天记录已归档，开始新话题。记忆文件没有动。"
    if t.startswith("!轮数"):
        parts = t.split()
        cap = cfg.get("max_rounds_cap", 30)
        try:
            n = int(parts[1])
        except (IndexError, ValueError):
            return f"现在默认最多连续 {cfg.get('max_rounds')} 轮。用法：!轮数 20（1–{cap}）"
        n = max(1, min(n, cap))
        cfg["max_rounds"] = n
        try:
            save_setting(cfg, ["max_rounds"], n)
            if cfg.get("budget_mode"):
                save_setting(cfg, ["budget_overrides", "max_rounds"], n)
            saved = "，已保存"
        except Exception as e:
            saved = f"（保存失败：{e}，只在这次运行有效）"
        return f"默认最多连续 {n} 轮{saved}。单次任务也可以在消息里写\"N轮以内\"（最多 {cap}）"
    if t.startswith("!大小姐上限"):
        parts = t.split()
        try:
            n = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            return "用法：!大小姐上限 次数（0 = 不限，只在 Claude 真的报额度用完时才暂停）"
        cfg["claude"]["daily_limit"] = n
        chat.usage.data.pop("claude_block_until", None)
        chat.usage._save()
        try:
            save_setting(cfg, ["claude", "daily_limit"], n)
            save_setting(cfg, ["_limit_v2"], True)
            saved = "，已保存"
        except Exception as e:
            saved = f"（保存到 config.json 失败：{e}，只在这次运行有效）"
        return f"大小姐每日上限：{'不限次数，只在 Claude 真的报额度用完时暂停' if n == 0 else str(n) + ' 次'}{saved}"
    if t.startswith("!头脑风暴"):
        chat.brainstorm = not (("关" in t) or ("off" in t.lower()))
        return ("💡 头脑风暴模式：AI 们只给简短点子，不查资料不写报告（!头脑风暴 关 退出）" if chat.brainstorm
                else "头脑风暴模式已关闭")
    if t in ("!高强度", "!默认强度"):
        chat.boost = t == "!高强度"
        return "⚡ 这个任务改用高强度思考，做完自动恢复" if chat.boost else "思考强度恢复默认"
    if t in ("!新会话", "!newsession"):
        chat.reset_sessions()
        return "🔄 三个 AI 下次发言会开新的对话（记忆、摘要、聊天记录都保留）。"
    if t.startswith("!记住"):
        return chat.remember_from_user(t)
    if t in ("!记忆", "!memory"):
        return chat.memory_info()
    if t.startswith("!旅行"):
        cfg["travel_mode"] = ("开" in t) or ("on" in t.lower())
        return f"旅行模式：{'开（只有 DeepSeek 回复）' if cfg['travel_mode'] else '关'}"
    if t in ("!帮助", "!help"):
        return HELP
    return None


# ================================================================ 本地终端模式
async def run_local(cfg, project):
    async def send(who, text, paths=None):
        extra = ("\n📎 " + "\n📎 ".join(str(p) for p in paths)) if paths else ""
        print(f"\n【{DISPLAY.get(who, who)}】\n{text}{extra}\n", flush=True)

    async def ping(msg, kind, mention):
        who, mid = DISPLAY[msg["who"]], msg.get("id")
        if kind == "ask":
            print(f"🔔 {who} 在 #{mid} @了你：{notice_snippet(msg, kind)}\n", flush=True)
        else:
            print(f"✅ 任务完成 —— {who} #{mid}：{notice_snippet(msg, kind)}\n", flush=True)

    chat = GroupChat(cfg, project, send, ping)
    print(f"本地模式，项目：{chat.project.dir}\n直接输入消息回车发送，!帮助 看命令，!退出 结束。\n")
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        if line == "!退出":
            break
        if line.startswith("!批准") or line.startswith("!否决"):
            r = await chat.approve(line.startswith("!批准"), line[3:].strip())
            if r:
                print(r, flush=True)
            continue
        if line.startswith("!撤回"):
            parts = line.split()
            print(await chat.retract(parts[1], "user") if len(parts) > 1 else "用法：!撤回 编号", flush=True)
            continue
        r = handle_command(chat, cfg, line)
        if r is not None:
            print(r, flush=True)
            continue
        await chat.user_message(line)
    if chat.task:
        await chat.task


# ================================================================ 交接班（预留接口）
CONTROL_NAME = "群聊值班"


def _has_battery():
    """有电池 = 笔记本：更省电，优先值班。"""
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        class _S(ctypes.Structure):
            _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("pct", ctypes.c_ubyte),
                        ("saver", ctypes.c_ubyte), ("life", ctypes.c_ulong), ("full", ctypes.c_ulong)]
        st = _S()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(st)):
            return False
        return st.flag not in (128, 255)
    except Exception:
        return False


class HostCoordinator:
    """
    多台电脑同时开着时，只让一台回复（值班），其他待命。
    - 每台电脑每 30 秒在「群聊值班」频道里更新自己的心跳（频道自动创建）。
    - 优先级数字小的先值班：笔记本 1、台式机 2（config 的 host.priorities 可以按电脑名覆盖）。同级按电脑名排。
    - 值班的电脑 100 秒没心跳，下一台自动接手；它回来后再交还。
    - !下线 会通知所有电脑一起下线。
    """
    BEAT, FRESH, GRACE, START_WAIT = 30, 100, 70, 8

    def __init__(self, cfg, client, make_channel=None, on_stop=None, on_become_active=None):
        import socket
        h = cfg.get("host", {})
        self.name = socket.gethostname()
        self.laptop = _has_battery()
        self.priority = int((h.get("priorities") or {}).get(self.name, 1 if self.laptop else 2))
        self.channel_id = str(h.get("control_channel_id") or "")
        self.client, self.make_channel, self.on_stop = client, make_channel, on_stop
        self.on_become_active = on_become_active  # 上岗前先从私人仓库拉取最新的项目和记忆
        self.active = False          # 先确认没人在值班再上岗，避免两台同时回复
        self.started = time.time()
        self.peers = {}              # 电脑名 -> (优先级, 最后心跳)
        self.my_msg = None
        self.ch = None
        self.running = False

    def _key(self, name, prio):
        return (prio, name)

    def describe(self):
        now = time.time()
        live = {n: v for n, v in self.peers.items() if now - v[1] < self.FRESH}
        me = f"本机：{self.name}（{'笔记本' if self.laptop else '台式机'}，优先级 {self.priority}）" \
             + ("，正在值班" if self.active else "，待命中")
        others = "；".join(f"{n}（优先级 {v[0]}）" for n, v in live.items()) or "无"
        return f"🖥 {me}\n其他在线电脑：{others}"

    async def stop_all(self):
        """!下线：通知其他电脑一起下线。"""
        if self.ch:
            with contextlib.suppress(Exception):
                await self.ch.send(f"STOP from={self.name} ts={int(time.time())}")

    async def run(self):
        if self.running:
            return
        self.running = True
        try:
            if self.channel_id:
                self.ch = await self.client.fetch_channel(int(self.channel_id))
            elif self.make_channel:
                self.ch = await self.make_channel()
        except Exception as e:
            log("值班频道不可用，按单机模式运行：", e)
        if not self.ch:
            await self._go_active()
            return
        log(f"本机「{self.name}」优先级 {self.priority}，正在确认有没有别的电脑在值班…")
        while True:
            try:
                await self._tick()
            except Exception as e:
                log("心跳出错：", e)
                if not self.peers and not self.active:  # 连值班频道都读不了：自己顶上
                    await self._go_active()
            await asyncio.sleep(self.BEAT)

    async def _tick(self):
        now = int(time.time())
        stamp = f"HEARTBEAT name={self.name} priority={self.priority} active={int(self.active)} ts={now}"
        if self.my_msg:
            await self.my_msg.edit(content=stamp)
        else:
            self.my_msg = await self.ch.send(stamp)
            await asyncio.sleep(self.START_WAIT)  # 两台同时开机时，给对方一点时间也发出心跳
        self.peers = {}
        async for m in self.ch.history(limit=50):
            if m.id == self.my_msg.id:
                continue
            words = m.content.split()
            if not words or words[0] not in ("HEARTBEAT", "STOP"):
                continue
            kv = dict(x.split("=", 1) for x in words[1:] if "=" in x)
            if words[0] == "STOP":
                if int(kv.get("ts", 0)) > self.started and kv.get("from") != self.name:
                    log(f"电脑「{kv.get('from')}」发了 !下线，本机也下线")
                    if self.on_stop:
                        await self.on_stop()
                    return
                continue
            name, ts = kv.get("name"), int(kv.get("ts", 0))
            if name == self.name:  # 本机上次运行留下的旧心跳，清掉
                with contextlib.suppress(Exception):
                    await m.delete()
                continue
            if name and now - ts < self.FRESH and name not in self.peers:
                self.peers[name] = (int(kv.get("priority", 99)), ts)
        mine = self._key(self.name, self.priority)
        better = any(self._key(n, v[0]) < mine for n, v in self.peers.items())
        # 刚启动、而别的电脑正在值班：先等它看到本机心跳主动让位，避免两台同时回复
        wait = self.peers and time.time() - self.started < self.GRACE
        want = not better and not wait
        if want and not self.active:
            await self._go_active()
        elif not want and self.active:
            self.active = False
            log("本机切换为 待命")

    async def _go_active(self):
        if self.on_become_active:
            try:
                await self.on_become_active()
            except Exception as e:
                log("上岗前同步出错：", e)
        self.active = True
        log("本机切换为 值班")


# ================================================================ Discord 模式：一个频道 = 一个项目
TAGS = {"claude": "@大小姐", "gpt": "@GPT", "deepseek": "@DeepSeek"}
MENTION_ID_RE = re.compile(r"<@[!&]?(\d+)>")


def run_discord(cfg):
    import discord

    d = cfg["discord"]
    owner_id = int(d["owner_user_id"])
    category = (d.get("project_category") or "").strip()
    ignore = {str(x) for x in d.get("ignore_channels", [])}
    control = str(cfg.get("host", {}).get("control_channel_id") or "")
    if control:
        ignore.add(control)

    # 三个机器人模式：每个 AI 一个账号；只填了 bot_token 就是单机器人 + webhook 模式
    tokens = {k: v for k, v in (d.get("bots") or {}).items()
              if k in TAGS and v and not str(v).startswith("在这里")}
    multi = len(tokens) == 3
    if not multi:
        if not d.get("bot_token") or str(d["bot_token"]).startswith("在这里"):
            sys.exit("config.json 里没有填机器人令牌（discord.bots 三个都要填，或者只填 discord.bot_token）")
        tokens = {"listener": d["bot_token"]}
    listener_key = d.get("listener", "gpt") if multi else "listener"

    clients = {}
    for key in tokens:
        intents = discord.Intents.default()
        intents.message_content = (key == listener_key)
        clients[key] = discord.Client(intents=intents)
    listener = clients[listener_key]

    async def make_control_channel():
        maker = clients.get("claude", listener) if multi else listener
        await maker.wait_until_ready()
        guild = next(iter(maker.guilds), None)
        if guild is None:
            return None
        ch = discord.utils.get(guild.text_channels, name=CONTROL_NAME)
        if ch is None:
            try:
                ch = await guild.create_text_channel(CONTROL_NAME, topic="多台电脑轮流值班用的，程序自动维护，不用在这里说话")
            except discord.Forbidden:
                log("没有权限建「群聊值班」频道（需要大小姐机器人的「管理频道」权限），按单机模式运行")
                return None
        ignore.add(str(ch.id))
        return listener.get_channel(ch.id) or await listener.fetch_channel(ch.id)

    async def stop_everything():
        (Path(cfg["state_dir"]) / "stop.flag").write_text("stop", encoding="utf-8")
        for c in clients.values():
            await c.close()

    async def become_active():
        if sync_url(cfg):
            log("同步：上岗前从私人仓库拉取最新的项目和记忆…")
            await asyncio.to_thread(sync_pull_all, cfg)
            chats.clear()  # 重新从硬盘读聊天记录和记忆

    host = HostCoordinator(cfg, listener, make_control_channel, stop_everything, become_active)
    usage = Usage(cfg["state_dir"])
    chats = {}       # 频道 ID -> GroupChat
    webhooks = {}    # 频道 ID -> Webhook 或 None
    mention_ids = {}  # 机器人用户 ID / 机器人身份组 ID -> AI

    def is_project_channel(ch):
        if not isinstance(ch, discord.TextChannel) or str(ch.id) in ignore:
            return False
        if category:
            return ch.category is not None and ch.category.name == category
        return True

    async def channel_for(key, ch):
        """同一个频道，用指定机器人的身份拿到它（这样消息就是那个机器人发的）。"""
        c = clients[key]
        return c.get_channel(ch.id) or await c.fetch_channel(ch.id)

    async def get_webhook(ch):
        if ch.id in webhooks:
            return webhooks[ch.id]
        hook = None
        if d.get("use_webhook", True):
            try:
                hooks = await ch.webhooks()
                hook = next((h for h in hooks if h.name == "ai-group-chat"), None) \
                    or await ch.create_webhook(name="ai-group-chat")
            except Exception as e:
                log("无法使用 webhook（缺少“管理 Webhook”权限？），改用普通消息：", e)
        webhooks[ch.id] = hook
        return hook

    async def post(ch, who, text, files):
        """把一段消息以 who 的身份发出去，返回 Discord 消息 ID。"""
        name = DISPLAY.get(who, who)
        if multi and who in clients:
            target = await channel_for(who, ch)
            return (await target.send(text, **files)).id
        hook = await get_webhook(ch)
        if hook:
            return (await hook.send(text, username=name, wait=True, **files)).id
        return (await ch.send(f"**【{name}】**\n{text}", **files)).id

    # 删消息用大小姐的账号（她有"管理消息"权限）；单机器人模式用 webhook 自己删
    deleter_key = "claude" if multi else listener_key

    async def delete_msgs(ch, ids):
        target = await channel_for(deleter_key, ch)
        hook = None if multi else await get_webhook(ch)
        for i in ids:
            try:
                if hook:
                    await hook.delete_message(int(i))
                else:
                    await (await target.fetch_message(int(i))).delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                log("没有权限删除消息：请给「大小姐」机器人加上「管理消息」权限")
                raise

    async def create_project(src_ch, name, key):
        """在项目分类下建频道。key = 用哪个机器人的身份建（需要"管理频道"权限）。"""
        guild = (await channel_for(key, src_ch)).guild
        try:
            cat = None
            if category:
                cat = discord.utils.get(guild.categories, name=category) \
                    or await guild.create_category(category)
            exist = discord.utils.get(cat.text_channels if cat else guild.text_channels,
                                      name=name.lower().replace(" ", "-"))
            ch = exist or await guild.create_text_channel(name, category=cat)
        except discord.Forbidden:
            return f"⚠️ 没有权限建频道：请给「{DISPLAY.get(key, key)}」机器人加上「管理频道」权限。"
        chat = get_chat(listener.get_channel(ch.id) or await listener.fetch_channel(ch.id))
        if exist:
            return f"已经有这个项目了：{ch.mention}"
        await post(ch, "system", f"这里是项目「{chat.project.name}」。直接说你要做什么。", {})
        return f"✅ 新项目 {ch.mention} 已创建\n文件夹：{chat.project.dir}"

    def get_chat(ch):
        if ch.id not in chats:
            async def send(who, text, paths=None, ch=ch):
                files, big = [], []
                for p in (paths or []):
                    try:
                        if os.path.getsize(p) <= ATTACH_LIMIT:
                            files.append(discord.File(str(p), filename=Path(p).name))
                        else:
                            big.append(str(p))
                    except OSError:
                        pass
                if big:
                    text += "\n\n📁 文件太大没法发到 Discord，在电脑上：\n" + "\n".join(f"`{x}`" for x in big)
                if len(text) > DISCORD_LIMIT * 4:  # 太长就附一个文件
                    files.append(discord.File(io.BytesIO(text.encode("utf-8")), filename=f"{who}-回复.md"))
                    text = text[:DISCORD_LIMIT - 40] + "\n…（全文见附件）"
                files = files[:10]  # Discord 一条消息最多 10 个附件
                parts = chunks(text)
                ids = []
                for i, part in enumerate(parts):
                    extra = {"files": files} if (files and i == len(parts) - 1) else {}
                    ids.append(await post(ch, who, part, extra))
                return ids

            async def ping(msg, kind, mention, ch=ch):
                who, mid = DISPLAY[msg["who"]], msg.get("id")
                dc = msg.get("dc") or []
                jump = f"\n↪ https://discord.com/channels/{ch.guild.id}/{ch.id}/{dc[0]}" if dc else ""
                at = f"<@{owner_id}> " if mention else ""
                quote = notice_snippet(msg, kind)
                if kind == "ask":
                    text = f"{at}🔔 **{who}** 在 `#{mid}` @了你：{quote}{jump}"
                else:
                    text = f"{at}✅ 任务完成 —— **{who}** `#{mid}`：{quote}{jump}"
                await post(ch, "system", text, {})

            @contextlib.asynccontextmanager
            async def thinking(who, ch=ch):
                # 三个机器人模式下，显示"GPT 正在输入…"
                target = None
                if multi and who in clients:
                    try:
                        target = await channel_for(who, ch)
                    except discord.HTTPException:
                        target = None
                if target is None:
                    yield
                    return
                async with target.typing():
                    yield

            async def _delete(ids, ch=ch):
                await delete_msgs(ch, ids)

            async def _create(name, ch=ch):
                return await create_project(ch, name, "claude" if multi else listener_key)

            async def choice(text, options, ch=ch):
                """弹出一条带按钮的消息，只有你能点；点完按钮变灰，并显示结果。"""
                view = discord.ui.View(timeout=None)
                for label, style, fn in options:
                    btn = discord.ui.Button(label=label, style=getattr(discord.ButtonStyle, style))

                    async def cb(interaction, fn=fn, label=label):
                        if interaction.user.id != owner_id:
                            await interaction.response.send_message("只有群主能点这个按钮。", ephemeral=True)
                            return
                        for item in view.children:
                            item.disabled = True
                        await interaction.response.edit_message(view=view)
                        try:
                            r = await fn()
                        except Exception as e:
                            r = f"⚠️ 出错：{e}"
                        await interaction.followup.send(r or f"已选择：{label}")
                    btn.callback = cb
                    view.add_item(btn)
                target = await channel_for(listener_key, ch)
                await target.send(f"<@{owner_id}> {text}\n（程序重启后旧按钮会失效）", view=view)

            chats[ch.id] = GroupChat(cfg, ch.name, send, ping, usage=usage, thinking=thinking,
                                     delete_msgs=_delete, create_channel=_create, choice=choice,
                                     jump_url=lambda mid, ch=ch: f"https://discord.com/channels/{ch.guild.id}/{ch.id}/{mid}")
            log(f"频道 #{ch.name} → 项目文件夹 {chats[ch.id].project.dir}")
        return chats[ch.id]

    def normalize_mentions(text):
        """你在手机上用 @ 补全选中的机器人，会变成 <@数字>，这里换回 @GPT 这种文字。"""
        def repl(m):
            who = mention_ids.get(int(m.group(1)))
            return TAGS[who] if who else m.group(0)
        return MENTION_ID_RE.sub(repl, text)

    def make_ready(key, client):
        @client.event
        async def on_ready():
            if key in TAGS:
                mention_ids[client.user.id] = key
                for g in client.guilds:
                    if g.self_role:
                        mention_ids[g.self_role.id] = key
            log(f"{'[' + DISPLAY[key] + '] ' if key in TAGS else ''}已登录为 {client.user}")
            if client is listener:
                log("模式：" + ("三个机器人" if multi else "单机器人 + webhook") + "；"
                    + (f"只管分类「{category}」下的频道。" if category else "所有文字频道都当作项目。"))
                asyncio.create_task(host.run())

    for key, c in clients.items():
        make_ready(key, c)

    @listener.event
    async def on_message(m):
        if m.author.bot or m.webhook_id or m.author.id != owner_id:
            return  # 只听你一个人的
        if not is_project_channel(m.channel) or not host.active:
            return
        chat = get_chat(m.channel)
        text = normalize_mentions(m.content.strip())
        if text.startswith("!新项目"):
            parts = text.split(None, 1)
            if len(parts) < 2 or not parts[1].strip():
                r = "用法：!新项目 项目名"
            else:
                r = await create_project(m.channel, parts[1].strip(), listener_key)
            await post(m.channel, "system", r, {})
            return
        if text in ("!下线", "!关机"):
            (Path(cfg["state_dir"]) / "stop.flag").write_text("stop", encoding="utf-8")
            await host.stop_all()
            await post(m.channel, "system", "👋 群聊已下线（所有电脑一起）。想重新上线：在任意一台电脑上双击「AI群聊 - Discord」。", {})
            log("收到 !下线，正在退出")
            for c in clients.values():
                await c.close()
            return
        if text.startswith("!批准") or text.startswith("!否决"):
            r = await chat.approve(text.startswith("!批准"), text[3:].strip())
            if r:
                await post(m.channel, "system", r, {})
            return
        if text.startswith("!撤回"):
            parts = text.split()
            r = await chat.retract(parts[1], "user") if len(parts) > 1 else "用法：!撤回 编号（比如 !撤回 12）"
            await post(m.channel, "system", r, {})
            return
        r = handle_command(chat, cfg, text)
        if r is not None and text in ("!状态", "!status"):
            r += "\n" + host.describe()
        if r is not None:
            await post(m.channel, "system", r, {})
            return
        saved = []
        inbox = chat.project.dir / "inbox"
        for a in m.attachments:
            if a.size > ATTACH_LIMIT:
                continue
            inbox.mkdir(parents=True, exist_ok=True)
            await a.save(inbox / a.filename)
            saved.append(f"inbox/{a.filename}")
        if saved:
            text += "\n（附件已保存到项目文件夹：" + "、".join(saved) + "）"
        if text:
            await chat.user_message(text, m.id)

    async def main():
        try:
            await asyncio.gather(*(c.start(tokens[k]) for k, c in clients.items()))
        finally:
            for c in clients.values():
                if not c.is_closed():
                    await c.close()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="终端模式，不连 Discord")
    ap.add_argument("--project", default="本地测试", help="终端模式下的项目名")
    ap.add_argument("--config", default=None)
    ap.add_argument("--set-sync", default=None, metavar="网址", help="设置用来同步项目和记忆的私人 GitHub 仓库")
    ap.add_argument("--setup-sync", action="store_true", help="交互式设置同步仓库")
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.setup_sync:
        print("=" * 44)
        print("  设置同步：两台电脑共用一个私人 GitHub 仓库")
        print("  （项目文件、记忆、聊天记录都会同步）")
        print("=" * 44)
        print("先在 GitHub 上新建一个「私人」（Private）空仓库，")
        print("然后把网址粘贴到这里，比如 https://github.com/你的用户名/Memory.git")
        print("当前：" + (sync_url(cfg) or "未开启"))
        print("直接按回车 = 关闭同步\n")
        args.set_sync = input("仓库网址：")
    if args.set_sync is not None:
        url = args.set_sync.strip()
        save_setting(cfg, ["sync"], {"enabled": bool(url), "remote": url})
        if not url:
            print("已关闭同步。")
            return
        import subprocess
        print("正在连接私人仓库（第一次会弹出 GitHub 登录，请登录）…")
        r = subprocess.run(["git", "ls-remote", url], capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("✅ 连接成功，同步已开启。" if r.returncode == 0 else "⚠️ 连接失败：" + (r.stderr or r.stdout).strip()[:300])
        return
    if args.local:
        asyncio.run(run_local(cfg, args.project))
    else:
        global _LOCK  # 保持文件句柄打开，进程结束时系统自动释放
        _LOCK = single_instance(cfg["state_dir"])
        if _LOCK is None:
            log("Discord 群聊已经在运行了，不重复启动。")
            sys.exit(3)
        (Path(cfg["state_dir"]) / "bot.pid").write_text(str(os.getpid()), encoding="utf-8")
        run_discord(cfg)


def single_instance(state_dir):
    """同一台电脑只允许一个 Discord 群聊在跑，防止每条消息被回复两遍。"""
    f = open(Path(state_dir) / "bot.lock", "a+")
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f
    except OSError:
        f.close()
        return None


if __name__ == "__main__":
    main()
