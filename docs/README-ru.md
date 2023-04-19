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

# Оглавление

- [Что такое Open Assistant?](#what-is-open-assistant)
- [Полезные ссылки](#useful-links)
- [Как попробовать это](#)
- [Видение](#the-vision)
- [План](#the-plan)
- [Как вы можете помочь](#how-you-can-help)

---

## Что такое Open Assistant?

<p align="center">
Open Assistant - это проект, призванный дать всем желающим доступ к большой чат-ориентированной
языковой модели.
</p>

Мы считаем, что таким образом мы создадим революцию в инновациях в области
языке. Подобно тому, как стабильная диффузия помогла миру создать искусство и
изображения по-новому, мы надеемся, что Open Assistant поможет улучшить мир путем
улучшения самого языка.

# Полезные ссылки

- [Сбор данных](https://open-assistant.io)

- [Чат](https://open-assistant.io/chat)

- [Проектная документация](https://projects.laion.ai/Open-Assistant/)

## Как это попробовать

### Общение с ИИ в чате

Онлайн чат теперь доступен [здесь](https://open-assistant.io/chat). Авторизуйтесь и начинайте общаться!
Пожалуйста, реагируйте на ответы помощника пальцем вверх или вниз в чате.

### Вклад в коллекцию данных

Общайтесь онлайн в чате [здесь](https://open-assistant.io/chat). Зайдите на сайт, авторизуйтесь и начинайте выполнять задания!
Мы хотим собрать большой объем качественных данных.
Оценивая, маркируя, ранжируя результаты работы модели вы будете непосредственно помогать улучшать возможности Open Assistant.

### Запуск проекта локально(без чата)

**Вам не нужно запускать проект локально, если вы не вносите свой вклад в
процесс разработки. Ссылка на веб-сайт, указанная выше, приведет вас на общедоступный веб-сайт
где вы можете использовать приложение для сбора данных и чат**

Если вы хотите запустить приложение локально для разработки,
вы можете установить весь стек, необходимый для работы **Open-Assistant**, включая
сайт, бэкенд и связанные с ним сервисы, с помощью Docker.

Чтобы запустить демонстрацию, выполните следующее в корневом каталоге репозитория (см.
[этот FAQ](https://projects.laion.ai/Open-Assistant/docs/faq#docker-compose-instead-of-docker-compose)
если у вас возникнут проблемы):

```sh
docker compose --profile ci up --build --attach-dependencies
```

Затем перейдите по адресу `http://localhost:3000` (загрузка может занять некоторое время) и
взаимодействуйте с веб-сайтом.

> **Примечание:** Если при сборке возникли проблемы, пожалуйста, обратитесь к разделу
> [FAQ](https://projects.laion.ai/Open-Assistant/docs/faq) и ознакомьтесь с
> записями о Docker.

> **Примечание:** При входе в систему по электронной почте перейдите по адресу `http://localhost:1080`, чтобы
> получить волшебную ссылку для входа по электронной почте.

> **Примечание:** Если вы хотите запустить это в стандартной среде разработки
> (["devcontainer"](https://code.visualstudio.com/docs/devcontainers/containers))
> используя
> [vscode locally](https://code.visualstudio.com/docs/devcontainers/create-dev-container#_create-a-devcontainerjson-file)
> или в веб-браузере, используя
> [GitHub Codespaces](https://github.com/features/codespaces), вы можете использовать
> предоставленную папку [`.devcontainer`](.devcontainer/).

### Запуск установки разработки локально для чата

**Вам не нужно запускать проект локально, если вы не вносите свой вклад в
процесс разработки. Ссылка на сайт, указанная выше, приведет вас на публичный сайт,
где вы можете использовать приложение для сбора данных и чат.**

**Также обратите внимание, что локальная установка предназначена только для разработки и не предназначена для использования в качестве локального чатбота,
если только вы не знаете, что делаете.**.

Если вы знаете, что делаете, то смотрите папку `inference` для получения информации об этом,
или взгляните на `--profile inference` в
дополнение к `--profile ci` в приведенной выше команде.

## Видение

Мы не собираемся останавливаться на воспроизведении ChatGPT. Мы хотим создать помощника
будущего, способного не только писать электронную почту и сопроводительные письма, но и выполнять осмысленную работу.
работу, использовать API, динамически исследовать информацию и многое другое, с возможностью персонализации и расширения возможностей для каждого. 
Мы хотим сделать это открытым и доступным способом, это значит, что мы должны не только создать отличного
помощника, но и сделать его достаточно маленьким и эффективным, чтобы он мог работать на потребительском
аппаратном обеспечении.

## План

##### Мы хотим как можно быстрее получить начальный MVP, следуя 3 этапам, описанным в [InstructGPT paper](https://arxiv.org/abs/2203.02155).

1. Собрать высококачественные сгенерированные человеком образцы выполнения инструкций
   (подсказка + ответ), цель >50k. Мы разработали краудсорсинговый процесс для сбора
   и рецензирования подсказок. Мы не хотим тренироваться на
   флуде/токсичных/спаме/мусоре/личной информации. У нас будет
   таблица лидеров для мотивации сообщества, показывающая прогресс и наиболее активных
   пользователей. Лучшие участники будут награждаться призами.
2. Для каждой из собранных подсказок мы сделаем выборку из нескольких завершений.
   Затем завершения одной подсказки будут показаны пользователям в случайном порядке, чтобы они ранжировали их
   от лучшего к худшему. Опять же, это должно происходить на основе толпы, например, нам необходимо
   иметь дело с ненадежными потенциально злонамеренными пользователями. По крайней мере, несколько голосов
   Независимые пользователи должны быть собраны, чтобы измерить общее согласие. Сайт
   собранные данные о рейтинге будут использованы для обучения модели вознаграждения.
3. Далее следует этап обучения RLHF на основе подсказок и модели вознаграждения.
   модели.

Затем мы можем взять полученную модель и продолжить шаг 2 для следующей итерации.

### Slide Decks

[Видение & Дорожная карта](https://docs.google.com/presentation/d/1n7IrAOVOqwdYgiYrXc8Sj0He8krn5MVZO_iLkCjTtu0/edit?usp=sharing)

[Important Data Structures](https://docs.google.com/presentation/d/1iaX_nxasVWlvPiSNs0cllR9L_1neZq0RJxd6MFEalUY/edit?usp=sharing)

## Как вы можете помочь

Все проекты с открытым исходным кодом начинаются с таких людей, как вы. Открытый исходный код - это вера в то,
что если мы будем сотрудничать, то сможем вместе подарить наши знания и технологии всему
миру на благо человечества.

Ознакомьтесь с нашим [Руководством по вкладу](./docs/CONTRIBUTING-ru.md) to get started.
