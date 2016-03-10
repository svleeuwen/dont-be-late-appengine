<strong>{{ title }}</strong>
<ul class="list-unstyled">
  <li>
    <a href="?{{ all_query }}">{% if not active_choice %}<strong>All</strong>{% else %}All{% endif %}</a>
  </li>
  {% for choice in choices %}
    <li>
      <a class="active" href="?{{ choice.query }}">{% if active_choice == choice.value %}
        <strong>{{ choice.label }}</strong>{% else %}{{ choice.label }}{% endif %}</a>
    </li>
  {% endfor %}
</ul>