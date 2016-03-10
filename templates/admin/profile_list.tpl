{% extends "admin/base.tpl" %}
{% block title %}
  Profiles
{% endblock %}

{% block head_extras %}
{% endblock %}

{% block filters_extras %}
{% endblock %}

{% block body_class %}change-list{% endblock %}

{% block content %}
  <h1>Profiles</h1>
  <form class="form-inline" action="" method="post">
    <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>
    <div class="form-group">
      <a class="btn btn-primary" href="/admin/profile/add" role="button">Create new Profile</a>
    </div>
    {% if actions %}
      <div class="form-group pull-right actions">
        {{ actions|safe }}
      </div>
    {% endif %}
    <table class="table table-striped">
      <tr>
        <th><input type="checkbox" id="actions-select-all"/></th>
        <th>User id</th>
        <th>Boxcar access token</th>
        <th>Boxcar send push</th>
        <th class="text-right">Actions</th>
      </tr>
      {% for object in object_list %}
        <tr>
          <td><input type="checkbox" name="_selected_action" value="{{ object.key.urlsafe() }}"/></td>
          <td>{{ object.user_id }}</td>
          <td>{{ object.boxcar_access_token }}</td>
          <td>
            {% if object.boxcar_send_push %}
              <span class="glyphicon glyphicon-ok"></span>
            {% endif %}
          </td>
          <td class="text-right action-buttons">
            <span class="btn-group btn-group-sm">
              <a class="btn btn-warning" href="/admin/profile/{{ object.key.id() }}" role="button" title="Edit">
                <i class="glyphicon glyphicon-edit"></i> Edit</a>
              <a class="btn btn-danger" href="/admin/profile/{{ object.key.id() }}/delete"
                 role="button" title="Delete"><i class="glyphicon glyphicon-remove"></i> Delete</a>
            </span>
          </td>
        </tr>
      {% endfor %}
    </table>
  </form>

{% endblock %}

{% block script_extras %}
{% endblock %}
