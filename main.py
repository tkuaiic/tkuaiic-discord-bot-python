import interactions, os
import firebase_admin
from firebase_admin import credentials, firestore

# These are basic inits for discord bot to function corrrectly
bot = interactions.Client(
    token = os.getenv("DISCORD_TOKEN"),
    default_scope = os.getenv("DISCORD_SCOPE"),
)
# These are basic inits for firestore
cred = credentials.Certificate("credentials.json") # <-Not for public
firebase_admin.initialize_app(cred)
db = firestore.client()
#------------------------Helper Functions------------------------
def check_df(collection, name):
    doc_ref = db.collection(collection).document(name)
    return doc_ref
#----------------------Main Code Starts Here----------------------
name = interactions.TextInput(
    style=interactions.TextStyleType.SHORT,
    label="姓名：",
    custom_id="name_input"
)
studentid = interactions.TextInput(
    style=interactions.TextStyleType.SHORT,
    label="學號：",
    custom_id="studentid_input",
    min_length=6,
    max_length=9,
)

@bot.command(
    name="verify",
    description="自助領取社員身分組",
)
async def verify(ctx):
    modal = interactions.Modal(
        title="社員身分組自助認證",
        custom_id="verify_modal",
        components=[name, studentid]
    )

    await ctx.popup(modal)

@bot.modal("verify_modal")
async def modal_response(ctx, name: str, studentid: int):
    doc_ref = check_df(u"1111-member", name)
    entry = doc_ref.get()
    # Authentication logic(check if name and student ID matches the record in database)
    if entry.exists and entry.to_dict()['student_id'] == studentid:
        # Add the user's discord account name into the database
        doc_ref.update({
            u'discord_account': f'{ctx.author.username}#{ctx.author.discriminator}'
        })
        # Gets role ID
        roles, = interactions.search_iterable(ctx.guild.roles, name='第2屆社員 2nd Gen. Club Member')
        # Add role to user
        await ctx.author.add_role(roles.id)
        # Confirm
        await ctx.channel.send(f"{name}您好，已將您加入`第2屆社員 2nd Gen. Club Member`身分組！", ephemeral=True)
    else:
        # In case cadre needs to add member role
        doc_ref = check_df(u"1111-cadre", name)
        entry = doc_ref.get()
        if entry.exists and entry.to_dict()['student_id'] == studentid:
            # Add the user's discord account name into the database
            doc_ref.update({
                u'discord_account': f'{ctx.author.username}#{ctx.author.discriminator}'
            })
            await ctx.send(f"已將您的Discord帳號登入至資料庫，謝謝！", ephemeral=True)
            return
        await ctx.send(f"驗證有誤，請確認姓名及學號是否正確。如有疑問，請透過<#1024724411074498591>頻道反應問題，謝謝！", ephemeral=True)

bot.start()