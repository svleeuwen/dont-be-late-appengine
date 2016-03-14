<!DOCTYPE html>
<html lang="en">
  <head>
    {% block head %}
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <title>{% block title %}{% endblock %} | Don't be late</title>

    <link rel="stylesheet" href="/static/admin/third_party/bootstrap/css/bootstrap.css">
    <link rel="stylesheet" href="/static/admin/third_party/bootstrap/css/bootstrap-theme.css">
    <link rel="stylesheet" href="/static/admin/style.css">
    <script src="/static/admin/third_party/jquery/jquery.js"></script>
    <script src="/static/admin/third_party/bootstrap/js/bootstrap.js"></script>
    {% block head_extras %}{% endblock %}
    {% endblock %}
  </head>
  <body class="{% block body_class %}{% endblock %}">
    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/admin">Don't be late</a>
        </div>
      </div>
    </nav>

    <div class="container-fluid"  id="mainPage">
      <div class="col-sm-2 col-md-2">
        <br />
        <ul class="nav nav-sidebar">
          <li><a href="/admin">Home</a></li>
          <li><a href="/admin/profile">Profiles</a></li>
          <li><a href="/admin/dont-be-late">API preview run</a></li>
        </ul>
      </div>

      <div class="{% if filters %}col-sm-8 col-md-8{% else %}col-sm-10 col-md-10{% endif %}" id="content">
        {% if error %}
          <div class="alert alert-danger" role="alert">
            {{ error }}
          </div>
        {% endif %}
        {% for msg, level in messages %}
          <div class="alert alert-{% if level %}{{ level }}{% else %}info{% endif %}" role="alert">
            {{ msg }}
          </div>
        {% endfor %}
        {% block content %}
          <h3>Project Tango</h3>
          <p>Choose a section in the menu on the left to begin.</p>
        {% endblock %}
      </div>

      {% if filters %}
        <div class="col-sm-2 col-md-2 filters">
          <h3>Filters</h3>
          <hr>
          {% block filters_extras %}
          {% endblock %}
          {{ filters|safe }}
        </div>
      {% endif %}
    </div>
    {% block script_extras %}
    {% endblock %}
  </body>
</html>
