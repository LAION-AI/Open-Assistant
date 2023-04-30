Act as the assistant and reply to the user.
Here is the conversation so far:
{% for message in task.conversation.messages %}
{% if message.is_assistant %}
:robot: Assistant:
{{ message.text }}
{% else %}
:person_red_hair: User:
**{{ message.text }}**"
{% endif %}
{% endfor %}
:robot: Assistant: { human, pls help me! ... }
