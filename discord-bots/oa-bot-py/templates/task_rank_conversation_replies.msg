Here is the conversation so far:
{% for message in task.conversation.messages %}{% if message.is_assistant %}
:robot: Assistant:
{{ message.text }}
{% else %}
:person_red_hair: User:
**{{ message.text }}**"
{% endif %}{% endfor %}
Rank the following replies:
{% for reply in task.replies %}
{{loop.index}}: {{reply}}{% endfor %}

:scroll: Reply with the numbers of best to worst prompts separated by commas (example: "4,1,3,2").
