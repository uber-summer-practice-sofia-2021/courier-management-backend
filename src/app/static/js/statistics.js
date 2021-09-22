$(document).ready(function () {
    google.charts.load('current', {
        'packages': ['corechart']
    });
    google.charts.setOnLoadCallback(drawChart);

    script = document.getElementById("script-statistics");
    completed = parseInt(script.getAttribute('completed'));
    cancelled = parseInt(script.getAttribute('cancelled'));

    function drawChart() {

        var data = google.visualization.arrayToDataTable([
            ['Trips', 'Count'],
            ['Completed', completed],
            ['Cancelled', cancelled],
        ]);

        var options = {
            titlePosition: 'none',
            titleTextStyle: {
                color: 'white',
                fontSize: 20,
                fontName: 'serif',
                bold: true,
            },
            pieHole: 0.4,
            legend: {
                position: 'bottom',
                textStyle: {
                    fontName: 'Sans-Serif',
                    color: 'white',
                },
            },
            maximize: true,
            slices: {
                0: {
                    color: 'green'
                },
                1: {
                    color: 'red'
                }
            },
            backgroundColor: 'transparent',
            sliceVisibilityThreshold: 0,
            fontSize: 16,
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart'));

        chart.draw(data, options);
    }

    $("text[x='127']").attr('x', '200');
});