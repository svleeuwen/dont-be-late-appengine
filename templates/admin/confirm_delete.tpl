{% extends "admin/base.tpl" %}
{% block title %}
  Confirm delete
{% endblock %}
{% block content %}
  <br/>
  <h1>Confirm delete</h1>

  <form method="post" class="form">
    <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>
    <input type="hidden" name="_confirm" value="1" />
    <input type="hidden" name="_action" value="delete" />

    {% for object in object_list %}
      <input type="hidden" name="_selected_action" value="{{ object.key.urlsafe() }}" />
    {% endfor %}

    <div class="form-group">
      <p><label>Are you sure you want to permanently delete the following objects?</label></p>
      <ul>
        {% for object in object_list %}
          <li>
            {{ object.__class__.__name__ }}: {{ object }}
          </li>
        {% endfor %}
      </ul>
      <p>
        <a href="{{ cancel_url }}" class="btn btn-default">Cancel</a>
        <button type="submit" class="btn btn-danger">Yes, I'm sure</button>
      </p>
    </div>

  </form>

  <br/><br/>


{% endblock %}
