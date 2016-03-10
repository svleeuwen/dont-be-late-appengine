{% extends "admin/base.tpl" %}

{% block title %}
Admin home
{% endblock %}

{% block content %}
  <h3>Don't be late</h3>
  <div class="row">
    <div class="col-md-4">
      <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>
    </div>
  </div>
{% endblock %}


{% block script_extras %}
  <script>
  </script>
{% endblock %}
