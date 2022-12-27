Please provide a reply to the assistant.
Here is the conversation so far:
{% for message in task.conversation.messages %}{% if message.is_assistant %}
:robot: Assistant:
{{ message.text }}
{% else %}
:person_red_hair: User:
**{{ message.text }}**"
{% endif %}{% endfor %}
{% if task.hint %}
Hint: {{ task.hint }}
{% endif %}
