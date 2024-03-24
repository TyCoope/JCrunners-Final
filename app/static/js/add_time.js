document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('roster').addEventListener('change', updateRunnersTable);
    document.getElementById('race_type').addEventListener('change', updateRunnersTable);

    function updateRunnersTable() {
        var rosterId = document.getElementById('roster').value;
        var raceTypeId = document.getElementById('race_type').value;
        var raceId = document.getElementById('race_id').value;  // Assuming you have a hidden input field with id 'race_id' in your HTML

        // Update the race_type_id hidden input field's value
        document.getElementById('race_type_id').value = raceTypeId;

        // Send an AJAX request to the server to fetch the runners
        fetch('/add_race_time/' + raceId + '?roster_id=' + rosterId + '&race_type_id=' + raceTypeId)
            .then(response => response.json())
            .then(runners => {
                // Clear the table
                var table = document.getElementById('runners_table');
                table.innerHTML = '';

                // Populate the table with the runners
                runners.forEach(runner => {
                    var row = table.insertRow();
                    var cell = row.insertCell();
                    cell.textContent = runner.first_name + ' ' + runner.last_name;

                    // Create a text input field for duration_time
                    var input = document.createElement('input');
                    input.type = 'text';
                    input.name = 'time_' + runner.runner_id;
                    row.insertCell().appendChild(input);

                    // Create a hidden input field for runner_id
                    var hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'runner_id_' + runner.runner_id;
                    hiddenInput.value = runner.runner_id;
                    row.appendChild(hiddenInput);
                });
            });
    }
});