function updateJsons() {
  var checkboxes = document.getElementsByName('status-checkbox');

  for (var i = 0; i < checkboxes.length; i++) {
    var checkbox = checkboxes[i];
    var checkboxValue = checkbox.value;
    var row = checkbox.parentNode.parentNode;
    var latitudeInput = row.cells[3].querySelector('input');
    var longitudeInput = row.cells[4].querySelector('input');

    if (checkbox.checked) {
      var jsonData = {
        'latitude': latitudeInput.value,
        'longitude': longitudeInput.value
      };

      fetch(`/data/${checkboxValue}.json`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
      })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    } else {
      fetch(`/data/${checkboxValue}.json`, {
        method: 'DELETE'
      })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }
  }
}
