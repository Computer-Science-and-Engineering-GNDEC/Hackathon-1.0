/*Dashboard Init*/
 
"use strict"; 

/*****Ready function start*****/
$(document).ready(function(){
	if( $('#ct_chart_1').length > 0 ){
		new Chartist.Bar('#ct_chart_1',{
			labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10'],
			  series: [
				[1, 2, 4, 8, 6, -2, -1, -4, -6, -2]
			  ]
			},
			{
			  high: 10,
			  low: -10,
			  axisX: {
				labelInterpolationFnc: function(value, index) {
				  return index % 2 === 0 ? value : null;
				}
			  }
			});
	}
	
	if($('#morris_extra_line_chart').length > 0)
		Morris.Line({
        element: 'morris_extra_line_chart',
        data: [{
            period: '2010',
            iphone: 50,
            ipad: 80,
            itouch: 20
        }, {
            period: '2011',
            iphone: 130,
            ipad: 100,
            itouch: 80
        }, {
            period: '2012',
            iphone: 80,
            ipad: 60,
            itouch: 70
        }, {
            period: '2013',
            iphone: 70,
            ipad: 200,
            itouch: 140
        }, {
            period: '2014',
            iphone: 180,
            ipad: 150,
            itouch: 140
        }, {
            period: '2015',
            iphone: 105,
            ipad: 100,
            itouch: 80
        },
         {
            period: '2016',
            iphone: 250,
            ipad: 150,
            itouch: 200
        }],
        xkey: 'period',
        ykeys: ['iphone', 'ipad', 'itouch'],
        labels: ['iPhone', 'iPad', 'iPod Touch'],
        pointSize: 2,
        fillOpacity: 0,
		lineWidth:2,
		pointStrokeColors:['#2ecd99', '#f0c541', '#ed6f56'],
		behaveLikeLine: true,
		grid: false,
		hideHover: 'auto',
		lineColors: ['#2ecd99', '#f0c541', '#ed6f56'],
		resize: true,
		gridTextColor:'#878787',
		gridTextFamily:"Poppins"
        
    });
	
	if( $('#ct_chart_5').length > 0 ){
		new Chartist.Bar('#ct_chart_5', {
		  labels: ['First quarter of the year', 'Second quarter of the year', 'Third quarter of the year', 'Fourth quarter of the year'],
		  series: [
			[60000, 40000, 80000, 70000],
			[40000, 30000, 70000, 65000],
			[8000, 3000, 10000, 6000]
		  ]
		}, {
		  seriesBarDistance: 10,
		  axisX: {
			offset: 60
		  },
		  axisY: {
			offset: 80,
			labelInterpolationFnc: function(value) {
			  return value + ' CHF'
			},
			scaleMinSpace: 15
		  }
		});
	}
		if( $('#chart_7').length > 0 ){
		var ctx7 = document.getElementById("chart_7").getContext("2d");
		var data7 = {
			 labels: [
			"lab 1",
			"lab 2",
			"lab 3"
		],
		datasets: [
			{
				data: [300, 50, 100],
				backgroundColor: [
					"rgba(46,205,153,.6)",
					"rgba(240,197,65,.6)",
					"rgba(78,157,230,.6)"
				],
				hoverBackgroundColor: [
					"rgba(46,205,153,.6)",
					"rgba(240,197,65,.6)",
					"rgba(78,157,230,.6)"
				]
			}]
		};
		
		var doughnutChart = new Chart(ctx7, {
			type: 'doughnut',
			data: data7,
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
	if( $('#employee_table').length > 0 ) {
		$('#employee_table').DataTable({
		 "bFilter": false,
		 "bLengthChange": false,
		 "bPaginate": false,
		 "bInfo": false,
		});
	}
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

var sparklineLogin = function() { 
	if( $('#sparkline_1').length > 0 ){
		$("#sparkline_1").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}	
	if( $('#sparkline_2').length > 0 ){
		$("#sparkline_2").sparkline([0,2,8,6,8], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}	
	if( $('#sparkline_3').length > 0 ){
		$("#sparkline_3").sparkline([0, 23, 43, 35, 44, 45, 56, 37, 40, 45, 56, 7, 10], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}
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
	$(window).resize(function(e) {
		clearTimeout(sparkResize);
		sparkResize = setTimeout(sparklineLogin, 200);
	});
sparklineLogin();