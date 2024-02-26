---
title: 更新 my_chat_member 和 chat_member
description: 更新 my_chat_member 和 chat_member
---

# 特别更新 {: id="special-updates" }

!!! info ""

    使用的 aiogram 版本： 3.1.1

## 导言 {: id="intro" }

Telegram 中几乎所有类型的事件都为用户提供了某种外部表现形式。服务消息、常规消息、回调、内联模式.....。但有两种类型的更新是针对机器人本身的。我们将讨论 `my_chat_member` 和 `chat_member` 。

曾几何时，群组中的机器人存在于 `信息真空` 中：必须通过 [getChatMember](https://core.telegram.org/bots/api#getchatadministrators) 或 [getChatAdministrators](https://core.telegram.org/bots/api#getchatadministrators) 方法检查调用用户的权限，查看是否有任何版主行为，无论是禁止还是限制，并将其缓存一小段时间，以免触及机器人 API 的限制，而这些限制的具体数值至今仍是个谜。

例如，某个狡猾的用户将一个机器人添加到一个群组中，取消了它的写入权，然后开始拉取命令，希望机器人不会处理这样的错误并崩溃。发送私信也很有趣：由于不知道机器人的活跃用户是哪些，开发者不得不向数据库中的用户列表发送一些信息，或者更人性化地向这些用户发送一些 ChatAction，比如 "键入......"；结果是，那些屏蔽了机器人的用户不会收到 "键入......"，机器人 API 会返回一个错误。

2021 年 3 月，随着 [Bot API v5.1](https://core.telegram.org/bots/api-changelog#march-9-2021) 更新的发布，情况发生了巨大的变化，其中添加了两种新的更新类型： `my_chat_member` 和 `chat_member` 。这两种更新在内部都包含一个相同类型的 [ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated) 对象。这两个事件的区别如下：

* `my_chat_member`. 这里是与机器人或用户与机器人的 PM 直接相关的所有内容：用户在 PM 中（取消）阻止机器人、将机器人添加到群组或频道、将其从群组或频道中删除、更改机器人在不同聊天中的权限和状态等。
* `chat_member`. 包含机器人作为管理员的群组和频道中用户状态的所有更改：用户加入/离开群组、订阅/取消订阅频道、更改用户权限和状态、分配/删除管理员等。

!!! warning "重要"

    默认情况下，Telegram 不会向机器人发送更新 `chat_member` ，必须单独启用机器人接收功能。更多详情，请参阅[相应章节](#chat-member)

在本章中，我们将尝试回顾这些更新中最常用的任务，但我强烈建议在阅读下一节之前先阅读 **aiogram 3.x** 文档中的[这一页](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html) 。

## ChatMemberUpdated 对象 {: id="chatmemberupdated" }

[ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated) 对象本身值得特别关注。为了更仔细地研究它，我们假设在某个群组中，管理员 Alisa 禁止了一名普通成员 Vitya。 `chat` 和 `date` 字段是显而易见的，我们跳过它们。

字段 `from` （在 Python 代码中为 `from_user` ）包含操作对象的信息。在我们的例子中，操作的主体是 Alice，因此在 `from` ( `from_user` ) 中会有一个 [User](https://core.telegram.org/bots/api#user) 对象，其中包含有关 Alice 的数据。

`old_chat_member` 和 `new_chat_member` 。在这些字段下，是操作对象在事件发生之前和之后的 `状态`。因此，在 `old_chat_member` 中，将出现一个 [ChatMemberMember](https://core.telegram.org/bots/api#chatmembermember) 类型的对象（这不是一个错别字），字段 `user` 包含有关 Vita 的信息，而在 `new_chat_member` 中，将出现一个 [ChatMemberBanned](https://core.telegram.org/bots/api#chatmemberbanned) 对象，字段 `user` 包含有关同样不幸的 Victor 的信息。

最后，如果有条件的 Masha 加入了群组或频道，则 ChatMemberUpdated 对象将有一个非空字段 `invite_link` ，其类型为 [ChatInviteLink](https://core.telegram.org/bots/api#chatinvitelink)，并包含她来自哪个邀请链接的信息。

!!! warning "关于邀请链接"

    在此我们需要说明一点：每个群组/频道管理员（包括机器人）都可以创建许多参数不同的邀请链接。如果一个机器人 `捕捉` 到一个参与者通过同一个机器人创建的链接加入，那么整个链接将在 ChatInviteLink 对象的 `invite_link` 字段中可见（当然不包括 `https://t.me` ）。但如果参与者来自另一个管理员的链接，机器人只能看到第一部分，第二部分将被虚线代替。
    
    这样做很可能是为了防止机器人向任何人发送其他聊天管理员创建的邀请链接。

    顺便说一下，根据某种奇怪的电报逻辑，如果您通过邀请链接（甚至不是通过用户名）加入一个公共群组，机器人不会看到该链接（得到 `None` ）。购物车 🤷‍♂️

## my_chat_member 更新 {: id="my-chat-member" }

### 禁止/解除 在PM中 {: id="ban-unban-pm" }

在个人资料聊天中，经常会出现这样的问题："如果有人可能已经屏蔽了机器人，如何让机器人向用户发送邮件？当然，最首要的建议是："创建一个[频道](https://telegram.org/faq_channels)"，因为频道是通知用户任何事情的最佳途径。

但是，如果你仍然决定直接通过机器人向用户发送邮件，那么有三种主要方法可以更新机器人的现有用户：

1. 直接在邮件过程中捕获发送错误并对用户数据库进行更改。
2. 通过定期发送一些 [ChatAction](https://core.telegram.org/bots/api#sendchataction)，例如在用户列表上 "打印"。
3. 监听 my_chat_member 的更新。

现在，我们只对第 3 点感兴趣。 让我们学习使用 `my_chat_member` 来判断用户是否阻止了机器人。不过，在尝试 aiogram 的 `魔法` 之前，我们先来看看 Bot API 本身是如何处理这些情况的。为此，我们先停止与机器人的对话，在 Telegram 中打开对话，然后使用信使用户界面中的选项依次阻止和解除阻止。然后，打开网页浏览器或 Insomnia/Postman，点击 `https://api.telegram.org/bot<TOKEN>/getupdates` 链接，查看 JSON 格式的未处理消息。

因此，当有人阻止机器人时，机器人会出现以下情况：

![Пользователь заблокировал бота](images/special-updates/my_chat_member-blocked.png)

需要注意的事项

* 事件 `my_chat_member` 发生在与用户 Groosha（chat_id 等于我的 Telegram ID）的 PM 中。
* 事件的发起人（主体）也是格罗沙。
* 在 `old_chat_member` 字段中，您可以看到对谁执行了操作（机器人），以及机器人在 PM 之前的状态：`member`，即该机器人之前未被阻止。
* 在 `new_chat_member` 字段中， `user` 的内容是一样的，但状态已经是 `kicked`，即在机器人被用户阻止之后。

也就是说，在与格罗沙的 PM 中的机器人已经完成了从 `member` 到 `kicked` 的状态转换。现在让我们来看看 Telegram 在解封后发送了什么信息：

![Пользователь разблокировал бота](images/special-updates/my_chat_member-unblocked.png)

这张截图与上一张截图相似，但如果你仔细观察，就会发现其中的不同之处： update_id 不同（增加了一个），而且 "之前" 和 "之后" 的状态也发生了变化。与格罗沙的 PM 中的机器人已经从 `kicked` 转变为 `member`。

此外，通常还会有另一次更新，内容中会包含 `message` 类型和 `/start` 命令。官方客户端在解锁机器人时会立即发送 `/start` 命令，但不要依赖于此：此类操作由客户端自行决定，它们的行为可能会有所不同。

现在，让我们通过一个简单的例子来学习如何通过 aiogram 对此类事件做出反应：我们有两个活跃的僵尸用户列表，id 分别为 111 和 222。使用 `/start` 命令，我们将把该用户添加到邮件列表中；使用 `/users`  命令，我们将显示未阻止该机器人的用户 ID（换句话说，当该机器人被阻止时，我们将从列表中删除其 ID，当其被解除阻止时，我们将再次添加其 ID）。

这里有一个满足上述条件的现成路由器：

```python title="handlers/in_pm.py"
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.filters.command import \
    CommandStart, Command
from aiogram.types import ChatMemberUpdated, Message

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")

# Исключительно для примера!
# В реальной жизни используйте более надёжные
# источники айди юзеров
users = {111, 222}


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    users.discard(event.from_user.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated):
    users.add(event.from_user.id)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello")
    users.add(message.from_user.id)


@router.message(Command("users"))
async def cmd_users(message: Message):
    await message.answer("\n".join(f"• {user_id}" for user_id in users))

```

注意：对于 `my_chat_member` 更新的处理程序，我们使用 `ChatMemberUpdatedFilter` 过滤器指定在更新后要捕获的结果（即更新的 `new_chat_member` 属性）。也就是说，在这种情况下，我们对用户之前的状态不感兴趣。

下面是实际操作的情况：

![type:video](images/special-updates/my_chat_member_video.mp4)

### 机器人添加到群组 {: id="bot-added-to-group" }

新手开发者经常提出的另一个问题是 "如何捕捉将机器人添加到群组的事件？" 好吧，让我们一探究竟。但在此之前，我们先来看看用户的 [状态](https://core.telegram.org/bots/api#chatmember) 可以是什么：

* 创建者（又称所有者）--聊天的所有者。显然，机器人不能拥有这种身份。除了 `匿名` 之外，所有者在聊天中拥有所有可能的权利，可以自由来回切换。
* 管理员 - 任何其他管理员。在应用程序界面中，您可以删除所有权限，但他仍然是管理员，例如，可以读取最近操作和忽略慢速模式。
* 具有默认权限的聊天成员。您可以通过调用 API 方法 [getChat](https://core.telegram.org/bots/api#getchat) 并查看 `permissions` 字段，了解群组的 "默认权限"。
* restricted - 限制某些权限的用户。例如，处于所谓 "只读" 状态的用户。**重要：**在 `restricted` 状态下，用户可能在某个群组中，也可能不在某个群组中，因此应额外检查 ChatMemberRestricted 标志 `is_member` 。
* left - "他飞走了，但答应会回来" ，即用户已离开小组，但如果他愿意，可以回来。而且他离开时并不处于 `restricted` 状态。
* banned - 用户被禁言，在[解禁](https://core.telegram.org/bots/api#unbanchatmember)前不能自行返回。

有了上述信息，我们就不难猜出 `机器人被添加到一个组` 事件是从 `{banned, left, restricted(is_member=False)}` 状态集到 `{restricted(is_member=True), member, administrator}` 状态集的过渡。这种过渡在英语中称为 `transition`，而 aiogram 3.x 已经为它提供了空白。

方案 1：让我们愚蠢地列出所有的 `前` 和 `后` 状态：

```python
# Не забываем импорты:
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, \
    RESTRICTED, ADMINISTRATOR, CREATOR

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | -RESTRICTED)
        >>
        (+RESTRICTED | MEMBER | ADMINISTRATOR | CREATOR)
    )
)
```

垂直破折号表示 `或`，位运算符 `>> `表示转换的方向，`RESTRICTED` 附近的加号和减号字符表示 `is_member` 标志（加号为 `True`，减号为 `False`）。

但是，aiogram 的开发者更进一步，将这两个集合分别封装为独立的状态 `IS_NOT_MEMBER` 和 `IS_MEMBER` 。让我们以变体 #2 的形式简化代码：

```python
# Немного другие импорты
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        IS_NOT_MEMBER >> IS_MEMBER
    )
)
```

但是，我再说一遍，这种过渡在机器人中使用得很频繁，因此开发人员更进一步，将这种过渡包装成变量 `JOIN_TRANSITION` 的形式，从而产生了变体 #3：

```python
# И ещё меньше импортов
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, JOIN_TRANSITION

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
```

我强烈建议您[阅读文档](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html)中的所有状态集和转换，以便使您的代码更加简洁。

现在，让我们创建另一个路由器，在路由器下将有两个处理程序，分别对将机器人添加到群组或超级群组中作为管理员和普通成员做出反应。添加机器人时，我们会向聊天发送一个摘要，说明机器人被添加到了哪里：

```python title="handlers/bot_in_group.py"
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

chats_variants = {
    "group": "группу",
    "supergroup": "супергруппу"
}


# 无法重现将机器人添加为受限机器人的情况、
# 这样就不会有他的榜样了


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    # 最简单的情况是：机器人被添加为管理员。
    # 我们可以轻松发送信息
    await event.answer(
        text=f"嗨！感谢您将我添加到"
             f'{chats_variants[event.chat.type]} "{event.chat.title}" '
             f"作为管理员。聊天 ID：{event.chat.id}"
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated):
    # 更复杂的变体：机器人作为普通参与者加入。
    # 但可能没有写帖子的权利，所以会提前检查。
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f"你好！感谢您将我添加到 "
                 f'{chats_variants[event.chat.type]} "{event.chat.title}" '
                 f"作为常规参与者。聊天ID：{event.chat.id}"
        )
    else:
        print("我们可以通过某种方式来理解这种情况")
```

但是，和往常一样，这其中也有细微的差别，要了解这一点，你需要将一个机器人添加到群组中，然后将其转换为超级群组。为了说明这一点，我用我的机器人 @my_id_bot 创建了一个群组，然后用上述代码在其中添加了一个测试机器人。请注意图片：

![конвертация группы в супергруппу](images/special-updates/group_supergroup.png)

哎呀，不知道为什么，机器人的反应就像刚刚添加了一个群组，尽管看起来什么都没变。事实上，在机器人看来，将群组转换为超级群组就像是将它添加到了一个新的聊天室。幸运的是，在这种情况下，机器人也会收到一条包含非空字段 `migrate_from_chat_id` 和 `migrate_to_chat_id` 的消息。然后就很简单了：当触发 `my_chat_member` 事件以将其添加到超级群组时，检查最近（例如几秒钟内）是否有包含非空 `migrate_to_chat_id` 字段的消息。

解决方案与上述示例几乎完全相同，而且在我的 @my_id_bot 中也是这样实现的：（欢迎在 github 上打星号）

!!! info "普通群组和超级群组"

    与常见的误解相反，常规群组仍然存在，不会消失。Telegram 官方客户端最初会创建一个普通群组，当某些事件发生时，该群组会隐式地转换为超级群组。人们强烈怀疑这种行为在未来几年内不会改变，尤其是考虑到普通（非付费）账户受总共 500 个超级群组和频道的限制。

    除了更改聊天 ID 外，转换还会有一些副作用，因此通常在创建群组后将其转换为超级群组会更容易，得到最终 ID 后就不用担心了。将群组转换为超级群组的全部操作列表可在此处查看：[https://t.me/tgbeta/3424](https://t.me/tgbeta/3424).


## chat_member 更新 {: id="chat-member" }

下一种特殊类型的更新 `chat_member` 比较棘手。Telegram 默认不发送此类更新，要让 Bot API 发送此类更新，您需要在调用 **getUpdates** 或 **setWebhook** 时传递所需的事件类型列表。例如

```python
# тут импорты

async def main():
    # тут код
    dp = Dispatcher()
    bot = Bot("токен")
    await dp.start_polling(
        bot, 
        allowed_updates=["message", "inline_query", "chat_member"]
    )
```

运行机器人后，Telegram 服务器将开始发送指定的三种事件类型，但不会发送其他所有事件类型。

aiogram 开发人员以一种巧妙的方式解决了这一问题：如果不明确指定 `allowed_updates` ，框架将从派发器开始递归遍历所有路由器，查看处理程序，并自行编译所需的更新列表。想要覆盖这种行为？请明确传递 `allowed_updates` 。

!!! tip "为什么我没有收到 <XXX\> 更新？"

    人们经常在资料聊天中问："我的代码不起作用，对事件没有反应，为什么？"

    要做的第一件事就是确保机器人能够获得所需的更新。换句话说，检查上次调用了哪个 `allowed_updates` 轮询/webhooks。最简单的方法是直接在浏览器中进行检查：

    1. 以机器人令牌为例，我们称之为 AAAAAA。
    2. 生成形式为 `https://api.telegram.org/botAAAAA/getWebhookInfo` 的链接
    3. 点击链接，查看 `allowed_updates` 的值。

    接下来，仔细检查响应中的 JSON。如果存在 `allowed_updates` 键，请确保所需的更新类型在列表中。如果不存在该键，则相当于 "除 `chat_member` 以外的所有内容都将出现"。

### 更新群组中的管理员列表 {: id="actualizing-admins" }

版主机器人的一个常见问题是如何对调用的命令进行权限检查。例如，如何使只有群组管理员才能使用 /ban 命令禁止成员。

第一个简单的想法是每次都调用 getChatMember 来确定呼叫用户在群组中的状态。第二个想法是在短时间内缓存这些知识。第三个也是更正确的想法是，在机器人启动时获取管理员列表，然后监听 chat_member 关于管理员组成变化的更新，并自行编辑列表。机器人重新启动了？没问题，我们可以重新获得当前列表并使用它。

让我们编写一个路由器，跟踪管理员组成的变化，并更新外部传递的列表（更准确地说，用 python 术语就是 Set）：

```python title="handlers/admin_changes_in_group.py"
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, \
    RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR
from aiogram.types import ChatMemberUpdated

from config_reader import config

router = Router()
router.chat_member.filter(F.chat.id == config.main_chat_id)


@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        >>
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_promoted(event: ChatMemberUpdated, admins: set[int]):
    admins.add(event.new_chat_member.user.id)
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) повышен(а) до Администратора!"
    )


@router.chat_member(
    ChatMemberUpdatedFilter(
        # Обратите внимание на направление стрелок
        # Или можно было поменять местами объекты в скобках
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        <<
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_demoted(event: ChatMemberUpdated, admins: set[int]):
    admins.discard(event.new_chat_member.user.id)
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера!"
    )
```

现在，让我们为 `/ban` 命令编写另一个带有处理程序的路由器。在处理程序中，我们将检查调用者的 id 是否在 `admins` 集中，并据此允许或禁止禁令：

```python title="handlers/events_in_group.py"
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message

router = Router()

# Вообще говоря, можно на роутер навесить кастомный фильтр
# с проверкой, лежит ли айди вызывающего во множестве admins.
# Тогда все хэндлеры в роутере автоматически будут вызываться
# только для людей из admins, это сократит код и избавит от лишнего if
# Но для примера сделаем через if-else, чтобы было нагляднее


@router.message(Command("ban"), F.reply_to_message)
async def cmd_ban(message: Message, admins: set[int]):
    if message.from_user.id not in admins:
        await message.answer(
            "У вас недостаточно прав для совершения этого действия"
        )
    else:
        await message.chat.ban(
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer("Нарушитель заблокирован")
```

剩下的工作就是在主文件中注册路由器，并在启动时加载管理员列表。实际上，这里就是全部内容，以及之前的所有编辑。

```python title="bot.py"
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from handlers import in_pm, bot_in_group, admin_changes_in_group, events_in_group


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher()
    bot = Bot(config.bot_token.get_secret_value(), parse_mode="HTML")
    dp.include_routers(
        in_pm.router, events_in_group.router,
        bot_in_group.router, admin_changes_in_group.router
    )

    # Подгрузка списка админов
    admins = await bot.get_chat_administrators(config.main_chat_id)
    admin_ids = {admin.user.id for admin in admins}

    await dp.start_polling(bot, admins=admin_ids)


if __name__ == '__main__':
    asyncio.run(main())
```

现在让我们看看最终结果如何。让我们尝试由非管理员调用 /ban 命令：

![У пользователя не хватает прав](images/special-updates/ban_insufficient_rights.png)

进入群组设置，指定亚瑟为管理员（机器人会看到更改并在聊天中报告）：

![Теперь прав достаточно](images/special-updates/ban_ok.png)

让我们撤销测试病人的管理员权限，并要求他再次调用 /ban 命令：

![Прав снова не хватает](images/special-updates/ban_insufficient_again.png)

现在你知道如何使用这些 "隐形" 更新了吧，好极了！最后，我推荐你阅读另一个演示机器人，其中使用了上述的一些技巧。
