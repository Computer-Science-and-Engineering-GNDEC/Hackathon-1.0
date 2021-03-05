/*Dashboard2 Init*/
"use strict"; 

/*****Ready function start*****/
$(document).ready(function(){
	if($('#chart_1').length > 0) {
		// Area Chart
		var data=[{
            period: '01',
            iphone: 180,
        }, {
            period: '02',
            iphone: 105,
        },
         {
            period: '03',
            iphone: 250,
        },
		 {
            period: '04',
            iphone: 160,
        },
		 {
            period: '05',
            iphone: 130,
        },
		{
            period: '06',
            iphone: 155,
        },
		{
            period: '07',
            iphone: 150,
        },
		{
            period: '08',
            iphone: 110,
        },
		{
            period: '09',
            iphone: 170,
        },
		{
            period: '10',
            iphone: 150,
        },
		{
            period: '11',
            iphone: 150,
        },
		{
            period: '12',
            iphone: 150,
        },
		{
            period: '13',
            iphone: 150,
        },
		{
            period: '14',
            iphone: 150,
        },
		{
            period: '15',
            iphone: 160,
        },
		{
            period: '16',
            iphone: 180,
        }, {
            period: '17',
            iphone: 105,
        },
         {
            period: '18',
            iphone: 250,
        },
		 {
            period: '19',
            iphone: 160,
        },
		 {
            period: '20',
            iphone: 130,
        },
		{
            period: '21',
            iphone: 155,
        },
		{
            period: '22',
            iphone: 150,
        },
		{
            period: '23',
            iphone: 110,
        },
		{
            period: '24',
            iphone: 170,
        },
		{
            period: '25',
            iphone: 150,
        },
		{
            period: '26',
            iphone: 150,
        },
		{
            period: '27',
            iphone: 150,
        },
		{
            period: '28',
            iphone: 150,
        },
		{
            period: '29',
            iphone: 150,
        },
		{
            period: '30',
            iphone: 160,
        }];
		var areaChart = Morris.Area({
				element: 'chart_1',
				data: data,
				xkey: 'period',
				ykeys: ['iphone'],
				labels: ['iPhone'],
				pointSize: 3,
				lineWidth: 2,
				grid: false,
				pointStrokeColors:['#2ecd99'],
				pointFillColors:['#ffffff'],
				behaveLikeLine: true,
				smooth: false,
				hideHover: 'auto',
				lineColors: ['#2ecd99'],
				resize: true,
				gridTextColor:'#878787',
				gridTextFamily:"Poppins",
				parseTime: false,
				fillOpacity:0.6
			});	
	}
	
	if( $('#chart_7').length > 0 ){
		var ctx7 = document.getElementById("chart_7").getContext("2d");
		var data7 = {
			 labels: [
			"lab 1",
			"lab 2",
			"lab 3",
			"lab 4",
			"lab 5"
		],
		datasets: [
			{
				data: [30,70,300, 50, 100],
				backgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)",
					"rgba(237,111,86,.6)",
					"rgba(241,161,199,.6)",
				],
				hoverBackgroundColor: [
					"rgba(240,197,65,.6)",
					"rgba(46,205,153,.6)",
					"rgba(78,157,230,.6)",
					"rgba(237,111,86,.6)",
					"rgba(241,161,199,.6)",
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
				elements: {
					arc: {
						borderWidth: 0
					}
				},
				responsive: true,
				maintainAspectRatio:false,
				percentageInnerCutout: 50,
				legend: {
					display:false
				},
				tooltips: {
					backgroundColor:'rgba(33,33,33,1)',
					cornerRadius:0,
					footerFontFamily:"'Poppins'"
				},
				cutoutPercentage: 70,
				segmentShowStroke: false
			}
		});
	}	
	
	if( $('#chart_8').length > 0 ){
		var ctx7 = document.getElementById("chart_8").getContext("2d");
		var data7 = {
			 labels: [
			"lab 1",
			"lab 2",
			"lab 3",
			"lab 4"
		],
		datasets: [
			{
				data: [80,40,20, 50],
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
		
		var pieChart  = new Chart(ctx7,{
			type: 'pie',
			data: data7,
			options: {
				animation: {
					duration:	3000
				},
				responsive: true,
				maintainAspectRatio:false,
				legend: {
					display:false
				},
				elements: {
					arc: {
						borderWidth: 0
					}
				},
				tooltips: {
					backgroundColor:'rgba(33,33,33,1)',
					cornerRadius:0,
					footerFontFamily:"'Poppins'"
				}
			}
		});
		
		}	
	
	if( $('#pie_chart_4').length > 0 ){
		$('#pie_chart_4').easyPieChart({
			barColor : 'rgba(46,205,153,.6)',
			lineWidth: 20,
			animate: 3000,
			size:	165,
			lineCap: 'square',
			trackColor: 'rgba(33,33,33,0.1)',
			scaleColor: false,
			onStep: function(from, to, percent) {
				$(this.el).find('.percent').text(Math.round(percent));
			}
		});
	}
	
	if( $('#datable_1').length > 0 )
		$('#datable_1').DataTable({
			"bFilter": false,
			"bLengthChange": false,
			"bPaginate": false,
			"bInfo": false,
			
		});
});
/*****Ready function end*****/

/*****Load function start*****/
$(window).load(function(){
	window.setTimeout(function(){
		$.toast({
			heading: 'Welcome to Hound',
			text: 'Use the predefined ones, or specify a custom position object.',
			position: 'top-right',
			loaderBg:'#2ecd99',
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
				lineColor: '#f0c541',
				fillColor: 'rgba(240,197,65,.6)',
				minSpotColor: '#f0c541',
				maxSpotColor: '#f0c541',
				spotColor: '#f0c541',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#f0c541'
			});
		}	
		if( $('#sparkline_5').length > 0 ){
			$("#sparkline_5").sparkline([0,2,8,6,8], {
				type: 'bar',
				width: '100%',
				height: '45',
				barWidth: '10',
				resize: true,
				barSpacing: '10',
				barColor: 'rgba(78,157,230,.6)',
				highlightSpotColor: '#4e9de6'
			});
		}	
		if( $('#sparkline_6').length > 0 ){
			$("#sparkline_6").sparkline([0, 23, 43, 35, 44, 45, 56, 37, 40, 45, 56, 7, 10], {
				type: 'line',
				width: '100%',
				height: '50',
				lineColor: '#2ecd99',
				fillColor: 'transparent',
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