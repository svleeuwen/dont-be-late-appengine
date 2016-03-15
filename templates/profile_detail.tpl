<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Edit profile</title>

  <link rel="stylesheet" href="/static/admin/third_party/bootstrap/css/bootstrap.css">
  <link rel="stylesheet" href="/static/admin/third_party/bootstrap/css/bootstrap-theme.css">
</head>
<body>
<div class="container">
  <h1>Edit profile</h1>
  {% if silence_until %}
    <p>Stil tot <strong>{{ silence_until }}</strong></p>
  {% endif %}

  <form method="post">
    <input type="hidden" id="xsrf" name="xsrf" value="{{ _xsrf }}"/>
    <label>Stil voor
      <select name="silence">
        <option value="1">1 uur</option>
        <option value="2">2 uur</option>
        <option value="4">4 uur</option>
        <option value="8">8 uur</option>
        <option value="12">12 uur</option>
        <option value="24">24 uur</option>
      </select>
      uur
    </label>
    <button class="btn btn-success" type="submit">Stel in</button>
    <br>
    <br>
    <button class="btn btn-danger" name="cancel_silence" value="1">Annuleer stil</button>
  </form>
</div>
</body>
</html>