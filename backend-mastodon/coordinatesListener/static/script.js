function updateJsons() {
  var checkboxes = document.getElementsByName('status-checkbox');

  var updates = [];
  var deletes = [];

  for (var i = 0; i < checkboxes.length; i++) {
    var checkbox = checkboxes[i];
    var checkboxValue = checkbox.value;
    var row = checkbox.parentNode.parentNode;
    var latitudeInput = row.cells[3].querySelector('input');
    var longitudeInput = row.cells[4].querySelector('input');

    if (checkbox.checked) {
      var updateData = {
        id: checkboxValue,
        latitude: latitudeInput.value,
        longitude: longitudeInput.value
      };

      updates.push(updateData);
    } else {
      deletes.push(checkboxValue);
    }
  }

  Promise.all([
    fetch('/update-jsons', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updates)
    }),
    Promise.all(deletes.map(file =>
      fetch(`/data/${file}.json`, {
        method: 'DELETE'
      })
    ))
  ])
    .then(([updateResponse, deleteResponses]) => {
      return Promise.all([updateResponse.json(), ...deleteResponses.map(response => response.json())]);
    })
    .then(data => {
      console.log(data);
      updateHtml(); // Call the function to update the status_list.html file
    })
    .catch(error => console.error(error));
}

function updateHtml() {
  fetch('/update-html', {
    method: 'POST'
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error updating HTML file');
      }
      return response.text();
    })
    .then(data => {
      console.log(data);
      location.reload(); // Reload the page after updating the HTML file
    })
    .catch(error => {
      console.error('Error:', error);
      location.reload(); // Reload the page on error
    });
}

function toggleCheckboxes() {
  const selectAllCheckbox = document.getElementById('select-all-checkbox');
  const checkboxes = document.getElementsByName('status-checkbox');

  checkboxes.forEach((checkbox) => {
    checkbox.checked = selectAllCheckbox.checked;
  });
}
