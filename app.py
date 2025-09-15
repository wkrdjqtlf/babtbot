import discord
from discord.ext import commands
import json
import os

# -----------------------------
# 설정
# -----------------------------
TOKEN = "MTQxNjAzNzAwNzY2MjI1MjE1Mg.Gj_Q9P.vFBH27k8NgFXucEyCefzLbiIXeJ4uttisH_Sb0"  # 실제 봇 토큰 입력
PREFIX = "!"
DATA_FILE = "donations.json"
DEVELOPER_ID = 1394833198214545489  # 본인 Discord ID 입력

# -----------------------------
# 데이터 초기화
# -----------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    donations = json.load(f)

# -----------------------------
# 역할 기준 (ID를 실제 값으로 교체)
# -----------------------------
role_thresholds = {
    2000000: 1409539367063523338,  # 예시
    500000: 1409539375725019178,
    300000: 1409539378883203244,
    250000: 1409539380833550511,
    100000: 1409539886373146767,
    50000: 1409539892597358742,
    30000: 1409539889376268298,
    10000: 1409920251080085676
}

# -----------------------------
# Intents 설정
# -----------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# -----------------------------
# 개발자 체크
# -----------------------------
def is_developer():
    async def predicate(ctx):
        return ctx.author.id == DEVELOPER_ID
    return commands.check(predicate)

# =========================
# 후원 관련 명령어
# =========================
@bot.command(name="후원추가")
@commands.has_permissions(administrator=True)
async def add_donation(ctx, member: discord.Member, amount: int):
    uid = str(member.id)
    donations[uid] = donations.get(uid, 0) + amount

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(donations, f, ensure_ascii=False, indent=2)

    # 관리자 임베드
    admin_embed = discord.Embed(
        title="🌸 슬이봇 후원 기록 🌸",
        description=f"✅ {member.mention} 님에게 **{amount}원** 후원 추가 완료!\n총 후원금: **{donations[uid]}원**",
        color=0x91d5ff
    )
    await ctx.send(embed=admin_embed)

    # 후원자 DM (서버명: 윤슬)
    try:
        dm_embed = discord.Embed(
            title="🌸 슬이봇 후원 알림 🌸",
            description=(
                f"안녕하세요 {member.display_name}님! "
                f"윤슬 서버에 {amount}원이 후원되었습니다. 감사합니다! "
                f"현재 누적 후원: {donations[uid]}원"
            ),
            color=0x91d5ff
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        fail_embed = discord.Embed(
            title="⚠️ DM 전송 실패",
            description=f"{member.mention} 님에게 DM을 보낼 수 없습니다 (DM 차단).",
            color=0xff5555
        )
        await ctx.send(embed=fail_embed)

    # 누적 후원 금액별 역할 부여
    for threshold in sorted(role_thresholds.keys(), reverse=True):
        if donations[uid] >= threshold:
            role = ctx.guild.get_role(role_thresholds[threshold])
            if role and role not in member.roles:
                await member.add_roles(role)
                await ctx.send(embed=discord.Embed(
                    title="🌸 슬이봇 후원 역할 부여 🌸",
                    description=f"{member.mention}님에게 **{role.name}** 역할이 부여되었습니다!",
                    color=0x91d5ff
                ))
                break  # 최고 등급 하나만 부여

@bot.command(name="내후원")
async def my_donation(ctx):
    uid = str(ctx.author.id)
    amount = donations.get(uid, 0)
    embed = discord.Embed(
        title="🌸 슬이봇 내 후원 🌸",
        description=f"당신의 총 후원금: **{amount}원**",
        color=0x91d5ff
    )
    await ctx.send(embed=embed)

@bot.command(name="후원순위")
async def donation_rank(ctx):
    if not donations:
        embed = discord.Embed(
            title="🌸 슬이봇 후원 순위 🌸",
            description="아직 후원자가 없습니다 😢",
            color=0xff5555
        )
        await ctx.send(embed=embed)
        return

    sorted_donors = sorted(donations.items(), key=lambda x: x[1], reverse=True)
    ranking = "\n".join(
        [f"**{i+1}위** <@{uid}> - **{amount}원**" for i, (uid, amount) in enumerate(sorted_donors[:10])]
    )
    embed = discord.Embed(title="🌸 슬이봇 후원 순위 🌸", description=ranking, color=0x91d5ff)
    await ctx.send(embed=embed)

@bot.command(name="후원안내")
async def donation_info(ctx):
    embed = discord.Embed(
        title="🌸 슬이봇 후원 안내 🌸",
        description=(
            "슬이봇을 후원해 주셔서 감사합니다!\n\n"
            "💳 후원 방법\n"
            " - 카카오페이, 토스, 계좌이체 등\n"
            " - 후원 후 관리자가 `!후원추가 @닉네임 금액` 명령어로 기록\n\n"
            "✨ 후원금 누적 확인: `!내후원`, 순위 확인: `!후원순위`\n\n"
            "항상 윤슬 서버와 슬이봇을 응원해 주셔서 감사합니다! 💖"
        ),
        color=0xffc0cb
    )
    embed.set_footer(text="🌸 슬이봇")
    await ctx.send(embed=embed)

@bot.command(name="개발자종료")
@is_developer()
async def dev_shutdown(ctx):
    embed = discord.Embed(title="⚠️ 봇 종료", description="봇을 종료합니다.", color=0xff5555)
    await ctx.send(embed=embed)
    await bot.close()

@bot.command(name="데이터초기화")
@is_developer()
async def dev_reset_data(ctx):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)
    donations.clear()
    embed = discord.Embed(
        title="⚠️ 데이터 초기화",
        description="후원 데이터가 초기화되었습니다.",
        color=0xff5555
    )
    await ctx.send(embed=embed)

@bot.command(name="디버그")
@is_developer()
async def dev_debug(ctx):
    embed = discord.Embed(
        title="🐞 디버그 정보",
        description=f"후원자 수: {len(donations)}",
        color=0xffff00
    )
    await ctx.send(embed=embed)

@bot.command(name="도움말")
async def help_command(ctx):
    embed = discord.Embed(
        title="🌸 슬이봇 명령어 도움말 🌸",
        description="주요 명령어와 사용 방법입니다.",
        color=0x91d5ff
    )

    embed.add_field(
        name="!후원추가 @닉네임 금액",
        value="관리자가 멤버에게 후원을 추가합니다. (관리자 전용)",
        inline=False
    )
    embed.add_field(name="!후원순위", value="서버 후원 상위 10명을 확인합니다.", inline=False)
    embed.add_field(name="!후원안내", value="후원 방법과 안내 메시지를 확인합니다.", inline=False)
    embed.add_field(name="!내후원", value="자신이 누적한 후원금을 확인합니다.", inline=False)

    embed.set_footer(text="🌸 슬이봇")
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ 슬이봇 로그인됨: {bot.user}")
    print("사용 가능한 명령어: !후원추가, !내후원, !후원순위, !후원안내, !도움말")
    print("개발자 전용: !개발자종료, !데이터초기화, !디버그")

bot.run(TOKEN)
