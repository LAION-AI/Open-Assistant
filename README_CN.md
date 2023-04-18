[English](./README.md) | 简体中文

<h1 align="center">
    <span>Open-Assistant</span>
  <img width="auto" height="50px" src="https://github.com/LAION-AI/Open-Assistant/blob/main/assets/logo_crop.png"/>
</h1>

<div align="center">

<a href="https://github.com/LAION-AI/Open-Assistant/stargazers">![GitHub Repo stars](https://img.shields.io/github/stars/LAION-AI/Open-Assistant?style=social)</a>
<a href="https://laion-ai.github.io/Open-Assistant/">![Docs](https://img.shields.io/badge/docs-laion--ai.github.io%2FOpen--Assistant%2F-green)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/build-frontend.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/build-frontend.yaml?label=build-frontend)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/build-postgres.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/build-postgres.yaml?label=build-postgres)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/pre-commit.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/pre-commit.yaml?label=pre-commit)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/test-api-contract.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/test-api-contract.yaml?label=tests-api)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/test-e2e.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/test-e2e.yaml?label=tests-web)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/deploy-docs-site.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/deploy-docs-site.yaml?label=deploy-docs)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/production-deploy.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/production-deploy.yaml?label=deploy-production)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/release.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/release.yaml?label=deploy-release)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/releases">![GitHub release (latest by date)](https://img.shields.io/github/v/release/LAION-AI/Open-Assistant)</a>

</div>

# 目录

- [什么是开放式助手?](#what-is-open-assistant)
- [有用的链接](#useful-links)
- [如何尝试](#how-to-try-it-out)
- [愿景](#the-vision)
- [计划](#the-plan)
- [您如何提供帮助](#how-you-can-help)

---

## 什么是开放式助理？

<p align="center">
Open Assistant是一个项目，旨在使每个人都可以访问基于聊天的大型语言模型。
</p>

我们相信，通过这样做我们将在语言创新方面创造一场革命. 就像稳定扩散帮助世界以新的
方式制作艺术和图像一样, 我们希望开放助手可以通过改善语言本身来帮助改善世界

# 有用的链接

- [数据收集](https://open-assistant.io)

- [聊天](https://open-assistant.io/chat)

- [项目文件](https://projects.laion.ai/Open-Assistant/)

## 如何尝试

### 与 AI 聊天

可以聊天的前端页面在[这里](https://open-assistant.io/chat). 登录并开始聊天!聊天
时请尝试对助手的回答使用大拇指做出反应。

### 贡献数据集

数据收集前端现在在[这里](https:// open-assistant.io/)。登录并开始承担任务!我们希
望收集大量高质量的数据。通过提交，排名和标签模型提示和响应，您将直接帮助提高
Open Assistant 的功能。

### Running the Development Setup Locally (without chat)

### 在本地运行开发设置 (没有聊天)

**除非您正在为开发过程做出贡献，否则您不需要在本地运行项目。上面的网站链接将带您
到公共网站，您可以在其中使用数据收集应用程序和聊天**

如果您想在本地运行数据收集应用程序以进行开发，则可以使用 Docker 设置运
行**Open-Assistant** 所需的整个堆栈，包括网站，后端和关联的依赖服务。

要启动演示，请在存储库的根目录中运行, 如果你遇到任何问题, 请在这里查
看[常见问题](https://projects.laion.ai/Open-Assistant/docs/faq#docker-compose-instead-of-docker-compose)

```sh
docker compose --profile ci up --build --attach-dependencies
```

然后，打开浏览器[http://localhost:3000](http://localhost:3000) (启动可能需要一些
时间) 并与网站进行交互。

> **注意:** 如果构建出现问题，请前往并查看有关 Docker 的条目
> 。[FAQ](https://projects.laion.ai/Open-Assistant/docs/faq)

> **注意:** 通过电子邮件登录时，导航到
> [http://localhost:1080](http://localhost:1080) 以获取神奇魔法的电子邮件登录链
> 接。

> **注意**: 如果您想在本地使用 vscode 的标准化开发环
> 境["devcontainer"](https://code.visualstudio.com/docs/devcontainers/containers)
> 中[vscode locally](https://code.visualstudio.com/docs/devcontainers/create-dev-container#_create-a-devcontainerjson-file)或
> 在使用[GitHub Codespaces](https://github.com/features/codespaces)代码的 web 浏
> 览器中运行此代码，则可以使用提供的[`.devcontainer`](.devcontainer/)文件夹。

### Running the Development Setup Locally for Chat

### 在本地运行开发设置以进行聊天

**除非您正在为开发过程做出贡献，否则您不需要在本地运行项目。上面的网站链接将带您
到公共网站，您可以在其中使用数据收集应用程序和聊天**

**另请注意，除非您知道自己在做什么，否则本地设置仅用于开发，并不打算用作本地聊天
机器人。**

如果您知道自己在做什么，请查看 `inference` 文件夹以启动并运行推理系统，或者查看
`--profile inference` 以及上述命令中的 `--profile ci`。

## The Vision

## 愿景

我们不会停止复制 ChatGPT。我们希望建立未来的助手，不仅能够写电子邮件和求职信，而
且能够做有意义的工作，使用 api，动态研究信息，以及更多能够被任何人个性化和扩展。
而且我们希望以一种开放且可访问的方式来做到这一点，这意味着我们不仅必须构建一个出
色的助手，而且还必须使其足够小且高效，可以在消费类硬件上运行。

## 计划

##### 我们希望通过遵循 InstructGPT 论文中概述的 3 个步骤，尽快获得初始 MVP [GPT 指导文件](https://arxiv.org/abs/2203.02155)

1. 收集高质量的人工生成的指令-履行样本 (快速响应)，目标> 50k。我们设计了一个众包
   流程来收集和审查提示。我们不想对洪水/有毒/垃圾邮件/垃圾/个人信息数据进行培训
   。我们将有一个排行榜来激励显示进步和最活跃用户的社区。奖励将被给予最高贡献者

2. 对于每个收集的提示，我们将采样多个完成。然后，将随机向用户显示一个提示的完成
   情况，以将其从最佳到最差进行排名。同样，这应该发生众包，例如我们需要处理不可
   靠的潜在恶意用户。至少必须收集独立用户的多次投票才能衡量总体协议。收集的排名
   数据将用于训练奖励模型。

3. 现在遵循基于提示和奖励模型的 RLHF 训练阶段。

然后，我们可以采用结果模型，并继续完成采样步骤 2 进行下一次迭代。

### 相关 PPT

[愿景和路线图](https://docs.google.com/presentation/d/1n7IrAOVOqwdYgiYrXc8Sj0He8krn5MVZO_iLkCjTtu0/edit?usp=sharing)

[重要数据结构](https://docs.google.com/presentation/d/1iaX_nxasVWlvPiSNs0cllR9L_1neZq0RJxd6MFEalUY/edit?usp=sharing)

## 您如何提供帮助

所有开源项目都是从像你这样的人开始的。开源是这样一种信念，即如果我们合作，我们可
以共同为人类造福我们的知识和技术。查看我们的 [贡献指南](./CONTRIBUTING.md) 开始
。
