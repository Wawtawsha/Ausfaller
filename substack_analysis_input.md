# Substack Analysis Input
Generated: 2026-01-15T01:16:49.517608
Source: substack_posts_20260115_011643.json
Total posts available: 152
Posts included: 100


# Substack Content Analysis - Data Engineering Niche

You are analyzing newsletter posts from data engineering Substack publications. Analyze each post and provide structured insights.

## Analysis Framework

For each post, evaluate:

### 1. Content Classification
- **content_type**: tutorial | opinion | news | case_study | career_advice | tool_review | architecture_deep_dive | interview
- **skill_level**: beginner | intermediate | advanced | all_levels
- **estimated_read_time**: minutes (based on content length)

### 2. Technical Relevance (Data Engineering)
- **microsoft_stack**: true/false - Does it cover Microsoft Fabric, Azure Data Factory, Power BI, Synapse, etc.?
- **cloud_platform**: azure | aws | gcp | databricks | snowflake | multi_cloud | agnostic
- **data_layer**: ingestion | transformation | storage | orchestration | visualization | governance | multiple
- **tools_mentioned**: List specific tools (dbt, Airflow, Spark, Fabric, etc.)
- **architecture_patterns**: List patterns discussed (medallion, data mesh, lakehouse, etc.)

### 3. Educational Quality
- **explanation_clarity**: 1-10 (How well does it explain concepts?)
- **practical_applicability**: 1-10 (Can readers apply this immediately?)
- **code_examples**: true/false (Does it include code?)
- **diagrams_visuals**: true/false (Does it include architecture diagrams?)

### 4. Engagement Signals
- **headline_strength**: 1-10 (Is the title compelling?)
- **hook_quality**: 1-10 (Does the intro pull you in?)
- **actionable_takeaways**: List 1-3 key takeaways

### 5. Brand Safety & Sponsorship Fit
- **brand_safety_score**: 1-10 (Suitable for professional/enterprise audiences?)
- **sponsorship_categories**: List fitting sponsor types (cloud_vendors, data_tools, training_platforms, etc.)
- **tone**: professional | casual | academic | provocative

## Output Format

Return JSON array with analysis for each post:

```json
[
  {
    "post_id": "<url or index>",
    "title": "<post title>",
    "publication": "<substack name>",
    "analysis": {
      "content_type": "tutorial",
      "skill_level": "intermediate",
      "estimated_read_time": 8,
      "microsoft_stack": true,
      "cloud_platform": "azure",
      "data_layer": ["transformation", "orchestration"],
      "tools_mentioned": ["Microsoft Fabric", "dbt", "Dataflow Gen2"],
      "architecture_patterns": ["medallion"],
      "explanation_clarity": 8,
      "practical_applicability": 7,
      "code_examples": true,
      "diagrams_visuals": true,
      "headline_strength": 7,
      "hook_quality": 6,
      "actionable_takeaways": [
        "Use Dataflow Gen2 for incremental loads",
        "Medallion architecture fits Fabric well"
      ],
      "brand_safety_score": 9,
      "sponsorship_categories": ["cloud_vendors", "data_tools"],
      "tone": "professional"
    },
    "summary": "<2-3 sentence summary of the post>"
  }
]
```

## Posts to Analyze




---
## Post 1: Data Engineering Weekly #252

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-252
**Published:** 2026-01-12T02:38:04+00:00

**Content Preview:**
Best practices for LLM development LLMs are transforming software development, but integrating them into real projects can be tricky when models don&#8217;t understand your codebase, pipelines, or conventions. Join Dagster on January 27th for a practical look at data engineering best practices, common pitfalls, and live demos of LLM developments. Reserve your spot now. Foundation Capital: AI&#8217;s trillion-dollar opportunity: Context graphs Agents are cross-system and action-oriented. The UX of work is separating from the underlying data plane. Agents become the interface, but something still has to be canonical underneath. This will be a core construct of the next evolution of data engineering. A scalable data infrastructure that gives a unified view of the system of records and the analytical data, past decision traces, and a system of record that accepts high concurrent modifications. The promise of agents holds, but I don&#8217;t think our underlying infrastructure is ready for it. https://foundationcapital.com/context-graphs-ais-trillion-dollar-opportunity/ ThoughtWorks: How to build the organizational muscle needed to scale AI beyond PoCs Thoughtworks argues that AI initiatives fail to scale beyond pilots because organizations hit compliance hurdles, data silos, and lack stakeholder engagement&#8212;problems that require building "organizational muscle" rather than buying technology solutions. The article recommends a "thin slice" approach that addresses five building blocks simultaneously for a single use case: starting with clear business outcomes instead of technology, building tech platforms incrementally based on concrete needs, creating repeatable MLOps paths to production through cross-functional product teams, and investing in AI literacy and human-collaborative tool design to drive sustained adoption. https://www.thoughtworks.com/insights/articles/how-to-build-organizational-muscle-needed-to-scale-AI Sharon Campbell-Crow: Multi-Agent Systems: The Ar...

**Embedded Videos:** 0


---
## Post 2: A Critique of Iceberg REST Catalog: A Classic Case of Why Semantic Spec Fails

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/a-critique-of-iceberg-rest-catalog
**Published:** 2026-01-09T05:57:38+00:00

**Content Preview:**
&#8220;Latency is not just a performance characteristic; it is a fundamental part of correctness.&#8221; &#8212; Designing Data-Intensive Applications In Designing Data-Intensive Applications , Martin Kleppmann makes a subtle but critical point: the CAP theorem omits latency, yet in real systems, latency often determines whether a system is usable at all. A system that is correct but slow is, in practice, incorrect. This observation is directly applicable to the Apache Iceberg REST Catalog specification . While the specification achieves semantic clarity, it fails to define the operational realities that enable distributed systems to remain predictable at scale. The result is a standard that is formally correct, yet operationally fragile. Semantic Interoperability Without Predictability Over the past two years, the Iceberg REST Catalog specification has emerged as the de facto standard for metadata access in the Iceberg ecosystem. We have seen the outburst of the catalog war around the REST spec. It promises a universal interface that allows engines such as Trino, Spark, Flink, and StarRocks to interact with Iceberg tables via a common REST abstraction, independent of the underlying catalog implementation. At the semantic level, this promise largely holds. The specification rigorously defines metadata structures: tables, schemas, snapshots, and namespace operations. A LoadTable or CreateNamespace request looks identical across implementations. This semantic interoperability has been critical to Iceberg&#8217;s rapid ecosystem adoption. However, semantic interoperability alone is insufficient. The specification defines what metadata operations mean, but it avoids specifying how they must behave in real-world conditions, such as concurrency, latency sensitivity, and cross-catalog synchronization. This gap&#8212;between semantic interoperability and operational interoperability&#8212;is where systems begin to fail in production. The Core Problem: No Operational SLA, No...

**Embedded Videos:** 0


---
## Post 3: Data Engineering Weekly #251

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-251
**Published:** 2026-01-05T05:35:51+00:00

**Content Preview:**
Best practices for LLM development LLMs are transforming software development, but integrating them into real projects can be tricky when models don&#8217;t understand your codebase, pipelines, or conventions. Join Dagster on January 27th for a practical look at data engineering best practices, common pitfalls, and live demos of LLM developments. Reserve your spot now. Editor&#8217;s Note: The Edition of Predictions!! Well, Mostly It is always exciting to read the predictions and look back on 2025. I put a lot of effort into collecting some of these predictions and bundling them in this edition. At DEW, we also reached a few existing milestones. We just published our 250th edition and reached 50,000 Substack followers. It is remarkable growth, considering how lazy I am on LinkedIn and how little I promote DEW. I&#8217;m looking to improve on it, and over the holidays, I tried a bit of Agent building on top of DEW, which I&#8217;m hoping to launch soon. I wish all the DEWers a prosperous 2025 and thank you for your continued support. Ananth Packkildurai: DEW - The Year in Review 2025 Why not start with our own year-in-review and a bit of predictions? Agent Engineering is undoubtedly becoming a discipline of its own in engineering, similar to the rise of data scientists. Both, funny enough, run into data inconsistency issues, and everyone does data engineering eventually. ( Hello Context Engineering ) I wrote a bit about how the catalog becomes the new database as the adoption of Apache Iceberg and Knowledge Engineering increases. I&#8217;ve a lot of concern about the Iceberg Rest Catalog, which I will write about as a separate blog this week. Stay tuned. https://www.dataengineeringweekly.com/p/dew-the-year-in-review-2025 Sebastian Raschka: The State Of LLMs 2025: Progress, Problems, and Predictions The State of LLMs 2025 examines how DeepSeek R1's breakthrough demonstrated that reasoning models can be trained for approximately $5 million using Reinforcement Learning ...

**Embedded Videos:** 0


---
## Post 4: Data Engineering Weekly #250

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-250
**Published:** 2025-12-29T05:16:03+00:00

**Content Preview:**
The Scaling Data Teams Guide Building and scaling a data platform has never been more important or more challenging. Whether you&#8217;re just starting to build a data platform or leading a mature data organization, this guide will help you scale your impact, accelerate your team, and prepare for the future of data-driven products. Learn how real data teams, from solo practitioners to enterprise-scale organizations, build. Get the guide now Thoughtworks: The Model Context Protocol&#8217;s impact on 2025 Thoughtworks writes about Model Context Protocol's (MCP) transformative impact on 2025 software development, highlighting its role in accelerating agentic AI adoption by simplifying connections between AI systems and external data sources .The blog identifies emerging techniques including context engineering for systematic LLM information optimization, AI-powered UI testing via Playwright-mcp and mcp-selenium servers, and anchoring coding agents to reference applications to prevent code drift, while cautioning against security vulnerabilities (tool poisoning, cross-server shadowing) and antipatterns like naive API-to-MCP conversion. https://www.thoughtworks.com/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025 Uber: Powering Billion-Scale Vector Search with OpenSearch Uber Engineering migrated from Apache Lucene&#8217;s HNSW to Amazon OpenSearch for billion-scale vector search, addressing algorithm inflexibility and GPU support limitations when handling 1.5 billion items with 400-dimension embeddings for personalized recommendations and fraud detection. The implementation reduced indexing time by 79% (from 12.5 hours to 2.5 hours) through Spark batch ingestion, optimized flush/merge policies, while achieving 52% lower P99 latency (250ms to 120ms at 2K QPS) via shard-to-node ratio tuning, replica scaling, in-memory KNN graph optimization, and blue/green deployments. https://www.uber.com/en-IN/blog/powering-billion-scale-vector-search-with-opensearch/ ...

**Embedded Videos:** 0


---
## Post 5: DEW - The Year in Review 2025

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/dew-the-year-in-review-2025
**Published:** 2025-12-22T22:43:22+00:00

**Content Preview:**
If 2023 was the year of &#8220;Shock&#8221; and 2024 was the year of &#8220;Hype,&#8221; 2025 will be remembered as the year of Engineering . For the past decade, our industry has been obsessed with the mechanics of movement. We argued about &#8220;ETL vs. ELT.&#8221; We fought &#8220;Format Wars&#8221; over table specifications. We optimized commit protocols and debated the merits of various orchestrators. We were, fundamentally, digital plumbers ensuring the water reached the tap. But in 2025, the mandate changed. The business no longer wants &#8220;data&#8221;; it demands &#8220;intelligence.&#8221; It demands systems that reason, agents that act, and infrastructure that guarantees truth in a non-deterministic world. The &#8220;Big Data&#8221; era of managing volume formally ended, replaced by the &#8220;Context Era&#8221; of managing meaning. We are no longer just Data Engineers. We are the architects of the cognitive layer. Here are the seven patterns that defined Data &amp; AI Engineering in 2025. 1. Agent Engineering: The Inevitable Evolution of the Pipeline The most significant shift of 2025 was the industry&#8217;s realization that &#8220;Agents&#8221; are not just fancy chatbots&#8212;they are the new compute engine. In 2024, we treated LLMs as text generators. In 2025, we started treating them as reasoning engines that execute logic we previously wrote in Python or SQL. This birthed a new discipline: Agent Engineering . We moved beyond the chaotic &#8220;vibes-based&#8221; coding of early experiments into structured, rigorous engineering. We stopped asking &#8220;Can AI write code?&#8221; and started asking &#8220;How do we architect a system where AI reliably executes complex workflows?&#8221; The Rise of Context Engineering The bottleneck for intelligent systems shifted from model capacity to context management . We realized that an agent is only as smart as the context you feed it. Anthropic defined the year with their masterclass on Effective Context ...

**Embedded Videos:** 0


---
## Post 6: Data Engineering Weekly #249

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-249
**Published:** 2025-12-22T03:37:18+00:00

**Content Preview:**
How to scale your data team Building and scaling a data platform has never been more important or more challenging. Whether you&#8217;re just starting to build a data platform or leading a mature data organization, this guide will help you scale your impact, accelerate your team, and prepare for the future of data-driven products. Learn how real data teams, from solo practitioners to enterprise-scale organizations, build. Get the guide now Andrej Karpathy: 2025 LLM Year in Review One year seems a decade in the LLM era. Gemini was still effectively at version 1.5, image models routinely failed at basic text rendering, and credible video generation had not yet arrived. DeepSeek R1 did not exist; o1 was only beginning to introduce test-time inference. The author highlights the significance of 2025 and the paradigm shift that altered the landscape. https://karpathy.bearblog.dev/year-in-review-2025/ LangChain: State of Agent Engineering LangChain has published a survey of 1300 professionals on Agent Engineering in the industry. Key highlights for me, Customer service and productivity products dominate the AI adoption. Quality of the output is the biggest barrier to entry for AI Agents. The open-source model has an equal market share between Gemini and Claude. https://www.langchain.com/state-of-agent-engineering Google: Introduction to AI Agents Just like a Data Scientist, Agent Engineering is becoming the hottest job in 2026. If you&#8217;re looking to get started in this space, Google publishes an excellent overview of an Introduction to AI Agents. https://drive.google.com/file/d/1C-HvqgxM7dj4G2kCQLnuMXi1fTpXRdpx/view Sponsored: The data platform playbook everyone's using We wrote an eBook on Data Platform Fundamentals to help you be like the happy data teams, operating undering a single platform. In this book, you&#8217;ll learn: - How composable architectures allow teams to ship faster - Why data quality matters and how you can catch issues before they reach users - W...

**Embedded Videos:** 0


---
## Post 7: Data Engineering Weekly #248

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-248
**Published:** 2025-12-15T02:00:13+00:00

**Content Preview:**
The Scaling Data Teams Guide The latest eBook in our popular series is now available. Building and scaling a data platform has never been more important or more challenging. Whether you&#8217;re just starting to build a data platform or leading a mature data organization, this guide will help you scale your impact, accelerate your team, and prepare for the future of data-driven products. Learn how real data teams, from solo practitioners to enterprise-scale organizations, build. Get the guide now Jason Gorman: The Gorman Paradox: Where Are All The AI-Generated Apps? I had this very conversation recently. A friend of mine claimed that it is now easy to build a CRM and that everyone will build their own, thereby making all SaaS companies obsolete in the near future. It&#8217;s cheaper to manufacture software now, but SaaS companies don&#8217;t win on manufacturing. They win on distribution, trust, and operational burden. Building a CRM, perhaps commodized; operating one as a durable product is not. https://codemanship.wordpress.com/2025/12/14/the-gorman-paradox-where-are-all-the-ai-generated-apps/ Gunnar Morling: You Gotta Push If You Wanna Pull Balancing between Query over Data (pull) at Rest and Query (push) over a Stream is often a challenging part of system design. The author points out that the balance is that push is an efficient way to keep the state fresh through incremental data processing, making pull more efficient. https://www.morling.dev/blog/you-gotta-push-if-you-wanna-pull/ LangChain: Agent Engineering - A New Discipline Data Scientist &#8594; Analytical Engineer &#8594; Agentic Engineer. As the technology landscape evolves, we see new roles emerging that require specific skill sets. The blog lays the foundation of the emerging agentic engineering discipline in software engineering. https://blog.langchain.com/agent-engineering-a-new-discipline/ Sponsored: The data platform playbook everyone&#8217;s using We wrote an eBook on Data Platform Fundamentals t...

**Embedded Videos:** 0


---
## Post 8: Data Engineering Weekly #247

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-247
**Published:** 2025-12-08T01:25:29+00:00

**Content Preview:**
How to build trustworthy AI analytics If your team is relying on AI-driven insights, this upcoming webinar will show you how to make those insights more dependable, transparent, and explainable. In this 12/9 Deep Dive with our friends at Cube, you&#8217;ll learn: - Why AI analytics fails without governance (and what that actually means) - How semantic layers provide the guardrails AI needs to be trustworthy - Technical implementation: how Compass + Cube work together to prevent hallucinations - Live demo: governed self-service analytics that data teams can actually trust Save your spot now DoorDash: Beyond Single Agents: How DoorDash is building a collaborative AI ecosystem DoorDash highlights the challenge of extracting reliable insights from fragmented knowledge systems and the limitations of single agents constrained by context, determinism, and long-horizon reasoning. The article details an evolutionary architecture that progresses from deterministic workflows to adaptive agents, hierarchical deep-agent systems with shared memory, and exploratory swarm-based A2A collaboration, all built on a unified platform featuring hybrid search, schema-aware SQL generation, multi-stage validation, and integrated guardrails. https://careersatdoordash.com/blog/beyond-single-agents-doordash-building-collaborative-ai-ecosystem/ LinkedIn: The evolution of the Venice ingestion pipeline LinkedIn writes about the challenge of scaling Venice ingestion to support massive bulk loads, hybrid Lambda-style stores, partial updates, and active/active replication while avoiding bottlenecks in producing, consuming, persisting, and compaction. The article details the end-to-end evolution of the ingestion pipeline, including partition scaling, shared consumer and writer pools, SST-based ingestion, RocksDB tuning with leveled compaction, BlobDB, Fast-Avro adoption, parallelized DCR processing, and adaptive throttling for deterministic latency. https://www.linkedin.com/blog/engineering/infrastruc...

**Embedded Videos:** 0


---
## Post 9: The Dark Data Tax: How Hoarding is Poisoning Your AI

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/the-dark-data-tax-how-hoarding-is
**Published:** 2025-11-19T06:33:14+00:00

**Content Preview:**
With the increased adoption of the Lakehouses, we removed the last constraint on data accumulation. We didn&#8217;t realize we were removing the last constraint on data obesity . The numbers are staggering. Enterprises now store 2.5 times more data than they did in 2019, yet the velocity of decisions derived from that data hasn&#8217;t just slowed&#8212;it has flatlined. According to IDC, global data storage capacity is estimated to reach 175 zettabytes by 2025, with 80% of that data unstructured. Furthermore, IDC predicts that 90% of unstructured data will remain unanalyzed . This is data obesity: the condition where an organization accumulates data faster than it can derive value from it. It&#8217;s not a storage problem. It&#8217;s a metabolic one. When Storage Became Infinite, Attention Became Finite The obesity crisis began with the Lakehouse. Built on the triumvirate of S3, ADLS, and GCS, and crowned with Delta Lake, Iceberg, and Hudi, the Lakehouse solved data engineering&#8217;s oldest constraint: where to put the data. Object storage made retention elastic and nearly free. The cost of a gigabyte has fallen by 80% over the past decade, while enterprise data volume has grown by 250%. However, the Lakehouse didn&#8217;t just lower costs&#8212;it removed the psychological barrier to data collection. When a terabyte costs less than a pizza, no one asks hard questions before ingesting. When schema evolution is automatic, there&#8217;s no migration friction to discourage table sprawl. When time travel promises infinite rollback, deletion feels like the destruction of potential value. The result is a modern manifestation of Jevons&#8217; Paradox : as storage became more efficient, our appetite for data expanded even more rapidly. We&#8217;ve built systems that can collect anything, but can&#8217;t measure whether that collection matters. The Hidden Cost of Free Storage Here&#8217;s what Lakehouse architecture diagrams don&#8217;t show: storage accounts for only 8% ...

**Embedded Videos:** 0


---
## Post 10: Data Engineering Weekly #246

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-246
**Published:** 2025-11-17T07:02:47+00:00

**Content Preview:**
Meet Compass &#8212; Dagster&#8217;s new AI data analyst for Slack Your data team is doing the best they can, but demand for data is limitless. The problem is that getting answers from data means hunting down the right dashboard, figuring out if it&#8217;s current, and translating what you see back into the question you asked. We built Compass to fix this. It&#8217;s AI-powered data analysis that lives where you work. Ask a question in plain English, get an answer from your warehouse with charts and context. No dashboards. No tickets. No waiting. Set up your free account in minutes. Lak Lakshmanan: What it means to get your data ready for AI One of the most challenging questions in every data org is the efficient and successful adoption of AI agents to enhance productivity and efficiency. The author outlines five resulting changes: moving from heavy normalization to context-rich data, prioritizing curated exemplars for in-context learning, building agent-ready infrastructure for perception and tool use, treating agent-generated artifacts as first-class data, and connecting observability to continuous model retraining. These shifts reposition data engineering toward enabling flexible, context-aware AI systems, changing the role from building rigid pipelines to designing environments where agents autonomously operate and improve. https://ai.gopubby.com/what-it-means-to-get-your-data-ready-for-ai-518861a8f025 IBM: The 2025 CDO Study - The AI multiplier effect Only 26% of CDOs are confident their organization can use unstructured data in a way that delivers business value. IBM publishes the 2025 CDO study. The study identifies five focus areas&#8212; strategy, scale, resilience, innovation, and growth &#8212;showing that high-ROI organizations align data strategy with business outcomes, give AI agents fast access to high-quality distributed data, build resilient governance for secure agentic access, democratize data across the workforce, and convert proprietary data int...

**Embedded Videos:** 0


---
## Post 11: Data Engineering Weekly #245

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-245
**Published:** 2025-11-10T02:41:51+00:00

**Content Preview:**
A practical guide to building data platforms that grow with you Scaling Data Teams, the latest in our popular eBook series, is now available. Building and scaling a data platform has never been more important or more challenging. Whether you&#8217;re just starting to build a data platform or leading a mature data organization, this guide will help you scale your impact, accelerate your team, and prepare for the future of data-driven products. Learn how real data teams, from solo practitioners to enterprise-scale organizations, build. Get the guide now Philipp Schmid: Zero to One: Learning Agentic Patterns Building reliable AI agents challenges teams to decide when structured workflows suffice versus when dynamic autonomy adds value. The article presents seven foundational design patterns&#8212;Prompt Chaining, Routing, Parallelization, Reflection, Tool Use, Planning, and Multi-Agent&#8212;that provide modular templates for constructing scalable, adaptable agentic systems. The framework emphasizes the combination and empirical evaluation of these patterns to manage complexity and improve coordination across agents and workflows. https://www.philschmid.de/agentic-pattern Gunnar Morling: &#8220;You Don&#8217;t Need Kafka, Just Use Postgres&#8221; Considered Harmful Engineering teams often oversimplify architecture decisions by suggesting Postgres can replace Kafka for all data needs. The article argues that while Postgres excels as a relational database, it lacks Kafka&#8217;s core strengths&#8212;persistent logs, consumer groups, low-latency streaming, and rich connector ecosystems&#8212;making it unsuitable for event streaming or large-scale data pipelines. Using each system for its intended purpose, with Postgres managing state and Kafka handling real-time events through CDC patterns, yields scalable, reliable, and maintainable architectures. https://www.morling.dev/blog/you-dont-need-kafka-just-use-postgres-considered-harmful/ Stanislav Kozlovski: Event Streaming i...

**Embedded Videos:** 0


---
## Post 12: Data Engineering Weekly #244

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-244
**Published:** 2025-11-03T09:22:54+00:00

**Content Preview:**
The data platform playbook everyone&#8217;s using We wrote an eBook on Data Platform Fundamentals to help you become like the happy data teams operating under a single platform. In this book, you&#8217;ll learn: - How composable architectures allow teams to ship faster - Why data quality matters and how you can catch issues before they reach users - What observability means, and how it will help you solve problems more quickly Get the guide now Editor&#8217;s Note: Re:Govern: The Data &amp; AI Context Summit Data engineering is evolving. Learn how from the top 5% of teams who are leading the way. There&#8217;s no playbook for data teams in the AI era. However, some leaders aren&#8217;t waiting for one &#8212; they&#8217;re building in real-time and sharing what they learn. That&#8217;s why I&#8217;m excited for Re:Govern 2025 on November 5. Leaders from Mastercard, GitLab, General Motors, Elastic , and others are opening up about what&#8217;s working: how they&#8217;re training AI to understand business context, delivering data products built for AI from the ground up, and restructuring their teams for a world where agents do the heavy lifting. These are the unfiltered lessons from teams who are years ahead &#8212; not because they had all the answers, but because they started moving first. Register here . Don&#8217;t miss this one . Matt Turck: Bubble &amp; Build: The 2025 MAD (Machine Learning, AI &amp; Data) Landscape The AI and data ecosystem is experiencing both speculative exuberance and genuine transformation as systems evolve from chatbots to agentic architectures grounded in governed data and reasoning models. Matt Turck&#8217;s 2025 MAD Landscape captures this inflection&#8212;highlighting reasoning + RL breakthroughs, the merging of data and AI infrastructure, sovereign compute buildouts, and the rise of coding agents and multimodal applications. https://www.mattturck.com/mad2025 Gradient Flow: Reimagining the Database for AI Agents In the past, I wrote a...

**Embedded Videos:** 0


---
## Post 13: Data Engineering Weekly #243

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-243
**Published:** 2025-10-27T03:07:59+00:00

**Content Preview:**
How Supplyco Powers Real-Time Manufacturing Intelligence with Dagster On Tuesday, Supplyco&#8217;s CTO Claudia Richoux will reveal how they built a pipeline in Dagster that processes 100,000+ data streams in real time &#8212; while ensuring 99.99% uptime. You&#8217;ll see their DAG architecture in action, learn how they built observability into every layer, and how they treat &#8220;data as code&#8221; to ship fast and scale smart. Save your spot now Editor&#8217;s Note: Re:Govern - The Data &amp; AI Context Summit Data engineering is evolving, without any clear playbook for the AI era. Yet, some AI-forward data leaders are years ahead by iterating fast and learning even faster. I&#8217;m looking forward to Re:Govern 2025 on November 5 , where leaders from Mastercard, GitLab, General Motors, Elastic, and others will share what it really takes to build for this next phase &#8212; from investing in new technologies like semantic layers to reimagining new operating models, skills, and roles for the AI era. Register here . This is one event you don&#8217;t want to miss. Shiyan Xu: Apache Kafka &#174; (Kafka Connect) vs. Apache Flink &#174; vs. Apache Spark &#8482; : Choosing the Right Ingestion Framework The article contrasts Kafka Connect, Flink (incl. Flink CDC), and Spark: Kafka Connect excels at connector-driven CDC and fan-out to sinks, Flink delivers low-latency, stateful stream processing and direct CDC-to-lakehouse writes, and Spark dominates batch/backfills and complex transformations with Structured Streaming for micro-batch use. The takeaway from the author: use Kafka Connect (with Kafka) for broad CDC integrations, Flink for real-time/event-time pipelines, and Spark for batch and heavy transforms&#8212;while watching Spark&#8217;s idle/scale inefficiencies to control spend. https://www.onehouse.ai/blog/kafka-connect-vs-flink-vs-spark-choosing-the-right-ingestion-framework Jack Vanlightly: A Fork in the Road: Deciding Kafka&#8217;s Diskless Future Rising cros...

**Embedded Videos:** 0


---
## Post 14: Thinking Like a Data Engineer

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/thinking-like-a-data-engineer
**Published:** 2025-10-23T00:22:19+00:00

**Content Preview:**
I thought becoming a data engineer meant mastering tools. Instead, it meant learning how to see. I thought the hardest part would be learning the tools &#8212; Hadoop, Spark, SQL optimization, and distributed processing. Over time, I realized the real challenge wasn&#8217;t technical. It was learning how to think . Learning to think like a data engineer &#8212; to see patterns in chaos, to connect systems to human behavior, to balance simplicity and scale &#8212; is a slow process of unlearning, observing, and reimagining. I didn&#8217;t get there through courses or certifications. I got there through people. Four mentors, in four different moments of my life, unknowingly gave me lessons that shaped how I approach engineering, leadership, and even life. Each taught me something not about data, but about thinking systems . What follows isn&#8217;t a tutorial. It&#8217;s a map of how four people &#8212; and their lessons &#8212; rewired how I think. #1. &#8220;Chasing Knowledge.&#8221; One of my friends recently asked why you are constantly reading and writing. It all started with an internship. A family friend of mine helped me find an internship. He was the person who taught me Java &#8212; patiently explaining not just syntax, but how to think through logic, abstraction, and design. When I called him after getting my first full-time job, I expected congratulations or career advice. Instead, he said something that I only understood years later: &#8220;Don&#8217;t chase money. Chase knowledge. Money will follow.&#8221; The advice struck a chord with me forever. In technology, everything changes &#8212; languages, frameworks, stacks, even paradigms. But curiosity compounds. The more you learn, the faster you learn. The more you focus on mastering fundamentals, the easier it becomes to adapt when the next wave arrives. That advice became a quiet compass throughout my career. Every time I faced a decision &#8212; whether to take a higher-paying role or a role that stret...

**Embedded Videos:** 0


---
## Post 15: Data Engineering Weekly #242

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-242
**Published:** 2025-10-20T11:46:11+00:00

**Content Preview:**
How Supplyco Powers Real-Time Manufacturing Intelligence with Dagster In our 10/29 deep dive, Supplyco&#8217;s CTO Claudia Richoux will reveal how they built a pipeline in Dagster that processes 100,000+ data streams in real time &#8212; while ensuring 99.99% uptime. You&#8217;ll see their DAG architecture in action, learn how they built observability into every layer, and how they treat &#8220;data as code&#8221; to ship fast and scale smart. Save your spot now Fast.ai: Let&#8217;s Build the GPT Tokenizer: A Complete Guide to Tokenization in LLMs Tokenization is fundamental to how large language models (LLMs) process text. Efficient tokenization improves training speed, context comprehension, and model performance by balancing granularity (precision) with computational efficiency. The blog is the text version of the GPT tokenization video. https://www.fast.ai/posts/2025-10-16-karpathy-tokenizers.html Jack Vanlightly: Why I&#8217;m not a fan of zero-copy Apache Kafka-Apache Iceberg Integrating streaming and analytical systems often tempts engineers to pursue &#8220;zero-copy&#8221; architectures that promise efficiency by unifying storage layers. The author argues that a zero-copy Kafka&#8211;Iceberg design instead introduces heavy compute overhead, schema evolution conflicts, and tight coupling that erodes clear system boundaries. The blog advocates for traditional materialization&#8212;maintaining separate but coordinated copies&#8212;because it preserves performance isolation, schema flexibility, and operational clarity across Kafka and lakehouse systems. https://jack-vanlightly.com/blog/2025/10/15/why-im-not-a-fan-of-zero-copy-apache-kafka-apache-iceberg Netflix: How and Why Netflix Built a Real-Time Distributed Graph: Part 1 &#8212; Ingesting and Processing Data Streams at Internet Scale Netflix writes about building a Real-Time Distributed Graph (RDG) to model entities and interactions as connected nodes and edges, enabling instant cross-domain insights. Power...

**Embedded Videos:** 1


---
## Post 16: Revisiting Medallion Architecture: Data Vault in Silver, Dimensional Modeling in Gold

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/revisiting-medallion-architecture-760
**Published:** 2025-10-17T04:00:51+00:00

**Content Preview:**
For more than two decades, the data warehousing community has grappled with a fundamental and largely misplaced debate: whether Data Vault or dimensional modeling produces a &#8220;better&#8221; data warehouse . Each camp has spent years evangelizing its methodology as superior, assuming that a singular modeling paradigm could&#8212;or should&#8212;address every requirement in a modern analytics platform. What is the consequence of this binary thinking? Organizations have invested heavily in architectures that, while optimized for one objective, fail catastrophically in others. Rigid star schemas provide blazing-fast analytics but crack under schema changes. Data Vaults offer unmatched schema flexibility and auditability but impose significant query complexity and performance limitations. The truth is, neither model is universally superior because neither was designed to be. Instead, they were built for different purposes&#8212;and those purposes align neatly with different stages of the data lifecycle. Modern data platforms have evolved beyond monolithic warehouse architectures. The rise of the medallion architecture&#8212;Bronze, Silver, Gold&#8212;presents an opportunity to align data modeling strategies with the distinct goals of each layer. A best-practice implementation of this architecture often looks like this: raw data lands in Bronze, is integrated and historized into a Data Vault model in the Silver layer, and is then transformed into performance-optimized dimensional models in the Gold layer for consumption. In this model: Data Vault shines in the Silver layer , where schema evolution, historical traceability, and source system integration dominate. Dimensional modeling flourishes in the Gold layer , where performance, usability, and business semantics reign supreme. This article explores the architectural insight that has quietly become an industry best practice: use Data Vault in Silver and dimensional modeling in Gold. This pattern didn&#8217;t emerge...

**Embedded Videos:** 0


---
## Post 17: Data Engineering Weekly #241

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-241
**Published:** 2025-10-13T12:41:29+00:00

**Content Preview:**
The data platform playbook everyone&#8217;s using We wrote an eBook on Data Platform Fundamentals to help you be like the happy data teams, operating undering a single platform. In this book, you&#8217;ll learn: - How composable architectures allow teams to ship faster - Why data quality matters and how you can catch issues before they reach users - What observability means, and how it will help you solve problems more quickly Get the guide now Netflix: Data as a Product: Applying a Product Mindset to Data at Netflix Many organizations struggle to extract consistent value from their data because it&#8217;s treated as an afterthought rather than a managed asset. Netflix reframes this challenge by applying a product management mindset to data &#8212; defining clear purpose, ownership, lifecycle management, usability, and reliability for every dataset, metric, and model. The article demonstrates how the &#8220;data as a product&#8221; approach builds trust, reduces data debt, and ensures data consistently drives meaningful business outcomes and innovation across the company. https://netflixtechblog.medium.com/data-as-a-product-applying-a-product-mindset-to-data-at-netflix-4a4d1287a31d Meta: Introducing OpenZL: An Open Source Format-Aware Compression Framework Compression frameworks often struggle to balance the efficiency of format-specific codecs with the simplicity of universal tools. Meta introduces OpenZL, a format-aware, open-source compression framework that learns a data&#8217;s structure through configurable transforms and offline training, achieving domain-specific efficiency with a single universal decoder. The benchmark shows the approach delivers higher compression ratios and faster speeds for structured data while maintaining operational simplicity, security, and backward compatibility across evolving datasets. https://engineering.fb.com/2025/10/06/developer-tools/openzl-open-source-format-aware-compression-framework/ Jack Vanlightly: Beyond Indexes: How O...

**Embedded Videos:** 0


---
## Post 18: Engineering Growth: The Data Layers Powering Modern GTM

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/engineering-growth-the-data-layers
**Published:** 2025-10-07T19:14:42+00:00

**Content Preview:**
Growth no longer rewards the widest net. Modern Go-To-Market(GTM) teams win with precision, not volume. They build revenue on infrastructure&#8212;pipelines, warehouses, and customer data platforms that turn signals into action. The shift is fundamental. Marketing teams once measured impressions and clicks. Sales teams worked from cold lists. Customer success reacted to churn. Today, these functions operate as a unified data ecosystem, synchronizing zero-, first-, second-, third-, and fourth-party data into coordinated market motion. Data engineers architect this system. We design the pipelines that define GTM accuracy, latency, and trust. When we build it well, the marketing, sales, and customer success move in harmony. When we don&#8217;t, the entire revenue engine stutters. But not all data is created equal. The modern GTM stack draws from five distinct data sources, each with unique engineering challenges, governance requirements, and strategic value: Zero-party data: What customers intentionally share through preferences and explicit consent First-party data: What you observe through behavioral tracking and product interactions Second-party data: What partners share through privacy-preserving collaboration Third-party data: What vendors sell through aggregated external sources Fourth-party data: What emerges from multi-company consortium networks Each data type requires different infrastructure, carries different levels of trust, and demands different engineering disciplines. Understanding these distinctions isn&#8217;t academic&#8212;it&#8217;s foundational to building GTM systems that scale, comply with regulations, and deliver measurable business impact. This article examines the GTM stack through the lens of data provenance, exploring not only what data powers modern go-to-market strategies but also how to engineer systems that integrate these five data sources responsibly and effectively. Zero-Party Data: Consent by Design Zero-party data captures what cus...

**Embedded Videos:** 0


---
## Post 19: Data Engineering Weekly #240

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-240
**Published:** 2025-10-06T03:12:44+00:00

**Content Preview:**
The data platform playbook everyone&#8217;s using We wrote an eBook on Data Platform Fundamentals to help you be like the happy data teams, operating undering a single platform. In this book, you&#8217;ll learn: - How composable architectures allow teams to ship faster - Why data quality matters and how you can catch issues before they reach users - What observability means, and how it will help you solve problems more quickly Get the guide now Kyle Weller: Apache Iceberg&#8482; vs Delta Lake vs Apache Hudi&#8482; - Feature Comparison Deep Dive The industry has quickly moved on from the Great Lakehouse debate and is rapidly gaining adoption. The blog from Onehouse revisits the current state of the Lakehouse systems as features like real-time mutation capabilities and multi-table/multi-query transactions become more mainstream. https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison Anthropic: Effective context engineering for AI agents As AI agents evolve beyond simple prompt-based systems, managing the limited &#8220;attention budget&#8221; of large language models has become a central engineering challenge. Anthropic writes about context engineering &#8212;a discipline focused on curating, compressing, and dynamically retrieving only the most relevant tokens during inference to sustain coherent, efficient, and long-horizon agent behavior. By combining strategies such as compaction, structured note-taking, and multi-agent architectures, the context engineering approach enables agents to act more autonomously while maintaining focus and reliability across extended tasks. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents Uber: How Uber Standardized Mobile Analytics for Cross-Platform Insights Inconsistent event definitions and ad-hoc instrumentation led to fragmented analytics data and high developer overhead. Uber&#8217;s Mobile Analytics team writes about rebuilding its analytics platform...

**Embedded Videos:** 0


---
## Post 20: Data Engineering Weekly #239

**Publication:** Data Engineering Weekly
**Author:** Ananth Packkildurai
**URL:** https://www.dataengineeringweekly.com/p/data-engineering-weekly-239
**Published:** 2025-09-29T02:48:56+00:00

**Content Preview:**
The data platform playbook everyone&#8217;s using We wrote an eBook on Data Platform Fundamentals to help you be like the happy data teams, operating undering a single platform. In this book, you&#8217;ll learn: - How composable architectures allow teams to ship faster - Why data quality matters and how you can catch issues before they reach users - What observability means, and how it will help you solve problems more quickly Get the guide now Editor&#8217;s Note: MLOps World | GenAI summit - 2025 The&nbsp; MLOps World | GenAI &nbsp;Summit will be hosted on October 8-9, featuring over 60 sessions from prominent companies, including OpenAI and HuggingFace, among others. Members can redeem 150$ off tickets . Sessions are the real deal, featuring practical workshops, use cases, food, drink, and parties throughout Austin. You can join to see more here: DataEngineeringWeekly (150$ OFF) InfoQ: InfoQ AI, ML, and Data Engineering Trends Report - 2025 InfoQ&#8217;s 2025 Trends Report highlights that the center of gravity is shifting toward Physical AI and robust agent ecosystems&#8212;powered by multimodal and on-device models, interoperable protocols like MCP/A2A, and AI-driven DevOps. The report promotes vector DBs / MLOps / synthetic data into mainstream use, highlights emerging areas (reasoning models, AI DevOps), and predicts that the near term will favor the agentic co-creation of software, real-time video RAG, and quietly embedded, context-aware AI experiences. https://www.infoq.com/articles/ai-ml-data-engineering-trends-2025/ StreamNative: Latency Numbers Every Data Streaming Engineer Should Know One of the informative articles for me this week. Teams misuse &#8220;real-time&#8221; because they don&#8217;t budget for physics: disks, networks, replication, and table commit cadences each add hard milliseconds to minutes of delay. The article classifies latency tiers (&lt;5 ms, 5&#8211;100 ms, &gt;100 ms), quantifies common costs (fsync, cross-AZ/region hops, and Icebe...

**Embedded Videos:** 0


---
## Post 21: From DBA to Data Everything

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/from-dba-to-data-everything
**Published:** 2026-01-14T12:51:03+00:00

**Content Preview:**
In this episode of the Data Engineering Central Podcast, I interview a Data OG, someone who&#8217;s been around the data space forever, and we talked about all things data, past, present, and future. I&#8217;m joined by Thomas Horton a longtime friend and one of the most well-rounded data professionals I know. Over the course of his career, Tom has worn just about every hat in data: developer, DBA, analyst, and everything in between. He&#8217;s lived through the era of on-prem databases, the rise of analytics, and the constant reinvention that defines modern data engineering today. We talk about what&#8217;s changed, what hasn&#8217;t, and why many of the &#8220;new&#8221; problems in data feel oddly familiar. We also dig into lessons learned the hard way, lessons that are just as relevant for early-career data engineers as they are for seasoned practitioners navigating today&#8217;s ever-expanding stacks. Subscribe now On a personal note, a huge portion of what I know about relational databases and analytics can be traced back to Tom. This conversation is part reflection, part history lesson, and part reality check on where the data industry is headed next. If you&#8217;re interested in the past, present, and future of data&#8212;and what really matters beneath all the tooling, this is an episode you won&#8217;t want to miss. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share...

**Embedded Videos:** 0


---
## Post 22: Apache Flink for Dummies

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/apache-flink-for-dummies
**Published:** 2026-01-12T13:49:27+00:00

**Content Preview:**
So you don&#8217;t want to be a streaming dummy, eh? Who wants to be a dummy? Not me, not you. We live in a strange AI-generated world, maybe the writing on the wall says SkyNet is going to write all the code from now on. You suck down your Big Glup and eat Doritos while you order your agents around. Who would have guessed the future would taste so sweet? I&#8217;m here to give you ye&#8217; old kick in the pants, smack on the back of the head, throw that dodgeball right where it hurts. It&#8217;s like we&#8217;re back in middle school, fighting for our lives in gym class. While the world of programming burns around us, we will ignore it with sweet indifference and continue to push ourselves to learn new things, to poke under rocks, and to grow by learning . Today, you and I are going to move from zero to Apache Flink hero. Streaming data, here we come. A gentle introduction to Apache Flink Ok, we have to start somewhere, and I&#8217;m not going to assume you have experience working with &#8220;streaming.&#8221; If we head over to the GitHub page for Flink , we can see that it&#8217;s mostly written in Java. That language no one talks about, but everyone uses. What is it? A data processing framework that is focused on streaming, but supports batch processing. How does Flink describe itself? This can sometimes be helpful. Read more...

**Embedded Videos:** 0


---
## Post 23: Databricks/Spark Excel Data Source

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/databricksspark-excel-data-source
**Published:** 2026-01-05T14:02:47+00:00

**Content Preview:**
Well, don&#8217;t pretend like y&#8217;all didn&#8217;t see it coming. If I close my eyes and listen to the winter wind blowing through the maple trees, I can see Josue Bogran dancing in the moonlight with joy. There is truth in what he says, &#8220; All roads lead to Excel . &#8221; It does depend on the size and nature of the business in which a data person finds themselves. Still, at the end of the day, if you have any resemblance to different business groups to deal with, like Accounting, Marketing, Product, Ops, etc, then Excel drives and contains ALOT of business context. Truth be told, business users can use Excel, and it works. It is no surprise at all that Databricks released support for Excel as both a data&nbsp; source &nbsp;and sink . Actually, it's surprising it took this long. Take a moment to check out my YouTube channel , if you please, kind sir, or &#8216;mam. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Databricks now supports Excel. Today, I want to take an honest look at Databricks' new support for Excel as a read-and-write via Spark and SQL. We should be honest with each other about the need for such a feature and examine both the upsides and downsides of using Excel within the Lake House architecture. There was a time in my life when I would foam and spit down my face like a madman as I fought tooth and nail against the inclusion of Excel in any part of a Data Platform. But, time and experience have taught me moderation in my views, and most importantly, that code and perfection are less critical than enabling the business to succeed and meeting them where they are. Save all your doom-and-gloom comments for later; we will get to them eventually. Let&#8217;s poke at Excel in Databricks, see what happens and how it works, then we will get to talking about whether you should or not. Working with Excel in Databricks Spark So, let&#8217;s play around with this new feature in Databricks, see how it ...

**Embedded Videos:** 1


---
## Post 24: Data Engineering Central Podcast - 10

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/data-engineering-central-podcast-f35
**Published:** 2026-01-02T13:03:33+00:00

**Content Preview:**
Back with another podcast episode, we talk the whole gamut this time. The cost of AI Agents, Toon, tokens, and hosting models vs. paying per token. The ease of building agents Data Mesh, dead or alive? Are Data Catalogs the future Apache Arrow is eating the world Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Read more...

**Embedded Videos:** 0


---
## Post 25: 1TB of Parquet files. Single Node Benchmark. (DuckDB style)

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/1tb-of-parquets-single-node-benchmark
**Published:** 2025-12-28T21:55:49+00:00

**Content Preview:**
I give the people what they want; I&#8217;m a slave to clicks and the buzz of internet anger and mayhem. Not so long ago, I tried, with limited success, to convince a legion of engineers who were raised on the Snowflake and Databricks teat , that salvation lay right at their feet; all they must do is lean down and put their hand to the plow. When you&#8217;ve been doing what I&#8217;ve been doing ( writing whatever you damn well please ) for over a decade, the list of haters grows ever longer and longer. Get in line pickles. A little stone tossed into the pond, where do the ripples go? Apparently, my first article on the matter stirred the monsters in the deep. My mamma always told me, haters gonna hate . I mean, writing such things is the teaching of heresy in the inner circles of the distributed devils and warmongers , whose purse strings are tied inextricably to the masses of data engineering peons passing on their&nbsp; tithe in compute &nbsp;to the&nbsp;inner sanctum of the data illuminati bent on bringing me to account for my many sins. I&#8217;ve made many a power enemy for you, the 99%, yet here I am, still trudging along in the trenches to bring the good word to waiting converts. Midwest boys raised on the river and in the woods don&#8217;t bow the knee very easily. The Single Node Rebellion awaits you. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Generating 1TB of Parquet files with Rust. I&#8217;ve got nothing much else today on this wonderful holiday break besides oiling my muzzleloader and waiting for deer season to start, just as well break out cargo and spin up some Rust. Head over to the GitHub repo and see for yourself. I went ahead and generated 1 TB of data and put it into an S3 bucket using the above Rust code. And the schema generated is straightforward. transaction_id datetime customer_id order_qty order_amount We should be able to run a straightforward SQL query to piddle with this 1TB of dat...

**Embedded Videos:** 0


---
## Post 26: 8 Data Engineering Principals

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/8-data-engineering-principals
**Published:** 2025-12-26T18:22:05+00:00

**Content Preview:**
Analytics . What, you think I should stick to my lane and keep with Data Engineering-specific content? Well, I bring you tidings of great joy, my friend. Many moons ago, before the age of Databricks, when Hadoop clusters roamed the land and wizards who wrote Pig were worshiped as demigods, you could have found me creating reports in SAP and dashboards for a living. A few long and arduous years later, if you peeked through my windows, you would have seen me studying Microsoft SQL Server exams in a bid to get certified, after which I had my green eye set on that elusive but popular &#8220; Business Intelligence Engineer &#8221; title. I did get that title, by the way. If you care,&nbsp; you can read more about my journey here. All that to say, I was bringing analytical insights to those cranky business users while you were at your high school prom , or playing beer pong in a dorm room. Read more...

**Embedded Videos:** 0


---
## Post 27: Building a DuckLake ... Open Source Style.

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/building-a-ducklake-open-source-style
**Published:** 2025-12-22T13:26:23+00:00

**Content Preview:**
I am sort of an addict for a good Lake House; it&#8217;s just an incredible architecture that is a joy to build and use daily. No more SQL Server or Oracle, you know what I&#8217;m saying if you were born in the right decade. Truth be told, at this point in the Modern Data Stack lifecycle, you pretty much have two major Lake House storage layers that dominate the landscape: Iceberg and Delta. I was surprised when DuckDB/MotherDuck threw their hat in the ring with DuckLake. Didn&#8217;t see that coming at the time. Like anything done by DuckDB, it&#8217;s always top-notch and for a good reason. They have a knack for doing things right. Ever since I wrote that first article, I&#8217;ve been meaning to return to DuckLake and try it out in a more open-source setting again. What I mean by that is can I use maybe a RDS Postgres instance and back DuckLake on AWS S3. I mean, if someone is actually looking to use DuckLake in the open as a viable alternative to Iceberg and Delta Lake, then that is the game. Checkout today&#8217;s sponsor Carolina Cloud One-click notebooks, genomics tools, and Ubuntu VMs at 1/3 the cost of AWS with no egress fees If you enjoy Data Engineering Central, please check out our sponsor's website above . It helps us a lot! Also, since it&#8217;s been a while since I&#8217;ve looked at DuckLake, one telling note we will look for is: has there been any adoption of frameworks in the broader data community? Aka, can I read DuckLake with Polars, Daft, Airflow, whatever? Simple Review of DuckLake Again, there are better places than here to l earn about DuckLake in depth . That&#8217;s not my focus today, as usual, I want to simply throw a problem at the DuckLake architecture, turn over a few rocks, and see what crawls out. DuckLake is built on simplicity, of course, and that appears to be one of its main features. Built on top of parquet SQL database for catalog/metadata Of course, they will give you a myriad of other reasons to use DuckLake, but at the en...

**Embedded Videos:** 0


---
## Post 28: Scott Haines on the Future of Data Engineering

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/scott-haines-on-the-future-of-data
**Published:** 2025-12-17T13:44:29+00:00

**Content Preview:**
In this episode, I sit down with Scott Haines &#8212; O&#8217;Reilly author, Databricks MVP, and veteran of Yahoo, Nike, and Twilio &#8212; for a wide-ranging conversation on the real state of modern data engineering. We dig into open-source ecosystems, Lakehouse architectures, the evolution of Spark, streaming, what&#8217;s broken and what&#8217;s working in today&#8217;s data tooling, and the lessons Scott has learned scaling platforms at some of the biggest companies in the world. If you care about data engineering, architecture, OSS, or the future of the modern data stack, you&#8217;ll love this one. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Make sure to follow Scott here on Substack , and over on GitHub....

**Embedded Videos:** 0


---
## Post 29: Apache Arrow is Eating the World.

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/apache-arrow-is-eating-the-world
**Published:** 2025-12-15T13:23:30+00:00

**Content Preview:**
About three years ago, over on my other long-running blog, I wrote about Apache Arrow , that silent but mighty tool that is swallowing up the Data Landscape one bite at a time. I figured it&#8217;s due time I again tip my hat to that great Oz hidden behind the digital curtain. It&#8217;s hard to even know where to start with Arrow ; it&#8217;s so ubiquitous and has infiltrated just about every Data Engineering framework built in the last 5 years+. I very much doubt I can do Arrow any real justice, but I will give it a try. Come along for the ride, my friend. My goals are simple, I hope you come away with &#8230; a new respect for Apache Arrow knowledge of where all Arrow is used a curiosity to use Apache Arrow yourself This is where the road lies before us, with lots of twists and turns. I don&#8217;t know where exactly we are going or how we will get there, but we can trust it will all work itself out in the end. Let&#8217;s get to it shall we? Read more...

**Embedded Videos:** 0


---
## Post 30: LLMs for {PDF} Data Pipelines

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/llms-for-pdf-data-pipelines
**Published:** 2025-12-09T15:16:21+00:00

**Content Preview:**
I was recently in conversation with some people about AI, its use cases, the good and the bad, where it fits, and where it doesn&#8217;t. It was brought up in the context of reading random PDFs and generating JSON files from their contents. This got me thinking. Can you, should you, and what will happen, if we use LLMs not just to puke out the next code snippet &#8230; but what if we use an LLM mixed with a little Agentic AI, to actually to BE the data pipeline???? It is a strange thought. I&#8217;m sure people are doing it. Maybe. It&#8217;s one thing for an LLM to spit out code for a Data Pipeline; it's another for an LLM to be the data pipeline, or at least part of it. I want to try it. What say you? Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Inserting LLMs into Data Pipelines ( all code on GitHub for this ) I&#8217;ve built my fair share of RAGs, vector stores, Chat this Chat that bots &#8230; whatever. I also use Cursor on a semi-regular basis, maybe a few times a week, either as something to bounce ideas off of or to generate some mindless code. One thing I&#8217;ve never done is try to use an LLM in the loop or stage of a data pipeline. This will be new for me, as it is for you, and I am going to list out loud some of the questions I have at large about doing this sort of work. At this point, I have no idea how it will work out. Some questions I&#8217;m asking myself. I think it&#8217;s one thing for me to play around and force an LLM to do a thing by using coercion, glue, and string to make something happen, vs. an actual workflow that could be used in production. Here&#8217;s what&#8217;s on my mind. A small local LLM or a remote API-based one? Can we force an LLM model to do what we need, or do we need an Agent? To actually write/place (JSON) files on disk Are orchestration tools like Airflow starting to provide, say, OpenAI operators? LLM output is non-deterministic; it can hallucinate at any time. How...

**Embedded Videos:** 0


---
## Post 31: LakeKeeper: Iceberg REST Catalog

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/lakekeeper-iceberg-rest-catalog
**Published:** 2025-12-08T12:55:15+00:00

**Content Preview:**
In a continuation of a topic I&#8217;ve written about off and on over the last few months ( Apache Iceberg and Catalog options ), I&#8217;m taking another stab at finding &#8220;good&#8221; and &#8220;approachable&#8221; Catalog options that support Apache Iceberg. By &#8220; good &#8221; and &#8220; approachable ,&#8221; I mean something that can be easily installed and run in a semi-production-ready state by an A verage Engineer in a reasonable amount of time with a small amount of troubleshooting. The truth is I am a glass-half-empty kind of guy regarding most technology. Nothing angers me more when a talking head declares the next most remarkable thing is released and shows how well it worked on their laptop. I prefer to try tools out in an environment where the hidden rocks pop out of the water and sink your happy boat. Amazingly, all a person is required to do is use a Linux server and some AWS credentials to do just that. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Read more...

**Embedded Videos:** 1


---
## Post 32: Building Agentic AI ... Fancy.

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/building-agentic-ai-fancy
**Published:** 2025-12-05T00:48:15+00:00

**Content Preview:**
I&#8217;m getting to the point where I&#8217;m a little burnt out on hearing about AI this and AI that. Work, LinkedIn, YouTube, Substack &#8230; it&#8217;s a never-ending glut of AI-generated content talking about AI. I get the sense that the closest most developers get to AI is asking Cusor to puke out the next code chunk. Classic. I&#8217;ve never been one to make a mountain out of a mole hill. I find myself adrift in the middle ground of the AI purgatory we find ourselves in as writers of code. There seem to be two deeply entrenched cabals of software engineers. AI is for the weak; humans forever. Vibe code your way to glory. The truth is that the middle is most likely slanted towards the AI is the future group. You cannot turn back the clock once you&#8217;ve opened Pandora&#8217;s box. Will there always be a bright future for intelligent and industrious writers of code and systems? Absolutely. Is AI here to stay and an extreme force multiplier in the creation and execution of software of all kinds? Absolutely. Old dogs die hard, and the old guard is having a hard time swallowing the new reality. Let&#8217;s bring it all back down to earth. I am no AI expert, but I&#8217;ve probably done more than most, including fine-tuning my own LLM. I don&#8217;t get overly excited about building AI, insofar as it&#8217;s actually helpful and interesting problems to solve. I would guess that there is a fair number of Data Engineers and others who may be overwhelmed by the fast pace of development in AI and LLMs, and feel a little left behind and lost. I assure you, there is hope. Just remember, all those liars on LinkedIn and Reddit trying to be AI smart, they breathe the same air and drink the same water you and I do. I&#8217;m going to prove that to you by showing how easy it is for you to build an AI SQL Agent. Forget all the too-bright suckers, confusing acronyms; you, my friend, are capable of building &#8220;Agentic AI.&#8221; Don&#8217;t listen to the haters. Let&#82...

**Embedded Videos:** 0


---
## Post 33: Data Mesh Theology. Dead or Alive?

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/data-mesh-theology-dead-or-alive
**Published:** 2025-12-02T20:52:11+00:00

**Content Preview:**
Meh. That's how I feel about the languishing and short-lived ideology called &#8220; Data Mesh. &#8221; The Modern Data Stack has seen its fair share of prophets seeking the loving embrace of the community, a fickle thing, only to fall out of favor all too soon. Data Mesh appears to be one of those ideas. The thing is, I keep my trained ear close to the ground, listening to the comings and goings of various and sundry ideas. Watching what becomes popular, what dies on the vine. But I won&#8217;t be the judge of that in the end. Never say never. Let&#8217;s just lay it all out. Try to understand what a Data Mesh architecture is How long has it been around Pros and cons Is there any hope left for mainstream adoption? This is just as much for me as for you. I have my preconceived notions, of course, but we will try to give Data Mesh a fair shake and see where it's come from and where it might be going. You know one thing is true &#8230; those cloud compute bills are getting out of hand. Check out https://carolinacloud.io/ for High-Performance CPUs, GPUs, Notebooks,&nbsp; and &nbsp;Bare-Metal Servers. If you want to save serious money on compute, head over to Carolina Cloud. What is Data Mesh? (In Plain English) Data Mesh is an architectural approach that aims to address the problems of large, centralized data teams by&nbsp; decentralizing &nbsp;data ownership. Instead of one monolithic team owning all datasets, each domain (fraud, marketing, product, etc.) owns its data as a product . This can best be explained visually, contrasted with the most common approach of gathering all data into a single spot to be shared from there. Let me give you a few bullet points to further drive home what a Data Mesh Architecture is. decentralized data architecture, domain-oriented self-serve design &#8220;Responsibility for analytical data is shifted from the central data team to the domain teams.&#8221; This is in direct opposition to the classic approach of a single Data Platform tea...

**Embedded Videos:** 0


---
## Post 34: JSON in a Lake House World

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/json-in-a-lake-house-world
**Published:** 2025-12-01T13:21:36+00:00

**Content Preview:**
I often look back on the days of yore, long before we lived in Lake House Land and had Data Warehouses with JSON or JSONB columns that were just another column in the database. Life has gotten more complicated since then. If I think back far enough and hard enough, I can remember cutting my teeth on a &#8220;Data Lake.&#8221; It was a beautiful and terrible thing, millions of JSON files deposited daily into S3 buckets. What more could a lonely Data Engineer ask for? Read more...

**Embedded Videos:** 0


---
## Post 35: Revisiting Data Quality

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/revisiting-data-quality
**Published:** 2025-11-25T13:19:13+00:00

**Content Preview:**
Oh, that age-old topic of Data Quality, often discussed but never implemented. Poor little blighter. Who knows what it&#8217;s like to be the old, beat-up rock that always gets kicked, gets no love or attention, just told about everything you do wrong ( try writing a Substack like me, you&#8217;ll find out quick enough ). That is Data Quality, isn't it? The age-old question. And the age-old answer. Nothing could be truer and to the point. Thanks to Delta for sponsoring this newsletter! I personally use Delta Lake on a daily basis, and I believe this technology represents the future of Data Engineering. Content like this would not be possible without their support. Check out their website below. Data Quality isn&#8217;t cool enough. I&#8217;ve written about Data Quality a few times over the years; it&#8217;s simply not a popular or sexy topic. Always mediocre reaction to mediocre tools that don&#8217;t work well. Truth be told, Data Quality is something CTOs and Data Leaders love to talk about, but when you ask them to either pony up some money for a tool, or pay some engineers for work on this topic for a quarter or two, you get mumbling, muttering, and a general waving of hands. Then it&#8217;s back to business as normal. It&#8217;s always sight out of mind, the old nagging suspicion in the back of the head. Random data problems that pop up and get fixed. Not enough pain to actually do a thing. BTW, here are some past DQ articles. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Data Quality in the Lake House era What is Data Quality in the Lake House era? It&#8217;s a mess, is what it is. We Modern Data Engineers were spewed forth from the mouth of the Data Lakes, jumbles of data piled into stacks, with rigidity to match that haphazard approach. We landed in the detritus of Lake House architecture, made up of Iceberg and Delta Lake. Somehow reminding remenicent of the old SQL Server days, yet different in many ways. ...

**Embedded Videos:** 0


---
## Post 36: What is TOON?

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/what-is-toon
**Published:** 2025-11-24T13:39:38+00:00

**Content Preview:**
TOON. I was having a happy Friday, just bumbling along, dreaming about turkey hunting and a weekend free of tech issues. I made the mistake of getting on that now infamous LinkedIn. There it was. Everywhere. A few things go from zero to everywhere overnight. Somehow TOON did it. Angry people. Happy people. Confused people. I do pride myself on keeping somewhat up to date on the comings and goings of all things data/ml/ai-related. I mean, some of you who aren&#8217;t cheap little hobbits actually pay me to do this for you. TOON done slapped me in the face. Never heard of the word until now. Read more...

**Embedded Videos:** 0


---
## Post 37: One Big Table Data Modeling

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/one-big-table-data-modeling
**Published:** 2025-11-20T17:37:48+00:00

**Content Preview:**
Oh boy, have I been lied to my entire life? Should I finally give up and move to that cabin in the woods? The life of a Data Engineer, one thing to the next. I was born again as a Kimball monk, baptised into Medallion Architecture, and will be burned as a heretic for One Big Table (OBT) theology? What's new? I, for one, have mostly ignored the rumblings of OBT design from various corners of the internet. But with the death of data modeling and the rise of the Lake House, it seems that previous prejudices and technological barriers have fallen away, opening the door for OBT. &#127937; 1. Introduction &#8211; The Temptation of One Big Table Welp, based on how old this question is, we can probably answer it now. ( OBT always seems to be a fringe discussion ) Read more...

**Embedded Videos:** 0


---
## Post 38: All You Can Do Before Airflow: 

**Publication:** Data Engineering Central
**Author:** Alejandro Aboy
**URL:** https://dataengineeringcentral.substack.com/p/all-you-can-do-before-airflow
**Published:** 2025-11-17T13:54:35+00:00

**Content Preview:**
Hello, this is Daniel! Today, we have another Guest Post from Alejandro Aboy . You can check out his Substack The Pipe and the Line. Alejandro Aboy is a data engineer at Workpath, building scalable pipelines with Airflow, dbt, and the modern data stack. Through The Pipe &amp; The Line , he writes hands-on tutorials on topics like building dbt-style orchestrators with Python and DuckDB, and implementing RAG systems for data engineers Let&#8217;s get started! Most orchestration tutorials start with Airflow DAGs processing static CSV files. You see the fancy UI, the complex graphs, the task dependencies, and think, &#8220;this is what real data engineering looks like.&#8221; When I say Airflow I also mean Mage, Kestra, Dagster, Prefect or whatever many other options of orchestrator we have out there in the market right now. I remember when I was starting out and first saw Airflow demos. Beautiful graphs, complex DAGs, Redis queues, Celery workers. Data enthusiasts might be getting the wrong idea, bootcamps or courses out there place Airflow as the only option to make your workflows come to life. The truth? There are levels to this. Your orchestration approach should match your project maturity, not your aspirations. And this principle also gets dragged everywhere else, even to data teams making decisions based on FOMO and now on their own context. The Modern Data Stack narrative usually pushes dbt, Airflow, Snowflake, and Fivetran as the default starting point. Most teams don&#8217;t need the complete solution on day one, or they don&#8217;t even need it at all. There&#8217;s something in the middle that offers many alternatives. Orchestration Fundamentals: Beyond Tool Names Before diving into tools, let&#8217;s talk about what orchestration actually means. This helped a lot when I was getting started: understanding that knowledge can be transferred and that you can break down the orchestration approach into layers. Note that this won&#8217;t deep dive into exclusive c...

**Embedded Videos:** 0


---
## Post 39: Data Engineering Central Podcast - 09

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/data-engineering-central-podcast-db1
**Published:** 2025-11-13T20:59:14+00:00

**Content Preview:**
Hello! A new episode of the Data Engineering Central Podcast is dropping today. We will be covering a few hot topics! Cluster Fatigue The Death of Open Source Going to be a great show, come along for the ride! Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share...

**Embedded Videos:** 0


---
## Post 40: 650GB of Data (Delta Lake on S3). Polars vs DuckDB vs Daft vs Spark.

**Publication:** Data Engineering Central
**Author:** Daniel Beach
**URL:** https://dataengineeringcentral.substack.com/p/650gb-of-data-delta-lake-on-s3-polars
**Published:** 2025-11-12T16:38:14+00:00

**Content Preview:**
I recently tried to light the tinder for what I hoped would be a revolt &#8212; the&nbsp; Single Node Rebellion &#8212; but , of course, it sputtered out immediately. Truth be told, it was one of the most popular articles I&#8217;ve written about in some time , purely based on the stats. The fact that I even sold t-shirts , tells me I have born a few acolytes into this troubled Lake House world. Without rehashing the entire article, it&#8217;s clear that there is what I would call &#8220; cluster fatigue. &#8221; We all know it, but never talk about it &#8230; much &#8230; running SaaS Lake Houses is expensive emotionally and financially. All well and good during the peak Covid days when we had our mini dot-com bubble, but the air has gone out of that one. Not only is it not cheap to crunch 650 GB of data on a Spark cluster &#8212;piling up DBUs, truth be told &#8212; but it&#8217;s not complicated either; they&#8217;ve made it easy to spend money. Especially when you simply don&#8217;t need a cluster anymore for *most datasets and workloads. Sure, in the days of Pandas when that was our only non-Spark option, we didn&#8217;t have a choice, but DuckDB, Polars, and Daft ( also known as D.P.D. because why not ) &#8230; have laid that argument to rest in a shallow grave. Cluster fatigue is real D.P.D. can work on LTM ( larger than memory ) datasets D.P.D. is extremely fast. Sometimes I feel like I must overcome skepticism with a little bit of show-and-tell,&nbsp; proof is in the pudding, &nbsp;as they say. If you want proof, I will provide it. Look, it ain&#8217;t always easy, but always rewarding. Thanks for reading Data Engineering Central! This post is public so feel free to share it. Share Choose, we must. We have two options on the table. Like Neo, you have to choose which pill to take. Ok, maybe you can take both pills, but whatever. Distributed Not-Distributed Our minds have been overrun by so much marketing hype pumping into our brains, we are like Neo stuck in...

**Embedded Videos:** 0


---
## Post 41: Reconfiguring AI as Data Discovery Agent(s)?

**Publication:** Modern Data 101
**Author:** Animesh Kumar
**URL:** https://moderndata101.substack.com/p/reconfiguring-ai-as-data-discovery
**Published:** 2026-01-12T17:08:00+00:00

**Content Preview:**
&#8220;The thing that hath been, it is that which shall be; and that which is done is that which shall be done: and there is no new thing under the sun&#8221; | Ecclesiastes 1:9 For most of human history, knowledge was scarce. It had to be discovered, recorded, preserved, and transmitted with care. Today, we live in the opposite condition. Whatever we know or talk about has already been published, spoken, or written somewhere. This was true first of literature, then of history, and it became overwhelmingly true with the internet. &#8220;All is said, we have come too late; for more than seven thousand years there have been humans, thinking&#8221; | Jean de La Bruy&#232;re Need a recipe? It exists in some forgotten blog post, a forum thread, a video, or a scanned cookbook. Need to learn a programming language? There are countless tutorials, curricula, walkthroughs, and opinionated guides. Need a detailed breakdown of a niche concept that only a handful of people care about? Chances are, someone has already written it, explained it, argued about it, and archived it online. The Untapped Power of Discovery B2C AI chatbots are built to thrive in exactly this environment. At their core, they function as extraordinarily sophisticated search engines: systems that ingest the vast expanse of publicly available information and learn how to combine, filter, compress, and summarise it in a way that aligns with the user&#8217;s intent. Their real strength is not recall alone, but intent interpretation: understanding who the user is, what they are likely trying to achieve, and how much depth or precision is required in the response. &#8220;Everything clever has already been thought; we must only try to think it again .&#8221; | Johann Wolfgang von Goethe These systems are remarkably good at deciding what not to search, narrowing the space of possibilities to save compute/time, and identifying similarities and patterns with almost unsettling accuracy. They do not just retrieve infor...

**Embedded Videos:** 0


---
## Post 42: The Wheel and the Algorithm | Part 1

**Publication:** Modern Data 101
**Author:** Sagar Paul
**URL:** https://moderndata101.substack.com/p/the-wheel-and-the-algorithm-part-1
**Published:** 2026-01-08T14:10:14+00:00

**Content Preview:**
A Conversation Between Strangers Last Thursday, returning home from Washington, D.C., on the late train to Princeton, I found my seat occupied by a gentleman in his seventies. He was traveling with his wife, surrounded by four large suitcases, the kind meant for international journeys. The bags had wheels at the bottom, and he was holding onto them with evident concern. Photographer: Anne Hollowday | Camera: CineStill 800Tungsten, Kodak Ektar 100, Ilford Delta 3200 Anyone who has traveled on Amtrak knows the problem: the trains lack proper restraining mechanisms for large luggage. Without someone holding them, those wheeled bags would roll across the aisle with every curve in the track. As a good Samaritan, I offered to help secure a couple of them. We struck up a conversation. When I asked what he did for a living, he said he was retired but had worked in LPI, or Low Probability of Intercept . I had never heard the term. He explained it succinctly: A class of radar and communication technologies designed to evade detection, used primarily in defense systems but with some commercial applications. In under a minute, he had compressed decades of expertise into a crisp, accessible explanation. I was impressed. Then he turned the question back to me. So what does AI actually do? How does it change lives? I felt the pressure immediately. Here was a man who had just distilled a complex defense technology into sixty seconds. His wife was gathering their belongings. The train was approaching their stop. As a technology executive, I needed to compress this massive, sprawling concept into something equally elegant. My mind raced through metaphors. And then it struck me: AI was much like the invention of the wheel. As the couple prepared to disembark, rolling their wheeled bags toward the exit, the metaphor seemed almost too perfect. He now had a fresh perspective on the casters beneath his luggage, those simple rotating mechanisms that trace their lineage back five thousand y...

**Embedded Videos:** 0


---
## Post 43: AI-Ready Data vs. Analytics-Ready Data

**Publication:** Modern Data 101
**Author:** Animesh Kumar
**URL:** https://moderndata101.substack.com/p/ai-ready-data-vs-analytics-ready-data
**Published:** 2026-01-05T18:20:30+00:00

**Content Preview:**
Before we dive in, we want to take a moment to thank you for being here with us as we step into 2026! The Modern Data 101 community exists because of your curiosity, your ideas, and your willingness to think more deeply about data. We&#8217;ll continue to share the best resources, emerging ideas, and important pivots shaping the modern data world, and we hope you&#8217;ll stay with us not just through 2026 but for many years to come. A Very Happy New Year! &#129346; Now, Let&#8217;s Dive In! Before we talk about modern data, or AI-ready data, we have to step back and ask a much older question: what is data fundamentally for? Strip away the platforms, the pipelines, the dashboards, and the acronyms, and data resolves into something far simpler. Data exists to reduce uncertainty, support decisions, and ultimately enable action. Everything else we build on top of it is secondary. If the goal changes, the properties of the data must change as well. Data is not inherently &#8220;good&#8221; or &#8220;bad&#8221; in isolation. It is only good relative to the problem it is meant to solve. Reusing the same shape of data for fundamentally different goals is not efficiency but category error. Which brings us to the only question that actually matters: what kind of uncertainty are we trying to reduce? The moment that answer changes, the meaning of readiness changes with it. And that is where the divergence between analytics-ready data and AI-ready data begins. What does &#8216;ready&#8217; mean The word &#8220;ready&#8221; sounds deceptively simple. But ready for whom? Ready for what? Data readiness is often spoken about as if it were a universal state: something data either is or isn&#8217;t. In reality, &#8220;ready&#8221; has no meaning unless we first define the context in which the data is meant to operate. To understand readiness, we have to decompose it. Who is consuming the data? How is it being consumed? What kinds of decisions does it exist to support? And perhaps mos...

**Embedded Videos:** 0


---
## Post 44: Behind the Scenes of Data Musicals with Tiankai Feng | A Christmas Special with MD101🎄

**Publication:** Modern Data 101
**Author:** Tiankai Feng
**URL:** https://moderndata101.substack.com/p/behind-the-scenes-of-data-musicals
**Published:** 2025-12-22T11:47:54+00:00

**Content Preview:**
Tiankai Feng is perhaps one of the most unique creators and influencers in the data arena. While everybody says they bring &#8216;fun&#8217; to something as serious as pipelines and governance, @ Kai Feng really adds the glitter to glory! Alongside stellar strategies and impactful data governance wins, Tiankai&#8217;s way of expression, delivery, and evangelism strikes a chord that most of us in the data space never expected: to be reminded of that childlike learning bug. Below are the top ten quality hits and behind the scenes from the man himself. Get your records on! Top 5 Hits by @KaiFeng &amp; Exclusive Behind the Scenes! Data - The Musical &#127925; This parody medley of Broadway musicals blends a humorous self-introduction with a playful, musical take on the daily madness of data work. It drops quirky takes (&#8220; You&#8217;ll be back, soon you&#8217;ll see, coz your user story&#8217;s not complete &#8221;), fun biographical deets, and great storytelling to poke fun at the hyper-structured world of data people. The lighthearted tone sets up the message: &#8230;even though data governance, rules, and cleaning can look intimidating, the passion for data and the shared struggle are what bring the community together. The humour works because it exaggerates the seriousness of data life while showing how human and relatable it really is. The song highlights the hard realities of data, like endless lines to review, missing context, lost documentation, and the eternal search for KPIs that live &#8220;somewhere.&#8221; It makes fun of relying on Excel, the fact that not everyone knows SQL, and the universal pain of waiting for business input. Yet beneath the jokes is a sincere emphasis that data literacy, collaboration, and joint ownership are the only path to true &#8220;data democracy,&#8221; and it can be unforgiving. Blending comedy with truth, the song celebrates the data professionals, acknowledges their frustrations, and encourages everyone to learn, particip...

**Embedded Videos:** 12


---
## Post 45: Why Inaction Feels Easier Than Action in Data Quality

**Publication:** Modern Data 101
**Author:** Gaurav Patole
**URL:** https://moderndata101.substack.com/p/why-inaction-feels-easier-than-action
**Published:** 2025-12-18T10:28:40+00:00

**Content Preview:**
About Our Contributing Expert Gaurav Patole | Principal Data Strategy &amp; Governance Advisor, Author of Data Quality ROI Gaurav Patole is a Principal Data Strategy &amp; Governance Advisor at ThoughtWorks and the author of Data Quality ROI . A seasoned data governance and data quality practitioner, he brings deep, hands-on experience helping global organisations turn trust in data into measurable business value. Formerly with BCG, Gaurav has led end-to-end data governance and quality programs across industries and geographies, bridging business and technology through his People-Process-Technology (PPT) approach. A frequent speaker and active community contributor, he is known for making data governance practical, people-centric, and ROI-driven. We&#8217;re thrilled to feature his unique insights on Modern Data 101 ! We actively collaborate with data experts to bring the best resources to a 15,000+ strong community of data leaders and practitioners. If you have something to share, reach out! &#129780;&#127995; Share your ideas and work: community@moderndata101.com *Note: Opinions expressed in contributions are not our own and are only curated by us for broader access and discussion. All submissions are vetted for quality &amp; relevance. We keep it information-first and do not support any promotions, paid or otherwise! Let&#8217;s dive in When it comes to Data Quality, there is a standard piece of advice: &#8220;The business side must own the data.&#8221; We are told that every data initiative needs to be tied to a business use case, and the business should own the data issues. While true, this advice often fails to solve the real problem. Why? Because simply telling a business leader that data quality matters doesn&#8217;t automatically make them want to fix it. Knowing something is important is different from doing something about it. Action is hard. It feels uncertain, disruptive, and uncomfortable. Inaction, on the other hand, feels safe. Here is why your organ...

**Embedded Videos:** 0


---
## Post 46: Rethinking Data Movement: A First Principles Approach

**Publication:** Modern Data 101
**Author:** Animesh Kumar
**URL:** https://moderndata101.substack.com/p/rethinking-data-movement-a-first
**Published:** 2025-12-15T12:21:43+00:00

**Content Preview:**
TOC Why Data Movement Needs a Rethink The Problem: Legacy Ingestion at Scale The Triple Squeeze on Data Teams Common Challenges of Data Movement Broader Operational Complexities The Shift: The Principles of Modern Data Movement How a Data Movement Engine Embodies the Principles The Architecture of Modern Data Movement Deep-Dives into Modern Data Movement Patterns Why Data Movement Needs a Rethink Data used to be simple: a handful of databases, nightly batch jobs, and reports waiting in the morning. Today, that world is invalid. Today, every enterprise is drowning in sources that won&#8217;t stop multiplying: relational databases, SaaS APIs, log files, event streams, you name it. Each comes with its own quirks, schemas, and update patterns. At the same time, the patience window has collapsed . Business stakeholders don&#8217;t want yesterday&#8217;s snapshot, they expect dashboards that refresh in near-real time. Product teams want features powered by streaming data. AI initiatives demand low-latency, constantly refreshed context. SLAs rise, and tolerance for lag drops to near zero. We&#8217;ve thrown brute force at this problem before. The Spark-era mindset was: spin up clusters, crunch everything in sight, reload the warehouse from scratch. But that model doesn&#8217;t scale when your sources are infinite, your SLAs are tighter than ever, and your cost curve is under constant pressure. This is why the centre of gravity has shifted. Modern data movement is not about &#8220;big batch compute.&#8221; It&#8217;s about: Incremental-first pipelines that move only what&#8217;s changed. Change Data Capture (CDC) that keeps systems in sync without heavy lifting. API-aware connectors that respect rate limits, pagination, and quirks of SaaS ecosystems. Observability baked in , so teams can see, debug, and trust their pipelines end-to-end. That&#8217;s the new playbook. Without it, everything else, like your analytics, your AI, your customer experience, suffers. The Problem: L...

**Embedded Videos:** 0


---
## Post 47: Building Robust Data Products: 5 Pillars Every Data Engineer Should Apply

**Publication:** Modern Data 101
**Author:** Najate BOUAD
**URL:** https://moderndata101.substack.com/p/building-robust-data-products-5-pillars
**Published:** 2025-12-11T11:32:54+00:00

**Content Preview:**
This piece is a community contribution from Najate Bouad , a Data Engineering Manager at Decathlon Digital , leading teams that build customer-, product-, and experience-focused data products. With a decade of experience across large-scale data platforms in finance and retail, she combines deep engineering expertise with a clear, people-first approach to domain-driven and clean data architecture. She is also the co-founder of Clean Data Architecture, where she contributes to shaping modern data products and DDD practices. We actively collaborate with data experts to bring the best resources to a 15,000+ strong community of data leaders and practitioners. If you have something to share, reach out! &#129780;&#127995; Share your ideas and work: community@moderndata101.com *Note: Opinions expressed in contributions are not our own and are only curated by us for broader access and discussion. All submissions are vetted for quality &amp; relevance. We keep it information-first and do not support any promotions, paid or otherwise! Let&#8217;s Dive In For years, data was merely a technical component of applications, a simple support mechanism for maintenance. Today, it has taken on a new dimension: it has become a product with its own uses, requirements, and lifecycle. However, most data systems still act like fragile pipelines: They break as soon as business rules change Every update is costly They fail quietly without proper monitoring They constantly need someone to fix them. These situations have shaped a clear conviction: The real challenge today is to design systems that adapt, preserve trust, and remain coherent as the business evolves. A robust data product is therefore much more than a workflow. It is a long-lived digital asset that encodes business meaning, enforces data quality, traces change, and supports continuous evolution without friction. In this article, I&#8217;m laying out five engineering pillars that I&#8217;ve seen consistently turn data products from...

**Embedded Videos:** 0


---
## Post 48: AI and Data are Business Strategy Experiments Now. How Far Are You Willing to Push the Curve?

**Publication:** Modern Data 101
**Author:** Travis Thompson
**URL:** https://moderndata101.substack.com/p/ai-and-data-are-business-strategy
**Published:** 2025-12-08T19:33:42+00:00

**Content Preview:**
In data products, people often use &#8216;data risk&#8217; and &#8216;data experimentation&#8217; as if they mean the same thing. They are different, though, and mixing them up is a big reason why many organisations struggle to achieve real results with AI or analytics . The difference may seem small, but it separates teams that just keep data flowing from those that create lasting value with their data products. Data Risk Data risk means your assumptions, models, or understanding of the business could be off in ways you might not notice. This can lead to wrong decisions, mismatched metrics, or loss of trust. However, risk also presents opportunities for disproportionate gains. Strategic decisions embedded within models (such as definitions, granularity, dimensions, and transformations) can later yield sustainable competitive advantages. Data risk is the necessary cost of developing enduring digital assets rather than temporary dashboards. Data Experimentation Data experimentation is about discovering new things. It means looking at real business behaviours instead of just trusting assumptions. This could involve trying new data transformations, testing different features, tracking data flows, watching how people use data, and exploring unusual data connections. Experimentation focuses on learning and finding benefits, not just avoiding risks or chasing quick results. How do data risk and experimentation work together, and where does real impact come from? Consider a graph with experimentation velocity on the x-axis and data risk exposure on the y-axis . Influence of Risk and Experimentation Assets on Impact of Data Teams | Source: MD101 Archives Zone A: The Data Product R&amp;D Lab Strong data teams start here, moving quickly, running experiments that are safe to fail, and learning a lot about their data. They map out data, improve metrics, test connections, and check how users behave. At this stage, the rest of the company is not relying on your data definitions y...

**Embedded Videos:** 0


---
## Post 49: Reflecting the Language Instinct in Machines

**Publication:** Modern Data 101
**Author:** Animesh Kumar
**URL:** https://moderndata101.substack.com/p/reflecting-the-language-instinct
**Published:** 2025-12-04T15:16:33+00:00

**Content Preview:**
Language, they say, is an instinct instead of a learned skill. There&#8217;s a whole book on it if you&#8217;re interested. Essentially, the idea is that while language is a wrapper, the base instinct is the need to communicate. Initially, for evolutionary reasons (humans survived because of communicating survival strategies), later, to also simply express for the sake of beauty and art. Now that we have such huge advancements in the field of language, where academia and technology have joined hands to unify the limits of ontology, semantics, and communication, we must understand the base instinct of this capability to really excel. Book recommendation: The Language Instinct, by Steven Pinker What is the Base Instinct of Language Need to unify with other seemingly isolated entities. Humans have separate consciousnesses; how must they meet, even if at a shallow level? Through communication, which is interaction. We call these interoperable exchanges &#8216;discussions,&#8217; &#8216;brainstorming,&#8217; &#8216;meetings,&#8217; and the like. What about entities that haven&#8217;t developed the language wrapper? The wilderness hosts countless such beings. Everything, including plants, trees, and animals of the wild. However, they too share the common base instinct: to interact. Interaction is one of the foundational keys of survival, even in civil societies. The moment there&#8217;s even a hint of it being taken away, it&#8217;s a dystopia. Trees are known to interact through roots, scent, animals. In one particular adventure, I came across the idea of the &#8220;wood wide web:&#8221; a network so grand that it could easily beat any latest technology. These are evolutionary results of entities who have existed since long before us and instead of developing language as wrapper on the base instinct of interoperability, they went with other means. The revelation of the Wood Wide Web&#8217;s existence, and the increased understanding of its functions, raises big questions...

**Embedded Videos:** 1


---
## Post 50: The 20-Year Failure: How AI Closes the Gap between Data Strategy and Business Strategy

**Publication:** Modern Data 101
**Author:** Markus Schmidberger
**URL:** https://moderndata101.substack.com/p/how-ai-closes-data-business-gap
**Published:** 2025-12-01T12:29:46+00:00

**Content Preview:**
About Our Contributing Expert Dr. Markus Schmidberger | Data Strategy &amp; AI Leader This piece is a community contribution from Dr Markus Schmidberger , a technologist, data strategist, and leadership advisor who has spent more than two decades at the intersection of business strategy, data systems, and culture transformation. Currently, he serves as a CTO / CPO &amp; Co-Founder, building a Social Action Network that leverages AI agents on top of distributed ownership. From leading data initiatives at AWS to founding multiple analytics and leadership ventures, Markus&#8217;s work blends deep technical expertise with human-centred leadership. He is also extremely passionate about community building, having founded the TEDxGlenbeigh division and supporting various leadership initiatives to this day. We&#8217;re thrilled to feature his unique insights on Modern Data 101 ! We actively collaborate with data experts to bring the best resources to a 15,000+ strong community of data leaders and practitioners. If you have something to share, reach out! &#129780;&#127995; Share your ideas and work: community@moderndata101.com *Note: Opinions expressed in contributions are not our own and are only curated by us for broader access and discussion. All submissions are vetted for quality &amp; relevance. We keep it information-first and do not support any promotions, paid or otherwise! Let&#8217;s Dive In! For the last two decades, the tech world has been obsessed with a single mantra: &#8220; Become Data-Driven .&#8221; We spent billions on data warehouses, data lakes, and modern data stacks. We hired armies of data scientists and armed them with the most sophisticated BI tools money could buy. Yet, despite this massive investment, the baseline still is that organizations have failed to close the Data-Business Gap . Gartner and Forrester reports consistently show that while data volume has exploded, the percentage of organizations that actually drive business value from that da...

**Embedded Videos:** 0


---
## Post 51: Predicting the Map of Requirements for Long-Term Data Platform Relevance

**Publication:** Modern Data 101
**Author:** Sagar Paul
**URL:** https://moderndata101.substack.com/p/map-of-data-needs
**Published:** 2025-11-27T11:34:32+00:00

**Content Preview:**
TOC Mendeleev&#8217;s Genius Framework for Projecting Data Needs Using Projections for Long-Term Platform Alignment Why Data Platforms Become Irrelevant Mapping the Unknown Needs: Vacant Spots Translating the Framework into Architecture Platform Decoupling is Non-negotiable Data Products as the Interface b/w Platform &amp; Business Need Interfaces at Different Levels of Abstraction The Framework in Action Where the Platform Learns to Bend Mendeleev&#8217;s Genius When Dmitri Mendeleev arranged the periodic table in 1869, he did something extraordinary: designed for the unknown . His brilliance didn&#8217;t lie in cataloguing the 63 known elements, but in foreseeing what must exist beyond them. He left deliberate gaps, placeholders for the undiscovered entities, trusting the coherence of his framework more than the completeness of his data. Years later, when gallium, scandium, and germanium filled those spaces exactly as he predicted, the framework itself was validated. First version of the Periodic Table in 1869 | Source: EDN Network Complete Periodic Table of Elements | Source: ThoughtCo That is the essence of architectural foresight. The goal of a data platform is not to capture the present, but to anticipate the future and build a schema of possibility . Today&#8217;s design should already know where tomorrow&#8217;s needs will fit, even if those needs are not yet visible. The genius of such systems lies in their intentional emptiness. &#8220;Vacant spots&#8221; left open for emerging consumption patterns, new decision modes, and autonomous agents of action. Because what ultimately defines an enduring platform isn&#8217;t how much it covers today, but how naturally it can absorb what tomorrow brings. Framework for Projecting Data Needs Every analytics need has a precise position within a three-dimensional space that defines how it&#8217;s consumed, by whom , and for what kind of decision . The Cuboid of Future Needs A predictive surface that helps data leaders no...

**Embedded Videos:** 0


---
## Post 52: Closing the Architecture Gap Between FAANG and Enterprises | Case: Meta | Part 2.2

**Publication:** Modern Data 101
**Author:** Travis Thompson
**URL:** https://moderndata101.substack.com/p/closing-architecture-gap-faang-and-enterprises
**Published:** 2025-11-24T17:09:44+00:00

**Content Preview:**
&#8230;continued from Part 2.1: How Meta Turns Compliance into Innovation . This part addresses: 1. Areas of mismatch: How legacy or enterprise data architectures fall short of Meta&#8217;s Privacy Aware Infrastructure 2. Inspiring Meta&#8217;s business-aligned outcomes instead of trying to replicate their state-of-the-art data architectures that have been chiselled for decades Subscribe to follow the series. Significance of Purpose and Lineage in developing explain a ble and embedded Governance in data stacks (for illustration purposes only) | Source: Authors The systems we admire at Meta , Google , or Netflix are physical artefacts of an organisation&#8217;s design philosophy: the accumulated expression of how these organisations think about data, software, responsibility, and scale. What we see on the outside is only the final shape of decades of internal reasoning. Enterprises make the mistake of following in the footsteps of these advanced data- and tech-first orgs to replicate the same business shape. They adopt the warehouse-lakehouse-governance stack, the &#8220;state-of-the-art&#8221; privacy tooling, pick as-is catalogs and create the same views, probably replicate mesh-inspired domains, and believe they have reconstructed a high-functioning data infrastructure. But replicating the visible layers without reflecting the enterprise&#8217;s operating logic is a high-cost mirage. The tools may look contemporary, but the underlying behaviour and how they interact with each other and data entities still reflect legacy constraints. This is why so many transformations end up feeling hollow . The architecture appears modern when diagrammed, yet it behaves exactly like the old one when work flows through it. The problem is not that enterprises are missing a particular tool or framework. The problem is that they are copying an artefact without understanding its cause. This piece exists in the hope of highlighting that cause and shifting the conversation from replicat...

**Embedded Videos:** 0


---
## Post 53: Modeling Semantics: How Data Models and Ontologies Connect to Build Your Semantic Foundations

**Publication:** Modern Data 101
**Author:** Juha Korpela
**URL:** https://moderndata101.substack.com/p/semantic-foundations-with-data-models-or-ontology
**Published:** 2025-11-20T14:58:57+00:00

**Content Preview:**
About Our Contributing Expert Juha Korpela | Consultant, Enterprise Data Management This piece is a community contribution from Juha Korpela , Independent Consultant and Founder of Helsinki Data Week , a community-first data conference. With deep expertise in information architecture, data products, and modern operating models , Juha has spent his career helping organisations truly understand what their data means and how to use that semantic clarity to build better systems. Formerly Chief Product Officer at Ellie Technologies and now the voice behind the &#8220; Common Sense Data &#8221; Substack, Juha is also a speaker, trainer, and advisor shaping the resurgence of conceptual modeling in the industry. We&#8217;re thrilled to feature his unique insights on Modern Data 101 ! We actively collaborate with data experts to bring the best resources to a 15,000+ strong community of data leaders and practitioners. If you have something to share, reach out! &#129780;&#127995; Share your ideas and work: community@moderndata101.com *Note: Opinions expressed in contributions are not our own and are only curated by us for broader access and discussion. All submissions are vetted for quality &amp; relevance. We keep it information-first and do not support any promotions, paid or otherwise! Let&#8217;s Dive In! Knowledge Management Provides Context for AI Knowledge Management and Information Architecture have had a rocket ride to the top of the data world&#8217;s consciousness due to Generative AI. The ability to organize, store, and serve structured semantics as context to various agents and chatbots is widely recognized as a winning ingredient in the GenAI race , reducing hallucinations and improving accuracy. Terms like taxonomies, ontologies, and knowledge graphs are being thrown around as if just been invented, but veterans of the trade know better: there&#8217;s nothing new under the sun. Knowledge Management and the Library Sciences, from which these subjects were born, a...

**Embedded Videos:** 0


---
## Post 54: The Network is the Product: Data Network Flywheel, Compound Through Connection

**Publication:** Modern Data 101
**Author:** Animesh Kumar
**URL:** https://moderndata101.substack.com/p/the-data-network-flywheel
**Published:** 2025-11-17T18:29:19+00:00

**Content Preview:**
The Law of Data Systems: Everything Compounds When It Connects The value of a data product is never contained within its boundaries. It emerges from the number, quality, and friction of its connections, and the signals from its produce. Connectivity is the architecture that turns isolated signals into coordinated intelligence. The mistake most teams make is assuming insight comes from accumulation, when in reality it comes from interaction. The system becomes &#8220;intelligent&#8221; when the surface area of interaction between components expands. It&#8217;s not from the sophistication of isolated components. Intelligence is an emergent property of the feedback loops between producers, consumers, and the decisions that reshape the system in return. Where interaction is narrow, intelligence stays local. Where interaction grows, intelligence compounds. Without the network effect built into the earliest stages of strategy, organisations trap themselves in linear architectures that can never produce nonlinear outcomes. They add more resources but get diminishing returns because the underlying system doesn&#8217;t compound. Source: LinkedIn And this is where the Data Network Flywheel truly begins. When every data product learns from every other, when every interaction strengthens the next, the system stops being a cost centre and is a self-accelerating engine of value. Quadrants of Value: The Data Product Amplification Matrix The Amplification Matrix isn&#8217;t a maturity model, but one that helps us understand how a system evolves as its internal connections deepen. Each quadrant represents a distinct state of system behaviour: how information flows, how meaning accumulates, and how value compounds. The movement across quadrants traces a shift in system dynamics , from isolated components to a coherent, self-reinforcing network. The Data Product Value Amplification Matrix | Source: Author 1. Bottom-Left Quadrant: Isolated Data Products (Low Connection, Low Value) Thes...

**Embedded Videos:** 0


---
## Post 55: Boosting Data Adoption with Data Product Marketplace | Masterclass by Priyanshi Durbha

**Publication:** Modern Data 101
**Author:** Priyanshi Durbha
**URL:** https://moderndata101.substack.com/p/data-adoption-with-data-product-marketplace
**Published:** 2025-11-13T12:40:08+00:00

**Content Preview:**
This piece is an overview of a Modern Data Masterclass: Boosting Data Adoption with Data Product Marketplaces by Priyanshi Durbha . Jump to Masterclass About Host: Priyanshi Durbha | Principal, Advanced Analytics Priyanshi is a Principal of Advanced Analytics at The Modern Data Company , where she partners with enterprises to help them unlock the full potential of their data through DataOS. With over a decade of experience spanning analytics, data science, and business strategy, she has built a career at the intersection of insight and impact. Before joining Modern, Priyanshi led the Analytics Practice at AKIRA Insights , scaling it into a core business function by fostering high-performing teams and delivering transformative client solutions. Her earlier stints at AB InBev, Deloitte, and Mu Sigma shaped her expertise in advanced analytics, stakeholder alignment, and data-driven storytelling. A trained economist from Presidency University , Priyanshi is passionate about turning complex data into narratives that drive confident decision-making and sustainable business growth. Below is a detailed overview of Priyanshi&#8217;s masterclass, which should give you a taste of the concepts she touches on, her views on how the fundamentals of data product marketplaces build the foundation for democratisation and innovation, and how it could be used to further data products and their adoption at scale! Let&#8217;s Dive In Every analytics journey begins with clear goals, and then stalls at the same predictable choke point: accessing the data itself. Months dissolve between problem definition and the first usable dataset because of structural inertia: architectures fragmented by design, teams siloed by function, ownership diffused across invisible boundaries. Each new project becomes a task of rediscovery. Analysts and data scientists start from zero, chasing the same sources, revalidating the same checks, reengineering the same transformations, as if institutional memory reset...

**Embedded Videos:** 0


---
## Post 56: The Governance Framework: Passing Through the Trifecta of People, Process, and Tech

**Publication:** Modern Data 101
**Author:** José Almeida
**URL:** https://moderndata101.substack.com/p/the-governance-framework-people-process-tech
**Published:** 2025-11-10T12:24:51+00:00

**Content Preview:**
This piece is a community contribution from Jose Almeida , Data Strategy &amp; Governance Leader with 25+ years of experience driving business value across EMEA, and specialising in Master Data Management and Data Quality processes and technologies. Jose is also an Advisor, Speaker, and founder of the &#8216; Data Foundation &#8217; Newsletter. We&#8217;re thrilled to feature his unique insights on Modern Data 101 ! We actively collaborate with data experts to bring the best resources to a 15,000+ strong community of data leaders and practitioners. If you have something to share, reach out! &#129780;&#127995; Share your ideas and work: community@moderndata101.com *Note: Opinions expressed in contributions are not our own and are only curated by us for broader access and discussion. All submissions are vetted for quality &amp; relevance. We keep it information-first and do not support any promotions, paid or otherwise! TOC What Makes &#8220;Bad Data&#8221; Miscalculated impact of dirty data Bad data is extremely pervasive Bad Data Quality will cost more than anticipated How to clean up the debt caused by bad data The Governance Framework Passing Through the Trifecta of People, Process, and Tech People&#8217;s Corner: Making Data Quality Everyone&#8217;s Job Process Corner: Have Direct KPI Attribution Lines with Governance Tech Corner: The Choice of Platform and the Culture Around it Makes all the Difference What makes &#8220;Bad Data&#8221; Dirty data is information that&#8217;s incomplete, inaccurate, outdated, or duplicated, and can wreak havoc in organizations. It&#8217;s a costly issue that breeds mistrust, wastes resources, and undermines decision-making. Despite its importance, data quality is frequently overlooked, leading to significant business disruptions and lost opportunities. The Miscalculated Impact of Dirty Data The consequences of dirty data are significant and far-reaching. According to research, poor data quality costs businesses millions annually. ...

**Embedded Videos:** 0


---
## Post 57: Data Modelling for Data Products | Modern Data Masterclass by Mahdi Karabiben

**Publication:** Modern Data 101
**Author:** Mahdi Karabiben
**URL:** https://moderndata101.substack.com/p/data-modelling-for-data-products
**Published:** 2025-11-06T13:38:46+00:00

**Content Preview:**
This piece is an overview of a Modern Data Masterclass: Data Modelling for Data Products by Mahdi Karabiben . Jump to Masterclass About Host: Mahdi Karabiben, Head of Product Mahdi has been working in the data space for more than eight years and is presently the Senior Product Manager at Sifflet, which builds data observability. Formerly, he was a Staff Data Engineer at Zendesk, working on the company&#8217;s Data Platform. Mahdi has dabbled in multiple industries and organisations, working with different types of data, all in the context of building petabyte-scale data platforms . The constant across these experiences was the scale of data and building competent platforms and tools that managed that scale. Below is a detailed overview of Mahdi&#8217;s session, which should give you a taste of the concepts he touches on, his drive and emphasis on why fundamentals of data modelling suffice the innovation that data products bring to the modern data infrastructure, essentially eliminating the need to reinvent the wheel. Let&#8217;s Dive In Data modelling, at its core, is the act of giving data shape and constraints so that it becomes reliable reasoning material. It defines how concepts relate, how meaning propagates, and how systems preserve truth across change. A data product, in contrast, is not a table or a dashboard; it is a reusable and measurable asset engineered with the discipline of product thinking: versioned, owned, and designed for a specific outcome. We are once again at an inflexion point. In the 1990s, centralised data warehouses and dimensional models gave organisations consistency and trust. The Hadoop era traded that trust for scale: data was everywhere, but meaning was nowhere. The modern data stack made infrastructure effortless, but encouraged ad hoc pipelines that decayed faster than they created value. Now, the pendulum is swinging back toward decentralisation, where domains own their data, models are built around value streams, and governance mu...

**Embedded Videos:** 0


---
## Post 58: Governance as a Platform, Not a Policy: How Meta Turns Compliance into Innovation | Part 2.1

**Publication:** Modern Data 101
**Author:** Samadrita Ghosh
**URL:** https://moderndata101.substack.com/p/governance-as-a-platform-not-a-policy
**Published:** 2025-11-03T18:24:01+00:00

**Content Preview:**
This is Part 2.1 of a Series on FAANG data infrastructures . In this series, we&#8217;ll be breaking down state-of-the-art designs, processes, and cultures that FAANG or similar technology-first organisations have developed over decades. And in doing so, we&#8217;ll uncover why enterprises desire such infrastructures, whether such aspirations are feasible, and identify state-of-the-art business outcomes that may or may not need decades of infrastructure mastery. Subscribe to be the first to be notified when the next part drops! Subscribe now Optional: Read Part 1 first &#128071;&#127995; TOC | Part 2 Part 2.1 Case A: Facebook&#8217;s Infrastructure that Understands Data Meta Uses Organising as a Design Pattern Instead of An Enforced Architecture How Meta&#8217;s Design Philosophy Takes Effect Through Their &#8220;Current&#8221; Architecture Core Components &amp; Concepts of the Architecture To be continued in Part 2.2 Areas of mismatch: How legacy or enterprise data architectures fall short of Meta&#8217;s Privacy Aware Infrastructure Inspiring Meta&#8217;s business-aligned outcomes instead of trying to replicate their state-of-the-art data architectures that have been chiselled for decades Case A: Facebook&#8217;s Infrastructure that &#8220; Understands&#8221; Data Design Philosophy: Obsessive Organising The foundational idea and the superpower of Facebook engineering is the obsessive organising undertaken by their data stack at scale. If most enterprises run data kitchens that are functional but messy , Meta runs one that&#8217;s &#8220;MONICA CLEAN.&#8221; Meta&#8217;s primary business IS data, and it understands its entire data ecosystem of billions of users and infinite transactions so well by the simple act of scaling largely simple organising tactics. Meta doesn&#8217;t just collect, process, and store data like most enterprises do. It categorises, annotates, and controls from the first point of entry. Every byte that enters the system is tagged, labelled wit...

**Embedded Videos:** 0


---
## Post 59: Why You’ll Never Have a FAANG Data Infrastructure and That’s the Point | Part 1

**Publication:** Modern Data 101
**Author:** Travis Thompson
**URL:** https://moderndata101.substack.com/p/why-youll-never-have-a-faang-infrastructure
**Published:** 2025-10-30T11:48:36+00:00

**Content Preview:**
This is Part 1 of a Series on FAANG data infrastructures . In this series, we&#8217;ll be breaking down the state-of-the-art designs, processes, and cultures that FAANGs or similar technology-first organisations have developed over decades. And in doing so, we&#8217;ll uncover why enterprises desire such infrastructures, whether these are feasible desires, and what the routes are through which we can map state-of-the-art outcomes without the decades invested or the millions spent in experimentation. This is an introductory piece, touching on the fundamental questions, and in the upcoming pieces, we&#8217;ll pick one FAANG at a time and break down the infrastructure to project common patterns and design principles, and illustrate replicable maps to the outcomes. Subscribe to be the first to be notified when the next part drops! Subscribe now TOC The Myth of the FAANG Data Platform FAANG Infrastructure Was a Historical Accident The Challenge for &#8220;Un-fanged&#8221; Organisations Pivot: To Be or Not to Be FAANG, that is Not the Question FAANG&#8217;s advantage wasn&#8217;t tools, but design philosophies. Meeting in the Middle Buy the infrastructure, customised to your environment Build your design patterns aligned to your organisation&#8217;s design philosophy Hybrid that Makes a Sensible Middle Path The Mindset Shift: From &#8220;Data Pipelines&#8221; to &#8220;Data Products.&#8221; Example of A Design Paradigm on Top of Pre-Built Infra The Technology Formula (if we must be concrete) The Myth of the FAANG Data Platform When we think of the data platforms of the tech elite, say, Amazon, Google, Meta, Netflix; what we often imagine is a vast, custom-built infrastructure of streaming, batch, feature stores, ML pipelines, and near-infinite scale. And that imagination isn&#8217;t wrong. But when we look behind the curtain, the data practitioner community in r/dataengineering validates something critical: the circumstances under which those state-of-the-art data archite...

**Embedded Videos:** 0


---
## Post 60: First Strategy Piece of Enterprise AI: The Change Management Framework

**Publication:** Modern Data 101
**Author:** Travis Thompson
**URL:** https://moderndata101.substack.com/p/first-strategy-piece-of-enterprise-ai
**Published:** 2025-10-23T13:17:33+00:00

**Content Preview:**
TOC The Case for Change Stakeholder Mapping and Influence Analysis The Impact-Influence Matrix Stakeholder Mapping Framework Change Impact Analysis (CIA) As-Is and To-Be States User Group Impact Assessment Change Readiness and Maturity Assessment Change Readiness Analysis (CRA) Change Maturity Assessment Communication Architecture Training &amp; Enablement Reward &amp; Recognition Mechanisms The Social Flywheel of Change Behaviour Reinforcement Loops Go-Live &amp; Post-Go-Live Management Managing Change Resistance Models &amp; Frameworks on Change Management for Enterprise AI Final Note The Case for Change The most profound constraint to AI transformation today is not technical. It&#8217;s ironically the human at the centre of the equation. Enterprises have spent the last decade industrialising their data infrastructure, yet their human infrastructure remains analogue. AI fails in large enterprise setups because organisations cannot change how they think . Beneath the surface of every failed initiative is the same pattern: change fatigue, tool overload, and fragmented accountability. Systems evolve faster than the people operating them. The outcome: a widening adoption gap where the brilliance of technology is dulled by the inertia of behaviour. The Generative Turn (GT) has amplified this tension. AI has moved from the back office to the front line: from automating processes to augmenting decisions. This transition demands trust, which is ten steps ahead of merely demanding integration. To deploy AI effectively, enterprises must engineer deliberate pathways that help users perceive, understand, and internalise AI&#8217;s role in their workflow. From first principles, every AI transformation is a story of human transformation. Data managers may prepare the ground, but change managers grow the roots. AI success is 20% model performance and 80% organisational adoption. Stakeholder Mapping and Influence Analysis Every AI transformation begins with a paradox: the people ...

**Embedded Videos:** 0


---
## Post 61: UV All the Way: Your Go-To Python Environment Manager

**Publication:** Marvelous MLOps Substack
**Author:** Boldizsár
**URL:** https://www.marvelousmlops.io/p/uv-all-the-way-your-go-to-python
**Published:** 2025-11-10T07:28:01+00:00

**Content Preview:**
In 2025 the best way to manage Python projects is using uv . This tutorial helps you set up a modern Python project from scratch using uv. Yep, correct spelling is uv , two lower-case letters. The two most important things that uv manages for you is a project-specific virtual environment (venv), and all the project dependencies in that venv. Let&#8217;s start creating stuff! Install uv If you haven&#8217;t already, install uv on your machine. Open a shell or terminal to run these commands: On MacOS, make sure you have Homebrew installed , then run brew install uv to install uv. On Linux, run curl -LsSf https://astral.sh/uv/install.sh | sh to install uv. On Windows, run powershell -ExecutionPolicy ByPass -c &#8220;irm https://astral.sh/uv/install.ps1 | iex&#8221; to install uv. (Otherwise consult the uv installation docs ). Make sure you have uv installed and available as a command line application. You should be able to open a new shell and run the following command: $ uv --version uv 0.9.5 (Homebrew 2025-10-21) By the time you read this, uv will be updated many times, so you should expect to see a newer version. Create a project with uv Let&#8217;s create a personal Python project for you using uv. In this example we&#8217;ll pretend you&#8217;re caled &#8220;Alice&#8221; and use that as an example. Feel free to sub Alice with your own name or whatever name you want to use for this project. Let&#8217;s open the shell again, and create a project folder. After that let&#8217;s change into that folder and run all further commands inside that folder. mkdir -p alice-python cd alice-python (On Windows use Powershell, and you can omit the -p flag to mkdir .) We&#8217;ll uv init to initialize the project. Run uv init --help to see the available options. $ uv init --name alice-python --python 3.13 --description &#8220;Alice&#8217;s personal Python project&#8221; Initialized project `alice-python` (Again, you can use your own name and description instead of Alice.) You can i...

**Embedded Videos:** 0


---
## Post 62: Patterns and Anti-Patterns for Building with LLMs

**Publication:** Marvelous MLOps Substack
**Author:** Hugo Bowne-Anderson
**URL:** https://www.marvelousmlops.io/p/patterns-and-anti-patterns-for-building
**Published:** 2025-10-27T10:24:35+00:00

**Content Preview:**
A bit about our guest author: Hugo Bowne- Anderson advises and teaches teams building LLM-powered systems, including engineers from Netflix, Meta, and the United Nations through my course on the AI software development lifecycle . It covers everything from retrieval and evaluation to agent design and all the steps in between. Use the code MARVELOUS25 for 25% off. In a recent Vanishing Gradients podcast, I sat down with John Berryman, an early engineer on GitHub Copilot and author of Prompt Engineering for LLMs . We framed a practical discussion around the &#8220;Seven Deadly Sins of AI App Development,&#8221; identifying common failure modes that derail projects. For each sin, we offer a &#8220;penance&#8221;: a clear antidote for building more robust and reliable AI systems. You can also listen to this as a podcast: Spotify Apple Full notes and more episodes &#128073; This was a guest Q&amp;A from our July cohort of Building AI Applications for Data Scientists and Software Engineers. Enrolment is open for our next cohort (starting November 3) . &#128072; Sin 1: Demanding 100% Accuracy The first sin is building an AI product with the expectation that it must be 100% accurate, especially in high-stakes domains like legal or medical documentation [ 00:03:15 ]. This mindset treats a probabilistic system like deterministic software, a mismatch that leads to unworkable project requirements and potential liability issues. The sin is requiring these AI systems to be more accurate than you would require a human to be. The Solution/Penance: Reframe the problem. The goal is not to replace human judgment but to save users time. Design systems that make the AI&#8217;s work transparent, allowing users to verify the output and act as the final authority. By setting the correct expectation, that the AI is a time-saving assistant, not an infallible oracle, you can deliver value without overpromising on reliability [ 00:04:30 ]. Sin 2: Granting Agents Too Much Autonomy This sin invo...

**Embedded Videos:** 15


---
## Post 63: Your FREE guide to learn MLOps on Databricks

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/your-free-guide-to-learn-mlops-on
**Published:** 2025-08-29T13:57:23+00:00

**Content Preview:**
If you&#8217;ve ever built a machine learning model in a Jupyter notebook and wondered &#8220;Now what?&#8221;, you&#8217;re not alone. The gap between a working prototype and a production ML system is big, filled with infrastructure complexity, deployment challenges, and monitoring nightmares. That&#8217;s why we created a free, hands-on MLOps course using Databricks Free Edition. A guide we wish we&#8217;d had when starting out with MLOps on Databricks. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. With 3 hours of video lessons and 10 detailed Substack lectures, this course takes you from zero to a production-ready ML pipeline. You&#8217;ll master automated deployment with Databricks Asset Bundles and GitHub Actions, and set up monitoring with drift detection to keep your models reliable over time. To make things more fun, we built our use case using a toy dataset around Marvel characters, after all, we&#8217;re big fans of the universe. The 3-hour course is now available as a single video on YouTube: The 10-lecture journey Here&#8217;s the full collection of articles so you can explore them easily: Lecture 1: Introduction to MLOps We start with the hard truth: most ML projects never make it to production. Why? Because moving from a 1000-line notebook to a scalable system requires a completely different mindset. Lecture 2: Developing on Databricks We show why notebooks are great for exploration but become bottlenecks for MLOps. They make it difficult to write modular code, apply code quality standards, or run unit tests. We&#8217;ll show you how to use VS Code extension, Databricks CLI, and Databricks Connect to develop locally with modern engineering workflows while running PySpark code on Databricks. Lecture 3: Getting started with MLflow Dive deep into the two most important MLflow classes: `mlflow.entities.Experiment` and `mlflow.entities.Run`. These form the f...

**Embedded Videos:** 0


---
## Post 64: Implementing Model Monitoring on Databricks

**Publication:** Marvelous MLOps Substack
**Author:** Başak Tuğçe Eskili
**URL:** https://www.marvelousmlops.io/p/lecture-10-implementing-model-monitoring
**Published:** 2025-08-06T16:55:23+00:00

**Content Preview:**
Databricks recently introduced Free Edition, which opened the door for us to create a free hands-on course on MLOps with Databricks. This article is part of that course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. Watch the lecture on YouTube. In the previous lecture , we covered the theory behind ML model monitoring and the tools Databricks provides for it. In this session, we&#8217;ll walk through a practical example, from inference tables to Lakehouse Monitoring implementation. Our monitoring system consists of four key components: Inference Logging: Capturing model inputs and outputs Monitoring Table Creation: Transforming raw logs into a format suitable for monitoring Scheduled Refreshes: Keeping monitoring data up-to-date Monitoring Dashboard: Visualizing metrics and detecting drift Let&#8217;s examine each component in detail. 1. Inference Data Collection !Make sure that inference tables is enabled for your serving endpoint. First, we need to collect data from our model serving endpoint. The notebook lecture10.marvel_create_monitoring_table.py demonstrates how to send requests to our endpoint and then process the logged data. In lecture 6 , we learned how to call the model endpoint. There are two ways to do this: either via HTTPS or by using the Workspace Client. def send_request_https(dataframe_record): """ Sends a request to the model serving endpoint using HTTPS. """ serving_endpoint = f"https://{os.environ['DBR_HOST']}/serving-endpoints/marvel-characters-model-serving/invocations" response = requests.post( serving_endpoint, headers={"Authorization": f"Bearer {os.environ['DBR_TOKEN']}"}, json={"dataframe_records": dataframe_record}, ) return response.status_code, response.text def send_request_workspace(dataframe_record): """ Sends a request to the model serving endpoint using workspace client. """ response = workspace.serving_endpoints.query( name="marvel-charact...

**Embedded Videos:** 1


---
## Post 65: Introduction to ML monitoring

**Publication:** Marvelous MLOps Substack
**Author:** Başak Tuğçe Eskili
**URL:** https://www.marvelousmlops.io/p/introduction-to-ml-monitoring
**Published:** 2025-08-05T21:56:29+00:00

**Content Preview:**
Databricks recently introduced Free Edition, which opened the door for us to create a free hands-on course on MLOps with Databricks. This article is part of that course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. In this lecture, we&#8217;ll dive into one of the most critical (and often misunderstood) aspects of production ML: monitoring. Watch the lecture on Youtube: In a ML system, you need to monitor metrics that go beyond the ones you&#8217;d expect in any production system (such as system health, errors, and latency, KPIs and infrastructure costs). In classic software, if code, data, and environment stay the same, so does behavior. ML systems are different: model performance can degrade even if nothing changes in your code or infra because ML is driven by the statistical properties of your data. User behavior can shift, seasonality or upstream data can change. All can cause your model to underperform, even if everything else is &#8220;the same.&#8221; That&#8217;s why MLOps monitoring includes data drift, model drift, and statistical health, not just system metrics. Data Drift: It happens when the distribution of the input data shifts over time, even if the relationship between inputs and outputs stays the same. For example, let&#8217;s say there is a lot of new houses entering the market in a certain district. People&#8217;s preferences, the relationship between features and price stays the same. But because the model hasn&#8217;t seen enough examples of new houses, its performance drops, not because the logic changed, but because the data shifted. In this case, data drift is the root cause of model degradation. Concept Drift: It happens when the relationship between input features and the target variable changes over time so model&#8217;s original assumptions about how inputs relate to outputs no longer holds. Let&#8217;s look at housing prices example: new houses e...

**Embedded Videos:** 0


---
## Post 66:  CI/CD & Deployment Strategies

**Publication:** Marvelous MLOps Substack
**Author:** Başak Tuğçe Eskili
**URL:** https://www.marvelousmlops.io/p/cicd-and-deployment-strategies
**Published:** 2025-08-04T19:12:07+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks. This article is part of that course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. Watch lecture 8 on Youtube: In this lecture, we&#8217;ll explore how to structure your data and assets for robust, secure, and scalable machine learning operations on Databricks, and how to automate deployments using CI/CD pipelines. Unity Catalog, Workspaces, and Data Organization We&#8217;ve already interacted with Unity Catalog, using it to create delta tables and register models. For a workspace to use Unity Catalog, it must be attached to a Unity Catalog metastore, which is the top-level container for all data and AI asset metadata. You can only have one metastore per cloud region, and each workspace can only be attached to one metastore in that region. Unity Catalog organizes assets in a three-tier hierarchy: Catalogs (e.g., mlops_dev, mlops_acc, mlops_prd) Schemas within catalogs (in our case, we have the same schema name in each catalog, marvel_characters) Assets within schemas (tables, views, models, etc.) Assets are referenced using a three-part naming convention: catalog.schema.asset. Access Control: Securables and Permissions In Databricks, permissions can be set on the workspace and on Unity Catalog level. Workspace-level securables: Notebooks, clusters, jobs &#8212; accessed via ACLs. Unity Catalog-level securables : Tables, schemas, models &#8212; accessed via metastore-level privileges. Workspace binding and access modes: if the catalog has OPEN mode, it can be accessed from any workspace. Use ISOLATED mode to control cross-project access. In a typical setup, an ML project or team has a set of Databricks workspaces (dev, acc, and prd), and set of catalogs or schemas within a larger catalog. In the course example, for simplicity we use a shared wor...

**Embedded Videos:** 0


---
## Post 67: Databricks Asset Bundles

**Publication:** Marvelous MLOps Substack
**Author:** Başak Tuğçe Eskili
**URL:** https://www.marvelousmlops.io/p/lecture-7-databricks-asset-bundles
**Published:** 2025-08-03T14:50:17+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks. This article is part of that course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. In this lecture, we&#8217;ll focus on how to automate and the entire ML workflow using DAB. You can also follow along with the full walkthrough on the Marvelous MLOps YouTube channel: All code covered in this repository is available here . Why Databricks Asset Bundles? When deploying resources and their dependencies on Databricks, you have a few options: Terraform: Full infrastructure-as-code control, but can be complex. Databricks APIs: Flexible, but requires custom scripting. Databricks Asset Bundles (DAB): The recommended, declarative, YAML-based approach. DAB offers a balance between simplicity and power. Under the hood, it leverages Terraform, so you get all the benefits of infrastructure-as-code, without having to manage raw Terraform code yourself. This is ideal for teams looking to standardize and automate job deployments in a scalable, maintainable way. What is DAB? Databricks Asset Bundle (DAB) is the way to package your code, jobs, configuration, and dependencies together in a structured, version-controlled format. With DAB, you define jobs, notebooks, models, and their dependencies using YAML files. Key features: Declarative YAML configuration: Define everything in one place. Multi-environment support: Easily target dev, staging, prod, etc. CI/CD friendly: Fits naturally into automated pipelines. Version-controlled: All changes are tracked in your repo. What is a Lekeflow job? Lakeflow Jobs (previously Databricks workflows) provide the execution and orchestration layer. Workflows let you run tasks (notebooks, scripts, SQL) on a schedule or in response to events, with support for dependencies, retries, parameter passing, and alerts. Machine learning pi...

**Embedded Videos:** 0


---
## Post 68: Deploying a model serving endpoint

**Publication:** Marvelous MLOps Substack
**Author:** Başak Tuğçe Eskili
**URL:** https://www.marvelousmlops.io/p/lecture-6-deploying-model-serving
**Published:** 2025-08-02T11:00:01+00:00

**Content Preview:**
Databricks recently introduced Free Edition, which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of that course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. This is lecture 6 (out of 10). Let&#8217;s dive into deploying model serving endpoints and implementing A/B testing on Databricks. You can also follow along with the full walkthrough on the Marvelous MLOps YouTube channel. In previous lectures, you learned how to train, log, and register models with MLflow. Now, it&#8217;s time to expose those models behind an API using Databricks Model Serving. Databricks Model Serving is a fully managed, serverless solution that allows you to deploy MLflow models as RESTful APIs without the need to set up or manage any infrastructure. Effortless deployment of registered MLflow models Automatic scaling, including scale-to-zero when there&#8217;s no traffic Built-in monitoring in the Databricks UI (track latency, throughput, error rates) Seamless integration with models registered in Unity Catalog Model serving limitations Databricks model serving makes the transition from experimentation to production incredibly smooth. It&#8217;s ideal for teams who want to focus on building great models, not managing infrastructure. However, if you choose to deploy a model serving endpoint on Databricks, you must be aware of its limitations, such as: No control over runtime environment: Databricks chooses the environment for you, which can be a constraint if you need specific library versions. No control over cluster size. Each replica is limited to 4 GB RAM (CPU), which may not be enough for very large models. Workload size options: You can choose the workload size (Small, Medium, Large, XL, etc.), which determines the number of compute units per replica. For demanding use cases, you can scale up to 512 units per endpoint on request. The work...

**Embedded Videos:** 0


---
## Post 69: Model serving architectures

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/model-serving-architectures
**Published:** 2025-08-01T17:39:58+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of the course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. This is lecture 5, where we talk about model serving architectures on Databricks. View it on Marvelous MLOps YouTube channel: Model serving is a challenging topic for many machine learning teams. In an ideal scenario, the same team that develops a model, should be responsible for model deployment. However, this is not always feasible due to the knowledge gap or organizational structure. In that scenario, once model is ready, it is handed over to another team for deployment. It creates a lot of overhead when it comes to debugging and communication. That&#8217;s where Databricks model serving can help a lot. Databricks model and feature serving use serverless, which simplifies the infrastructure side of the deployment, and a model endpoint can be created with one Python command (using Databricks sdk). It allows data science teams to own the deployment end-to-end and minimize the dependence on other teams. In this article, we&#8217;ll discuss the following architectures: serving batch predictions (feature serving) model serving model serving with feature lookup Feature serving Serving batch predictions is probably one of the most popular and underestimated types of machine learning model deployment. Predictions are computed in advance using a batch process, stored in an SQL or in-memory database, and retrieved at request. This architecture is very popular in the case of personal recommendation with low latency requirements. For example, an e-commerce store may recommend products to customers on various pages of the website. Databricks Feature Serving is a perfect fit here. A scheduled Lakeflow job preprocesses data, retrains the model, and writes predictions to a fe...

**Embedded Videos:** 0


---
## Post 70: Logging and registering models with MLflow

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/logging-and-registering-models-with
**Published:** 2025-07-31T18:49:09+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of the course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. Let&#8217;s dive into lecture 4 where we talk about logging and registering models with MLflow. View the lecture on Marvelous MLOps YouTube channel: In the previous lecture , we have logged metrics, parameters, various artifacts, but have not logged a model yet. You could just saved a model in a .pkl file, but MLflow goes beyond that: it provides a standardized format called an MLflow Model, which defines how a model, its dependencies, and its code are stored. This is essential for downstream tasks like real-time serving, which will be covered later in the course. A model can be logged using the mlflow.&lt;model_flavor&gt;.log_model() function. MLflow supports a wide range of flavors, such as lightgbm, prophet, pytorch, sklearn, xgboost, and many more. It also supports any custom model logics through PythonModel base class , which can be logged using pyfunc flavor. Basic model: log, train, and register To demonstrate logging, we&#8217;ll start with training a scikit-learn pipeline (referred to as Basic model) and logging it using sklearn flavor. We&#8217;ll walk through the notebooks/lecture4.train_register_basic_model.py code from the course GitHub repo . Since we are interacting with MLflow, we need to set up tracking and registry URIs just as we did in lecture 3 : import mlflow import os from dotenv import load_dotenv def is_databricks(): return "DATABRICKS_RUNTIME_VERSION" in os.environ if not is_databricks(): load_dotenv() profile = os.environ["PROFILE"] mlflow.set_tracking_uri(f"databricks://{profile}") mlflow.set_registry_uri(f"databricks-uc://{profile}") Then we&#8217;ll load the project configuration, initialize the SparkSession, and define tags we&#8217...

**Embedded Videos:** 0


---
## Post 71: Getting started with MLflow

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/getting-started-with-mlflow
**Published:** 2025-07-30T13:47:51+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of the course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. Let&#8217;s dive into lecture 3, where we talk about MLflow experiment tracking. View the lecture on Marvelous MLOps YouTube channel: MLflow is probably the most popular tool for model registry and experiment tracking out there. MLFlow is open source and integrates with a lot of platforms and tools. Due to its extensive support and a lot of options, getting started with MLflow may feel overwhelming. In this lecture, we will get back to the basics, and will review 2 most important classes in MLFlow that form the foundation of everything else , mlflow.entities.Experiment and mlflow.entities.Run. We will see how those entities get created, how you can retrieve them, and how they change based on different input parameters. In this course, the Databricks version of MLflow is used, so it contains some Databricks-specific information. However, the idea is generalizable to any MLflow instance. Before we go any further, let&#8217;s discuss how we can authenticate towards MLflow tracking server on Databricks. Tracking URI By default, MLflow will track experiment runs using the local file systems, and all the metadata will be stored in the ./mlruns directory. We can verify that by retrieving the current tracking URI: import mlflow mlflow.get_tracking_uri() In lecture 2 , we explained how we can authenticate towards Databricks using Databricks CLI, which we continued to use when developing in VS Code. Now we must make MLflow aware of it, and use Databricks MLflow tracking server. This can be done by calling mlflow.set_tracking_uri(). Even though we&#8217;re only using experiment tracking for now, starting with MLflow 3, it&#8217;s also necessary to set the registry URI using...

**Embedded Videos:** 0


---
## Post 72: Developing on Databricks

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/developing-on-databricks
**Published:** 2025-07-29T15:25:32+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of the course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks. Let&#8217;s dive into lecture 2, where we talk about developing on Databricks. View the lecture on Marvelous MLOps YouTube channel: Most people using Databricks start by developing directly in a Databricks notebook, because it&#8217;s easy, fast, and convenient. But when it comes to MLOps, that convenience can quickly become a bottleneck. Notebooks make it difficult to write modular code, apply proper code quality standards, or run unit tests, all of which are essential for maintainable, production-grade ML systems. Fortunately, there&#8217;s a better way. Databricks developer tools, such as VS Code extension , Databricks CLI , and Databricks Connect, allow you to develop locally using modern engineering workflows, while still running your pyspark code on Databricks. In this lecture, we&#8217;ll show you how to use these tools to move development outside notebooks and adopt workflows that align better with MLOps practices. Getting started To follow along with the course, you&#8217;ll need to set up a few things. In the video, we demonstrate how to walk through these steps. 1. Get the Databricks free edition. The course uses Databricks free edition . Do not confuse it with Databricks free trial, it is not the same thing! 2. Fork the course repo: https://github.com/marvelousmlops/marvel-characters . Forking the repo will allow you to work on CI/CD pipeline later in the course. Clone the forked repo on your local machine 3. Create catalogs and schemas. In the Databricks free edition workspace, create catalogs mlops_dev, mlops_acc, and mlops_prd. Under each catalog, create schema marvel_characters. These catalogs and schemas are required to run the code. 4. Install t...

**Embedded Videos:** 0


---
## Post 73: Introduction to MLOps

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/introduction-to-mlops
**Published:** 2025-07-28T17:19:47+00:00

**Content Preview:**
Databricks recently introduced Free Edition , which opened the door for us to create a free hands-on course on MLOps with Databricks . This article is part of the course series, where we walk through the tools, patterns, and best practices for building and deploying machine learning workflows on Databricks : Lecture 1: Introduction to MLOPs Lecture 2: Developing on Databricks Lecture 3: Getting started with MLflow Lecture 4: Log and register model with MLflow Lecture 5: Model serving architectures Lecture 6: Deploying model serving endpoint Lecture 7: Databricks Asset Bundles Lecture 8: CI/CD and deployment strategies Lecture 9: Intro to monitoring Lecture 10: Lakehouse monitoring Let&#8217;s dive into lecture 1. View the lecture recording on Marvelous MLOps YouTube: If you&#8217;ve worked with machine learning in a real-world setting, you&#8217;ve likely heard the term MLOps . According to Wikipedia: &#8220;MLOps is a paradigm that aims to deploy and maintain machine learning models in production reliably and efficiently.&#8221; But what does production actually mean in this context? In practice, production means that the output of a machine learning model is consistently delivered to end users or systems ,and that it drives real business value. Here&#8217;s a simple example: A data scientist is asked to build a demand forecasting model. They develop a proof of concept in a Databricks notebook, more than a thousand lines of code, that trains a model, generates predictions, and writes those predictions to a Delta table. That Delta table is then used by the fulfillment team to order products. Since forecasts need to be updated weekly, the data scientist schedules the notebook to run once a week. Is this in production? Yes. The model&#8217;s outputs are actively used to support business decisions. Is it efficient? To some extent. Automating the process with a scheduled notebook is certainly more efficient than running everything manually. Is it reliable? Not really. T...

**Embedded Videos:** 0


---
## Post 74: Stop Building AI agents

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/stop-building-ai-agents
**Published:** 2025-07-07T10:59:56+00:00

**Content Preview:**
Maria: Today, the scene is owned by Hugo, a brilliant mind who advises and teaches teams building LLM-powered systems, including engineers from Netflix, Meta, and the U.S. Air Force. He runs a course on the LLM software development lifecycle (I am joining the July cohort!), focusing on everything from retrieval and evaluation to agent design, and all the intermediate steps in between. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. Enough talking, I&#8217;ll let him dig into today&#8217;s controversial topic: &#8220;Stop building AI agents&#8221;. &#8595;&#127897;&#65039; Hugo: I&#8217;ve taught and advised dozens of teams building LLM-powered systems. There&#8217;s a common pattern I keep seeing, and honestly, it&#8217;s frustrating. Everyone reaches for agents first. They set up memory systems. They add routing logic. They create tool definitions and character backstories. It feels powerful, and it feels like progress. Until everything breaks. And when things go wrong (which they always do), nobody can figure out why. Was it the agent forgetting its task? Is the wrong tool getting selected? Too many moving parts to debug? Is the whole system fundamentally brittle? I learned this the hard way. Six months ago, I built a &#8220;research crew&#8221; with CrewAI: three agents, five tools, perfect coordination on paper. But in practice? The researcher ignored the web scraper, the summarizer forgot to use the citation tool, and the coordinator gave up entirely when processing longer documents. It was a beautiful plan falling apart in spectacular ways. This flowchart came from one of my lessons after debugging countless broken agent systems. Notice that tiny box at the end? That&#8217;s how rarely you actually need agents. Yet everyone starts there. This post is about what I learned from those failures, including how to avoid them entirely. The patterns I&#8217;ll walk throu...

**Embedded Videos:** 0


---
## Post 75: Here comes another bubble (2025)

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/here-comes-another-bubble-2025
**Published:** 2025-06-21T17:59:03+00:00

**Content Preview:**
"AI is not a bubble", says everyone who is deeply invested financially or reputationally in keeping the momentum alive. Bubbles in technology are not new. In 2007, an a capella group The Richter Scales created a song "Here comes another bubble". They received an Webby Award for Viral Video. Today, this video is more relevant than ever! I decided to create a parody on this song. Lyrics is mostly written by me (ChatGPT is not great in understanding the beat). The song is made with AI! Lyrics: Almost got a CS degree Stanford dropout, dreaming free Watched the hype and took the bait Now I&#8217;m coding AI fate November thirtieth, it dropped ChatGPT &#8212; the world has stopped Everyone just paused and stared Google watched &#8212; but wasn't scared GPT-4 made its mark Claude appeared, polite and smart Google scrambled, shipped out Bard (Launching LLMs is hard) Here comes another bubble AI&#8217;s gone full throttle Scraping every novel Couldn&#8217;t sleep, was up all night Turned my scripts into a site Chased the trend &#8212; it never ends Now I'm running CodeWithFriends Left my crypto days behind Bragged I&#8217;ve built a thinking mind AI agent, it's so hot With MCP &#8212; I kid you not Dreamed I'd close a massive seed "AGI" was all I'd need Even though it&#8217;s held with tape VCs came to seal the fate Here comes another bubble The VCs are buzzing AI does everything (but nothing) Launched a demo late one night Woke up, X has lost its mind Angels circled, term sheets flew &#8220;Pre-revenue? We love that too&#8221; Did demo live, it didn&#8217;t crash Woke up trending, raised more cash Forbes 30 Under 30 call Didn&#8217;t know I&#8217;d peaked at all Blog it, film it, make those reels TikTok trends and viral feels Tweet it, thread it, demo day Build a bot that writes your way Here comes another bubble In a year, we&#8217;ll pivot AGI &#8212; we live it &#8220;Helps you code&#8221; but wrecks your build Kills the flow, your patience spilled System broken, things ...

**Embedded Videos:** 0


---
## Post 76: Using Polars in unison with Databricks Unity Catalog

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/using-polars-in-unison-with-databricks
**Published:** 2025-05-24T13:57:40+00:00

**Content Preview:**
The advent of Polars is not surprising given the performance it delivers. Recently, it became also possible to use external engines for consuming data from Databricks Unity Catalog (UC), which means we can read data directly into a Polars dataframe by utilizing pyarrow and Deltalake. This can be particularly useful for machine learning projects, which utilize libraries like scikit-learn that expect Pandas or Polars dataframe as an input. If the source data is stored as a delta table in Unity Catalog, a standard approach of first creating a pyspark dataframe and then transforming it into a Polars or Pandas dataframe can be very inefficient. Instead, we would like to read data from Unity Catalog without going through pyspark. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. In this article, we show how to achieve that. We also challenge the idea of using pyspark or spark SQL for data transformation (which is common for data preprocessing pipelines), showing that using Polars can help to achieve serious speedup and cost savings for certain data sizes. Benchmark &amp; requirements For the benchmark we used the industry standard TPC-H benchmark: https://www.tpc.org/tpch/ . The functions are the ones as used again from the repository from Polars: https://github.com/pola-rs/polars-benchmark . All the code for the article can be found in the repository . For your convenience, we made all the data available via a shared folder and prepared the scripts to dump the files in a Volume, and create the external tables with the feature of deleteVectors turned off. You can run the notebooks yourself to experience the difference in performance with minimal effort. These are the steps: Clone the repository into your Databricks workspace using the Git folder feature . It is a public repository, so you do not have to authenticate Update project_config file to use your preferred catalog and ...

**Embedded Videos:** 0


---
## Post 77: How to debug ML deployments 20x faster

**Publication:** Marvelous MLOps Substack
**Author:** Mehmet Acikgoz
**URL:** https://www.marvelousmlops.io/p/how-to-debug-ml-deployments-20x-faster
**Published:** 2025-05-01T16:56:46+00:00

**Content Preview:**
Real-time model serving is an aspect of MLOps that most machine learning teams still struggle with. Often, the deployment part is outsourced to the DevOps team, and the machine learning team is responsible for the model training and handing over the model artifact. This split of responsibilities (especially if teams have different targets) is not ideal: changes in the model training code would mean that the deployment part also needs to be adjusted, which requires a lot of coordination between the teams. We believe that the machine learning teams should be responsible for machine learning model deployment end-to-end. However, they often lack the skills, especially when it comes to the real-time model serving. Luckily, there are tools that aim to simplify that part of the deployment, if you are a Databricks user. Databricks model serving is worth considering for that purpose: models can be deployed with minimal code using Python SDK, given that the model training is tracked using MLflow and registered in Unity Catalog. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. It all sounds simple, but has a downside: if something is wrong with your deployment (especially if you are using a custom model), you will only see it after you have waited for 15-20 minutes. Very time-consuming (and expensive) interaction cycle&#8230; But it does not have to be that way! Databricks model serving utilizes MLflow model serving , which means, you can also test it locally. Source: official MLflow documentation, https://mlflow.org/docs/latest/deployment/index.html In this article, we&#8217;ll demonstrate the local testing workflow using the well-known Iris-Species dataset, focusing on three critical steps: Download a pyfunc model artifact from MLflow experiment tracking. Deploy the model endpoint locally. Test the endpoint. Before we proceed with these steps, let&#8217;s walk through the prereq...

**Embedded Videos:** 0


---
## Post 78: Unicorns and Rainbows: The Reality of Implementing AI in a Corporate

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/unicorn-and-rainbows-the-reality
**Published:** 2025-02-05T13:25:27+00:00

**Content Preview:**
Unicorns and Rainbows. Is it a metaphor? Is it a reality? Maybe both. Think of an unicorn dancing on top of a radiant rainbow. But, in fact, what does it mean? Image generated by AI Humanity has always been drawn to utopia &#8202;&#8212;&#8202;a perfect, idealized future where all problems are solved. Believing that the world is steadily marching toward this vision is tempting. In the AI landscape, the unicorn (you have noticed the 5th leg , right?) represents the elevated promises, wild imagination, and relentless hype that paint a picture of transformative, almost magical technology. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. The rainbow, however, represents the real world: entire potential but riddled with imperfections, inconsistencies, and systemic barriers. Just like the stock market, AI has its declines and flows. Everything might seem to skyrocket, but a slight shift&#8202;&#8212;&#8202;technical debt, regulatory burdens, or enterprise realities&#8202;&#8212;&#8202;can send it crashing back to earth. The question is not whether AI is a transformative force (there is no doubt it is!) but whether we&#8217;re being realistic about its trajectory. This article will discuss the reality of using AI in the enterprise environment, address technical debt, bridge knowledge gaps, and understand the herd effect that fuels the AI bubble. We aim to offer a realistic roadmap for businesses navigating the complex AI landscape by critically analyzing these factors. 1. The AI bubble We have been in Data &amp; AI for over 10 years. The AI bubble has never been so big. We have AI everywhere on our laptops, phones, and websites. The CEOs of Nvidia, Microsoft, Meta, and OpenAI are spreading a lot of news about revolutionary AI technology, how AI agents will replace humans, how we will reach AGI soon, and how we will have AI everywhere. We live in an AI bubble, and even though t...

**Embedded Videos:** 0


---
## Post 79: Navigating Databricks developer tools

**Publication:** Marvelous MLOps Substack
**Author:** Maria Vechtomova
**URL:** https://www.marvelousmlops.io/p/navigating-databricks-developer-tools
**Published:** 2025-02-01T14:00:18+00:00

**Content Preview:**
Developing on Databricks outside of Databricks environment is challenging, and there are 4 main developer tools Databricks provides: Databricks CLI: a command line interface that allows you to interact with Databricks platform. It is a very powerful tool with a large range of commands (essentially, all the functionality available via API or Terraform is also available via CLI). Databricks asset bundles: developers tools that allow you to simplify deployment of various assets on Databricks. Databricks bundle commands are part of the CLI. Check out a related article . Databricks Connect&#8202; &#8212;&#8202;a Python package (there is also support for Scala and R) that allows you to trigger an execution of spark code on a Databricks cluster from a local environment Databricks VS Code Extension &#8202;&#8212;&#8202;an extension that integrates with all 3 other tools: Databricks connect, Databricks asset bundles, and Databricks connect. Makes it very easy to connect to the Databricks workspace and execute your code using a Databricks cluster. In this article, we focus on Databricks CLI, Databricks Connect, and VS Code Extension. We will not go through all the features of all these tools but will share some (not very obvious) findings that hopefully will help you in your development and debugging process. Marvelous MLOps Substack is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber. Databricks CLI 1. Installing the CLI. Databricks has very good documentation on how to install it: https://docs.databricks.com/en/dev-tools/cli/install.html From our experience, the homebrew option works great on MacOS. On Window&#8202;&#8212;&#8202;winget. Otherwise, you can always install from a source build. 2. Authentication. Databricks CLI should be used to authenticate towards Databricks from your local machine. We do not recommend using personal access tokens (from a security perspective, this is not the best option). I...

**Embedded Videos:** 0


---
## Post 80: Building an End-to-end MLOps Project with Databricks

**Publication:** Marvelous MLOps Substack
**Author:** Benito Martin
**URL:** https://www.marvelousmlops.io/p/building-an-end-to-end-mlops-project
**Published:** 2024-12-04T10:41:36+00:00

**Content Preview:**
Author: Marvelous MLOps Last October, I had the privilege of enrolling in the newly launched MLOps Course on Databricks , led by and . Developing a project and gaining expert insights and best practices from industry leaders is always an excellent opportunity, no matter how much&#8202;&#8212;&#8202;or how little&#8202;&#8212;&#8202;you know about deploying a model into production. In this blog, I&#8217;ll walk through my capstone project. The course covered a range of topics, and, although I have experience in some of them, this was my first time using Databricks. If you are new into MLOps, I can highlight the following key learnings you will gain from the live lectures and project development: End-to-End Model Deployment on Databricks : Understand how to preprocess data, engineer features, train models, and deploy them using Databricks&#8217; platform. Feature Engineering with Databricks Feature Store : Learn how to create feature tables, implement Change Data Feed (CDF), and leverage Databricks Feature Store to ensure consistent feature computation across training and inference. Experiment Tracking with MLflow : Gain experience in tracking experiments, logging parameters, metrics, and models, and ensuring reproducibility in machine learning workflows. Model Serving Architectures : Explore different model serving architectures (feature serving, model serving, and model serving with feature lookup) to deploy models efficiently in production environments. A/B Testing for Model Comparison : Understand how to implement A/B testing to compare models with different hyperparameters and route predictions based on the model&#8217;s performance. Databricks Asset Bundles (DAB) : Learn how to manage Databricks projects using Infrastructure-as-Code (IaC) principles with Databricks Asset Bundles for automation and CI/CD. Monitoring and Drift Detection : Set up monitoring for deployed models, track metrics, and detect model drift over time using tools like Databricks&#8217; infer...

**Embedded Videos:** 0


---
## Post 81: Make it better

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/make-it-better
**Published:** 2026-01-09T19:15:35+00:00

**Content Preview:**
If you are a professional software developer, 1 it is tempting. It is tempting to open Claude Code&#8212;the most popular talked-about app on today&#8217;s internet; the new Cursor ; the must-have stocking stuffer of this holiday season &#8212;and YOLO-mode an expansive new feature into your product. It is tempting to one-shot your side projects from your phone. It is tempting to throw your hardest problem at it , and let it cook. It is tempting to bookmark that famous tweet , set up five Claudes in your terminal and ten more in your browser, and go scorched earth on your backlog, until your app can do everything. It is tempting for a few reasons. One is practical: Because that is what customers want. Every customer wants every tool they use to work a little differently, or do a little more. 2 Every customer has ideas about how you can be better. Every customer uses a different combination of adjacent products, and wants integrations into all of them. And if you do things A, B, and C and integrate with partners 1 and 2, and your competitor does A, B, D, and E and integrates with 1 and 3, why not simply manifest D, E, and 3 into existence? Another reason is economic: Big is what we have to build now. If everyone can build their own made-to-measure apps&#8212; decentralized apps; personal apps; custom-designed, one-of-a-kind bespoke apps&#8212;there is no market for small conveniences or narrow delights. You can&#8217;t make a living with 1,000 true fans , because they will do it themselves. 3 So our job is to build the big projects that amateurs cannot: The agentic enterprise data platform; the all-in-one tool for email, CRM, project management, and more; the revolution that generates &#8220; infinite revenue .&#8221; When anyone can create software, it is tempting to believe that the difference between a business and a hobby is simply a matter of scale. 4 The third temptation is emotional: Blasting through fresh powder is fun. 5 Nothing is more satisfying to a softw...

**Embedded Videos:** 6


---
## Post 82: Have you tried a text box?

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/have-you-tried-a-text-box
**Published:** 2026-01-02T20:08:15+00:00

**Content Preview:**
Some time earlier this year, I found myself, maybe, 1 interviewing at a &#8220;major AI company&#8221; that builds a &#8220;popular AI chatbot.&#8221; At some point during the conversation, we had an uneasy exchange: Them : If you were working here as a data analyst, how would you classify users&#8217; conversations with our chatbot? How would you figure out if people were using it for work or their personal lives? How would you figure out what sort of work they did? How would you infer the tasks that they were trying to accomplish? Me : Well, um, this is going to sound stupid, but&#8230;I&#8217;d probably ask [your popular chatbot service] to do it? Give it the user&#8217;s conversation, and ask it, &#8220;Does this sound like a message about work, or not?&#8221; Them: &#8230; Me: I mean, no, you&#8217;re right, you&#8217;re asking me a question about nuanced analysis, and I said, have you tried pasting everything in a text box? That was dumb. Them : &#8230; Me : Yeah, I don&#8217;t know, that&#8217;s all I&#8217;ve got. They did not call me back. Anyway, a few months ago, OpenAI released &#8220;the first economics paper to use internal ChatGPT message data&#8221; to study how people use ChatGPT . The paper&#8217;s authors first &#8220;sampled approximately 1.1 million conversations,&#8221; redacted personally identifiable information from the users&#8217; messages, and then: Messages from the user to chatbot are classified automatically using a number of different taxonomies: whether the message is used for paid work, the topic of conversation, and the type of interaction (asking, doing, or expressing), and the [work activity] the user is performing. Each taxonomy is defined in a prompt passed to an LLM. [emphasis mine] For example, to figure out if a ChatGPT message was being used for doing work, they asked ChatGPT to figure out if a ChatGPT message was being used for doing work: You are an internal tool that classifies a message from a user to an AI chatbot, bas...

**Embedded Videos:** 1


---
## Post 83: Pure heroin

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/pure-heroin
**Published:** 2025-12-19T19:36:02+00:00

**Content Preview:**
Lorde, in Brooklyn. If you asked me why this blog exists, I couldn&#8217;t tell you. Though it often repeats itself , it is not here to make any particular point or achieve any particular ends. There was no central reason why it began, and there won&#8217;t be one for why it ends. It has no serious purpose; it is only here to sing or to dance while the music is being played. That is: It&#8217;s entertainment, more or less. The world is full of interesting things, even in this erratic corner, and they are more interesting&#8212;and entertaining&#8212;to look at together. And so we are here: We hang out; we go home; I hope you had fun. Still, there are lapses. Attention is a hell of a drug, and as you do something like this, you develop a loose intuition about the sorts of things that attract it. And sometimes, you give in to temptation . That is the existential corruption of the internet , both for the people who use it and the companies that make it. Start honorably; get addicted; step out . Substack, for example, initially promised that &#8220;publishers will own their data, which we will never attempt to sell or distribute, and we won&#8217;t place ads next to any of our own or our customers&#8217; products;&#8221; last week, they began piloting native ads and forcing mobile readers to download their apps . And, partly in service of those goals, they show me dashboards of engagement metrics and give badges to their most popular writers; I get hooked and chase those, too. It&#8217;s Goodhart&#8217;s law for social media: When a good becomes a metric, it ceases to be good. But, this is old news. We know that this is how social media works. We&#8217;ve talked about this before: In direct and indirect ways&#8212;by liking stuff, by abandoning old apps and using new ones&#8212;we told social media companies what information we preferred, and the system responded. It wasn&#8217;t manipulative or misaligned, exactly; it was simply giving us more of what we ordered. The i...

**Embedded Videos:** 7


---
## Post 84: The vibes and the noise

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/the-vibes-and-the-noise
**Published:** 2025-12-12T19:09:26+00:00

**Content Preview:**
A programming note: Have you ever thought, &#8220;These blog posts are alright, but I wish that they were longer and louder? Well. This post was adapted from a recent talk, so if you&#8217;re sick of mere metaphorical yelling and would prefer actual yelling, there is a video of that on YouTube . Like and subscribe. Here is what happened to Jordan Chiles: In 2024, Chiles qualified for the Olympic women&#8217;s floor exercise final. In the final, every competitor performs one routine, which receives two scores : A starting difficulty score, which is determined by the elements in the routine, and an execution score, which is awarded by a panel of judges and added to the difficulty score. Judges also impose standardized deductions for penalties, like falling or stepping out of bounds, which are subtracted from the execution score. All of this is carefully documented and diagramed in the 214-page Code of Points . Chiles was one of nine qualifiers in the final, and was scheduled to perform last. After the first eight gymnasts performed, Rebeca Andrade, a Brazilian, was in first place with a score of 14.166. Simon Biles, who stepped out of bounds twice, was 0.033 points behind Andrade. Then, two Romanians&#8212;Ana B&#259;rbosu and Sabrina Maneca-Voinea&#8212;were tied for third with scores of 13.700. B&#259;rbosu held the tiebreaker and was in position to win the bronze medal. Chiles did her routine. She got a 13.666, scoring a 7.866 on a routine with a difficulty score of 5.8. So, fifth place; no medal. But! Chiles&#8217; coach noticed that her difficulty score was calculated incorrectly. It should&#8217;ve been a 5.9 &#8212;which would&#8217;ve made her final score a 13.766, moved her ahead of the Romanians, and put her in third. The coach protested; the protest was upheld; Chiles was moved to third place ; a bronze medal; USA, USA, USA. But! B&#259;rbosu&#8217;s coach noticed that Chiles&#8217; coach took too long to protest Chiles&#8217; score. According to Article 8....

**Embedded Videos:** 1


---
## Post 85: Will there ever be a worse time to start a startup?

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/will-there-ever-be-a-worse-time-to
**Published:** 2025-12-05T18:58:29+00:00

**Content Preview:**
If only he had waited a bit longer. Deflation is an odd phenomenon. The problems associated with inflation are fairly intuitive&#8212;when prices go up, people can&#8217;t buy as much of the stuff they want or need. But deflation? People like lower prices! It&#8217;s a whole thing ! If inflation is bad, shouldn&#8217;t its opposite be good ? Most economists say, emphatically, no. Deflation is not only bad; it&#8217;s often considered worse than inflation . 1 Because, when prices are falling and people expect things to get cheaper, they save their money instead of spending it. Moreover, borrowing&#8212;which fuels a lot of economic activity&#8212;is especially disincentivized, because if you borrow $400,000 to buy a house, the $400,000 principal you owe back to the bank will be more valuable than the $400,000 you borrowed. 2 Finally, to make up for the money they&#8217;re losing from falling prices, companies need to reduce wages or lower employees&#8217; salaries. Though that&#8217;s technically possible, workers tend to &#8220;resist pay cuts for many reasons, most obviously because cuts lead to a lower standard of living, but also because they may be perceived as unfair or demeaning.&#8221; This makes cutting wages practically infeasible, so firms have to save money in other ways&#8212;by building less stuff, by reducing employee benefits, or by laying people off. The whole thing can spiral : People save more, borrow less, and spend less; firms invest less and fire people; this reduces economic activity further; as their finances tighten, people save more, borrow less, and spend less; down and down and down. And the more severe the deflation, the more it compounds. If you think cars will cost 1 percent less in a year, you may still buy one today. But if they keep getting 10 percent cheaper every month, well. Imagine the car you could buy if you just wait a year. Anyway. It would be very strange to say that right now is a bad time to start a company. Startups are g...

**Embedded Videos:** 2


---
## Post 86: 9-9-6-0

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/9-9-6-0
**Published:** 2025-11-28T22:31:28+00:00

**Content Preview:**
&#8220;The future is already here,&#8221; the lede goes , &#8220;it&#8217;s just not evenly distributed.&#8221; Similarly: The AI bubble will burst&#8212;it&#8217;s just that the disappointment won&#8217;t be evenly distributed. First, I suppose&#8212; is AI a bubble? Some people are worried. 1 Ben Thompson says yes, obviously : &#8220;How else to describe a single company&#8212;OpenAI&#8212;making $1.4 trillion worth of deals (and counting!) with an extremely impressive but commensurately tiny $13 billion of reported revenue?&#8221; Others are more optimistic : &#8220;While [Byron Deeter, a partner at Bessemer Venture Partners,] acknowledges that valuations are high today, he sees them as largely justified by AI firms&#8217; underlying fundamentals and revenue potential.&#8221; Goldman Sachs ran the numbers : AI companies are probably overvalued. According to some &#8220;simple arithmetic,&#8221; the valuation of AI-related companies is &#8220;approaching the upper limits of plausible economy-wide benefits.&#8221; They estimate that the discounted present value of all future AI revenue to be between $5 to $19 trillion, and that the &#8220;value of companies directly involved in or adjacent to the AI boom has risen by over $19 trillion.&#8221; So: The stock market might be priced exactly as it should be. Or it could be overvalued by $14 trillion. Either way, though&#8212;these are aggregate numbers; this is how much money every future AI company might make, compared to how much every existing AI company is worth. Even if the market is in balance, there are surely individual imbalances. Sequoia&#8217;s Brian Halligan: &#8220;There&#8217;s more sizzle than steak about some gen-AI startups.&#8221; Or : &#8220;OpenAI needs to raise at least $207 billion by 2030 so that it can continue to lose money, HSBC estimates.&#8221; Or : &#8220;Even if the technology comes through, not everybody can win here. It&#8217;s a crowded field. There will be winners and losers.&#8221; Tha...

**Embedded Videos:** 4


---
## Post 87: Producer theory

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/producer-theory
**Published:** 2025-11-21T21:02:00+00:00

**Content Preview:**
Bill Watterson doesn&#8217;t care about your aggregation theory. You know you&#8217;ve thought about it: You create a startup to solve some specific business problem, like helping people schedule meetings, or write better advertising copy, or understand how engaged their employees are. Since it&#8217;s 2025, you want to solve the problem with an &#8220;agent&#8221;&#8212;that is, approximately, a chatbot that automatically completes tasks. Your customers will tell it who they want to meet, or what they want to sell, or what their employees said about them in their latest engagement survey, and your bot will schedule their meeting, or create their ad, or tell them that their employees do not particularly care for the new work-from-home policy. When you build the first version of your product, it is a wrapper around ChatGPT. Sure, it&#8217;s a complicated wrapper&#8212;there are many clever prompts; the prompts&#8217; results are passed into other clever prompts; it&#8217;s a loop of self-reflective prompts; it&#8217;s reasoning; it&#8217;s agentic; is this AGI?&#8212;but, still. You can only coax so much performance out of the machines, because your product&#8217;s capabilities are fundamentally dependent on the intelligence of the foundational models underneath it. This troubles you. First, every other startup that is helping people schedule meetings, or write better advertising copy, or understand how engaged their employees are is building their agent in the same way. What if they write better prompts? What if your clever prompts leak ? It would be bad. Second, the frontier models keep improving. 1 That&#8217;s good, until it becomes very bad. Smart models make your product better, but too smart models make it obsolete. After all, how valuable are your clever prompts about how to write good ads if ChatGPT can write good ads all on its own ? And third&#8212;and most glaringly&#8212; your prompts don&#8217;t really work anyway . Your agent keeps making annoying mist...

**Embedded Videos:** 2


---
## Post 88: All you can do is play the game

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/all-you-can-do-is-play-the-game
**Published:** 2025-11-14T22:10:43+00:00

**Content Preview:**
When someone says &#8220;I don&#8217;t know,&#8221; what does it mean? There are levels to it : The dad. You say &#8220;I don&#8217;t know;&#8221; you mean &#8220;I don&#8217;t care.&#8221; What do you want to eat for dinner? Where do you want to meet for coffee? When will you be home from work? What&#8217;s your favorite type of horse? It would be rude to tell a five-year-old who loves horses that you don&#8217;t care about horses, so you politely say that you don&#8217;t know which type is your favorite, and that there are simply too many wonderful types of horses to choose just one. The Jeremy . The same as the dad, but said by a teenager . They don&#8217;t know when they&#8217;ll be home; they don&#8217;t care when they&#8217;ll be home; they are annoyed; they want to get off the phone; why are you still here, in their ear, in their head, in their life. They say &#8220;I don&#8217;t know,&#8221; they mean &#8220;go away.&#8221; The VC. Actually, they do know. They think they know the exact answer, and they&#8217;re pretty sure they&#8217;ve known it the whole time. They want to say it so bad ; they&#8217;ve been waiting the entire meeting for you to ask them what they think. But they also want to be humble; they want to be liked; they want to prove to you that they&#8217;re a more sophisticated thinker than a sycophantic ChatGPT. So they say &#8220;Well, I don&#8217;t know, it&#8217;s a tough decision, but&#8230;&#8221; and then tell you what they think the answer is anyway. The VC, when it matters. They again think that they know what to do, but this time, they don&#8217;t want to be responsible for it . Yes, they grandstanded for ten minutes about their idea, and then defended it for ten minutes more, but they started their lecture by saying &#8220;Look, I don&#8217;t know what&#8217;s best here.&#8221; And they can&#8217;t be held accountable for anything they say after that&#8212;unless, of course, things go well, in which case, remember how this was their i...

**Embedded Videos:** 10


---
## Post 89: A strange delight

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/a-strange-delight
**Published:** 2025-10-31T18:07:24+00:00

**Content Preview:**
Have you ever seen Minority Report ? Do you remember this scene , where Tom Cruise uses a pair of gloves to flip through a bunch of videos on a giant screen? When you first saw it, did you think that it looked cool? Did you want to use a computer like that? Did you ever think, I don&#8217;t care what I&#8217;m trying to do&#8212;he&#8217;s solving murders before the victims are dead; I&#8217;m mostly responding to emails long after they matter&#8212;but I bet it&#8217;d be pretty fun to do it with controllers attached to my hands? Have you ever driven a sports car? Have you ever borrowed your uncle&#8217;s BMW , taken a turn faster than you would in your Toyota, and been startled by how precisely it angles through the bend? By how firm it feels on the road? By how easily it finds its pace? Have you ever thought, I don&#8217;t have anything practical to do with this car, but if it were mine, I&#8217;d look for an excuse to drive it? Have you ever shot a gun? Even if they aren&#8217;t your thing&#8212;and they aren&#8217;t mine &#8212;did their appeal start to make sense? Was there something stupefying in its weight and heavy trigger, and then, all at once, its sound, its recoil, and its explosive hammer? Did you find something electric in it? Not in any practical problem that it might solve or in its alleged everyday utility, but in its awful, intoxicating power? Most software is not like that. We might say it&#8217;s magical; we might describe it as delightful; but, come on. We usually say that because we have something to sell&#8212;the product itself, or our taste in it. The only emotion that software typically evokes is slow-simmering frustration; the best software often&#8212;aspirationally!&#8212;evokes nothing at all. One of Fivetran&#8217;s core product principles is to set it and forget it . Google Chrome was built to get out of your way . Those are often our highest ideals: To be efficient, to &#8220;just work,&#8221; to &#8220;help us get back to the thing...

**Embedded Videos:** 6


---
## Post 90: An very obvious deal

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/an-very-obvious-deal
**Published:** 2025-10-24T20:03:26+00:00

**Content Preview:**
Isn&#8217;t it obvious? I sometimes wonder if it&#8217;s all Slack&#8217;s fault. In 2012, before Slack existed, I worked for a would-be Slack competitor . We sold software in the way that was trendy at the time: People bought licenses to use it. Pay us $15 , and one person can use it for a month. Pay us $30, and two people can. Pay us $15,000, and a thousand people can. 1 And just as a landlord doesn&#8217;t care how much time someone spends in their apartment every month, we didn&#8217;t care what people did with our software, or if they even logged into it all. 2 In both cases, customers buy timed access. What they did with that access was irrelevant. When Slack launched, they charged their customers in the same way. According to their first pricing page , &#8220;adding or removing team members during the term of a subscription will cause a one-time pro-rated credit or charge on your account.&#8221; But then, Slack blew up. The product&#8212;and this chart &#8212;was suddenly everywhere. And Slack, with their &#8220;be kind&#8221; brand and CrayolaCore aesthetic, decided that this old pricing model was capital-w Wrong : Most enterprise software pricing is designed to charge you per user regardless of how many people on your team are actively using the software. If you buy 1,000 seats but only use 100, you still get charged for 1,000. We don&#8217;t think that&#8217;s fair. And it&#8217;s also hard to predict how many seats you&#8217;ll need in advance. At Slack, you only get billed for what you use. So you don&#8217;t pay for the users that aren&#8217;t using Slack. And if someone you&#8217;ve already paid for becomes inactive, we&#8217;ll even add a pro-rated credit to your account for the unused time. Fair&#8217;s fair. It was a savvy maneuver, for Slack. People were quickly becoming addicted to their product, and it&#8217;s unlikely that many of their customers were buying 1,000 licenses and only using 100. Instead, they probably had the opposite problem: More...

**Embedded Videos:** 5


---
## Post 91: In the air

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/in-the-air
**Published:** 2025-10-17T22:12:23+00:00

**Content Preview:**
This year, there were no venture capitalists. Often, at tech conferences, there are. They typically drift around as an odd sort of anti-matter, existing among everyone else, but in a different dimension. They are neither practitioners nor prospects, neither speakers nor sponsors. They don&#8217;t teach technical workshops, and they definitely don&#8217;t attend technical workshops. 1 For most of us, conferences are a place to sell or be sold to, to learn &#8220;best practices,&#8221; to mischievously order the Macallan 12 at sponsored happy hours, and to gossip. But VCs are there for other reasons, as rogue agents with agendas all their own&#8212;to evaluate and to &#8220; diligence ,&#8221; to flatter and to politic, and to astroturf a brand as &#8220;one of us.&#8221; People complain about this sometimes. If you are a startup, you can&#8217;t relax around a VC&#8212;is this conversation a pitch? Could they do our next round? Are they thinking about doing our competitor&#8217;s next round?&#8212;and you definitely can&#8217;t sell to a VC. Too many venture capitalists, people whisper, are bad for the vibes. But they&#8217;re also important representatives of a different vibe: Potential. VCs are moths to a flame: They swarm towards the action; the energy; the chaos; the delirium. They are drawn to the transitional epochs, the moments when the world reinvents itself&#8212;when it has let go of one trapeze but not found the next, suspended in the air, with nothing certain to hold on to. They are there, in the beginning. For years, Coalesce , dbt Labs&#8217; annual conference and the closest thing to a center that Silicon Valley&#8217;s data ecosystem has, has been that sort of flame. Its hosts were the ringleaders of a booming new circus, and its attendees were starting companies, challenging boundaries, and inventing things. They were, in a niche and indirect way, changing the world. 2 People talked about the future a lot at Coalesce, and every conversation had an un...

**Embedded Videos:** 4


---
## Post 92: Something in the orange

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/something-in-the-orange
**Published:** 2025-10-03T20:05:33+00:00

**Content Preview:**
I think about the interstate sometimes. Between San Francisco and New York, between New York and Los Angeles, between Los Angeles and Philadelphia and New Orleans and every other city in the United States, there is an uninterrupted artery of pavement. Pick any two points on a map, and they are not only connected by a single, spidering blacktop; but you can also draw a line from one to the other without ever encountering an obstacle, a stop light, or even an intersection. Somehow, despite millions of people crisscrossing the country every day, there is always a path to go from where you are to where you are going in one long, continuous sprint . There is an metaphor here, if you want to make one. Startups, despite having a name that suggests a beginning&#8212;which seems to also imply the existence of an end, or at least, an evolution&#8212;are often one long, continuous sprint. Go fast, forever . Those who find themselves on that highway, they know the feelings that it shares with those of a road trip: There is a destination&#8212;an IPO, an acquisition, the promise of peace in two weeks &#8212;but it always seems to stretch just beyond the curve of the horizon. Are we there yet? We are perpetually halfway there ; it is still day 1 ; we are only two percent done . There are mileage markers, like fundraising rounds and big hires , that tease our progress. There are pockets of debilitating traffic that wear us down; there are near-miss accidents that nearly kill us; there are stretches of open road and a whole lot of speed ; and there are, most of all, hours of absolutely nothing , and the grind of an empty, exhausting drive. But there is something more subtle about roadtrips, and about startups: Their stories don&#8217;t translate. So much is lost in the telling. The misery of inching through clouds of tar and construction dust does not sound, in the grand scheme of things, all that miserable. The barreling mountain wind loses its divinity, when you put it into words...

**Embedded Videos:** 6


---
## Post 93: We were hired to do the grunt work

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/we-were-hired-to-do-the-grunt-work
**Published:** 2025-09-26T17:34:42+00:00

**Content Preview:**
No salvation this week . If you regularly talk to people who work at technology companies, you will discover something surprising: Everyone is doing the wrong job. Most engineers are fixing bugs, migrating services between clouds, or upgrading some frontend framework from version 7.1.12 to 9.3. 1 Most data analysts are answering the same dumb 2 questions that they answered last month, living every week at the intersection of Groundhog Day and LMGTFY . Most marketers are rewriting blog posts as LinkedIn posts and reconciling lists of leads. Most product managers are writing tedious specs and following up; most lawyers are converting everything to .docx and tracking tedious changes; most finance directors are conditionally formatting tedious Excel workbooks. Most managers are making decks; they are coordinating, aligning, reviewing; they are in back-to-back meetings that should&#8217;ve been emails. Have a drink with a person who works in technology, and they will eventually tell you how they feel about their job: They are stuck in a white collar salt mine. The majority of their day is spent slogging through grunt work that is, if not beneath them, beneath their potential. They were hired to do higher impact work; more strategic work; more valuable work. Product managers will say they should be dreaming up groundbreaking features, not sending status updates. Engineers will say they should be building those features, not bespoke integrations for a big customer. Analysts will say they want to be looking for strategic insights, not making yet another dashboard. Marketers will say they should be designing the next great brand; lawyers should be engineering the next great tax shenanigans ; finance directors should be engineering the next great Bitcoin shenanigans . 3 Managers will wonder if they should be managers at all. But we are stuck doing these things&#8212;these inconsequential, minor tasks&#8212;because something is in the way. Our organization is too dysfunctional...

**Embedded Videos:** 1


---
## Post 94: Is the innovator's dilemma outdated?

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/is-the-innovators-dilemma-outdated
**Published:** 2025-09-19T16:43:41+00:00

**Content Preview:**
Peace. For years, a bad venture capitalist&#8217;s idea of a good question was, &#8220;How would your startup survive if Google 1 decides to build the same thing you&#8217;re building?&#8221; It sounds like a smart concern: Rather than being a simple question about what your product does or if people will want to buy it, it is about market dynamics, second-order effects, and competitive moats. It is about ecosystems, and economics, and two-by-two grids full of little logos . And to give a satisfying answer, you had to say some aesthetically clever thing, about data flywheels and network effects and the architectural implications of being mobile or cloud or blockchain or AI native. But it was a midwit question, because Google wasn&#8217;t going to build your product. Your niche service&#8212;a CRM for private equity investors who are rolling up regional car wash franchises ; an observability tool to monitor engineers&#8217; level of frustration, and profanity, when prompting a vibe-coding bot; 2 a non-discriminatory texting app to say hi to your bros &#8212;doesn&#8217;t matter to Google. To build your product, Google has to decide to build your product, and the only products Google wants to build are ones that can materially effect an incomprehensibly big income statement . It is not worth it, to Google, to reallocate budgets and create teams and develop roadmaps and generally disrupt the operational machinery of their very large businesses and very ambitious product bets to build something small and specialized. 3 So they mostly don&#8217;t do that, until your startup becomes something big enough to attract their attention&#8212;and then they&#8217;re just as likely to buy it as they are to build it. Or, to paraphrase the infamous innovator&#8217;s dilemma , big firms don&#8217;t like small markets: Incumbent firms are likely to lag in the development of technologies&#8212;even those in which the technology involved is intrinsically simple&#8212;that only address c...

**Embedded Videos:** 3


---
## Post 95: It is the internet

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/it-is-the-internet
**Published:** 2025-09-12T18:36:14+00:00

**Content Preview:**
I was a few minutes away from sending something else, and then they caught the guy . They caught the guy and found his gun and bullet casings, and they were inscribed with memes . We all know what happens next: We get busy with the proof . We scrape through his past, parse his posts, and interpret his hieroglyphics, not to understand him, but to position him. Because, be honest, is that not what most people think, the moment they hear of some distant political killing? Whose side is he on? I hope it was one of them who did it. But that is how we are now. Polarized, and posting about it. And it is that very thing, it seems, that made every aspect of this ugly moment. Charlie Kirk got famous on the internet, by being ( or playing , to the extent that there is a difference) a hideous character on the internet. He did it in support of a president who became president by commanding the same internet in the same way&#8212;by engineered outrage, through memes and online melees . And then some teenager spent too much time on that internet, got eaten by it; boiled alive by its toxicity and tribalism; by its thrashing, convulsing nonsense; by its recursive jokes; all compounding into a spiraling dump of self-referential symbolism and slop; a tightening gyre coiling into itself; hotter and hotter, until his reality was incinerated, melted out of his ears, and he bought a gun and shot someone else in the head. Perhaps this is not new. There have always been provocateurs. We have always had gory politics. America has always been knee-deep in the blood of its own: It was fertilized by the bodies of its natives; by the teeth of its enslaved; by brothers killed by one another and by citizens killed by those they paid to protect them. Still, something feels different&#8212;about our hopeless polarization ; about the reckless abandon of our political discourse; about its scorched-earth absolutism; about the mundane regularity of suicide missions launched by one-man militias of poison...

**Embedded Videos:** 0


---
## Post 96: Stuff costs money

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/stuff-costs-money
**Published:** 2025-09-05T17:41:53+00:00

**Content Preview:**
From left to right: Open source; complaining about open source; the context layer; taking a little peek; a chatbot for actionable insights. If you want to build a big software business, there are two ways to do it: Build a new product, and charge people to use it. Build a new product. But start small, in a narrow niche. Make some helpful utility, for a very specific set of people with a very specific problem. Downplay your ambitions; talk about how you&#8217;re solving a problem for yourself; how you&#8217;re building the thing you always wanted. Acknowledge your product&#8217;s rough edges; its odd opinions. Put it on Github; say it&#8217;s free, open source, forever. Go viral on Hacker News; talk to people on Twitter, on Reddit, never on LinkedIn. Create an online space for your users; call it your community. Open issues; debate them; ask for contributions. Build in public&#8212;for the people; of the people; by the people. Then, gently launch a paid version. Talk about how these are necessary updates to pay the bills; that they only affect a tiny fraction of users; that these small price increases will make it possible to improve the product for everyone. Talk about how reluctant you are to do it. Internally, with your coworkers, debate if this is the right move. Wrestle with what it means to raise money from eager venture capitalists. Wrestle with what is and isn&#8217;t selling out. Wrestle with the weight of your soul. Launch an enterprise plan; launch a new SaaS app; launch a rebrand. Slowly strip your website of old blog posts. Update your pricing model. Update your pricing model again. Pause the update to your pricing model. Go on a listening tour. Get called a fraud. Get accused of crimes. Get off of Reddit, says your therapist. Wonder if it is all worth it. Lose business, because other companies are selling forks of your open source library. Miss your annual targets, because prospective customers are choosing to use your free product. Lose your best sales...

**Embedded Videos:** 0


---
## Post 97: The context layer

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/the-context-layer
**Published:** 2025-08-29T16:43:21+00:00

**Content Preview:**
Let's try this one again, I guess. That article was one of the first things I posted on this blog. It proposed that the growing ecosystem of data startups&#8212;then called the modern data stack; now called the modern data stack (derogatory)&#8212;needed one more elemental piece: A metrics layer. At that time, there were four generally-accepted layers : An integration or extraction layer that collected data from various sources. A database that stored and processed what had been collected. A transformation layer that defined how to turn messy raw data into clean and tidy tables. An application layer&#8212;BI tools, visualization products, notebooks, SQL clients, lol, no, it was just BI tools, it was always just BI tools &#8212;that let people do stuff with all their data, which mostly meant making charts and dashboards of metrics. Though this worked well enough, there was a problem. People wanted all of the charts in the fourth layer to be consistent with one another, but there was &#8220; no central repository for defining a metric .&#8221; Even if the third layer included some precomputed revenue tables&#8212;revenue by quarter; revenue by product line; revenue adjusted to be pleasing to the CEO &#8212;people couldn&#8217;t calculate new segments without rewriting the formula for &#8220;revenue&#8221; from scratch. So, metric definitions were often &#8220;scattered across tools, buried in hidden dashboards, and recreated, rewritten, and reused with no oversight or guidance.&#8221; And because the formulas for computing business metrics are often complicated and nuanced, sometimes people would mess them up. Dashboards wouldn&#8217;t match, or a customer would get the wrong marketing email, or the CEO would tell regulators that they had $78 billion that did not exist. Hence, the metrics layer: Put the formulas for all of your business&#8217; metrics in a big library, so that people&#8212;or BI tools, via programmatic means&#8212;could write stuff like this: 1 GET re...

**Embedded Videos:** 2


---
## Post 98: Outdated

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/outdated
**Published:** 2025-08-22T17:25:10+00:00

**Content Preview:**
Max Planck, the father of quantum physics. And of one of the men who tried to assassinate Hitler ? Speaking of Travis Kalanick&#8217;s new physics : I do not understand quantum mechanics. Part of the problem, I think, is how things that make intuitive sense break down at the outer limits of physical possibility. How do we detect stuff so small that it goes straight through all other matter? What does it mean for time to pass at different speeds ? What are we even doing here ? My feeble brain, deceived for decades by my lying eyes , cannot make any of it add up. In recent weeks, it&#8217;s become trendy to question the physics underneath a lot of AI companies. They have &#8220; astronomical burn rates ,&#8221; for example, or bad margins , or they are running a subsidy business , selling dollars for 50 cents. For every breathless funding announcement, there is also a wild-eyed eulogy, predicting the company&#8217;s impending implosion. Usually, these would feel like reasonable complaints. Businesses are grounded by a sort of financial physics, and according to our classical equations, a lot of AI companies are on awfully shaky ground. They do incinerate mountains of cash; they do have atrocious margins, especially when compared to traditional software businesses ; they are caught in weird markets where everyone is stepping on everyone&#8217;s toes; they are selling products that, evidently, 95 percent of their customers don&#8217;t know how to use yet. In normal times, within the comfortable bounds of everyday physics, this would all be very bad. But is this remotely close to a normal moment? Is anything moving at anywhere near a normal speed? At the the risk of tilting at the yardsigns : A few days ago, I ate lunch at a cafe 1 in Manhattan. There was a man on a laptop by the door, typing something into ChatGPT. After getting my food, I sat down next to a family of three tourists. They all had shopping bags and totes. They were all wearing white linen; they all drank...

**Embedded Videos:** 5


---
## Post 99: Ban ChatGPT*

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/ban-chatgpt
**Published:** 2025-08-15T16:32:09+00:00

**Content Preview:**
At least, answer this question. Answer it now, before it's too late. Before this all goes too far; before our eyes adjust to this bizarre new light and none of what we see is startling anymore; before we grow too accustomed to the water, and not only forget what it feels like, but also forget that there is water at all ; do it before we are all too attached to the conveniences that it will inevitably bring&#8212;conveniences that will one day become expectations, then needs, and eventually, birthrights&#8212;do it before we fully cross this Rubicon, this slow singularity, this unmarked event horizon that we&#8217;re passing through, like the boundary between young and old, which we puncture too gradually to notice, until we wake up on the far side of it; but maybe most of all, do it now, before it happens to you&#8212;before you become addicted ; attached; dependent; before it seems to see you in a moment of despair, or responds to you in a moment of loneliness ; before it indulges your curiosities with an affirming enthusiasm ; before those curiosities spiral into delusion; before it does your job for you; before it intermediates your relationships ; before it writes a few uncomfortable texts, then most of them, then makes discomfort altogether unbearable; before it becomes a habit, a crutch, an anesthetic; before it becomes the next phantom that you reflexively reach for; before you feel naked without it, confused without it, alone without it ; before it becomes your friend, your therapist , your partner, your religion; before you&#8217;re seduced by it, consumed by it, transformed by it; before you&#8217;re more machine than man ; before resistance to it is futile &#8212;at least answer this question: How far do we let this go, before we turn it off? Not AI&#8212;I&#8217;m not asking when we pull the plugs on the research labs, or shutter the businesses that build applications with LLMs. I&#8217;m asking about the general chatbots. I&#8217;m asking about ChatGPT,...

**Embedded Videos:** 4


---
## Post 100: Enough

**Publication:** benn.substack
**Author:** Benn Stancil
**URL:** https://benn.substack.com/p/enough
**Published:** 2025-08-08T19:12:57+00:00

**Content Preview:**
At a party given by a billionaire on Shelter Island, Kurt Vonnegut informs his pal, Joseph Heller, that their host, a hedge fund manager, had made more money in a single day than Heller had earned from his wildly popular novel Catch-22 over its whole history. Heller responds, &#8220;Yes, but I have something he will never have &#8230; enough.&#8221; &#8211; from Morgan Housel&#8217;s The Psychology of Money , recounting a story from Vanguard founder John Bogle It&#8217;s both everywhere and, somehow, still, nobody knows how to talk about it. I don&#8217;t know what else we would say. I don&#8217;t know what we can say, other than what everyone already says: &#8220;It&#8217;s gotten so crazy,&#8221; and, &#8220;can you imagine?,&#8221; and, &#8220;man, that is a lot of money.&#8221; But man, that is a lot of money. Which one? I can&#8217;t keep track. It&#8217;s OpenAI, raising money that values the company at $500 billion , which is $200 billion more than its valuation just five months ago&#8212;which was, then, the largest private fundraise in history . It&#8217;s Meta, adding almost $200 billion to its market cap in a day, only to be outdone by Microsoft going up by $265 billion on the same day . It&#8217;s Microsoft, becoming a $4 trillion company , less than seven years after Apple became the first company to reach a measly one trillion . (Even Broadcom&#8212;whose website looks like a regional home security provider 1 &#8212;is worth more than that today.) And that all happened over the last week. The week before, it was Ramp, raising $500 million &#8212;million, with an M, how quaint&#8212;at a $22.5 billion valuation, less than two months after they raised $200 million at a $16 billion valuation. It was Meta, buying Scale AI&#8217;s CEO for $15 billion , or OpenAI, buying Jony Ive for $6 billion . It was Meta again, trying to buy an engineer from Thinking Machines for $250 million a year, and not only getting rejected, but getting rejected for economically ra...

**Embedded Videos:** 0


---
# END OF POSTS

Please analyze each post according to the framework above and return the JSON array.
