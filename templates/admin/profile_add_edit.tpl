{% extends "admin/base.tpl" %}
{% block title %}
  Profiles
{% endblock %}

{% block head_extras %}
{% endblock %}

{% block content %}
  <br/>

  <form method="post" class="form" enctype="multipart/form-data">
    <p>
      <a href="/admin/profile" class="btn btn-default"><span class="glyphicon glyphicon-arrow-left"></span>
        Profiles</a>
      <button type="submit" class="btn btn-primary">Save</button>
    </p>

    <h1>{{ object }}</h1>

    <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>

    {% for error in errors %}
      {% include 'admin/includes/error_alert.tpl' %}
    {% endfor %}

    <div class="row">
      <div class="form-group col-md-3">
        <label for="user_id">User id</label>
        <input type="text" class="form-control" id="user_id" readonly
               value="{% if object.user_id %}{{ object.user_id }}{% endif %}">
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-3">
        <label for="boxcar_access_token">Boxcar access token</label>
        <input type="text" class="form-control" maxlength="200" id="boxcar_access_token" name="boxcar_access_token"
               value="{% if object.boxcar_access_token %}{{ object.boxcar_access_token }}{% endif %}">
      </div>
    </div>

    <div class="row">
      <div class="form-group col-md-3">
        <label for="boxcar_send_push">
          <input type="checkbox" class="form-control" id="boxcar_send_push" name="boxcar_send_push"
                 {% if object.boxcar_send_push %}checked{% endif %}>
          Boxcar send push token</label>
      </div>
    </div>

    <h3>Routes</h3>
    {% for route in object.get_routes() %}
      <div class="panel">
        <div class="panel-body">
          <input type="hidden" name="route_id" value="{% if route.key %}{{ route.key.id() }}{% endif %}">
          <div class="row">
            <div class="form-group col-md-3">
              <label for="station_from-{{ loop.index }}">Van</label>
              <input type="text" class="form-control" maxlength="200" id="station_from-{{ loop.index }}" name="station_from"
                     value="{% if route.station_from %}{{ route.station_from }}{% endif %}">
            </div>
          </div>
          <div class="row">
            <div class="form-group col-md-3">
              <label for="station_to-{{ loop.index }}">Naar</label>
              <input type="text" class="form-control" maxlength="200" id="station_to" name="station_to"
                     value="{% if route.station_to %}{{ route.station_to }}{% endif %}">
            </div>
          </div>
          <div class="row">
            <div class="form-group col-md-3">
              <label for="departure_time_from-{{ loop.index }}">Vertrektijd van</label>
              <input type="time" class="form-control" maxlength="200" id="departure_time_from-{{ loop.index }}" name="departure_time_from"
                     value="{% if route.departure_time_from %}{{ route.departure_time_from.strftime('%H:%M') }}{% endif %}">
            </div>
            <div class="form-group col-md-3">
              <label for="departure_time_until-{{ loop.index }}">Vertrektijd tot</label>
              <input type="time" class="form-control" maxlength="200" id="departure_time_until-{{ loop.index }}" name="departure_time_until"
                     value="{% if route.departure_time_until %}{{ route.departure_time_until.strftime('%H:%M') }}{% endif %}">
            </div>
          </div>
          <div class="row">
            <div class="form-group col-md-3">
              <label for="departure_time_from_offset-{{ loop.index }}">Vertrektijd offset</label>
              <input type="time" class="form-control" maxlength="200" id="departure_time_from_offset-{{ loop.index }}" name="departure_time_from_offset"
                     value="{% if route.departure_time_from_offset %}{{ route.departure_time_from_offset.strftime('%H:%M') }}{% endif %}">
              <p class="help-block">Begin met checken vanaf deze tijd</p>
            </div>
          </div>
          {% if route.key %}
            <label for="delete-{{ loop.index }}">
              <input type="checkbox" id="delete-{{ loop.index }}" name="delete" value="{{ route.key.id() }}">
              Delete
            </label>
          {% endif %}
        </div>
      </div>
    {% endfor %}


    <hr/>
    <div class="bottom">
      <button type="submit" class="btn btn-primary">Save</button>
    </div>
  </form>

{% endblock %}

{% block script_extras %}
{% endblock %}