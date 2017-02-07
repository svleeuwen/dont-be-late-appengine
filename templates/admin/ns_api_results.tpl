{% extends "admin/base.tpl" %}
{% block title %}
  Don't be late
{% endblock %}

{% block head_extras %}
{% endblock %}

{% block filters_extras %}
{% endblock %}

{% block body_class %}change-list{% endblock %}

{% block content %}
  <h1>Don't be late</h1>

  {% if delays %}
    <table class="table table-striped">
      <tr>
        <th>Time (delay)</th>
        <th>Train type</th>
        <th>Track</th>
        <th>Status</th>
      </tr>
      {% for delay in delays %}
        <tr>
          <td>{{ delay.departure_planned }} (+{{ delay.delay }} minutes)</td>
          <td>{{ delay.train_type }}</td>
          <td>{% if delay.track_change %}<span class="text-danger">{% endif %}{{ delay.track }}</span></td>
          <td>{{ delay.status }}</td>
        </tr>
      {% endfor %}
    </table>
  {% else %}
    <p>No results</p>
  {% endif %}
  <hr>
{% endblock %}

{% block script_extras %}
  <script>
    $(function () {
       var xsrf = $('#xsrf').val();
    });
  </script>
{% endblock %}
