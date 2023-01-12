Rank the following prompts:
{% for prompt in task.prompts %}
{{loop.index}}: {{prompt}}{% endfor %}

:scroll: Reply with the numbers of best to worst prompts separated by commas (example: "4,1,3,2").
