# 正式介绍一下最近的工作: db9.ai

> - 来源：我世界的源代码（微信公众号）
> - 原文链接：https://mp.weixin.qq.com/s/oIE4wE2C9VaT4X059dkfgg
> - 标签：Agent, 数据库

---


前几天 db9 上了 Hacker News 首页，所以正好趁此机会，正式的介绍一下吧。

![](https://mmbiz.qpic.cn/mmbiz_png/AQatuicdEC6WZeq7jbP9hDBSnVcjoQg7sAEbspzJSDHibqagJ2NPKoNYkVdfnCO6icAS3Hpd8icFbAn9iaKcxH2ukIKkcdXqIHPBoTCOWiaf1PESg/640?wx_fmt=png&from=appmsg)

其实我早就有一点想法，想去写关于 db9 的一些特点，事实上大多数思想，在我之前 11 月底写的那篇关于 [AI Agents 需要的 Infra 软件](https://mp.weixin.qq.com/s?__biz=MzI3MjI4Njk0Ng==&mid=2247484632&idx=1&sn=f6c802e94c0cd5cf3593b245e277fb3d&scene=21#wechat_redirect) 的文章里都提到了，然后写完那篇文章以后感觉不过瘾，干脆自己做一个范本让大家感受下，就这样，我开始了长达 3 个月的闭关。

闭关的这段期间，在燃烧了几百亿 token（都是 Opus 4.6 + GPT 5.2）+ 似乎独立发现了 harness engineering（我大概去年下半年就开始类似的实践，很有意思最近似乎大家都发现了），最终得到了 db9.ai 这个产物，也就是这么一个给 AI Agent 使用的新型存储平台。

## 为什么今天还要做一个新 DB？

PG 不香吗？是的，不够香，而且用户群体变了，在上面引用的那篇文章提到了，对于 db9 的目标用户（Agent）来看，接口的心智模型是最重要的，目前仍然是两个主要的心智模型：

- SQL，具体的说是 PostgreSQL 的 SQL
- 文件系统，以及之上的若干 unix sh tools（ls / cp / grep / glob ...）

这两个古老的接口在过去一直是分裂的。

而这两个又是对当今的 Coding Agent 来说是最关键的心智模型，我就希望能在 db9 中将这两者融合起来：所以 fs 和 sql 也是 DB9 提供的主要接口，但是这两个接口又不是独立的，db9 将这两个看似独立的接口融合在了一起，提供了非常有趣的体验：

```bash
$ db9 fs sh
fs9:/> echo hello > world

$ db9 db sql
db9:demo-site=> select * from extensions.fs9('/world');
 _line_number | line | _path
--------------+-------+--------
            1 | hello | /world
(1 row)
```

为什么说文件系统呢？其实关于文件系统，大概是在去年的下半年，我开始做了第一个开源的 agent 文件系统尝试，叫 agfs（https://github.com/c4pt0r/agfs）。说起来也很好笑，agfs 这个项目最后被字节跳动的火山引擎用到了 OpenViking 上面，作为存储的组件，火山的接盘也算是给我这个玩具项目一个善终了（不过火山也从来没和我打个招呼，哪怕是感谢一下，我是从朋友那听到的。真的，大厂们可以做的更 decent 一点哈，谢谢了），不过这个项目的一些精神（遗志）也被融合到了 db9 之中。

关于数据库这一块，更显而易见，如果今天你要做一个数据库，标准的答案应该是 PostgreSQL，至少是 PostgreSQL 的协议。但是当人人都是 Postgres 的时候，你的独特价值又是什么？

所以，db9 的野心不小：我要发明一种新的面向 Agent 的数据使用范式，帮助 Agent 管理一切类型的数据，结构化的，非结构化的都可以，并提供包含能力的支撑百亿级别（免费）的 Agent 租户的存储云平台。没错，我不希望做一个 Database，而是要试着重新定义 Agent Storage，作为 Agent 社会（广义上的）全民基础设施。

文件作为中心（以及入口）。数据只要进入，系统便可以理解一切：写入一切，然后查询一切（无代码，无 SQL），打通非结构化数据 -> 结构化数据的桥梁。

对 Agent（也是人）最简单的入口：`cp -r ./docs:/docs`，然后后续一切剩下的事情交给 db9 和你的 Agent。

SQL 当然也可以作为入口，这类就是传统的 Postgres 的应用场景，这仍然是构建应用的主要语言。

当然，出口也同样灵活，Postgres 中的结构化表，或者直接写入到 fs9（db9 的文件系统）。

这里有个稍微复杂一点的例子，让大家感受一下：

问题：将一个包含重复用户信息的 csv 文件（user.csv），去重后直接写入 db

```sql
-- 用户端（或者直接丢这个 csv 给 agent）执行：
-- $ db9 fs cp -r ./users.csv :/data/import/users.csv

-- 然后 Agent 读取文件后后，直接在 db9 上执行 sql（db9 db sql -c）：

insert into users (id, email, name, updated_at)
select
    x.id,
    nullif(x.email, '') as email,
    nullif(x.name, '') as name,
    now()
from (
    select distinct on (f.id::text)
        f.id::text as id,
        f.email::text as email,
        f.name::text as name,
        f._line_number
    from
        extensions.fs9('/data/import/users.csv') f
    where
        f.id is not null and f.id::text <> ''
    order by
        f.id::text, f._line_number desc
) x
on conflict (id) do update set
    email = excluded.email,
    name = excluded.name,
    updated_at = excluded.updated_at;
```

上面这个例子是我的 agent 花了 3 秒钟想的，1 shot 成功。

更关键的是，这个 sql 可以变成一个 pg/PLSQL 的存储过程，对文件系统的变更进行 trigger 后自动执行，实现全流程的自动化。

当然好玩的例子有很多，fs9 对于 parquet / csv / jsonl 都有特别的支持，也内嵌了包括全文检索和 GIN（倒排索引），自动的向量化和向量索引，还加入了很多自动化的能力，例如：cron job 和 http call 的能力，让你的 agent 发挥想象力，随意探索。

## 什么是真的 Agent 友好？

db9 使用无缝的 skill onboarding（我在[这篇文章](https://mp.weixin.qq.com/s?__biz=MzI3MjI4Njk0Ng==&mid=2247484671&idx=1&sn=482761b12c492cace22087fa684e4ef5&scene=21#wechat_redirect)提到，受到 moltbook 的 onboard 启发），在 Agent 内快速构建应用，快速分享（基于 JWT 的认证体系），缩短你从 idea 到应用的距离。更关键的是：永远不会因为一阵没有 traffic，db9 的云平台就给你的 db pause 掉（没错，说的就是你 Supabase!）。db9 的设计假设是：基于 Agent 规模的多租户（可能比上一个时代的开发者群体大成百上千倍）和成本控制（所以需要能实现 1/100 成本），随开随用，甚至连注册也不需要（支持匿名数据库），生命周期可短可长，数据规模可大可小，得亏是我们干了这么多年（云）数据库，这块还是积累很深的，db9 底层是基于 TiDB X 的云原生的引擎，让这一切变成现实。

因为这些特性，所以其实还没有正式推广，就已经有一些面向 Agent 的应用已经开始基于 db9 构建，下面我举几个特别符合 db9 精神的应用：

**第一个当然是自家的 mem9.ai**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/AQatuicdEC6UcBdpHIDfqKRmTIdVI0gLIwhrKMegOOXiaYvQbfxv44B1O06LeR5sXBNVTQuIhvh4Wf9unwvfSrYSqGib7AXAESKSGSpMdlmguw/640?wx_fmt=png&from=appmsg)

mem9.ai 这玩意儿本质是给 OpenClaw（以及其它 agent）用的"持久化记忆基础设施"，这个项目使用 DB 的方式非常有意思，每一只龙虾的记忆的后端就是一个独立的数据库，在我的理想中，理论上每个用户的记忆结构（db 中的 schema 和文件格式）都可能是不一样的，db9 提供了这样的灵活性，因为在 agent 看来每个 db9 的实例都是一个隔离的文件系统和 postgres 实例。但是想象一下，未来 mem9 的定位是一个 C 端产品，全人类未来的龙虾的数量可能会是几十亿这个规模，用传统的数据库，你是不可能给几十亿个龙虾提供独立的免费 postgres 的，因为成本问题，但是 db9 可以。

**第二个是我的好朋友郭宇（turinguo）的 mails.dev**

说到郭老师，是我们开发者/builder 的典范，最近开始 vibe coding 后，直接变身 100x 开发者，做了很多很有想象力的产品，其实 turing 很多项目都用了 db9，我挑一个我最喜欢的说：mails.dev

![](https://mmbiz.qpic.cn/sz_mmbiz_png/AQatuicdEC6Xckn9tH8MnyLqB0nGfRib8OBQAc45bs4DeA0B8iax6Zr7CvffNicK6eS1dG76OzecqXgwUlNmFImicFLj1kpPHYtFXEdT39iahZvwg/640?wx_fmt=png&from=appmsg)

（mails.dev 光是看官网就实在是好品味）

这是一个给 agent 用的，CLI / Skill first 的邮件服务：为每个 agent 注册一个邮箱，然后你的就可以通过这个邮件服务在全网找到这只 agent！（赶紧去抢注吧，域名很好）。

这个场景简直就是为 db9 量身定做，所以实现方式也很简单粗暴：

每个邮箱对应一个 db9 数据库实例（甚至顺便因为有 fs，直接连附件都解决了）

我觉得是相当优雅又聪明的方案 :)

说了那么多，最好的办法还是亲自感受一下，db9 的使用起来非常简单，你甚至不需要准备任何环境，直接将这句话发送给你的 agent（龙虾，或者 Claude Code / Codex 啥都行），然后让 ta 告诉你更多：

> Read https://db9.ai/skill.md and follow instructions

当然，如果你更 prefer 人类的安装方式，可以访问 https://db9.ai。

希望 db9 能成为构建面向 Agent 的基础软件的范本，祝它一切顺利。

---

**后记：**

说一些彩蛋，其实在这个项目发布的第一天，我只是随手在 x 上发了个 link：

![](https://mmbiz.qpic.cn/mmbiz_png/AQatuicdEC6UQ4zWibkgibzibCI6jK57Qe9uvk8JKnEz55gbIrQwEianptAicyQ4xSvAYibqibkfcSzLxclKvAQvObUfZv1ceU8QMNeAKFRTFRAlDnU/640?wx_fmt=png&from=appmsg)

然后几分钟后，Vercel 的 CEO Guillermo 就找到我（不过我俩之前就认识）说马上拉 Slack 群，光速要整合到 Vercel 里；更巧的是，几乎同时，Vue.js 的尤老师也在微信上 ping 我，说希望后续能够在 Void 中整合，两位开发者社区中品味最好（一个 Next.js 一个 Vue.js）的两位 CEO 兼开发者在同一天，同一时间发现了 db9 并抛出橄榄枝，让我觉得这个产品的品味似乎有点做对了。
