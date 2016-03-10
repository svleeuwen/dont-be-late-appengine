<select class="form-control input-sm" name="_action">
  <option value="">Select an action</option>
  {% for action, label in actions %}
    <option value="{{ action }}">{{ label }}</option>
  {% endfor %}
</select>
<button type="submit" class="btn btn-default btn-sm">Go</button>