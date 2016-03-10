{% extends "admin/base.tpl" %}
{% block title %}
  Profile
{% endblock %}
{% block content %}
  <br/>
  <p>
    <a href="/admin/profile" class="btn btn-default"><span class="glyphicon glyphicon-arrow-left"></span> Profiles</a>
  </p>
  <h1>Delete {{ object }}</h1>

  <form method="post" class="form">
    <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>

    <div class="form-group">
      <p><label>Are you sure you want to delete this profile?</label></p>

      <p>
        <a href="/admin/profile" class="btn btn-default">Cancel</a>
        <button type="submit" class="btn btn-danger">Delete profile</button>
      </p>
    </div>

  </form>

  <br/><br/>


{% endblock %}
