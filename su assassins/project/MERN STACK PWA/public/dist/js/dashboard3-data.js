/*Dashboard3 Init*/
 
"use strict"; 

/*****Ready function start*****/
$(document).ready(function(){
	$('#support_table').DataTable({
		"bFilter": false,
		"bLengthChange": false,
		"bPaginate": false,
		"bInfo": false,
	});
	if( $('#chart_7').length > 0 ){
		var ctx7 = document.getElementById("chart_7").getContext("2d");
		var data7 = {
			 labels: [
			"Low",
			"Medium",
			"High"
		],
		datasets: [
			{
				data: [300, 500, 50],
				backgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)"
				],
				hoverBackgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)"
				]
			}]
		};
		
		var doughnutChart = new Chart(ctx7, {
			type: 'doughnut',
			data: data7,
			options: {
				animation: {
					duration:	2000
				},
				responsive: true,
				maintainAspectRatio:false,
				legend: {
					labels: {
					fontFamily: "Poppins",
					fontColor:"#878787"
					}
				},
				elements: {
					arc: {
						borderWidth: 0
					}
				},
				tooltip: {
					backgroundColor:'rgba(33,33,33,1)',
					cornerRadius:0,
					footerFontFamily:"'Poppins'"
				}
			}
		});
	}
	if( $('#chart_6').length > 0 ){
		var ctx6 = document.getElementById("chart_6").getContext("2d");
		var data6 = {
			 labels: [
			"Completed",
			"Delayed",
			"Overdue",
			"Not Started"
		],
		datasets: [
			{
				data: [300, 50, 100,70],
				backgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)",
					"rgba(237,111,86,.6)",
				],
				hoverBackgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)",
					"rgba(237,111,86,.6)",
				]
			}]
		};
		
		var pieChart  = new Chart(ctx6,{
			type: 'pie',
			data: data6,
			options: {
				animation: {
					duration:	3000
				},
				responsive: true,
				maintainAspectRatio:false,
				legend: {
					labels: {
					fontFamily: "Poppins",
					fontColor:"#878787"
					}
				},
				tooltip: {
					backgroundColor:'rgba(33,33,33,1)',
					cornerRadius:0,
					footerFontFamily:"'Poppins'"
				},
				elements: {
					arc: {
						borderWidth: 0
					}
				}
			}
		});
	}
	
	if($('#morris_extra_bar_chart').length > 0)
		// Morris bar chart
		Morris.Bar({
			element: 'morris_extra_bar_chart',
			data: [{
				y: '2006',
				a: 100,
				b: 90,
				c: 60
			}],
			xkey: 'y',
			ykeys: ['a', 'b', 'c'],
			labels: ['A', 'B', 'C'],
			barColors:['#2ecd99', '#4e9de6', '#f0c541'],
			barOpacity: 0.6,
			hideHover: 'auto',
			grid: false,
			resize: true,
			barGap:7,
			gridTextColor:'#878787',
			gridTextFamily:"Poppins"
		});

});
/*****Ready function end*****/

/*****Load function start*****/
$(window).load(function(){
	window.setTimeout(function(){
		$.toast({
			heading: 'Welcome to Philbert',
			text: 'Use the predefined ones, or specify a custom position object.',
			position: 'top-right',
			loaderBg:'#f0c541',
			icon: 'success',
			hideAfter: 3500, 
			stack: 6
		});
	}, 3000);
});
/*****Load function* end*****/

/*****Sparkline function start*****/
var sparklineLogin = function() { 
		if( $('#sparkline_4').length > 0 ){
			$("#sparkline_4").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
				type: 'line',
				width: '100%',
				height: '45',
				lineColor: '#2ecd99',
				fillColor: 'rgba(46,205,153,.6)',
				minSpotColor: '#2ecd99',
				maxSpotColor: '#2ecd99',
				spotColor: '#2ecd99',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#2ecd99'
			});
		}	
	}
	var sparkResize;
/*****Sparkline function end*****/

$(window).resize(function(e) {
	clearTimeout(sparkResize);
	sparkResize = setTimeout(sparklineLogin, 200);
});
sparklineLogin();