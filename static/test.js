var energy = [];
var maximum = [0,0];

var latitude = 34.5;

function calculate(){

    energy = [];
    maximum = [0,0];

    var l = (latitude/180)*Math.PI; //latitude
    var p = (23.4371/180)*Math.PI; //tilt of earth
    var points = 1000; //number of calculations
    var min = 0;
    var max = (Math.PI)/2;

    var incrament = (Math.abs(max)-Math.abs(min))/points;
    var d = (2*Math.PI)/365;

    for(j=0;j<=points;j++)
    {
        var x = min+incrament*j;

        var y = 0;

        for(i=1;i<=365;i++)
        {

            var inside = Math.tan(l)*Math.tan(p*Math.cos(d*i)); // inside the acos
            if(inside > 1)
            {
                inside = 1;
            }
            if(inside < -1)
            {
                inside = -1;
            }
            var a = Math.acos(inside);
            var b = 2*Math.PI-Math.acos(inside);

            var calc = Math.cos(l-x)*Math.cos(p*Math.cos(d*i))*(Math.sin(a)-Math.sin(b))
                +Math.sin(l-x)*Math.sin(p*Math.cos(d*i))*(b-a);

            y = y + calc;
        }

        energy.push([x,y]);
    }


    for(k=0;k<=points;k++)
    {
        if(energy[k][1] > maximum[1])
        {
            maximum[1] = energy[k][1];
            maximum[0] = energy[k][0];
        }
    }

    document.getElementById("max_theta").innerHTML = "Maximum point, theta = "+ maximum[0] + " =" + (maximum[0]/Math.PI)*180+" degrees"; // amount of energy = "+maximum[1];

    activate();
}

function set_latitude()
{
    latitude = document.getElementById("set_latitude").value;
    calculate();
}

// GRAPHING STUFF FROM HERE:

google.charts.load('current', {packages: ['corechart', 'line']});
function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'theta');
    data.addColumn('number', 'f(θ)');
    data.addRows(energy);

    var options = {
        curveType: 'function',
    };


    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data,options);
}

function activate()
{
    document.getElementById("data1").innerHTML = "latitude = " + latitude;
    google.charts.setOnLoadCallback(drawChart); //activate graph
}

calculate();